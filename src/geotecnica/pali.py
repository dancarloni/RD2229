"""Calcoli per fondazioni profonde su pali (P.3).

Supporta:
- portanza in argilla (metodo α, N_c=9)
- portanza in sabbia da SPT (correlazioni Meyerhof)
- portanza in sabbia da CPT (correlazioni Robertson-Campanella)
- verifica SLU NTC2018 §6.4.3
- efficienza gruppo pali (formula Converse-Labarre)
"""

from __future__ import annotations

import math

from .models import InputGruppoPali, InputPortanzaPalo, RisultatoPortanzaPalo, TipologiaPalo


# ---------------------------------------------------------------------------
# Fattori e correlazioni
# ---------------------------------------------------------------------------

_NC_PALO = 9.0  # Fattore di portanza di punta in argilla (Skempton)

# Meyerhof SPT: coefficiente punta (kg/cm2 per NSPT)
_ALPHA_B_MEYERHOF = 4.0  # kg/cm2 per unita di N_SPT (sabbia)
# Meyerhof SPT: coefficiente laterale (kg/cm2 per NSPT)
_ALPHA_S_MEYERHOF = 0.2  # kg/cm2 per unita di N_SPT (sabbia)

# Robertson-Campanella CPT
_KC_CPT = 0.40  # fattore punta q_b = k_c * q_c
_NS_CPT = 100.0  # fattore laterale f_s = q_c / n_s  (dimensioni kg/cm2)


def _area_punta_cm2(diametro_cm: float) -> float:
    return math.pi * (diametro_cm / 2.0) ** 2


def _area_laterale_cm2(diametro_cm: float, lunghezza_cm: float) -> float:
    return math.pi * diametro_cm * lunghezza_cm


def portanza_punta_argilla_kg(diametro_cm: float, c_u_kg_cm2: float) -> float:
    """Portanza di punta in argilla: Q_p = N_c * c_u * A_p (N_c=9)."""

    return _NC_PALO * c_u_kg_cm2 * _area_punta_cm2(diametro_cm)


def portanza_laterale_argilla_kg(diametro_cm: float, lunghezza_cm: float, c_u_kg_cm2: float) -> float:
    """Portanza laterale in argilla: Q_s = α * c_u * A_s.

    Il fattore α (adesione) è stimato con relazione di Terzaghi:
    α = 1.0 per c_u ≤ 0.25 kg/cm2; α = 0.5 per c_u ≥ 0.5 kg/cm2;
    interpolazione lineare nel range intermedio.
    """

    alpha = _fattore_adesione_argilla(c_u_kg_cm2)
    return alpha * c_u_kg_cm2 * _area_laterale_cm2(diametro_cm, lunghezza_cm)


def _fattore_adesione_argilla(c_u_kg_cm2: float) -> float:
    if c_u_kg_cm2 <= 0.0:
        return 0.0
    if c_u_kg_cm2 <= 0.255:  # ~25 kPa
        return 1.0
    if c_u_kg_cm2 >= 0.510:  # ~50 kPa
        return 0.5
    # interpolazione lineare tra 0.255 e 0.510 kg/cm2
    return 1.0 - 0.5 * (c_u_kg_cm2 - 0.255) / (0.510 - 0.255)


def portanza_punta_spt_kg(diametro_cm: float, n_spt: float) -> float:
    """Portanza di punta da SPT (correlazione Meyerhof, sabbia).

    q_b = alpha_b * N_SPT  [kg/cm2]
    """

    q_b = _ALPHA_B_MEYERHOF * max(n_spt, 0.0)
    return q_b * _area_punta_cm2(diametro_cm)


def portanza_laterale_spt_kg(diametro_cm: float, lunghezza_cm: float, n_spt: float) -> float:
    """Portanza laterale da SPT (correlazione Meyerhof, sabbia).

    f_s = alpha_s * N_SPT  [kg/cm2]
    """

    f_s = _ALPHA_S_MEYERHOF * max(n_spt, 0.0)
    return f_s * _area_laterale_cm2(diametro_cm, lunghezza_cm)


def portanza_punta_cpt_kg(diametro_cm: float, q_c_kg_cm2: float) -> float:
    """Portanza di punta da CPT (Robertson-Campanella).

    q_b = k_c * q_c
    """

    q_b = _KC_CPT * max(q_c_kg_cm2, 0.0)
    return q_b * _area_punta_cm2(diametro_cm)


def portanza_laterale_cpt_kg(diametro_cm: float, lunghezza_cm: float, q_c_kg_cm2: float) -> float:
    """Portanza laterale da CPT (Robertson-Campanella).

    f_s = q_c / n_s
    """

    f_s = max(q_c_kg_cm2, 0.0) / _NS_CPT
    return f_s * _area_laterale_cm2(diametro_cm, lunghezza_cm)


# ---------------------------------------------------------------------------
# Efficienza gruppo pali (Converse-Labarre)
# ---------------------------------------------------------------------------


def efficienza_gruppo_converse_labarre(
    n_righe: int, n_colonne: int, diametro_cm: float, interasse_cm: float
) -> float:
    """Formula di Converse-Labarre per l'efficienza del gruppo di pali.

    η = 1 - θ/(90) * [(n_col-1)*n_rig + (n_rig-1)*n_col] / (n_rig*n_col)

    dove θ = arctan(d/s) in gradi, d = diametro, s = interasse.
    """

    if interasse_cm <= 0 or diametro_cm <= 0:
        raise ValueError("interasse e diametro devono essere > 0")

    theta_gradi = math.degrees(math.atan(diametro_cm / interasse_cm))
    n = n_righe * n_colonne
    if n == 1:
        return 1.0

    somma = (n_colonne - 1) * n_righe + (n_righe - 1) * n_colonne
    eta = 1.0 - (theta_gradi / 90.0) * somma / n
    return max(eta, 0.0)


