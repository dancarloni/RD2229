"""Fattore di comportamento q per edifici in muratura — NTC2018.

Calcolo automatico da NTC2018 §7.8.1.3 (Tab. 7.3.II) con possibilità
di override manuale da parte dell'utente.

Per edifici esistenti: Circolare n.7/2019 §C8.5.5.1
- α_u/α_1 ≤ 1.50 (vs 2.50 per nuovi)
- q massimo pratico ≈ 3.0

Formula: q = q₀ × K_R
- q₀ = coefficiente × (α_u/α_1)
- K_R = 1.0 (regolare in altezza) o 0.8 (irregolare)

Unità: adimensionale.

Riferimenti:
- NTC2018 §7.8.1.3, Tabella 7.3.II
- Circolare n.7/2019 §C8.5.5.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TipoMuraturaQ(str, Enum):
    """Tipo di muratura per il fattore di comportamento."""
    ORDINARIA = "ordinaria"         # muratura non armata
    ARMATA = "armata"               # muratura armata


class RegolaritaAltezza(str, Enum):
    """Regolarità in altezza dell'edificio."""
    REGOLARE = "regolare"           # K_R = 1.0
    IRREGOLARE = "irregolare"       # K_R = 0.8


class RegolaritaPianta(str, Enum):
    """Regolarità in pianta dell'edificio."""
    REGOLARE = "regolare"
    IRREGOLARE = "irregolare"


class TipoEdificio(str, Enum):
    """Tipo di edificio (nuovo o esistente)."""
    NUOVO = "nuovo"
    ESISTENTE = "esistente"


# ═══════════════════════════════════════════════════════════
#  Tabella α_u/α_1 — NTC2018 Tab. 7.3.II
# ═══════════════════════════════════════════════════════════

# Valori tabulati α_u/α_1 per muratura ordinaria, regolare in pianta
ALPHA_U_ALPHA_1_TAB: dict[str, dict[str, float]] = {
    "ordinaria": {
        "1_piano": 1.4,
        "2_piani": 1.8,
        "3+_piani": 1.3,  # nota: valore ≥3 piani, con cordoli e solai rigidi
    },
    "armata": {
        "1_piano": 1.3,
        "2_piani": 1.5,
        "3+_piani": 1.3,
    },
}


# ═══════════════════════════════════════════════════════════
#  Risultato calcolo q
# ═══════════════════════════════════════════════════════════

@dataclass
class RisultatoFattoreQ:
    """Risultato del calcolo del fattore di comportamento."""
    q: float = 2.0                   # fattore di comportamento finale
    q_0: float = 2.0                 # q₀ prima di K_R
    alpha_u_alpha_1: float = 1.0     # rapporto sovraresistenza
    K_R: float = 1.0                 # fattore regolarità in altezza
    coefficiente_base: float = 1.75  # coefficiente moltiplicativo (1.75 ordinaria, 2.0÷3.0 armata)
    q_override: bool = False         # True se q impostato manualmente

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "q": round(self.q, 3),
            "q_0": round(self.q_0, 3),
            "alpha_u_alpha_1": round(self.alpha_u_alpha_1, 3),
            "K_R": self.K_R,
            "coefficiente_base": self.coefficiente_base,
            "q_override": self.q_override,
            "passaggi": self.passaggi,
        }


# ═══════════════════════════════════════════════════════════
#  Calcolo q
# ═══════════════════════════════════════════════════════════

