"""Calcoli per fondazioni superficiali (P.1).

Implementazione iniziale focalizzata su portanza con schema Vesic,
strutturata per estensioni future di fattori correttivi e norme.
"""

from __future__ import annotations

import math

from .models import InputPortanzaFondazione, RisultatoPortanzaFondazione, RisultatoVerificaSLU
from .norme import crea_norma_geotecnica
from .utils import clamp_non_negativo, riduci_tan_phi, sovraccarico_geostatico_kg_cm2


def fattori_portanza_vesic(phi_gradi: float) -> tuple[float, float, float]:
    """Restituisce (Nc, Nq, Ngamma) secondo schema Vesic."""

    if not (0.0 <= phi_gradi < 90.0):
        raise ValueError("phi_gradi deve essere compreso tra 0 e 90")

    if abs(phi_gradi) < 1e-12:
        return 5.14, 1.0, 0.0

    phi = math.radians(phi_gradi)
    n_q = math.exp(math.pi * math.tan(phi)) * (math.tan(math.radians(45.0) + phi / 2.0) ** 2)
    n_c = (n_q - 1.0) / math.tan(phi)
    n_gamma = 2.0 * (n_q + 1.0) * math.tan(phi)
    return n_c, n_q, n_gamma


def fattori_forma_vesic(b_eff_cm: float, l_eff_cm: float) -> tuple[float, float, float]:
    """Fattori di forma iniziali per geometria rettangolare."""

    rapporto = min(b_eff_cm, l_eff_cm) / max(b_eff_cm, l_eff_cm)
    s_c = 1.0 + 0.2 * rapporto
    s_q = 1.0 + 0.1 * rapporto
    s_gamma = 1.0 - 0.4 * rapporto
    return s_c, s_q, max(s_gamma, 0.60)


def fattori_profondita_vesic(d_f_cm: float, b_eff_cm: float) -> tuple[float, float, float]:
    """Fattori di profondita' iniziali (versione estensibile)."""

    if b_eff_cm <= 0:
        raise ValueError("b_eff_cm deve essere > 0")
    rapporto = d_f_cm / b_eff_cm
    d_c = 1.0 + 0.2 * rapporto
    d_q = 1.0 + 0.1 * rapporto
    d_gamma = 1.0
    return d_c, d_q, d_gamma


def fattori_inclinazione_carico(
    h_orizzontale_kg: float, n_verticale_kg: float
) -> tuple[float, float, float]:
    """Fattori di inclinazione carico in forma semplice e robusta."""

    if n_verticale_kg <= 0.0:
        raise ValueError("n_verticale_kg deve essere > 0")

    rapporto = clamp_non_negativo(abs(h_orizzontale_kg) / n_verticale_kg)
    if rapporto >= 1.0:
        return 0.0, 0.0, 0.0

    i_q = (1.0 - rapporto) ** 2
    i_c = i_q
    i_gamma = (1.0 - rapporto) ** 3
    return i_c, i_q, i_gamma


def _larghezze_efficaci(
    b_cm: float, l_cm: float, e_b_cm: float, e_l_cm: float
) -> tuple[float, float]:
    b_eff = b_cm - 2.0 * abs(e_b_cm)
    l_eff = l_cm - 2.0 * abs(e_l_cm)
    if b_eff <= 0.0 or l_eff <= 0.0:
        raise ValueError("Eccentricita eccessive: B' e/o L' <= 0")
    return b_eff, l_eff


def _calcola_q_lim_kg_cm2(
    *,
    coesione_kg_cm2: float,
    gamma_kg_m3: float,
    b_eff_cm: float,
    d_f_cm: float,
    n_c: float,
    n_q: float,
    n_gamma: float,
    i_c: float,
    i_q: float,
    i_gamma: float,
    s_c: float,
    s_q: float,
    s_gamma: float,
    d_c: float,
    d_q: float,
    d_gamma: float,
) -> float:
    q_sovraccarico = sovraccarico_geostatico_kg_cm2(gamma_kg_m3, d_f_cm)

    return (
        coesione_kg_cm2 * n_c * i_c * s_c * d_c
        + q_sovraccarico * n_q * i_q * s_q * d_q
        + 0.5 * (gamma_kg_m3 / 1_000_000.0) * b_eff_cm * n_gamma * i_gamma * s_gamma * d_gamma
    )


