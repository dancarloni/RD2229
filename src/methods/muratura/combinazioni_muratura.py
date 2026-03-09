"""Combinazioni di carico personalizzabili per muratura.

Gestione delle combinazioni di carico NTC2018 §2.5.3 con supporto
per personalizzazione utente:
- Generazione automatica combinazioni default NTC2018
- Aggiunta, modifica, eliminazione combinazioni
- Attivazione/disattivazione senza eliminare
- Ripristino configurazione default

Le combinazioni calcolano N_Ed combinato a partire dalle componenti
G1, G2, Q dei carichi verticali.

Unità: kg per forze.

Riferimenti:
- NTC2018 §2.5.3 — Combinazioni delle azioni
- NTC2018 Tab. 2.5.I — Coefficienti ψ
- NTC2018 Tab. 2.6.I — Coefficienti parziali γ
"""

from __future__ import annotations

from dataclasses import dataclass

# ═══════════════════════════════════════════════════════════
#  Coefficienti ψ per categoria d'uso (NTC2018 Tab. 2.5.I)
# ═══════════════════════════════════════════════════════════

PSI_0: dict[str, float] = {
    "A": 0.7,    # residenziale
    "B": 0.7,    # uffici
    "C": 0.7,    # affollamento
    "D": 0.7,    # commerciale
    "E": 1.0,    # magazzini
    "F": 0.6,    # rimesse peso ≤ 30 kN
    "G": 0.3,    # rimesse peso > 30 kN
    "H": 0.0,    # coperture
}

PSI_1: dict[str, float] = {
    "A": 0.5,
    "B": 0.5,
    "C": 0.7,
    "D": 0.7,
    "E": 0.9,
    "F": 0.3,
    "G": 0.6,
    "H": 0.0,
}

PSI_2: dict[str, float] = {
    "A": 0.3,
    "B": 0.3,
    "C": 0.6,
    "D": 0.6,
    "E": 0.8,
    "F": 0.0,
    "G": 0.3,
    "H": 0.0,
}


# ═══════════════════════════════════════════════════════════
#  Combinazione di carico
# ═══════════════════════════════════════════════════════════

@dataclass
class CombinazioneCarico:
    """Singola combinazione di carico.

    N_Ed = γ_G1 × G1 + γ_G2 × G2 + γ_Q × ψ_0 × Q

    Per combinazioni sismiche:
    N_Ed = G1 + G2 + ψ_2 × Q  (NTC2018 §2.5.3)
    """
    nome: str = ""
    tipo: str = "SLU"             # "SLU", "SLE_rara", "SLE_freq", "SLE_qperm", "sismica"

    # Coefficienti parziali
    gamma_G1: float = 1.3         # permanente strutturale
    gamma_G2: float = 1.5         # permanente non strutturale
    gamma_Q: float = 1.5          # variabile

    # Coefficiente combinazione
    psi: float = 0.7              # ψ₀ per SLU, ψ₁ per SLE freq, ψ₂ per SLE qperm/sismica

    # Gestione utente
    attiva: bool = True           # se False, combinazione non usata nel calcolo
    predefinita: bool = False     # True se generata automaticamente
    id_combinazione: int = 0      # identificativo univoco

    def calcola_N(self, G1: float, G2: float, Q: float) -> float:
        """Calcola N_Ed combinato.

        Args:
            G1: carico permanente strutturale [kg]
            G2: carico permanente non strutturale [kg]
            Q: carico variabile [kg]

        Returns:
            N_Ed [kg]
        """
        return self.gamma_G1 * G1 + self.gamma_G2 * G2 + self.gamma_Q * self.psi * Q

    def to_dict(self) -> dict:
        return {
            "id": self.id_combinazione,
            "nome": self.nome,
            "tipo": self.tipo,
            "gamma_G1": self.gamma_G1,
            "gamma_G2": self.gamma_G2,
            "gamma_Q": self.gamma_Q,
            "psi": self.psi,
            "attiva": self.attiva,
            "predefinita": self.predefinita,
        }