# ---------------------------------------------------------------------------
# Portanza palo singolo
# ---------------------------------------------------------------------------


def calcola_portanza_palo(input_data: InputPortanzaPalo) -> RisultatoPortanzaPalo:
    """Calcola portanza palo singolo e verifica SLU NTC2018 §6.4.3."""

    d = input_data.diametro_palo_cm
    l = input_data.lunghezza_palo_cm
    passaggi: list[str] = [
        f"Palo: diametro={d:.1f} cm, lunghezza={l:.1f} cm",
        f"Tipologia terreno: {input_data.tipologia.value}",
    ]

    if input_data.tipologia == TipologiaPalo.ARGILLA:
        q_punta = portanza_punta_argilla_kg(d, input_data.c_u_kgcm2)
        q_laterale = portanza_laterale_argilla_kg(d, l, input_data.c_u_kgcm2)
        alpha = _fattore_adesione_argilla(input_data.c_u_kgcm2)
        passaggi += [
            f"c_u = {input_data.c_u_kgcm2:.4f} kg/cm2",
            f"α (adesione) = {alpha:.3f}",
            f"A_punta = {_area_punta_cm2(d):.2f} cm2",
            f"A_laterale = {_area_laterale_cm2(d, l):.2f} cm2",
            f"Q_punta = N_c({_NC_PALO}) * c_u * A_p = {q_punta:.1f} kg",
            f"Q_laterale = α * c_u * A_s = {q_laterale:.1f} kg",
        ]

    elif input_data.tipologia == TipologiaPalo.SABBIA_SPT:
        q_punta = portanza_punta_spt_kg(d, input_data.n_spt_medio)
        q_laterale = portanza_laterale_spt_kg(d, l, input_data.n_spt_medio)
        passaggi += [
            f"N_SPT_medio = {input_data.n_spt_medio:.1f}",
            f"q_b = α_b * N_SPT = {_ALPHA_B_MEYERHOF} * {input_data.n_spt_medio:.1f} = {_ALPHA_B_MEYERHOF*input_data.n_spt_medio:.2f} kg/cm2",
            f"Q_punta = q_b * A_p = {q_punta:.1f} kg",
            f"f_s = α_s * N_SPT = {_ALPHA_S_MEYERHOF} * {input_data.n_spt_medio:.1f} = {_ALPHA_S_MEYERHOF*input_data.n_spt_medio:.2f} kg/cm2",
            f"Q_laterale = f_s * A_s = {q_laterale:.1f} kg",
        ]

    elif input_data.tipologia == TipologiaPalo.SABBIA_CPT:
        q_punta = portanza_punta_cpt_kg(d, input_data.q_c_kgcm2)
        q_laterale = portanza_laterale_cpt_kg(d, l, input_data.q_c_kgcm2)
        passaggi += [
            f"q_c = {input_data.q_c_kgcm2:.4f} kg/cm2",
            f"q_b = k_c * q_c = {_KC_CPT} * {input_data.q_c_kgcm2:.4f} = {_KC_CPT*input_data.q_c_kgcm2:.4f} kg/cm2",
            f"Q_punta = q_b * A_p = {q_punta:.1f} kg",
            f"f_s = q_c / n_s = {input_data.q_c_kgcm2:.4f} / {_NS_CPT} = {input_data.q_c_kgcm2/_NS_CPT:.6f} kg/cm2",
            f"Q_laterale = f_s * A_s = {q_laterale:.1f} kg",
        ]

    else:
        raise ValueError(f"Tipologia non supportata: {input_data.tipologia}")

    q_lim = q_punta + q_laterale
    # Verifica SLU: applicazione separata gamma_R su punta e laterale (NTC2018 §6.4.3)
    q_rd = q_punta / input_data.gamma_r_punta + q_laterale / input_data.gamma_r_laterale
    forza = input_data.forza_verticale_kg
    rapporto = forza / q_rd if q_rd > 0 else math.inf

    passaggi += [
        f"Q_lim = Q_punta + Q_laterale = {q_lim:.1f} kg",
        f"γ_R_punta = {input_data.gamma_r_punta:.2f}, γ_R_laterale = {input_data.gamma_r_laterale:.2f}",
        f"Q_Rd = Q_punta/γ_R_punta + Q_lat/γ_R_lat = {q_rd:.1f} kg",
        f"Forza verticale Q_Ed = {forza:.1f} kg",
        f"Rapporto utilizzo = Q_Ed / Q_Rd = {rapporto:.4f}",
        f"Verificato: {rapporto <= 1.0}",
    ]

    return RisultatoPortanzaPalo(
        q_punta_kg=q_punta,
        q_laterale_kg=q_laterale,
        q_lim_kg=q_lim,
        q_rd_kg=q_rd,
        forza_verticale_kg=forza,
        rapporto_utilizzo=rapporto,
        verificato=rapporto <= 1.0,
        passaggi_calcolo=passaggi,
    )


def calcola_efficienza_gruppo(input_data: InputGruppoPali) -> float:
    """Calcola efficienza gruppo pali con formula Converse-Labarre."""

    return efficienza_gruppo_converse_labarre(
        input_data.n_pali_riga,
        input_data.n_pali_colonna,
        input_data.diametro_palo_cm,
        input_data.interasse_cm,
    )