def verifica_portanza_slu(input_data: InputPortanzaFondazione) -> RisultatoPortanzaFondazione:
    """Esegue verifica SLU portanza su entrambe le combinazioni DA1."""

    norma = crea_norma_geotecnica(input_data.norma)
    terreno = input_data.terreno
    geometria = input_data.geometria

    b_eff_cm, l_eff_cm = _larghezze_efficaci(
        geometria.larghezza_b_cm,
        geometria.lunghezza_l_cm,
        geometria.eccentricita_b_cm,
        geometria.eccentricita_l_cm,
    )

    s_c, s_q, s_gamma = fattori_forma_vesic(b_eff_cm, l_eff_cm)
    d_c, d_q, d_gamma = fattori_profondita_vesic(geometria.profondita_piano_posa_cm, b_eff_cm)
    i_c, i_q, i_gamma = fattori_inclinazione_carico(
        input_data.carico.h_orizzontale_kg,
        input_data.carico.n_verticale_kg,
    )

    risultati: list[RisultatoVerificaSLU] = []
    passaggi_globali = [
        f"B'={b_eff_cm:.3f} cm, L'={l_eff_cm:.3f} cm",
        f"Fattori forma: s_c={s_c:.3f}, s_q={s_q:.3f}, s_gamma={s_gamma:.3f}",
        f"Fattori profondita: d_c={d_c:.3f}, d_q={d_q:.3f}, d_gamma={d_gamma:.3f}",
        f"Fattori inclinazione: i_c={i_c:.3f}, i_q={i_q:.3f}, i_gamma={i_gamma:.3f}",
    ]

    for combinazione in input_data.combinazioni_da1:
        coeff = norma.coefficienti_da1(combinazione)
        phi_ridotto = riduci_tan_phi(terreno.phi_gradi, coeff.gamma_m_phi)
        coesione_ridotta = terreno.coesione_kg_cm2 / coeff.gamma_m_c
        n_c, n_q, n_gamma = fattori_portanza_vesic(phi_ridotto)

        q_lim = _calcola_q_lim_kg_cm2(
            coesione_kg_cm2=coesione_ridotta,
            gamma_kg_m3=terreno.gamma_kg_m3,
            b_eff_cm=b_eff_cm,
            d_f_cm=geometria.profondita_piano_posa_cm,
            n_c=n_c,
            n_q=n_q,
            n_gamma=n_gamma,
            i_c=i_c,
            i_q=i_q,
            i_gamma=i_gamma,
            s_c=s_c,
            s_q=s_q,
            s_gamma=s_gamma,
            d_c=d_c,
            d_q=d_q,
            d_gamma=d_gamma,
        )

        q_rd = q_lim / coeff.gamma_r
        q_ed = input_data.pressione_agente_kg_cm2
        rapporto = q_ed / q_rd if q_rd > 0 else math.inf

        passaggi = [
            f"{combinazione.value}: gamma_m_phi={coeff.gamma_m_phi:.3f}",
            f"{combinazione.value}: gamma_m_c={coeff.gamma_m_c:.3f}",
            f"{combinazione.value}: gamma_r={coeff.gamma_r:.3f}",
            f"{combinazione.value}: phi_ridotto={phi_ridotto:.3f} deg",
            f"{combinazione.value}: c_ridotta={coesione_ridotta:.5f} kg/cm2",
            f"{combinazione.value}: N_c={n_c:.3f}, N_q={n_q:.3f}, N_gamma={n_gamma:.3f}",
            f"{combinazione.value}: q_lim={q_lim:.5f} kg/cm2",
            f"{combinazione.value}: q_rd={q_rd:.5f} kg/cm2",
            f"{combinazione.value}: q_ed={q_ed:.5f} kg/cm2",
        ]

        risultati.append(
            RisultatoVerificaSLU(
                combinazione=combinazione,
                q_ed_kg_cm2=q_ed,
                q_rd_kg_cm2=q_rd,
                rapporto_utilizzo=rapporto,
                verificato=rapporto <= 1.0,
                passaggi_calcolo=passaggi,
            )
        )

    governante = max(risultati, key=lambda item: item.rapporto_utilizzo)
    return RisultatoPortanzaFondazione(
        risultati_slu=risultati,
        combinazione_governante=governante.combinazione,
        verificato_globale=all(r.verificato for r in risultati),
        passaggi_calcolo=passaggi_globali,
    )