# ═══════════════════════════════════════════════════════════
#  Combinazioni default NTC2018
# ═══════════════════════════════════════════════════════════

def _combinazioni_default_ntc2018(categoria: str = "A") -> list[CombinazioneCarico]:
    """Genera le combinazioni default per NTC2018 §2.5.3.

    Args:
        categoria: categoria d'uso per ψ (A, B, C, ...)

    Returns:
        Lista combinazioni default
    """
    psi_0 = PSI_0.get(categoria, 0.7)
    psi_1 = PSI_1.get(categoria, 0.5)
    psi_2 = PSI_2.get(categoria, 0.3)

    return [
        # SLU fondamentale — massimo carico
        CombinazioneCarico(
            nome="SLU fondamentale (sfavorevole)",
            tipo="SLU",
            gamma_G1=1.3, gamma_G2=1.5, gamma_Q=1.5,
            psi=psi_0,
            predefinita=True,
            id_combinazione=1,
        ),
        # SLU fondamentale — minimo carico (favorevole)
        CombinazioneCarico(
            nome="SLU fondamentale (favorevole)",
            tipo="SLU",
            gamma_G1=1.0, gamma_G2=0.0, gamma_Q=0.0,
            psi=0.0,
            predefinita=True,
            id_combinazione=2,
        ),
        # SLE rara
        CombinazioneCarico(
            nome="SLE rara",
            tipo="SLE_rara",
            gamma_G1=1.0, gamma_G2=1.0, gamma_Q=1.0,
            psi=psi_0,
            predefinita=True,
            id_combinazione=3,
        ),
        # SLE frequente
        CombinazioneCarico(
            nome="SLE frequente",
            tipo="SLE_freq",
            gamma_G1=1.0, gamma_G2=1.0, gamma_Q=1.0,
            psi=psi_1,
            predefinita=True,
            id_combinazione=4,
        ),
        # SLE quasi permanente
        CombinazioneCarico(
            nome="SLE quasi permanente",
            tipo="SLE_qperm",
            gamma_G1=1.0, gamma_G2=1.0, gamma_Q=1.0,
            psi=psi_2,
            predefinita=True,
            id_combinazione=5,
        ),
        # Sismica
        CombinazioneCarico(
            nome="Sismica (SLV)",
            tipo="sismica",
            gamma_G1=1.0, gamma_G2=1.0, gamma_Q=1.0,
            psi=psi_2,
            predefinita=True,
            id_combinazione=6,
        ),
    ]


# ═══════════════════════════════════════════════════════════
#  Gestore combinazioni
# ═══════════════════════════════════════════════════════════

