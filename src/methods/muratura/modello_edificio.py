"""Modello geometrico edificio in muratura per analisi POR / telaio equivalente.

Struttura dati gerarchica:
  Edificio → Piano → Parete → Apertura

Ogni Parete contiene aperture (porte, finestre) che vengono usate dal modulo
``discretizzazione`` per generare automaticamente maschi e fasce.

Unità: cm per geometria, kg per forze, kg/cm² per tensioni, kg/cm³ per peso specifico.

Riferimenti:
- NTC2018 §7.8 — Costruzioni di muratura
- Circolare n.7/2019 §C8.7.1 — Edifici esistenti in muratura
- Circolare n.7/2019 Tab. C8.5.I — Parametri meccanici muratura esistente
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

# ═══════════════════════════════════════════════════════════
#  Enumerazioni
# ═══════════════════════════════════════════════════════════


class TipoApertura(str, Enum):
    """Tipo di apertura nella parete."""

    PORTA = "porta"
    FINESTRA = "finestra"


class TipoDiaframma(str, Enum):
    """Tipo di diaframma (solaio) al piano."""

    RIGIDO = "rigido"  # solaio in CA, laterocemento rigido
    DEFORMABILE = "deformabile"  # solaio in legno, voltine, putrelle


class LivelloConoscenza(str, Enum):
    """Livello di conoscenza edificio esistente (NTC2018 §8.5.4)."""

    LC1 = "LC1"  # conoscenza limitata  → FC = 1.35
    LC2 = "LC2"  # conoscenza adeguata  → FC = 1.20
    LC3 = "LC3"  # conoscenza accurata  → FC = 1.00


# Tabella FC da NTC2018 §8.5.4 / Circolare §C8.5.4
FC_DA_LC: dict[str, float] = {
    "LC1": 1.35,
    "LC2": 1.20,
    "LC3": 1.00,
}


class TipoMuraturaC85I(str, Enum):
    """Tipologie murarie da Tabella C8.5.I della Circolare n.7/2019."""

    PIETRAME_DISORDINATA = "pietrame_disordinata"
    PIETRAME_A_SPACCO = "pietrame_a_spacco"
    PIETRE_SBOZZATE = "pietre_sbozzate"
    PIETRE_SQUADRATE = "pietre_squadrate"
    MATTONI_PIENI_CALCE = "mattoni_pieni_calce"
    MATTONI_PIENI_CEMENTO = "mattoni_pieni_cemento"
    BLOCCHI_LATERIZIO = "blocchi_laterizio"
    BLOCCHI_CLS = "blocchi_cls"
    BLOCCHI_CLS_PIENI = "blocchi_cls_pieni"
    TUFO = "tufo"
    PIETRA_LAVORATA = "pietra_lavorata"


# ═══════════════════════════════════════════════════════════
#  Materiale muratura
# ═══════════════════════════════════════════════════════════


@dataclass
class MaterialeMuratura:
    """Proprietà meccaniche muratura per analisi POR.

    I valori possono venire da:
    - Tabella C8.5.I (muratura esistente) con correttivi
    - Catalogo DM87 / Circ81 / NTC2018
    - Input manuale dell'utente

    Tutti i valori in kg/cm².
    """

    nome: str = ""

    # Resistenza
    f: float = 0.0  # resistenza a compressione media [kg/cm²]
    tau_0: float = 0.0  # resistenza a taglio di riferimento [kg/cm²]
    fvk0: float = 0.0  # resistenza caratteristica a taglio senza compressione [kg/cm²]

    # Deformabilità
    E: float = 0.0  # modulo elastico [kg/cm²]
    G: float = 0.0  # modulo di taglio [kg/cm²]

    # Peso
    gamma: float = 0.0018  # peso specifico [kg/cm³] (default 1800 kg/m³)

    # Coefficienti parziali
    gamma_M: float = 2.0  # coefficiente parziale materiale
    FC: float = 1.35  # fattore di confidenza

    # Attrito (per scorrimento Mohr-Coulomb)
    mu: float = 0.4  # coefficiente d'attrito

    # Origine dati
    tipologia_c85i: str = ""  # tipologia Tab. C8.5.I se usata
    norma: str = "NTC2018"

    @property
    def fd(self) -> float:
        """Resistenza di calcolo a compressione fd = f / (γ_M × FC) [kg/cm²]."""
        denom = self.gamma_M * self.FC
        return self.f / denom if denom > 0 else 0.0

    @property
    def tau_0d(self) -> float:
        """Resistenza di calcolo a taglio τ₀d = τ₀ / (γ_M × FC) [kg/cm²]."""
        denom = self.gamma_M * self.FC
        return self.tau_0 / denom if denom > 0 else 0.0

    @property
    def fvk0d(self) -> float:
        """Resistenza di calcolo a taglio senza compressione fvk0d [kg/cm²]."""
        denom = self.gamma_M * self.FC
        return self.fvk0 / denom if denom > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "f": round(self.f, 2),
            "tau_0": round(self.tau_0, 3),
            "fvk0": round(self.fvk0, 3),
            "E": round(self.E, 0),
            "G": round(self.G, 0),
            "gamma": self.gamma,
            "gamma_M": self.gamma_M,
            "FC": self.FC,
            "fd": round(self.fd, 2),
            "tau_0d": round(self.tau_0d, 4),
        }


# ═══════════════════════════════════════════════════════════
#  Apertura
# ═══════════════════════════════════════════════════════════


@dataclass
class Apertura:
    """Apertura (porta o finestra) in una parete.

    Le coordinate sono relative alla parete:
    - x_offset: distanza dal punto iniziale della parete lungo il suo asse [cm]
    - z_offset: distanza dal pavimento del piano [cm]
    """

    tipo: TipoApertura = TipoApertura.FINESTRA
    x_offset: float = 0.0  # distanza dall'inizio parete [cm]
    z_offset: float = 0.0  # distanza dal pavimento [cm]
    larghezza: float = 0.0  # larghezza apertura [cm]
    altezza: float = 0.0  # altezza apertura [cm]

    @property
    def x_fine(self) -> float:
        """Coordinata x di fine apertura [cm]."""
        return self.x_offset + self.larghezza

    @property
    def z_fine(self) -> float:
        """Coordinata z di fine apertura [cm]."""
        return self.z_offset + self.altezza

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo.value,
            "x_offset": round(self.x_offset, 1),
            "z_offset": round(self.z_offset, 1),
            "larghezza": round(self.larghezza, 1),
            "altezza": round(self.altezza, 1),
        }


# ═══════════════════════════════════════════════════════════
#  Parete
# ═══════════════════════════════════════════════════════════


@dataclass
class Parete:
    """Parete in pianta definita da coordinate iniziale e finale.

    Le coordinate (x_ini, y_ini) → (x_fin, y_fin) definiscono l'asse
    della parete in pianta. Lo spessore si estende simmetricamente.
    """

    id_parete: int = 0
    x_ini: float = 0.0  # coordinata x inizio [cm]
    y_ini: float = 0.0  # coordinata y inizio [cm]
    x_fin: float = 0.0  # coordinata x fine [cm]
    y_fin: float = 0.0  # coordinata y fine [cm]
    spessore: float = 30.0  # spessore parete [cm]
    materiale: MaterialeMuratura | None = None
    aperture: list[Apertura] = field(default_factory=list)

    @property
    def lunghezza(self) -> float:
        """Lunghezza della parete in pianta [cm]."""
        dx = self.x_fin - self.x_ini
        dy = self.y_fin - self.y_ini
        return math.sqrt(dx**2 + dy**2)

    @property
    def angolo(self) -> float:
        """Angolo della parete rispetto all'asse X [radianti]."""
        dx = self.x_fin - self.x_ini
        dy = self.y_fin - self.y_ini
        return math.atan2(dy, dx)

    @property
    def direzione_principale(self) -> str:
        """Direzione principale della parete ('X' o 'Y').

        Basata sull'angolo: se |cos(θ)| > |sin(θ)| → 'X', altrimenti → 'Y'.
        """
        a = self.angolo
        if abs(math.cos(a)) >= abs(math.sin(a)):
            return "X"
        return "Y"

    @property
    def x_baricentro(self) -> float:
        """Coordinata x del baricentro [cm]."""
        return (self.x_ini + self.x_fin) / 2

    @property
    def y_baricentro(self) -> float:
        """Coordinata y del baricentro [cm]."""
        return (self.y_ini + self.y_fin) / 2

    def aperture_ordinate(self) -> list[Apertura]:
        """Aperture ordinate per x_offset crescente."""
        return sorted(self.aperture, key=lambda a: a.x_offset)

    def to_dict(self) -> dict:
        return {
            "id_parete": self.id_parete,
            "x_ini": round(self.x_ini, 1),
            "y_ini": round(self.y_ini, 1),
            "x_fin": round(self.x_fin, 1),
            "y_fin": round(self.y_fin, 1),
            "spessore": round(self.spessore, 1),
            "lunghezza": round(self.lunghezza, 1),
            "direzione": self.direzione_principale,
            "aperture": [a.to_dict() for a in self.aperture],
        }


