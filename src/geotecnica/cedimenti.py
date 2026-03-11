"""Calcoli cedimenti (P.2).

Contiene il nucleo iniziale per cedimento elastico immediato e
consolidazione primaria 1D con impostazione estendibile.
"""

from __future__ import annotations

import math

from .models import InputCedimenti, RisultatoCedimenti


def cedimento_elastico_boussinesq(input_data: InputCedimenti) -> float:
    """Calcola cedimento elastico immediato in cm.

    Formula: rho = q * B * (1 - nu^2) / E_s * I_rho
    """

    q = input_data.pressione_media_kg_cm2()
    e_s = input_data.modulo_elastico_kg_cm2()
    return (
        q
        * input_data.larghezza_fondazione_cm
        * (1.0 - input_data.coeff_poisson**2)
        / e_s
        * input_data.fattore_influenza_i_rho
    )


def cedimento_consolidazione_primaria(input_data: InputCedimenti) -> float:
    """Calcola cedimento da consolidazione primaria 1D in cm."""

    if (
        input_data.indice_compressione_cc <= 0.0
        or input_data.indice_vuoti_e0 <= 0.0
        or input_data.spessore_strato_consolidante_cm <= 0.0
        or input_data.sigma_eff_iniziale <= 0.0
        or input_data.sigma_eff_finale <= 0.0
    ):
        return 0.0

    sigma_0 = input_data.sigma_eff_iniziale_kg_cm2()
    sigma_f = input_data.sigma_eff_finale_kg_cm2()
    if sigma_f <= sigma_0:
        return 0.0

    rapporto = sigma_f / sigma_0
    return (
        input_data.indice_compressione_cc
        / (1.0 + input_data.indice_vuoti_e0)
        * input_data.spessore_strato_consolidante_cm
        * math.log10(rapporto)
    )


def grado_consolidazione_medio(t_v: float) -> float:
    """Stima rapida del grado di consolidazione medio U(Tv)."""

    if t_v <= 0.0:
        return 0.0
    if t_v < 0.2:
        return min((2.0 / math.sqrt(math.pi)) * math.sqrt(t_v), 1.0)
    return min(1.0 - math.exp(-math.pi**2 * t_v / 4.0), 1.0)


def coefficiente_tempo_consolidazione(c_v_cm2_s: float, t_secondi: float, h_d_cm: float) -> float:
    """Calcola il fattore tempo Tv = c_v * t / H_d^2."""

    if h_d_cm <= 0.0:
        raise ValueError("h_d_cm deve essere > 0")
    return c_v_cm2_s * t_secondi / (h_d_cm**2)


def calcola_cedimenti(input_data: InputCedimenti) -> RisultatoCedimenti:
    """Esegue il calcolo completo dei cedimenti P.2."""

    rho_immediato = cedimento_elastico_boussinesq(input_data)
    rho_consolidazione = cedimento_consolidazione_primaria(input_data)
    rho_tot = rho_immediato + rho_consolidazione

    passaggi = [
        "Cedimento immediato: rho = q * B * (1 - nu^2) / E_s * I_rho",
        f"rho_immediato = {rho_immediato:.5f} cm",
        "Cedimento consolidazione: rho_c = Cc/(1+e0) * H * log10(sigma_f/sigma_0)",
        f"rho_consolidazione = {rho_consolidazione:.5f} cm",
        f"rho_totale = {rho_tot:.5f} cm",
    ]

    return RisultatoCedimenti(
        cedimento_immediato_cm=rho_immediato,
        cedimento_consolidazione_cm=rho_consolidazione,
        cedimento_totale_cm=rho_tot,
        passaggi_calcolo=passaggi,
    )