def calcola_fattore_comportamento(
    tipo_muratura: TipoMuraturaQ = TipoMuraturaQ.ORDINARIA,
    n_piani: int = 2,
    regolarita_altezza: RegolaritaAltezza = RegolaritaAltezza.REGOLARE,
    regolarita_pianta: RegolaritaPianta = RegolaritaPianta.REGOLARE,
    tipo_edificio: TipoEdificio = TipoEdificio.ESISTENTE,
    alpha_u_alpha_1_override: float | None = None,
    q_override: float | None = None,
) -> RisultatoFattoreQ:
    """Calcola il fattore di comportamento q per edifici in muratura.

    NTC2018 §7.8.1.3:
    q = q₀ × K_R

    dove:
    - q₀ = coefficiente × (α_u/α_1)
    - coefficiente = 1.75 (ordinaria) o 2.0 (armata con capacity design)
    - K_R = 1.0 (regolare) o 0.8 (irregolare in altezza)

    Per edifici esistenti (Circ. §C8.5.5.1):
    - α_u/α_1 ≤ 1.50

    Args:
        tipo_muratura: ordinaria o armata
        n_piani: numero di piani
        regolarita_altezza: regolare o irregolare
        regolarita_pianta: regolare o irregolare (influenza α_u/α_1)
        tipo_edificio: nuovo o esistente
        alpha_u_alpha_1_override: override manuale di α_u/α_1
        q_override: override manuale di q (ignora tutto il resto)

    Returns:
        RisultatoFattoreQ
    """
    passaggi: list[str] = []
    res = RisultatoFattoreQ()

    # Override diretto di q
    if q_override is not None:
        res.q = q_override
        res.q_override = True
        passaggi.append(f"q = {q_override:.3f} (override manuale)")
        res.passaggi = passaggi
        return res

    # Coefficiente base
    if tipo_muratura == TipoMuraturaQ.ORDINARIA:
        coeff = 1.75
    else:
        coeff = 2.0  # armata base (fino a 3.0 con capacity design)

    res.coefficiente_base = coeff
    passaggi.append(
        f"Tipo muratura: {tipo_muratura.value} → coefficiente = {coeff}"
    )

    # α_u/α_1 da tabella o override
    if alpha_u_alpha_1_override is not None:
        alpha = alpha_u_alpha_1_override
        passaggi.append(f"α_u/α_1 = {alpha:.3f} (override)")
    else:
        # Dalla tabella
        chiave_tipo = tipo_muratura.value
        if n_piani <= 1:
            chiave_piani = "1_piano"
        elif n_piani == 2:
            chiave_piani = "2_piani"
        else:
            chiave_piani = "3+_piani"

        alpha_tab = ALPHA_U_ALPHA_1_TAB.get(chiave_tipo, {}).get(chiave_piani, 1.0)

        # Per irregolarità in pianta: media tra 1.0 e valore tabulato
        if regolarita_pianta == RegolaritaPianta.IRREGOLARE:
            alpha = (1.0 + alpha_tab) / 2
            passaggi.append(
                f"α_u/α_1 tab = {alpha_tab:.1f}, irregolare in pianta → "
                f"α = (1.0 + {alpha_tab:.1f})/2 = {alpha:.3f}"
            )
        else:
            alpha = alpha_tab
            passaggi.append(f"α_u/α_1 = {alpha:.3f} (Tab. 7.3.II, {chiave_piani})")

    # Limite per edifici esistenti
    if tipo_edificio == TipoEdificio.ESISTENTE:
        limite = 1.50
        if alpha > limite:
            passaggi.append(
                f"Edificio esistente: α_u/α_1 = {alpha:.3f} → limitato a {limite} "
                f"(Circ. §C8.5.5.1)"
            )
            alpha = limite
    else:
        limite = 2.50
        if alpha > limite:
            alpha = limite
            passaggi.append(f"Limitato a α_u/α_1 = {limite}")

    res.alpha_u_alpha_1 = alpha

    # q₀ = coefficiente × α_u/α_1
    q_0 = coeff * alpha
    res.q_0 = q_0

    # K_R
    if regolarita_altezza == RegolaritaAltezza.IRREGOLARE:
        K_R = 0.8
    else:
        K_R = 1.0
    res.K_R = K_R

    # q = q₀ × K_R
    q = q_0 * K_R
    res.q = q

    passaggi.append(f"q₀ = {coeff} × {alpha:.3f} = {q_0:.3f}")
    passaggi.append(f"K_R = {K_R}")
    passaggi.append(f"q = q₀ × K_R = {q_0:.3f} × {K_R} = {q:.3f}")

    res.passaggi = passaggi
    return res