# ═══════════════════════════════════════════════════════════
#  Piano
# ═══════════════════════════════════════════════════════════


@dataclass
class Piano:
    """Piano dell'edificio."""

    id_piano: int = 0
    quota_z: float = 0.0  # quota del pavimento rispetto alla fondazione [cm]
    altezza_interpiano: float = 300.0  # altezza interpiano [cm]
    pareti: list[Parete] = field(default_factory=list)

    # Massa del piano (solaio + tamponature + carichi permanenti + ψ×variabili)
    massa: float = 0.0  # massa sismica del piano [kg]

    # Tipo diaframma
    tipo_diaframma: TipoDiaframma = TipoDiaframma.RIGIDO

    @property
    def quota_sommita(self) -> float:
        """Quota della sommità del piano [cm]."""
        return self.quota_z + self.altezza_interpiano

    @property
    def n_pareti(self) -> int:
        return len(self.pareti)

    def pareti_in_direzione(self, direzione: str) -> list[Parete]:
        """Filtra pareti per direzione ('X' o 'Y')."""
        return [p for p in self.pareti if p.direzione_principale == direzione]

    def to_dict(self) -> dict:
        return {
            "id_piano": self.id_piano,
            "quota_z": round(self.quota_z, 1),
            "altezza_interpiano": round(self.altezza_interpiano, 1),
            "massa": round(self.massa, 0),
            "tipo_diaframma": self.tipo_diaframma.value,
            "n_pareti": self.n_pareti,
            "pareti": [p.to_dict() for p in self.pareti],
        }


