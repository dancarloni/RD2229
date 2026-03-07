"""Tabulati di Calcolo Strutturale.

Modulo per la generazione di tabulati di calcolo completi e tracciabili.
Ogni verifica produce un tabulato con:
1. Dati di input (geometria, materiale, azioni)
2. Normativa applicata (articolo, comma, tabella, riferimento completo)
3. Formule utilizzate (in notazione Unicode)
4. Passaggi intermedi con valori numerici
5. Risultato finale (VERIFICATO / NON VERIFICATO)
6. Rapporto domanda/capacità (D/C)

Formato: tabelle ASCII nel log + HTML/PDF nella relazione di calcolo.

Utilizzo::

    from src.report.tabulati_calcolo import TabulatoCalcolo, RigaCalcolo

    tab = TabulatoCalcolo(
        titolo="Verifica a flessione — Trave T1",
        normativa="NTC2018 §4.1.2.1.3.2 + Circ. 7/2019 §C4.1.2.1.3.2",
        modulo="flessione_ntc2018",
    )
    tab.aggiungi_sezione_input({
        "b": ("Larghezza sezione", 30, "cm"),
        "h": ("Altezza sezione", 50, "cm"),
        "d": ("Altezza utile", 46, "cm"),
        "A_s": ("Area armatura tesa", 8.04, "cm²"),
    })
    tab.aggiungi_riga_calcolo(
        descrizione="Resistenza di calcolo calcestruzzo",
        formula="f_cd = α_cc × f_ck / γ_c",
        sostituzione="f_cd = 0.85 × 250 / 1.50",
        risultato=141.7,
        unita="kg/cm²",
    )
    tab.imposta_esito(
        domanda=1080000,
        capacita=1330460,
        unita="kg⋅cm",
        nome_domanda="M_Ed",
        nome_capacita="M_Rd",
    )
    print(tab.come_ascii())
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RigaCalcolo:
    """Singola riga di un passaggio di calcolo.

    Attributi:
        descrizione: Spiegazione testuale del passaggio.
        formula: Formula in notazione simbolica (es. "M_Rd = A_s × f_yd × (d - 0.4x)").
        sostituzione: Formula con valori numerici sostituiti.
        risultato: Valore numerico del risultato.
        unita: Unità di misura del risultato.
        nota: Nota aggiuntiva opzionale (riferimento normativo puntuale).
    """
    descrizione: str = ""
    formula: str = ""
    sostituzione: str = ""
    risultato: float | str = 0.0
    unita: str = ""
    nota: str = ""


@dataclass
class SezioneInput:
    """Sezione dei dati di input del tabulato.

    Attributi:
        parametri: Dizionario {nome: (descrizione, valore, unità)}.
    """
    parametri: dict[str, tuple[str, Any, str]] = field(default_factory=dict)


@dataclass
class EsitoVerifica:
    """Esito della verifica strutturale.

    Attributi:
        domanda: Valore della domanda (sollecitazione agente).
        capacita: Valore della capacità (resistenza).
        rapporto_DC: Rapporto domanda/capacità.
        verificato: True se domanda ≤ capacità.
        unita: Unità di misura.
        nome_domanda: Nome del parametro di domanda (es. "M_Ed").
        nome_capacita: Nome del parametro di capacità (es. "M_Rd").
    """
    domanda: float = 0.0
    capacita: float = 0.0
    rapporto_DC: float = 0.0
    verificato: bool = False
    unita: str = ""
    nome_domanda: str = "Domanda"
    nome_capacita: str = "Capacità"


class TabulatoCalcolo:
    """Tabulato di calcolo strutturale completo e tracciabile.

    Genera output in formato ASCII (per log/debug) e HTML (per relazione).
    Ogni tabulato rappresenta una singola verifica strutturale con
    tutti i passaggi documentati.

    Parametri:
        titolo: Titolo della verifica (es. "Verifica a flessione — Trave T1").
        normativa: Riferimento normativo completo.
        modulo: Nome del modulo di calcolo che genera il tabulato.
    """

    def __init__(
        self,
        titolo: str = "",
        normativa: str = "",
        modulo: str = "",
    ) -> None:
        self.titolo = titolo
        self.normativa = normativa
        self.modulo = modulo
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._input = SezioneInput()
        self._righe_calcolo: list[RigaCalcolo] = []
        self._esito: EsitoVerifica | None = None
        self._note_aggiuntive: list[str] = []

    def aggiungi_sezione_input(self, parametri: dict[str, tuple[str, Any, str]]) -> None:
        """Aggiunge i parametri di input al tabulato.

        Parametri:
            parametri: Dizionario {nome_simbolo: (descrizione, valore, unità)}.
                       Es. {"b": ("Larghezza sezione", 30, "cm")}
        """
        self._input.parametri.update(parametri)

    def aggiungi_riga_calcolo(
        self,
        descrizione: str,
        formula: str = "",
        sostituzione: str = "",
        risultato: float | str = 0.0,
        unita: str = "",
        nota: str = "",
    ) -> RigaCalcolo:
        """Aggiunge un passaggio di calcolo al tabulato.

        Parametri:
            descrizione: Spiegazione del passaggio.
            formula: Formula simbolica.
            sostituzione: Formula con valori numerici.
            risultato: Risultato numerico.
            unita: Unità di misura.
            nota: Riferimento normativo puntuale (opzionale).

        Restituisce:
            La riga di calcolo creata.
        """
        riga = RigaCalcolo(
            descrizione=descrizione,
            formula=formula,
            sostituzione=sostituzione,
            risultato=risultato,
            unita=unita,
            nota=nota,
        )
        self._righe_calcolo.append(riga)
        return riga

    def imposta_esito(
        self,
        domanda: float,
        capacita: float,
        unita: str = "",
        nome_domanda: str = "Domanda",
        nome_capacita: str = "Capacità",
    ) -> EsitoVerifica:
        """Imposta l'esito della verifica.

        Parametri:
            domanda: Valore della sollecitazione agente.
            capacita: Valore della resistenza.
            unita: Unità di misura.
            nome_domanda: Nome del parametro di domanda (es. "M_Ed").
            nome_capacita: Nome del parametro di capacità (es. "M_Rd").

        Restituisce:
            L'esito della verifica.
        """
        rapporto = domanda / capacita if capacita != 0 else float('inf')
        self._esito = EsitoVerifica(
            domanda=domanda,
            capacita=capacita,
            rapporto_DC=rapporto,
            verificato=domanda <= capacita,
            unita=unita,
            nome_domanda=nome_domanda,
            nome_capacita=nome_capacita,
        )
        return self._esito

    def aggiungi_nota(self, nota: str) -> None:
        """Aggiunge una nota testuale al tabulato."""
        self._note_aggiuntive.append(nota)

    # --- Generazione output ---

    def come_ascii(self) -> str:
        """Genera il tabulato in formato ASCII (tabella testo).

        Restituisce:
            Stringa con il tabulato formattato come tabella ASCII.
        """
        larghezza = 78
        righe: list[str] = []

        # Intestazione
        righe.append("╔" + "═" * larghezza + "╗")
        righe.append(_centra(self.titolo, larghezza))
        righe.append(_centra(f"Normativa: {self.normativa}", larghezza))
        righe.append(_centra(f"Data: {self.timestamp}", larghezza))
        righe.append("╠" + "═" * larghezza + "╣")

        # Sezione input
        if self._input.parametri:
            righe.append(_centra("DATI DI INPUT", larghezza))
            righe.append("╟" + "─" * larghezza + "╢")
            righe.append(
                "║ " + f"{'Simbolo':<10} {'Descrizione':<35} {'Valore':>12} {'Unità':<10}" +
                " " * (larghezza - 69) + "║"
            )
            righe.append("╟" + "─" * larghezza + "╢")
            for simbolo, (desc, valore, unita) in self._input.parametri.items():
                val_str = _formatta_numero(valore)
                riga = f"║ {simbolo:<10} {desc:<35} {val_str:>12} {unita:<10}"
                riga += " " * (larghezza - len(riga) + 1) + "║"
                righe.append(riga)
            righe.append("╠" + "═" * larghezza + "╣")

        # Sezione calcolo
        if self._righe_calcolo:
            righe.append(_centra("PASSAGGI DI CALCOLO", larghezza))
            righe.append("╟" + "─" * larghezza + "╢")
            for i, riga_calc in enumerate(self._righe_calcolo, 1):
                # Descrizione
                righe.append(
                    f"║ {i:>2}. {riga_calc.descrizione}"
                    + " " * max(0, larghezza - len(f" {i:>2}. {riga_calc.descrizione}") - 1) + "║"
                )
                # Formula
                if riga_calc.formula:
                    testo_f = f"     Formula: {riga_calc.formula}"
                    righe.append(f"║{testo_f}" + " " * max(0, larghezza - len(testo_f)) + "║")
                # Sostituzione
                if riga_calc.sostituzione:
                    testo_s = f"     Calcolo: {riga_calc.sostituzione}"
                    righe.append(f"║{testo_s}" + " " * max(0, larghezza - len(testo_s)) + "║")
                # Risultato
                val_str = _formatta_numero(riga_calc.risultato)
                testo_r = f"     Risultato: {val_str} {riga_calc.unita}"
                righe.append(f"║{testo_r}" + " " * max(0, larghezza - len(testo_r)) + "║")
                # Nota
                if riga_calc.nota:
                    testo_n = f"     Rif.: {riga_calc.nota}"
                    righe.append(f"║{testo_n}" + " " * max(0, larghezza - len(testo_n)) + "║")
                righe.append("╟" + "─" * larghezza + "╢")

        # Sezione esito
        if self._esito:
            righe.append("╠" + "═" * larghezza + "╣")
            righe.append(_centra("ESITO VERIFICA", larghezza))
            righe.append("╟" + "─" * larghezza + "╢")
            d_str = _formatta_numero(self._esito.domanda)
            c_str = _formatta_numero(self._esito.capacita)
            dc_str = f"{self._esito.rapporto_DC:.3f}"
            esito_str = "✓ VERIFICATO" if self._esito.verificato else "✗ NON VERIFICATO"

            testo_d = f"     {self._esito.nome_domanda} = {d_str} {self._esito.unita}"
            testo_c = f"     {self._esito.nome_capacita} = {c_str} {self._esito.unita}"
            testo_dc = f"     D/C = {self._esito.nome_domanda}/{self._esito.nome_capacita} = {dc_str}"
            testo_e = f"     Esito: {esito_str}"

            for t in [testo_d, testo_c, testo_dc, testo_e]:
                righe.append(f"║{t}" + " " * max(0, larghezza - len(t)) + "║")

        # Note aggiuntive
        if self._note_aggiuntive:
            righe.append("╟" + "─" * larghezza + "╢")
            for nota in self._note_aggiuntive:
                testo_nota = f"  NOTA: {nota}"
                # Gestisci righe lunghe
                while len(testo_nota) > larghezza - 2:
                    righe.append(f"║ {testo_nota[:larghezza - 2]}" + "║")
                    testo_nota = "        " + testo_nota[larghezza - 2:]
                righe.append(f"║{testo_nota}" + " " * max(0, larghezza - len(testo_nota)) + "║")

        # Chiusura
        righe.append("╚" + "═" * larghezza + "╝")

        return "\n".join(righe)

    def come_html(self) -> str:
        """Genera il tabulato in formato HTML (per relazione di calcolo).

        Restituisce:
            Stringa HTML con il tabulato formattato.
        """
        html = []
        html.append(f'<div class="tabulato-calcolo" data-modulo="{self.modulo}">')
        html.append(f'<h3>{_escape_html(self.titolo)}</h3>')
        html.append(f'<p class="normativa"><b>Normativa:</b> {_escape_html(self.normativa)}</p>')

        # Input
        if self._input.parametri:
            html.append('<h4>Dati di Input</h4>')
            html.append(
                '<table class="input-table" border="1" cellpadding="4" cellspacing="0" '
                'style="border-collapse:collapse;">'
            )
            html.append('<tr style="background:#e8e8e8;"><th>Simbolo</th>'
                        '<th>Descrizione</th><th>Valore</th><th>Unità</th></tr>')
            for simbolo, (desc, valore, unita) in self._input.parametri.items():
                val_str = _formatta_numero(valore)
                html.append(
                    f'<tr><td><code>{_escape_html(simbolo)}</code></td>'
                    f'<td>{_escape_html(desc)}</td>'
                    f'<td style="text-align:right;">{val_str}</td>'
                    f'<td>{_escape_html(unita)}</td></tr>'
                )
            html.append('</table>')

        # Calcolo
        if self._righe_calcolo:
            html.append('<h4>Passaggi di Calcolo</h4>')
            html.append('<ol class="passaggi-calcolo">')
            for riga in self._righe_calcolo:
                html.append('<li>')
                html.append(f'<b>{_escape_html(riga.descrizione)}</b><br>')
                if riga.formula:
                    html.append(
                        f'<code style="background:#f0f0f0;padding:2px 6px;">'
                        f'{_escape_html(riga.formula)}</code><br>'
                    )
                if riga.sostituzione:
                    html.append(f'<code>{_escape_html(riga.sostituzione)}</code><br>')
                val_str = _formatta_numero(riga.risultato)
                html.append(f'<b>= {val_str} {_escape_html(riga.unita)}</b>')
                if riga.nota:
                    html.append(f'<br><i style="color:#666;">Rif.: {_escape_html(riga.nota)}</i>')
                html.append('</li>')
            html.append('</ol>')

        # Esito
        if self._esito:
            colore = "#4CAF50" if self._esito.verificato else "#F44336"
            esito_txt = "VERIFICATO" if self._esito.verificato else "NON VERIFICATO"
            dc_str = f"{self._esito.rapporto_DC:.3f}"
            d_str = _formatta_numero(self._esito.domanda)
            c_str = _formatta_numero(self._esito.capacita)

            html.append(f'<div class="esito" style="border:2px solid {colore};'
                        f'padding:12px;margin:8px 0;border-radius:6px;">')
            html.append(f'<h4 style="color:{colore};margin:0;">Esito: {esito_txt}</h4>')
            html.append(
                f'<p>{_escape_html(self._esito.nome_domanda)} = {d_str} {_escape_html(self._esito.unita)}<br>'
                f'{_escape_html(self._esito.nome_capacita)} = {c_str} {_escape_html(self._esito.unita)}<br>'
                f'<b>D/C = {dc_str}</b></p>'
            )
            html.append('</div>')

        # Note
        for nota in self._note_aggiuntive:
            html.append(f'<p class="nota"><i>Nota: {_escape_html(nota)}</i></p>')

        html.append('</div>')
        return '\n'.join(html)

    def come_dizionario(self) -> dict[str, Any]:
        """Esporta il tabulato come dizionario (per serializzazione JSON).

        Restituisce:
            Dizionario con tutti i dati del tabulato.
        """
        risultato: dict[str, Any] = {
            "titolo": self.titolo,
            "normativa": self.normativa,
            "modulo": self.modulo,
            "timestamp": self.timestamp,
            "input": {},
            "calcolo": [],
            "esito": None,
            "note": self._note_aggiuntive,
        }

        for simbolo, (desc, valore, unita) in self._input.parametri.items():
            risultato["input"][simbolo] = {
                "descrizione": desc,
                "valore": valore,
                "unita": unita,
            }

        for riga in self._righe_calcolo:
            risultato["calcolo"].append({
                "descrizione": riga.descrizione,
                "formula": riga.formula,
                "sostituzione": riga.sostituzione,
                "risultato": riga.risultato,
                "unita": riga.unita,
                "nota": riga.nota,
            })

        if self._esito:
            risultato["esito"] = {
                "domanda": self._esito.domanda,
                "capacita": self._esito.capacita,
                "rapporto_DC": self._esito.rapporto_DC,
                "verificato": self._esito.verificato,
                "unita": self._esito.unita,
                "nome_domanda": self._esito.nome_domanda,
                "nome_capacita": self._esito.nome_capacita,
            }

        return risultato


# --- Funzioni di utilità ---

def _formatta_numero(valore: Any) -> str:
    """Formatta un numero per la visualizzazione nel tabulato."""
    if isinstance(valore, float):
        if abs(valore) >= 1000:
            # Separatore migliaia con apostrofo (convenzione italiana)
            parte_intera = int(valore)
            parte_decimale = abs(valore) - abs(parte_intera)
            segno = "-" if valore < 0 else ""
            intero_str = f"{abs(parte_intera):,}".replace(",", "'")
            if parte_decimale > 0.0005:
                return f"{segno}{intero_str}.{parte_decimale:.2f}"[2:]
            return f"{segno}{intero_str}"
        elif abs(valore) < 0.01 and valore != 0:
            return f"{valore:.6f}"
        else:
            return f"{valore:.4g}"
    return str(valore)


def _centra(testo: str, larghezza: int) -> str:
    """Centra il testo in una riga della tabella ASCII con bordi ║."""
    spazio = larghezza - len(testo)
    if spazio < 0:
        testo = testo[:larghezza]
        spazio = 0
    sx = spazio // 2
    dx = spazio - sx
    return "║" + " " * sx + testo + " " * dx + "║"


def _escape_html(testo: str) -> str:
    """Escapa caratteri speciali HTML."""
    return testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sezione_cordolo_reticolare(risultato: object) -> str:
    """Tabulato ASCII per la verifica del cordolo metallico reticolare.

    Args:
        risultato: RisultatoCordoloReticolare (importato dinamicamente per evitare dipendenze circolari)

    Returns:
        Stringa ASCII del tabulato.
    """
    r = risultato
    linee: list[str] = []
    SEP = "═" * 72
    sep = "─" * 72

    linee.append(SEP)
    linee.append("  CORDOLO METALLICO RETICOLARE — Verifica TA")
    linee.append(SEP)

    # --- Schema e geometria ---
    schema = getattr(r, "schema", "?") if not hasattr(r, "schema") else r.schema
    # Tenta di leggere da cordolo se disponibile (non sempre nel risultato)
    linee.append(f"  Schema: {getattr(r, 'schema', 'N/D')}")
    linee.append(f"  Convergenza solutore: {'SÌ' if r.convergenza else 'NO'}")
    linee.append(sep)

    # --- Risultati globali ---
    linee.append("  RISULTATI GLOBALI")
    linee.append(f"  K_globale    = {r.K_globale:.2f} kg/cm")
    linee.append(f"  δ_max        = {r.delta_max:.4f} cm")
    linee.append(f"  N_max (comp) = {r.N_max_compressione:.1f} kg")
    linee.append(f"  N_max (traz) = {r.N_max_trazione:.1f} kg")
    linee.append(f"  F_ritegno    = {r.F_ritegno_disponibile:.1f} kg")
    linee.append(sep)

    # --- Tabella aste ---
    linee.append("  VERIFICHE ASTE")
    linee.append(f"  {'ID':>4}  {'Tipo':<12}  {'L[cm]':>7}  {'N[kg]':>9}  {'σ[kg/cm²]':>10}  {'Sfrutt':>7}  {'Esito':<12}")
    linee.append("  " + "-" * 68)
    for v in r.verifiche_aste:
        id_asta = v.get("id_asta", "?")
        tipo = v.get("tipo", "?")
        L = v.get("L", 0.0)
        N = v.get("N", 0.0)
        sigma = v.get("sigma", 0.0)
        sfrutt = v.get("sfruttamento", 0.0)
        esito = "VERIF." if v.get("verificato", False) else "NON VER."
        linee.append(
            f"  {id_asta:>4}  {tipo:<12}  {L:>7.1f}  {N:>9.1f}  {sigma:>10.2f}  {sfrutt:>7.3f}  {esito:<12}"
        )
    linee.append(sep)

    # --- Collegamento muro ---
    vc = r.verifica_collegamento
    if isinstance(vc, dict):
        linee.append("  COLLEGAMENTO MURO (F3 — inghisaggio)")
        linee.append(f"  A_tot ancoraggi = {vc.get('A_tot', 0.0):.3f} cm²")
        linee.append(f"  τ_nodo          = {vc.get('tau', 0.0):.2f} kg/cm²")
        linee.append(f"  τ_adm           = {vc.get('tau_adm', 0.0):.2f} kg/cm²")
        esito_col = "VERIFICATO" if vc.get("verificato", False) else "NON VERIFICATO"
        linee.append(f"  Esito           = {esito_col}")
    linee.append(sep)

    # --- Esito finale ---
    esito_fin = "✓ VERIFICATO" if r.verificato else "✗ NON VERIFICATO"
    linee.append(f"  ESITO FINALE: {esito_fin}")
    linee.append(SEP)

    return "\n".join(linee)
def sezione_meccanismo_cantonale(risultato: object) -> str:
    r = risultato
    linee = []
    SEP = '═' * 72
    sep = '─' * 72
    linee.append(SEP)
    linee.append('  RIBALTAMENTO CANTONALE 3D — Verifica Cinematica (Fase E.6.1)')
    linee.append(SEP)

    # Dati riepilogativi
    esito = 'VERIFICATO' if getattr(r, 'is_verificato', False) else 'NON VERIFICATO'
    linee.append(f'  Esito verifica: {esito}')
    if hasattr(r, 'alpha_0'):
        linee.append(f'  Moltiplicatore collasso alpha_0 = {r.alpha_0:.4f}')
    if hasattr(r, 'peso_cuneo_kg'):
        linee.append(f'  Peso cuneo cinematico V_c = {r.peso_cuneo_kg:.1f} kg')
    if hasattr(r, 'momento_ribaltante_kg_cm'):
        linee.append(f'  M_ribaltante = {r.momento_ribaltante_kg_cm:.1f} kg*cm')
        linee.append(f'  M_stabilizzante = {r.momento_stabilizzante_kg_cm:.1f} kg*cm')
    linee.append(sep)

    # Lista passaggi calcolo
    passaggi = getattr(r, 'passaggi_calcolo', [])
    if passaggi:
        linee.append('  PASSAGGI DI CALCOLO:')
        for p in passaggi:
            linee.append(f'   - {p}')
        linee.append(sep)

    # Warnings
    warnings = getattr(r, 'warnings', [])
    if warnings:
        linee.append('  WARNINGS E LIMITAZIONI:')
        for w in warnings:
            linee.append(f'   ! {w}')
        linee.append(sep)

    return '\n'.join(linee)

def sezione_diagnostica_angolo(risultato: object) -> str:
    r = risultato
    linee = []
    SEP = '═' * 72
    sep = '─' * 72
    linee.append(SEP)
    linee.append('  DIAGNOSTICA APERTURE D\'ANGOLO — Riduzione Cantonale (Fase E.6.2)')
    linee.append(SEP)

    status = getattr(r, 'status', 'N/D')
    k = getattr(r, 'coeff_riduzione_k', 1.0)
    d = getattr(r, 'distanza_minima_richiesta_cm', 0.0)

    linee.append(f'  Stato diagnostica: {status}')
    linee.append(f'  Distanza minima richiesta (d_min) = {d:.1f} cm')
    linee.append(f'  Coefficiente di riduzione (k)     = {k:.3f}')
    linee.append(sep)

    passaggi = getattr(r, 'passaggi_calcolo', [])
    if passaggi:
        linee.append('  LOG DECISIONALE:')
        for p in passaggi:
            linee.append(f'   - {p}')
        linee.append(sep)

    return '\n'.join(linee)

def sezione_meccanismo_cantonale(risultato: object) -> str:
    r = risultato
    linee = []
    SEP = '═' * 72
    sep = '─' * 72
    linee.append(SEP)
    linee.append('  RIBALTAMENTO CANTONALE 3D — Verifica Cinematica (Fase E.6.1)')
    linee.append(SEP)

    # Dati riepilogativi
    esito = 'VERIFICATO' if getattr(r, 'is_verificato', False) else 'NON VERIFICATO'
    linee.append(f'  Esito verifica: {esito}')
    if hasattr(r, 'alpha_0'):
        linee.append(f'  Moltiplicatore collasso alpha_0 = {r.alpha_0:.4f}')
    if hasattr(r, 'peso_cuneo_kg'):
        linee.append(f'  Peso cuneo cinematico V_c = {r.peso_cuneo_kg:.1f} kg')
    if hasattr(r, 'momento_ribaltante_kg_cm'):
        linee.append(f'  M_ribaltante = {r.momento_ribaltante_kg_cm:.1f} kg*cm')
        linee.append(f'  M_stabilizzante = {r.momento_stabilizzante_kg_cm:.1f} kg*cm')
    linee.append(sep)

    # Lista passaggi calcolo
    passaggi = getattr(r, 'passaggi_calcolo', [])
    if passaggi:
        linee.append('  PASSAGGI DI CALCOLO:')
        for p in passaggi:
            linee.append(f'   - {p}')
        linee.append(sep)

    # Warnings
    warnings = getattr(r, 'warnings', [])
    if warnings:
        linee.append('  WARNINGS E LIMITAZIONI:')
        for w in warnings:
            linee.append(f'   ! {w}')
        linee.append(sep)

    return '\n'.join(linee)

def sezione_diagnostica_angolo(risultato: object) -> str:
    r = risultato
    linee = []
    SEP = '═' * 72
    sep = '─' * 72
    linee.append(SEP)
    linee.append('  DIAGNOSTICA APERTURE D\'ANGOLO — Riduzione Cantonale (Fase E.6.2)')
    linee.append(SEP)

    status = getattr(r, 'status', 'N/D')
    k = getattr(r, 'coeff_riduzione_k', 1.0)
    d = getattr(r, 'distanza_minima_richiesta_cm', 0.0)

    linee.append(f'  Stato diagnostica: {status}')
    linee.append(f'  Distanza minima richiesta (d_min) = {d:.1f} cm')
    linee.append(f'  Coefficiente di riduzione (k)     = {k:.3f}')
    linee.append(sep)

    passaggi = getattr(r, 'passaggi_calcolo', [])
    if passaggi:
        linee.append('  LOG DECISIONALE:')
        for p in passaggi:
            linee.append(f'   - {p}')
        linee.append(sep)

    return '\n'.join(linee)