class GestoreCombinazioni:
    """Gestore combinazioni di carico personalizzabili.

    Supporta:
    - Generazione default NTC2018
    - CRUD (aggiungi, modifica, elimina)
    - Attiva/disattiva senza eliminare
    - Ripristino default
    """

    def __init__(self, categoria: str = "A"):
        self._categoria = categoria
        self._combinazioni: list[CombinazioneCarico] = []
        self._next_id: int = 100
        self.genera_default()

    @property
    def combinazioni(self) -> list[CombinazioneCarico]:
        """Tutte le combinazioni (attive e non)."""
        return list(self._combinazioni)

    @property
    def combinazioni_attive(self) -> list[CombinazioneCarico]:
        """Solo le combinazioni attive."""
        return [c for c in self._combinazioni if c.attiva]

    @property
    def n_combinazioni(self) -> int:
        return len(self._combinazioni)

    @property
    def n_attive(self) -> int:
        return len(self.combinazioni_attive)

    def genera_default(self) -> None:
        """Genera le combinazioni default NTC2018 (reset completo)."""
        self._combinazioni = _combinazioni_default_ntc2018(self._categoria)
        self._next_id = max(c.id_combinazione for c in self._combinazioni) + 100

    def ripristina_default(self) -> None:
        """Ripristina le combinazioni default, mantenendo quelle personalizzate."""
        default = _combinazioni_default_ntc2018(self._categoria)
        default_ids = {c.id_combinazione for c in default}

        # Rimuovi le predefinite esistenti
        self._combinazioni = [c for c in self._combinazioni if not c.predefinita]

        # Aggiungi quelle default all'inizio
        self._combinazioni = default + self._combinazioni

    def aggiungi(
        self,
        nome: str,
        tipo: str = "SLU",
        gamma_G1: float = 1.3,
        gamma_G2: float = 1.5,
        gamma_Q: float = 1.5,
        psi: float = 0.7,
    ) -> CombinazioneCarico:
        """Aggiunge una combinazione personalizzata.

        Returns:
            La combinazione creata
        """
        combo = CombinazioneCarico(
            nome=nome,
            tipo=tipo,
            gamma_G1=gamma_G1,
            gamma_G2=gamma_G2,
            gamma_Q=gamma_Q,
            psi=psi,
            attiva=True,
            predefinita=False,
            id_combinazione=self._next_id,
        )
        self._next_id += 1
        self._combinazioni.append(combo)
        return combo

    def modifica(self, id_combinazione: int, **kwargs) -> bool:
        """Modifica una combinazione esistente.

        Args:
            id_combinazione: id della combinazione
            **kwargs: campi da modificare (nome, gamma_G1, gamma_G2, gamma_Q, psi, tipo)

        Returns:
            True se trovata e modificata
        """
        for c in self._combinazioni:
            if c.id_combinazione == id_combinazione:
                for key, val in kwargs.items():
                    if hasattr(c, key) and key not in ("id_combinazione", "predefinita"):
                        setattr(c, key, val)
                return True
        return False

    def elimina(self, id_combinazione: int) -> bool:
        """Elimina una combinazione.

        Returns:
            True se trovata e eliminata
        """
        for i, c in enumerate(self._combinazioni):
            if c.id_combinazione == id_combinazione:
                self._combinazioni.pop(i)
                return True
        return False

    def attiva(self, id_combinazione: int) -> bool:
        """Attiva una combinazione.

        Returns:
            True se trovata
        """
        for c in self._combinazioni:
            if c.id_combinazione == id_combinazione:
                c.attiva = True
                return True
        return False

    def disattiva(self, id_combinazione: int) -> bool:
        """Disattiva una combinazione (senza eliminarla).

        Returns:
            True se trovata
        """
        for c in self._combinazioni:
            if c.id_combinazione == id_combinazione:
                c.attiva = False
                return True
        return False

    def per_id(self, id_combinazione: int) -> CombinazioneCarico | None:
        """Cerca una combinazione per id."""
        for c in self._combinazioni:
            if c.id_combinazione == id_combinazione:
                return c
        return None

    def calcola_N_tutte(
        self,
        G1: float,
        G2: float,
        Q: float,
        solo_attive: bool = True,
    ) -> dict[int, float]:
        """Calcola N_Ed per tutte le combinazioni (attive).

        Args:
            G1, G2, Q: componenti di carico [kg]
            solo_attive: se True, calcola solo per le attive

        Returns:
            {id_combinazione: N_Ed}
        """
        combo_list = self.combinazioni_attive if solo_attive else self._combinazioni
        return {c.id_combinazione: c.calcola_N(G1, G2, Q) for c in combo_list}

    def N_Ed_max(self, G1: float, G2: float, Q: float) -> float:
        """Calcola il massimo N_Ed tra le combinazioni attive.

        Returns:
            N_Ed massimo [kg]
        """
        valori = self.calcola_N_tutte(G1, G2, Q)
        return max(valori.values()) if valori else 0.0

    def to_dict(self) -> dict:
        return {
            "categoria": self._categoria,
            "n_combinazioni": self.n_combinazioni,
            "n_attive": self.n_attive,
            "combinazioni": [c.to_dict() for c in self._combinazioni],
        }