# ═══════════════════════════════════════════════════════════
#  Configurazione POR
# ═══════════════════════════════════════════════════════════


@dataclass
class ConfigPOR:
    """Configurazione analisi POR — parametri configurabili dall'utente."""

    # Drift limite SLC (NTC2018 §7.8.2.2)
    drift_taglio: float = 0.005  # 0.5% muratura non armata
    drift_pressoflessione: float = 0.010  # 1.0% muratura non armata

    # Criterio collasso globale
    criterio_collasso: str = "caduta_resistenza"  # "caduta_resistenza" o "maschi_collassati"
    soglia_caduta_resistenza: float = 0.80  # V_base scende sotto 80% V_max
    soglia_maschi_collassati: float = 0.50  # 50% maschi di un piano collassano

    # Diaframma default
    tipo_diaframma_default: TipoDiaframma = TipoDiaframma.RIGIDO

    # Eccentricità accidentale (NTC2018 §7.2.6)
    eccentricita_accidentale: float = 0.05  # ±5% della dimensione in pianta

    # Numero passi pushover
    n_passi: int = 100

    # Spostamento massimo [cm] (come limite di sicurezza)
    spostamento_max: float = 20.0

    def to_dict(self) -> dict:
        return {
            "drift_taglio": self.drift_taglio,
            "drift_pressoflessione": self.drift_pressoflessione,
            "criterio_collasso": self.criterio_collasso,
            "soglia_caduta_resistenza": self.soglia_caduta_resistenza,
            "soglia_maschi_collassati": self.soglia_maschi_collassati,
            "eccentricita_accidentale": self.eccentricita_accidentale,
            "n_passi": self.n_passi,
        }


# ═══════════════════════════════════════════════════════════
#  Parametri sismici (esteso da cinematica.py)
# ═══════════════════════════════════════════════════════════


