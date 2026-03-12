"""Registro di log centralizzato per tutte le operazioni di calcolo.

Modulo trasversale collegato a tutte le funzioni del programma.
Registra ogni calcolo, operazione utente, scelta di parametro,
verifica strutturale con tracciamento completo dei passaggi.

Utilizzo::

    from src.core.registro_log import registro, LogCalcolo, LogOperazione

    # Registrare un passaggio di calcolo
    registro.calcolo(
        modulo="flessione_ntc2018",
        operazione="Verifica flessione SLU",
        input_dati={"M_Ed": 150.0, "b": 30, "h": 50},
        output_dati={"M_Rd": 185.3, "rapporto_DC": 0.81},
        normativa="NTC2018 §4.1.2.1.3.2",
        formula="M_Rd = A_s × f_yd × (d - 0.4x)",
        esito="VERIFICATO"
    )

    # Registrare un'operazione utente
    registro.operazione(
        modulo="editor_materiali",
        azione="Selezione materiale",
        dettagli="C25/30 da archivio NTC2018"
    )

    # Accedere al log come lista di voci
    voci = registro.ottieni_voci(modulo="flessione_ntc2018")
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from src.rd2229.logging_bridge import get_logger

_logger = get_logger("registro_log")


class LivelloLog(Enum):
    """Livello di log per le voci del registro."""

    INFO = "INFO"
    AVVISO = "AVVISO"
    ERRORE = "ERRORE"
    CALCOLO = "CALCOLO"
    DEBUG = "DEBUG"


@dataclass
class VoceLog:
    """Singola voce nel registro di log.

    Attributi:
        timestamp: Data e ora della registrazione.
        livello: Livello del log (INFO, CALCOLO, ERRORE, etc.).
        modulo: Nome del modulo che ha generato la voce.
        operazione: Descrizione dell'operazione eseguita.
        input_dati: Dati di input dell'operazione (opzionale).
        output_dati: Risultati dell'operazione (opzionale).
        normativa: Riferimento normativo citato (opzionale).
        formula: Formula utilizzata nel calcolo (opzionale).
        passaggi: Passaggi intermedi del calcolo (opzionale).
        esito: Risultato della verifica: VERIFICATO/NON VERIFICATO (opzionale).
        dettagli: Testo libero con dettagli aggiuntivi (opzionale).
    """

    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    )
    livello: LivelloLog = LivelloLog.INFO
    modulo: str = ""
    operazione: str = ""
    input_dati: dict[str, Any] | None = None
    output_dati: dict[str, Any] | None = None
    normativa: str = ""
    formula: str = ""
    passaggi: list[str] = field(default_factory=list)
    esito: str = ""
    dettagli: str = ""

    def come_testo(self) -> str:
        """Restituisce la voce formattata come testo leggibile."""
        righe = [
            f"[{self.timestamp}] [{self.livello.value}] [{self.modulo}]",
            f"  Operazione: {self.operazione}",
        ]
        if self.normativa:
            righe.append(f"  Normativa: {self.normativa}")
        if self.formula:
            righe.append(f"  Formula: {self.formula}")
        if self.input_dati:
            righe.append(f"  Input: {_formatta_dati(self.input_dati)}")
        if self.passaggi:
            righe.append("  Passaggi:")
            for i, passo in enumerate(self.passaggi, 1):
                righe.append(f"    {i}. {passo}")
        if self.output_dati:
            righe.append(f"  Output: {_formatta_dati(self.output_dati)}")
        if self.esito:
            righe.append(f"  Esito: {self.esito}")
        if self.dettagli:
            righe.append(f"  Dettagli: {self.dettagli}")
        return "\n".join(righe)

    def come_tabella_ascii(self) -> str:
        """Restituisce la voce come tabella ASCII compatta."""
        righe = []
        larghezza = 72
        righe.append("+" + "-" * larghezza + "+")
        righe.append(f"| {'Timestamp:':<14} {self.timestamp:<{larghezza - 16}} |")
        righe.append(f"| {'Modulo:':<14} {self.modulo:<{larghezza - 16}} |")
        righe.append(f"| {'Operazione:':<14} {self.operazione:<{larghezza - 16}} |")
        if self.normativa:
            righe.append(f"| {'Normativa:':<14} {self.normativa:<{larghezza - 16}} |")
        if self.formula:
            # Formula può essere lunga, tronca se necessario
            formula_troncata = self.formula[: larghezza - 16]
            righe.append(f"| {'Formula:':<14} {formula_troncata:<{larghezza - 16}} |")
        if self.input_dati:
            testo_input = _formatta_dati(self.input_dati)[: larghezza - 16]
            righe.append(f"| {'Input:':<14} {testo_input:<{larghezza - 16}} |")
        if self.output_dati:
            testo_output = _formatta_dati(self.output_dati)[: larghezza - 16]
            righe.append(f"| {'Output:':<14} {testo_output:<{larghezza - 16}} |")
        if self.esito:
            righe.append(f"| {'Esito:':<14} {self.esito:<{larghezza - 16}} |")
        righe.append("+" + "-" * larghezza + "+")
        return "\n".join(righe)


class RegistroLog:
    """Registro centralizzato di log per tutte le operazioni del software.

    Thread-safe. Supporta listener per aggiornamento in tempo reale della GUI.

    Esempio::

        registro = RegistroLog()
        registro.calcolo(
            modulo="taglio_ntc2018",
            operazione="Verifica taglio SLU",
            input_dati={"V_Ed": 80.0, "b_w": 30, "d": 45},
            output_dati={"V_Rd_c": 95.2},
            normativa="NTC2018 §4.1.2.1.3.1 + Circ.7 §C4.1.2.1.3.1",
            formula="V_Rd,c = [0.18/γ_c × k × (100 × ρ_l × f_ck)^(1/3)] × b_w × d",
            esito="VERIFICATO"
        )
    """

    def __init__(self, capacita_max: int = 10000) -> None:
        """Inizializza il registro.

        Parametri:
            capacita_max: Numero massimo di voci mantenute in memoria.
                          Le voci più vecchie vengono eliminate (FIFO).
        """
        self._voci: list[VoceLog] = []
        self._lock = threading.Lock()
        self._capacita_max = capacita_max
        self._listener: list[Callable[[VoceLog], None]] = []

    def calcolo(
        self,
        modulo: str,
        operazione: str,
        input_dati: dict[str, Any] | None = None,
        output_dati: dict[str, Any] | None = None,
        normativa: str = "",
        formula: str = "",
        passaggi: list[str] | None = None,
        esito: str = "",
    ) -> VoceLog:
        """Registra un passaggio di calcolo strutturale.

        Parametri:
            modulo: Nome del modulo di calcolo (es. "flessione_ntc2018").
            operazione: Descrizione dell'operazione (es. "Verifica flessione SLU").
            input_dati: Dizionario dei parametri di input con valori.
            output_dati: Dizionario dei risultati.
            normativa: Riferimento normativo completo (articolo, comma, tabella).
            formula: Formula matematica utilizzata.
            passaggi: Lista dei passaggi intermedi del calcolo.
            esito: Esito della verifica (VERIFICATO / NON VERIFICATO).

        Restituisce:
            La voce di log creata.
        """
        voce = VoceLog(
            livello=LivelloLog.CALCOLO,
            modulo=modulo,
            operazione=operazione,
            input_dati=input_dati,
            output_dati=output_dati,
            normativa=normativa,
            formula=formula,
            passaggi=passaggi or [],
            esito=esito,
        )
        self._aggiungi(voce)
        _logger.info(
            "[CALC] %s | %s | %s | Esito: %s", modulo, operazione, normativa, esito or "N/D"
        )
        return voce

    def operazione(
        self,
        modulo: str,
        azione: str,
        dettagli: str = "",
    ) -> VoceLog:
        """Registra un'operazione utente (selezione, apertura, modifica).

        Parametri:
            modulo: Nome del modulo GUI (es. "editor_materiali").
            azione: Descrizione dell'azione (es. "Selezione materiale").
            dettagli: Dettagli aggiuntivi (es. "C25/30 da archivio NTC2018").

        Restituisce:
            La voce di log creata.
        """
        voce = VoceLog(
            livello=LivelloLog.INFO,
            modulo=modulo,
            operazione=azione,
            dettagli=dettagli,
        )
        self._aggiungi(voce)
        _logger.info("[OP] %s | %s | %s", modulo, azione, dettagli)
        return voce

    def avviso(self, modulo: str, messaggio: str, dettagli: str = "") -> VoceLog:
        """Registra un avviso (warning) nel log."""
        voce = VoceLog(
            livello=LivelloLog.AVVISO,
            modulo=modulo,
            operazione=messaggio,
            dettagli=dettagli,
        )
        self._aggiungi(voce)
        _logger.warning("[WARN] %s | %s", modulo, messaggio)
        return voce

    def errore(self, modulo: str, messaggio: str, dettagli: str = "") -> VoceLog:
        """Registra un errore nel log."""
        voce = VoceLog(
            livello=LivelloLog.ERRORE,
            modulo=modulo,
            operazione=messaggio,
            dettagli=dettagli,
        )
        self._aggiungi(voce)
        _logger.error("[ERR] %s | %s | %s", modulo, messaggio, dettagli)
        return voce

    def debug(self, modulo: str, messaggio: str, dettagli: str = "") -> VoceLog:
        """Registra un messaggio di debug."""
        voce = VoceLog(
            livello=LivelloLog.DEBUG,
            modulo=modulo,
            operazione=messaggio,
            dettagli=dettagli,
        )
        self._aggiungi(voce)
        _logger.debug("[DBG] %s | %s", modulo, messaggio)
        return voce

    def ottieni_voci(
        self,
        modulo: str | None = None,
        livello: LivelloLog | None = None,
        testo_ricerca: str | None = None,
        limite: int | None = None,
    ) -> list[VoceLog]:
        """Restituisce le voci del registro, con filtri opzionali.

        Parametri:
            modulo: Filtra per nome modulo (match parziale, case-insensitive).
            livello: Filtra per livello di log.
            testo_ricerca: Ricerca testuale in tutti i campi della voce.
            limite: Numero massimo di voci restituite (le più recenti).

        Restituisce:
            Lista di VoceLog filtrate, ordinate dalla più recente.
        """
        with self._lock:
            risultato = list(self._voci)

        if modulo:
            modulo_lower = modulo.lower()
            risultato = [v for v in risultato if modulo_lower in v.modulo.lower()]

        if livello:
            risultato = [v for v in risultato if v.livello == livello]

        if testo_ricerca:
            testo_lower = testo_ricerca.lower()
            risultato = [v for v in risultato if _voce_contiene(v, testo_lower)]

        # Ordina dalla più recente
        risultato.reverse()

        if limite:
            risultato = risultato[:limite]

        return risultato

    def svuota(self) -> None:
        """Svuota il registro (per test)."""
        with self._lock:
            self._voci.clear()

    def numero_voci(self) -> int:
        """Restituisce il numero totale di voci nel registro."""
        with self._lock:
            return len(self._voci)

    def esporta_testo(self, limite: int | None = None) -> str:
        """Esporta il registro come testo leggibile.

        Parametri:
            limite: Numero massimo di voci da esportare.

        Restituisce:
            Stringa con tutto il log formattato.
        """
        voci = self.ottieni_voci(limite=limite)
        # Ripristina ordine cronologico per export
        voci.reverse()
        righe = [
            "=" * 76,
            "  REGISTRO LOG - RD2229 Calcolo Strutturale",
            f"  Esportato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Voci totali: {self.numero_voci()}",
            "=" * 76,
            "",
        ]
        for voce in voci:
            righe.append(voce.come_testo())
            righe.append("")
        return "\n".join(righe)

    def esporta_csv(self, limite: int | None = None) -> str:
        """Esporta il registro in formato CSV.

        Parametri:
            limite: Numero massimo di voci da esportare.

        Restituisce:
            Stringa CSV con intestazione e dati.
        """
        voci = self.ottieni_voci(limite=limite)
        voci.reverse()
        righe = ["timestamp;livello;modulo;operazione;normativa;formula;esito;dettagli"]
        for v in voci:
            righe.append(
                f"{v.timestamp};{v.livello.value};{v.modulo};{v.operazione};"
                f"{v.normativa};{v.formula};{v.esito};{v.dettagli}"
            )
        return "\n".join(righe)

    def aggiungi_listener(self, callback: Callable[[VoceLog], None]) -> None:
        """Aggiunge un listener notificato ad ogni nuova voce.

        Utilizzato dalla GUI per aggiornamento in tempo reale.

        Parametri:
            callback: Funzione chiamata con la nuova VoceLog.
        """
        self._listener.append(callback)

    def rimuovi_listener(self, callback: Callable[[VoceLog], None]) -> None:
        """Rimuove un listener precedentemente registrato."""
        try:
            self._listener.remove(callback)
        except ValueError:
            pass

    # --- Metodi interni ---

    def _aggiungi(self, voce: VoceLog) -> None:
        """Aggiunge una voce al registro (thread-safe)."""
        with self._lock:
            self._voci.append(voce)
            # Limita dimensione: rimuovi voci più vecchie se necessario
            if len(self._voci) > self._capacita_max:
                self._voci = self._voci[-self._capacita_max :]

        # Notifica listener (fuori dal lock per evitare deadlock)
        for listener in self._listener:
            try:
                listener(voce)
            except Exception:
                _logger.debug("Errore in listener registro log", exc_info=True)


def _formatta_dati(dati: dict[str, Any]) -> str:
    """Formatta un dizionario di dati come stringa leggibile."""
    parti = []
    for chiave, valore in dati.items():
        if isinstance(valore, float):
            parti.append(f"{chiave}={valore:.4g}")
        else:
            parti.append(f"{chiave}={valore}")
    return ", ".join(parti)


def _voce_contiene(voce: VoceLog, testo: str) -> bool:
    """Verifica se una voce contiene il testo cercato in qualsiasi campo."""
    campi = [
        voce.modulo,
        voce.operazione,
        voce.normativa,
        voce.formula,
        voce.esito,
        voce.dettagli,
    ]
    if voce.input_dati:
        campi.append(str(voce.input_dati))
    if voce.output_dati:
        campi.append(str(voce.output_dati))
    for passo in voce.passaggi:
        campi.append(passo)
    return any(testo in c.lower() for c in campi)


# --- Istanza singleton globale ---
# Tutti i moduli del software accedono a questa istanza condivisa.
registro = RegistroLog()
