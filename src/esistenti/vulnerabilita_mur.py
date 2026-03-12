"""Analisi di vulnerabilità sismica per edifici in muratura esistenti.

Implementa:
- LV1 speditivo (formule resistenza globale vs domanda sismica)
- LV2 meccanismi locali (integra cinematica.py: ribaltamento, scorrimento, flessione)
- Meccanismo di scorrimento in quota (implementazione completa in R.3)
- Classificazione pareti e indice globale α_u / α_1

Riferimenti normativi:
- NTC2018 §8.7.1: Verifiche muratura esistente
- Circolare 7/2019 §C8.7.1: Analisi meccanismi e LV1/LV2
- Circolare 7/2019 §C8A.4.1: Analisi cinematica lineare e non lineare
- OPCM 3274/2003 §11.2: Metodo speditivo storico

Unità: cm per geometria, kg e kg/cm² per forze e tensioni.

Note di progettazione (Fase R):
- Scorrimento: implementazione completa (non stub) — meccanismo base della parete
- LV1: tre formule selezionabili (NTC2018, OPCM3274, letteratura)
- Degrado: preset basso/medio/alto con riduzione fvd0 e fd
- Output doppio: α_min e α_medio per edificio
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.registro_log import registro
from src.methods.muratura.cinematica import (
    ForzaCatena,
    ParametriSismici,
    PareteMuraria,
    RisultatoCinematica,
    TipoMeccanismo,
    analisi_meccanismi_locali,
    flessione_orizzontale,
    flessione_verticale,
    ribaltamento_composto,
    ribaltamento_semplice,
)

_MODULO_LOG = "esistenti.vulnerabilita_mur"

# ═══════════════════════════════════════════════════════════
#  Enumerazioni e configurazione
# ═══════════════════════════════════════════════════════════


class FormuleLV1(str, Enum):
    """Metodo usato per il calcolo LV1 speditivo."""

    NTC2018 = "NTC2018"  # Circ. 7/2019 §C8.7.1.1 — τ × A / W – domanda
    OPCM3274 = "OPCM3274"  # OPCM 3274/2003 §11.2 — IS = τ_u / τ_g
    LETTERATURA = "letteratura"  # Turnšek-Čačovič (1970) generalizzato


class DegradoPreset(str, Enum):
    """Preset per la riduzione delle proprietà meccaniche per degrado."""

    NESSUNO = "nessuno"  # Nessuna riduzione (default OFF)
    BASSO = "basso"  # Riduzione 5% fvd0, 5% fd
    MEDIO = "medio"  # Riduzione 15% fvd0, 10% fd
    ALTO = "alto"  # Riduzione 30% fvd0, 20% fd


_FATTORI_DEGRADO: dict[str, dict[str, float]] = {
    DegradoPreset.NESSUNO.value: {"fvd0": 1.0, "fd": 1.0},
    DegradoPreset.BASSO.value: {"fvd0": 0.95, "fd": 0.95},
    DegradoPreset.MEDIO.value: {"fvd0": 0.85, "fd": 0.90},
    DegradoPreset.ALTO.value: {"fvd0": 0.70, "fd": 0.80},
}


class ClasseVulnerabilitaMur(str, Enum):
    """Classe di vulnerabilità basata su α = a₀*/a_domanda."""

    VERIFICATA = "verificata"  # α ≥ 1.0 (capacità ≥ domanda)
    CRITICA = "critica"  # 0.8 ≤ α < 1.0
    VULNERABILE = "vulnerabile"  # α < 0.8


@dataclass
class ConfigVulnerabilitaMur:
    """Parametri di configurazione analisi muratura."""

    formula_lv1: FormuleLV1 = FormuleLV1.NTC2018
    degrado: DegradoPreset = DegradoPreset.NESSUNO

    # Meccanismi LV2 da includere (default: tutti principali)
    meccanismi_lv2: list[str] = field(
        default_factory=lambda: [
            TipoMeccanismo.RIBALTAMENTO_SEMPLICE.value,
            TipoMeccanismo.RIBALTAMENTO_COMPOSTO.value,
            TipoMeccanismo.FLESSIONE_VERTICALE.value,
            TipoMeccanismo.FLESSIONE_ORIZZONTALE.value,
            "scorrimento",  # R.3: meccanismo completo implementato qui
        ]
    )

    # Soglie classificazione α
    soglia_verificata: float = 1.0
    soglia_critica: float = 0.8

    normativa: str = "NTC2018"

    def classifica(self, alpha: float) -> ClasseVulnerabilitaMur:
        if alpha >= self.soglia_verificata:
            return ClasseVulnerabilitaMur.VERIFICATA
        elif alpha >= self.soglia_critica:
            return ClasseVulnerabilitaMur.CRITICA
        else:
            return ClasseVulnerabilitaMur.VULNERABILE


# ═══════════════════════════════════════════════════════════
#  Input parete muraria per vulnerabilità
# ═══════════════════════════════════════════════════════════


@dataclass
class PareteVulnerabile:
    """Dati di una parete muraria per analisi di vulnerabilità.

    Combina geometria + proprietà meccaniche + dati sismici localizzati.
    Le proprietà maccanicche sono già ridotte dal fattore di confidenza FC.
    """

    id_parete: str

    # Geometria
    h: float  # altezza parete [cm]
    t: float  # spessore [cm]
    L: float  # lunghezza / lunghezza maschio [cm]

    # Proprietà muratura (già ridotte per FC)
    fd: float  # resistenza a compressione [kg/cm²] (fk/γM)
    fvd0: float  # resistenza a taglio per scorrimento [kg/cm²] (fvk0/γM)
    E: float  # modulo elastico [kg/cm²]
    G: float | None = None  # modulo di taglio [kg/cm²] (default E/3)
    gamma: float = 0.0018  # peso specifico [kg/cm³; ≈1800 kg/m³]
    mu: float = 0.4  # coefficiente di attrito (NTC2018 §4.5.6.1.2)

    # Carichi
    N_sommita: float = 0.0  # carico verticale in sommità [kg/m lineare]

    # Posizione edificio
    Z: float = 0.0  # quota cerniera da fondazione [cm]
    H_edificio: float = 0.0  # altezza totale edificio [cm]

    # Posizione strutturale
    piano: str = ""
    note: str = ""

    @property
    def A_sezione(self) -> float:
        """Area della sezione trasversale [cm²]."""
        return self.L * self.t

    @property
    def peso_proprio(self) -> float:
        """Peso proprio parete [kg]."""
        return self.h * self.t * self.L * self.gamma

    @property
    def N_tot(self) -> float:
        """Carico verticale totale alla base [kg] (peso + sovraccarico)."""
        return self.peso_proprio + self.N_sommita * self.L / 100

    def G_eff(self) -> float:
        """Modulo di taglio effettivo [kg/cm²]."""
        return self.G if self.G is not None else self.E / 3.0


# ═══════════════════════════════════════════════════════════
#  LV1 — Valutazione speditiva
# ═══════════════════════════════════════════════════════════


def lv1_ntc2018(
    pareti: list[PareteVulnerabile],
    sismica: ParametriSismici,
    config: ConfigVulnerabilitaMur | None = None,
) -> tuple[float, list[str]]:
    """LV1 speditivo — NTC2018 + Circ. 7/2019 §C8.7.1.1.

    α = (τ_Rd × A_muratura_tot × g) / (W_tot × a_g × S) × q

    Il coefficiente α confronta la resistenza a taglio globale alla base
    con la domanda di taglio sismico.

    Riferimento: Circ. 7/2019 §C8.7.1.1 — formula (C8.7.11)
    """
    cfg = config or ConfigVulnerabilitaMur()
    passaggi: list[str] = ["═══ LV1 SPEDITIVO NTC2018 §C8.7.1.1 ═══"]

    fatt_deg = _FATTORI_DEGRADO[cfg.degrado.value]
    deg_fvd0 = fatt_deg["fvd0"]

    # Area totale muratura resistente in direzione di riferimento
    # (assumiamo pareti in media il 50% dell'area in pianta — semplificato)
    A_mur_tot = sum(p.A_sezione for p in pareti)
    W_tot = sum(p.N_tot for p in pareti)

    # fvd0 medio (media pesata per area)
    if A_mur_tot > 0:
        fvd0_medio = sum(p.fvd0 * p.A_sezione for p in pareti) / A_mur_tot
    else:
        fvd0_medio = 0.0

    fvd0_eff = fvd0_medio * deg_fvd0

    passaggi.append(f"Pareti analizzate: {len(pareti)}")
    passaggi.append(f"A_muratura totale = {A_mur_tot:.0f} cm²")
    passaggi.append(f"W_totale = {W_tot:.0f} kg")
    passaggi.append(
        f"fvd0 medio = {fvd0_medio:.4f} kg/cm² × degrado({cfg.degrado.value})={deg_fvd0} → {fvd0_eff:.4f}"
    )

    # Resistenza a taglio globale alla base
    V_Rd = fvd0_eff * A_mur_tot
    passaggi.append(f"V_Rd = fvd0_eff × A_tot = {V_Rd:.0f} kg")

    # Domanda sismica (taglio alla base)
    # V_Ed = W_tot × a_g × S × FC / q   (NTC2018 §7.3.3 — forze sismiche)
    a_sismo = sismica.a_g * sismica.S * sismica.FC / sismica.q
    V_Ed = W_tot * a_sismo
    passaggi.append(
        f"V_Ed = W × a_g × S × FC / q = {W_tot:.0f} × {sismica.a_g}×{sismica.S}×{sismica.FC}/{sismica.q}"
        f" = {V_Ed:.0f} kg"
    )

    alpha = V_Rd / V_Ed if V_Ed > 0 else 0.0
    passaggi.append(
        f"α = V_Rd / V_Ed = {V_Rd:.0f} / {V_Ed:.0f} = {alpha:.3f}"
        f" → {'VERIFICATO' if alpha >= 1.0 else 'NON VERIFICATO'}"
    )

    return alpha, passaggi


def lv1_opcm3274(
    pareti: list[PareteVulnerabile],
    sismica: ParametriSismici,
    config: ConfigVulnerabilitaMur | None = None,
) -> tuple[float, list[str]]:
    """LV1 speditivo — OPCM 3274/2003 §11.2.

    IS = τ_u / τ_g
    τ_u = fvd0 (resistenza a taglio di progetto)
    τ_g = W_tot × a_g / (A_muratura × g) (tensione di taglio da sisma)

    Riferimento: OPCM 3274/2003 §11.2, Tab. 11.II.
    """
    cfg = config or ConfigVulnerabilitaMur()
    passaggi: list[str] = ["═══ LV1 SPEDITIVO OPCM 3274/2003 §11.2 ═══"]

    fatt_deg = _FATTORI_DEGRADO[cfg.degrado.value]
    deg_fvd0 = fatt_deg["fvd0"]

    A_mur_tot = sum(p.A_sezione for p in pareti)
    W_tot = sum(p.N_tot for p in pareti)
    if A_mur_tot > 0:
        fvd0_medio = sum(p.fvd0 * p.A_sezione for p in pareti) / A_mur_tot
    else:
        fvd0_medio = 0.0
    fvd0_eff = fvd0_medio * deg_fvd0

    # τ_u = resistenza a taglio unitaria
    tau_u = fvd0_eff

    # τ_g = taglio sismico / area resistente
    tau_g = (
        (W_tot * sismica.a_g * sismica.S * sismica.FC) / A_mur_tot
        if A_mur_tot > 0
        else float("inf")
    )

    IS = tau_u / tau_g if tau_g > 0 else 0.0

    passaggi.append(f"τ_u = fvd0_eff = {tau_u:.4f} kg/cm²")
    passaggi.append(f"τ_g = W×ag×S×FC/A = {tau_g:.4f} kg/cm²")
    passaggi.append(f"IS (Indice Sicurezza) = τ_u/τ_g = {IS:.3f}")

    return IS, passaggi


def lv1_letteratura(
    pareti: list[PareteVulnerabile],
    sismica: ParametriSismici,
    config: ConfigVulnerabilitaMur | None = None,
) -> tuple[float, list[str]]:
    """LV1 speditivo — Criterio Turnšek-Čačovič generalizzato.

    Il criterio diagonale (§C8.7.1.1) usa la resistenza τ_cr = fvk0 × √(1 + σ_n/fvk0).
    Confrontata con τ_g = V_sismica / A_muratura.

    Riferimento: Turnšek & Čačovič (1970) — muratura non armata.
    """
    cfg = config or ConfigVulnerabilitaMur()
    passaggi: list[str] = ["═══ LV1 SPEDITIVO Turnšek–Čačovič (letteratura) ═══"]

    fatt_deg = _FATTORI_DEGRADO[cfg.degrado.value]

    A_mur_tot = sum(p.A_sezione for p in pareti)
    W_tot = sum(p.N_tot for p in pareti)

    alphas = []
    for parete in pareti:
        A = parete.A_sezione
        sigma_n = parete.N_tot / A if A > 0 else 0.0
        fvd0_eff = parete.fvd0 * fatt_deg["fvd0"]
        # Resistenza critica a taglio diagonale
        tau_cr = fvd0_eff * math.sqrt(1.0 + sigma_n / fvd0_eff) if fvd0_eff > 0 else 0.0
        # Domanda a taglio per parete (quota proporzionale al peso)
        V_g = (
            (parete.N_tot / W_tot) * W_tot * sismica.a_g * sismica.S * sismica.FC
            if W_tot > 0
            else 0.0
        )
        tau_g = V_g / A if A > 0 else float("inf")
        alpha_p = tau_cr / tau_g if tau_g > 0 else float("inf")
        alphas.append(alpha_p)
        passaggi.append(
            f"Parete {parete.id_parete}: σ_n={sigma_n:.2f}, τ_cr={tau_cr:.4f}, "
            f"τ_g={tau_g:.4f}, α={alpha_p:.3f}"
        )

    alpha_medio = sum(alphas) / len(alphas) if alphas else 0.0
    passaggi.append(f"α medio Turnšek–Čačovič = {alpha_medio:.3f}")

    return alpha_medio, passaggi


# ═══════════════════════════════════════════════════════════
#  Meccanismo di scorrimento (R.3 — completo)
# ═══════════════════════════════════════════════════════════


def scorrimento_parete(
    parete: PareteVulnerabile,
    sismica: ParametriSismici,
    config: ConfigVulnerabilitaMur | None = None,
) -> RisultatoCinematica:
    """Meccanismo di scorrimento della parete lungo il piano orizzontale.

    Analisi cinematica lineare per il meccanismo di scorrimento rigido-plastico
    lungo la sezione di base (o di un giunto orizzontale).

    Resistenza (forza orizzontale critica):
    R_hor = fvd0 × A_base + μ × N_tot  [Circ. 7/2019 §C8A.4.1 — Mohr-Coulomb]

    Azione sismica:
    H_sis = α × N_tot  (dove N_tot = peso parete + carichi verticali)

    All'equilibrio:
    α₀ = R_hor / N_tot = fvd0 × (L×t) / N_tot + μ  [adimensionale]

    Verifica cinematica lineare:
    a₀* = α₀ / (e* × FC)
    a₀* ≥ a_domanda = a_g × S / q  (parete a terra)
    oppure
    a₀* ≥ S_e(T1) × ψ(Z/H) × γ / q  (parete in quota)

    Riferimento: Circ. 7/2019 §C8A.4.1 — meccanismi locali pianali.
    """
    cfg = config or ConfigVulnerabilitaMur()
    passaggi: list[str] = ["═══ SCORRIMENTO PARETE ═══"]

    fatt_deg = _FATTORI_DEGRADO[cfg.degrado.value]
    fvd0_eff = parete.fvd0 * fatt_deg["fvd0"]

    A_base = parete.L * parete.t
    N_tot = parete.N_tot  # kg
    mu = parete.mu

    passaggi.append(f"Parete {parete.id_parete}: L={parete.L:.0f}cm × t={parete.t:.0f}cm")
    passaggi.append(f"N_tot = peso_proprio + N_sommita = {N_tot:.0f} kg")
    passaggi.append(f"fvd0_eff = {fvd0_eff:.4f} kg/cm² (degrado: {cfg.degrado.value})")
    passaggi.append(f"μ = {mu} (coefficiente attrito NTC2018 §4.5.6.1.2)")

    # Resistenza orizzontale (Mohr-Coulomb)
    R_hor = fvd0_eff * A_base + mu * N_tot
    passaggi.append(
        f"R_hor = fvd0×A + μ×N = {fvd0_eff:.4f}×{A_base:.0f} + {mu}×{N_tot:.0f} = {R_hor:.0f} kg"
    )

    # Moltiplicatore di collasso
    alpha_0 = R_hor / N_tot if N_tot > 0 else 0.0
    passaggi.append(f"α₀ = R_hor / N_tot = {R_hor:.0f} / {N_tot:.0f} = {alpha_0:.4f}")

    # Cinematica lineare: a₀* = α₀ / (e* × FC)
    e_star = 1.0  # scorrimento rigido: tutte le masse si muovono per la stessa quantità
    a_0_star = alpha_0 / (e_star * sismica.FC) if (e_star * sismica.FC) > 0 else 0.0

    passaggi.append(f"e* = {e_star:.2f} (scorrimento rigido)")
    passaggi.append(
        f"a₀* = α₀ / (e*×FC) = {alpha_0:.4f} / ({e_star}×{sismica.FC}) = {a_0_star:.4f} g"
    )

    # Domanda sismica
    if parete.Z <= 0 or parete.H_edificio <= 0:
        a_domanda = sismica.a_g * sismica.S / sismica.q
        passaggi.append(
            f"Verifica A TERRA: a_domanda = a_g×S/q = {sismica.a_g}×{sismica.S}/{sismica.q}"
            f" = {a_domanda:.4f} g"
        )
    else:
        psi_Z = parete.Z / parete.H_edificio
        S_e_T1 = sismica.a_g * sismica.S * 2.5  # approssimazione plateau spettrale
        a_domanda = S_e_T1 * psi_Z * sismica.gamma_modal / sismica.q
        passaggi.append(
            f"Verifica IN QUOTA: ψ(Z={parete.Z:.0f}/{parete.H_edificio:.0f})={psi_Z:.3f}, "
            f"a_domanda = {a_domanda:.4f} g"
        )

    verifica_lin = a_0_star >= a_domanda
    passaggi.append(
        f"a₀* = {a_0_star:.4f} {'≥' if verifica_lin else '<'} a_domanda = {a_domanda:.4f}"
        f" → {'VERIFICATO' if verifica_lin else 'NON VERIFICATO'}"
    )

    # Cinematica non lineare: d*_u = 0.4 × d*₀
    # Per scorrimento: d*₀ ≈ t/2 (regime plastico completo)
    d_0_star = parete.t / 2.0
    d_u_star = 0.4 * d_0_star
    a_0_star_cms2 = a_0_star * 981.0
    T_s = (
        2 * math.pi * math.sqrt(d_0_star / a_0_star_cms2)
        if a_0_star_cms2 > 0 and d_0_star > 0
        else 0.0
    )
    if sismica.S_De_Ts > 0:
        d_domanda = sismica.S_De_Ts
    else:
        S_D1_cms2 = sismica.a_g * sismica.S * 981.0 * 2.5
        d_domanda = S_D1_cms2 * T_s**2 / (4 * math.pi**2) if T_s > 0 else 0.0
    if parete.Z > 0 and parete.H_edificio > 0:
        d_domanda *= parete.Z / parete.H_edificio

    verifica_nlin = d_u_star >= d_domanda
    passaggi.append(
        f"d*₀={d_0_star:.2f}cm, d*_u={d_u_star:.2f}cm, d_domanda={d_domanda:.3f}cm"
        f" → {'VERIFICATO' if verifica_nlin else 'NON VERIFICATO'}"
    )

    return RisultatoCinematica(
        meccanismo="scorrimento",
        alpha_0=alpha_0,
        M_star=N_tot,
        e_star=e_star,
        a_0_star=a_0_star,
        a_domanda=a_domanda,
        verifica_lineare=verifica_lin,
        d_0_star=d_0_star,
        d_u_star=d_u_star,
        d_domanda=d_domanda,
        verifica_non_lineare=verifica_nlin,
        forze_stabilizzanti=R_hor,
        forze_ribaltanti=N_tot,
        passaggi=passaggi,
    )


# ═══════════════════════════════════════════════════════════
#  LV2 — Analisi meccanismi locali per parete
# ═══════════════════════════════════════════════════════════


@dataclass
class RisultatoParete:
    """Risultato LV2 per una singola parete muraria."""

    id_parete: str

    meccanismi: dict[str, RisultatoCinematica] = field(default_factory=dict)

    # Indici sintetici
    alpha_min: float = 0.0  # α minimo tra tutti i meccanismi (lineare)
    alpha_medio: float = 0.0  # α medio tra meccanismi
    meccanismo_critico: str = ""

    classe: ClasseVulnerabilitaMur = ClasseVulnerabilitaMur.VULNERABILE

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_parete": self.id_parete,
            "alpha_min": round(self.alpha_min, 3),
            "alpha_medio": round(self.alpha_medio, 3),
            "meccanismo_critico": self.meccanismo_critico,
            "classe": self.classe.value,
            "meccanismi": {
                k: {
                    "alpha_0": round(v.alpha_0, 4),
                    "a_0_star": round(v.a_0_star, 4),
                    "a_domanda": round(v.a_domanda, 4),
                    "verifica_lineare": v.verifica_lineare,
                }
                for k, v in self.meccanismi.items()
            },
        }


def analisi_lv2_parete(
    parete: PareteVulnerabile,
    sismica: ParametriSismici,
    config: ConfigVulnerabilitaMur | None = None,
    catene: list[ForzaCatena] | None = None,
    cuneo_h: float | None = None,
) -> RisultatoParete:
    """Analisi LV2 meccanismi locali per una parete muraria.

    Esegue i meccanismi selezionati in config.meccanismi_lv2 e restituisce
    il risultato sintetico con α_min e meccanismo critico.

    Args:
        parete: dati parete (resistenze già con FC)
        sismica: parametri sismici (FC già incluso)
        config: configurazione meccanismi e soglie
        catene: eventuali catene stabilizzanti (applicate a tutti i meccanismi)
        cuneo_h: altezza cuneo per ribaltamento composto [cm] (default h/4)

    Returns:
        RisultatoParete con tutti i meccanismi calcolati
    """
    cfg = config or ConfigVulnerabilitaMur()
    meccanismi_out: dict[str, RisultatoCinematica] = {}

    # Costruisce PareteMuraria per cinematica
    pm = PareteMuraria(
        h=parete.h,
        t=parete.t,
        L=parete.L,
        gamma=parete.gamma,
        N_sommita=parete.N_sommita,
        Z=parete.Z,
        H_edificio=parete.H_edificio,
    )

    mecs = cfg.meccanismi_lv2

    if TipoMeccanismo.RIBALTAMENTO_SEMPLICE.value in mecs:
        ris = ribaltamento_semplice(pm, sismica, catene)
        meccanismi_out[TipoMeccanismo.RIBALTAMENTO_SEMPLICE.value] = ris

    if TipoMeccanismo.RIBALTAMENTO_COMPOSTO.value in mecs:
        ch = cuneo_h if cuneo_h is not None else parete.h / 4.0
        ris = ribaltamento_composto(pm, ch, sismica=sismica, catene=catene)
        meccanismi_out[TipoMeccanismo.RIBALTAMENTO_COMPOSTO.value] = ris

    if TipoMeccanismo.FLESSIONE_VERTICALE.value in mecs:
        ris = flessione_verticale(pm, sismica=sismica, catene=catene)
        meccanismi_out[TipoMeccanismo.FLESSIONE_VERTICALE.value] = ris

    if TipoMeccanismo.FLESSIONE_ORIZZONTALE.value in mecs:
        ris = flessione_orizzontale(pm, sismica=sismica, catene=catene)
        meccanismi_out[TipoMeccanismo.FLESSIONE_ORIZZONTALE.value] = ris

    if "scorrimento" in mecs:
        ris_scorr = scorrimento_parete(parete, sismica, cfg)
        meccanismi_out["scorrimento"] = ris_scorr

    if not meccanismi_out:
        return RisultatoParete(id_parete=parete.id_parete)

    # Indice sintetico: usa a₀*/a_domanda come misura di α
    alphas: dict[str, float] = {}
    for nome, res in meccanismi_out.items():
        alpha_ratio = res.a_0_star / res.a_domanda if res.a_domanda > 0 else float("inf")
        alphas[nome] = alpha_ratio

    alpha_min_val = min(alphas.values())
    alpha_medio_val = sum(alphas.values()) / len(alphas)
    mec_critico = min(alphas, key=lambda k: alphas[k])

    classe = cfg.classifica(alpha_min_val)

    ris_parete = RisultatoParete(
        id_parete=parete.id_parete,
        meccanismi=meccanismi_out,
        alpha_min=alpha_min_val,
        alpha_medio=alpha_medio_val,
        meccanismo_critico=mec_critico,
        classe=classe,
    )

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione=f"LV2 meccanismi locali: {parete.id_parete}",
        input_dati={
            "meccanismi": list(meccanismi_out.keys()),
            "FC": sismica.FC,
        },
        output_dati={
            "alpha_min": round(alpha_min_val, 3),
            "meccanismo_critico": mec_critico,
            "classe": classe.value,
        },
        normativa="Circ. 7/2019 §C8A.4.1",
        formula="α = a₀*/a_domanda",
        esito="OK" if classe == ClasseVulnerabilitaMur.VERIFICATA else "ATTENZIONE",
    )

    return ris_parete


# ═══════════════════════════════════════════════════════════
#  Risultato globale edificio muratura
# ═══════════════════════════════════════════════════════════


@dataclass
class IndiceVulnerabilitaMur:
    """Indice globale vulnerabilità edificio in muratura."""

    alpha_min_globale: float  # peggiore parete/meccanismo
    alpha_medio_globale: float  # media su tutte le pareti

    # LV1
    alpha_lv1: float | None = None
    formula_lv1: str = ""

    n_verificate: int = 0
    n_critiche: int = 0
    n_vulnerabili: int = 0

    # Ranking pareti
    ranking: list[dict[str, Any]] = field(default_factory=list)
    classe: ClasseVulnerabilitaMur = ClasseVulnerabilitaMur.VULNERABILE

    def to_dict(self) -> dict[str, Any]:
        return {
            "alpha_lv1": (round(self.alpha_lv1, 3) if self.alpha_lv1 is not None else None),
            "formula_lv1": self.formula_lv1,
            "alpha_min_globale": round(self.alpha_min_globale, 3),
            "alpha_medio_globale": round(self.alpha_medio_globale, 3),
            "n_verificate": self.n_verificate,
            "n_critiche": self.n_critiche,
            "n_vulnerabili": self.n_vulnerabili,
            "classe": self.classe.value,
            "ranking_top5": self.ranking[:5],
        }


def analisi_vulnerabilita_mur(
    pareti: list[PareteVulnerabile],
    sismica: ParametriSismici,
    config: ConfigVulnerabilitaMur | None = None,
    catene_per_parete: dict[str, list[ForzaCatena]] | None = None,
) -> tuple[IndiceVulnerabilitaMur, list[RisultatoParete]]:
    """Analisi completa vulnerabilità muratura (LV1 + LV2 per ogni parete).

    Args:
        pareti: lista di PareteVulnerabile (FC applicato alle proprietà)
        sismica: parametri sismici edificio
        config: configurazione analisi (formule, meccanismi, degrado)
        catene_per_parete: dict {id_parete: [ForzaCatena, ...]} facoltativo

    Returns:
        (IndiceVulnerabilitaMur, [RisultatoParete per ogni parete])
    """
    cfg = config or ConfigVulnerabilitaMur()
    catene_map = catene_per_parete or {}

    if not pareti:
        return IndiceVulnerabilitaMur(alpha_min_globale=0.0, alpha_medio_globale=0.0), []

    # LV1
    alpha_lv1: float | None = None
    if cfg.formula_lv1 == FormuleLV1.NTC2018:
        alpha_lv1, _ = lv1_ntc2018(pareti, sismica, cfg)
        formula_txt = "NTC2018 §C8.7.1.1"
    elif cfg.formula_lv1 == FormuleLV1.OPCM3274:
        alpha_lv1, _ = lv1_opcm3274(pareti, sismica, cfg)
        formula_txt = "OPCM 3274/2003 §11.2"
    else:
        alpha_lv1, _ = lv1_letteratura(pareti, sismica, cfg)
        formula_txt = "Turnšek–Čačovič"

    # LV2 per ogni parete
    risultati: list[RisultatoParete] = []
    for parete in pareti:
        catene = catene_map.get(parete.id_parete)
        ris = analisi_lv2_parete(parete, sismica, cfg, catene)
        risultati.append(ris)

    # Statistiche globali
    n_ver = sum(1 for r in risultati if r.classe == ClasseVulnerabilitaMur.VERIFICATA)
    n_crit = sum(1 for r in risultati if r.classe == ClasseVulnerabilitaMur.CRITICA)
    n_vul = sum(1 for r in risultati if r.classe == ClasseVulnerabilitaMur.VULNERABILE)

    alphas_min = [r.alpha_min for r in risultati]
    alpha_min_gl = min(alphas_min)
    alpha_medio_gl = sum(alphas_min) / len(alphas_min)

    ranking = sorted(
        [
            {
                "id": r.id_parete,
                "alpha_min": round(r.alpha_min, 3),
                "meccanismo_critico": r.meccanismo_critico,
                "classe": r.classe.value,
            }
            for r in risultati
        ],
        key=lambda x: x["alpha_min"],
    )

    # Classe globale sul peggiore
    classe_gl = cfg.classifica(alpha_min_gl)

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Vulnerabilità globale edificio muratura",
        input_dati={"n_pareti": len(pareti), "formula_lv1": cfg.formula_lv1.value},
        output_dati={
            "alpha_lv1": round(alpha_lv1, 3) if alpha_lv1 is not None else None,
            "alpha_min": round(alpha_min_gl, 3),
            "alpha_medio": round(alpha_medio_gl, 3),
        },
        normativa="NTC2018 §8.7.1 + Circ. 7/2019",
        formula="α = a₀*/a_domanda; LV1: α=VRd/VEd",
        esito="OK" if classe_gl == ClasseVulnerabilitaMur.VERIFICATA else "ATTENZIONE",
    )

    indice = IndiceVulnerabilitaMur(
        alpha_min_globale=alpha_min_gl,
        alpha_medio_globale=alpha_medio_gl,
        alpha_lv1=alpha_lv1,
        formula_lv1=formula_txt,
        n_verificate=n_ver,
        n_critiche=n_crit,
        n_vulnerabili=n_vul,
        ranking=ranking,
        classe=classe_gl,
    )
    return indice, risultati