@dataclass
class ParametriSismiciEdificio:
    """Parametri sismici per analisi globale edificio.

    Estende i ParametriSismici di cinematica.py con parametri per
    l'analisi globale (spettro, q, distribuzioni forze).
    """

    # Accelerazione e amplificazione
    a_g: float = 0.0  # accelerazione al suolo a_g/g [adimensionale]
    F_0: float = 2.5  # fattore amplificazione spettrale
    S: float = 1.0  # coefficiente amplificazione stratigrafica × topografica

    # Periodi spettrali
    T_B: float = 0.0  # inizio plateau spettrale [s]
    T_C: float = 0.0  # fine plateau spettrale [s]
    T_D: float = 0.0  # inizio ramo a spostamento costante [s]

    # Fattore di comportamento (calcolato da fattore_comportamento.py o override)
    q: float = 2.0  # fattore di comportamento

    # Livello di conoscenza
    livello_conoscenza: LivelloConoscenza = LivelloConoscenza.LC1
    FC: float = 1.35  # fattore di confidenza (auto da LC o override)
    FC_override: bool = False  # True se FC impostato manualmente

    def aggiorna_FC_da_LC(self) -> None:
        """Aggiorna FC dal livello di conoscenza, se non in override."""
        if not self.FC_override:
            self.FC = FC_DA_LC.get(self.livello_conoscenza.value, 1.35)

    def spettro_elastico(self, T: float) -> float:
        """Ordinata spettrale elastica S_e(T) in [g].

        NTC2018 §3.2.3.2.1:
        - 0 ≤ T < T_B: S_e = a_g·S·η·F₀·[T/T_B + 1/(η·F₀)·(1 - T/T_B)]
        - T_B ≤ T < T_C: S_e = a_g·S·η·F₀
        - T_C ≤ T < T_D: S_e = a_g·S·η·F₀·(T_C/T)
        - T ≥ T_D: S_e = a_g·S·η·F₀·(T_C·T_D/T²)

        con η = 1 (smorzamento 5%)
        """
        eta = 1.0
        a_g_S = self.a_g * self.S

        if self.T_B <= 0 or self.T_C <= 0 or self.T_D <= 0:
            # Parametri non definiti: ritorna plateau
            return a_g_S * eta * self.F_0

        if T < 0:
            T = 0.0

        if T < self.T_B:
            return (
                a_g_S
                * eta
                * self.F_0
                * (T / self.T_B + 1.0 / (eta * self.F_0) * (1.0 - T / self.T_B))
            )
        elif T < self.T_C:
            return a_g_S * eta * self.F_0
        elif T < self.T_D:
            return a_g_S * eta * self.F_0 * (self.T_C / T)
        else:
            return a_g_S * eta * self.F_0 * (self.T_C * self.T_D / (T**2))

    def spettro_progetto(self, T: float) -> float:
        """Ordinata spettrale di progetto S_d(T) = S_e(T) / q [g]."""
        Se = self.spettro_elastico(T)
        return Se / self.q if self.q > 0 else Se

    def to_dict(self) -> dict:
        return {
            "a_g": self.a_g,
            "F_0": self.F_0,
            "S": self.S,
            "T_B": self.T_B,
            "T_C": self.T_C,
            "T_D": self.T_D,
            "q": self.q,
            "livello_conoscenza": self.livello_conoscenza.value,
            "FC": self.FC,
        }


# ═══════════════════════════════════════════════════════════
#  Edificio
# ═══════════════════════════════════════════════════════════


@dataclass
class Edificio:
    """Modello geometrico completo dell'edificio in muratura.

    Struttura gerarchica:
    Edificio → Piano → Parete → Apertura

    Ogni piano contiene le pareti con le loro aperture.
    I maschi e le fasce vengono generati dal modulo ``discretizzazione``.
    """

    nome: str = ""
    piani: list[Piano] = field(default_factory=list)
    parametri_sismici: ParametriSismiciEdificio = field(default_factory=ParametriSismiciEdificio)
    config: ConfigPOR = field(default_factory=ConfigPOR)

    @property
    def n_piani(self) -> int:
        return len(self.piani)

    @property
    def altezza_totale(self) -> float:
        """Altezza totale edificio [cm]."""
        if not self.piani:
            return 0.0
        ultimo = max(self.piani, key=lambda p: p.quota_z)
        return ultimo.quota_z + ultimo.altezza_interpiano

    @property
    def dimensione_x(self) -> float:
        """Dimensione massima in pianta direzione X [cm]."""
        xs = []
        for piano in self.piani:
            for p in piano.pareti:
                xs.extend([p.x_ini, p.x_fin])
        if not xs:
            return 0.0
        return max(xs) - min(xs)

    @property
    def dimensione_y(self) -> float:
        """Dimensione massima in pianta direzione Y [cm]."""
        ys = []
        for piano in self.piani:
            for p in piano.pareti:
                ys.extend([p.y_ini, p.y_fin])
        if not ys:
            return 0.0
        return max(ys) - min(ys)

    @property
    def massa_totale(self) -> float:
        """Massa sismica totale [kg]."""
        return sum(p.massa for p in self.piani)

    def piano_per_id(self, id_piano: int) -> Piano | None:
        """Cerca un piano per id."""
        for p in self.piani:
            if p.id_piano == id_piano:
                return p
        return None

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "n_piani": self.n_piani,
            "altezza_totale": round(self.altezza_totale, 1),
            "dimensione_x": round(self.dimensione_x, 1),
            "dimensione_y": round(self.dimensione_y, 1),
            "massa_totale": round(self.massa_totale, 0),
            "parametri_sismici": self.parametri_sismici.to_dict(),
            "config": self.config.to_dict(),
            "piani": [p.to_dict() for p in self.piani],
        }
