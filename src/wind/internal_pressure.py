"""Internal pressure – calcolo della pressione interna cp_i.

Supporta due metodi:
- Semplificato: cp_i = ±0.2 (NTC2018 / EC1 §7.2.9(6) Note 2)
- Dettagliato: cp_i = f(μ) (EC1 Fig. 7.13)

dove μ = rapporto area aperture sopravento / area totale aperture.
"""

from __future__ import annotations

import logging

from src.wind.models import InternalPressureConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tabella interpolazione cp_i = f(μ) — EC1 Fig. 7.13
# μ: rapporto area aperture sopravento / area totale aperture
# ---------------------------------------------------------------------------
_MU_TABLE = [0.0, 0.10, 0.25, 0.33, 0.50, 0.67, 0.75, 0.90, 1.0]
_CPI_TABLE = [-0.50, -0.40, -0.30, -0.18, 0.00, 0.18, 0.30, 0.48, 0.55]


def _interpolate(x: float, xs: list[float], ys: list[float]) -> float:
    """Interpolazione lineare con clamp."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def compute_cpi_simplified() -> tuple[float, float]:
    """Pressione interna semplificata (±0.2).

    Valida per edifici senza apertura dominante (EC1 §7.2.9(6) Note 2).

    Returns:
        Tupla (cp_i_pos, cp_i_neg) = (+0.2, -0.2).
    """
    return (0.2, -0.2)


def compute_cpi_detailed(mu: float) -> float:
    """Pressione interna dettagliata in funzione di μ (EC1 Fig. 7.13).

    Args:
        mu: Rapporto area aperture sopravento / area totale aperture.
            μ = 0: tutte le aperture sottovento/laterali → cp_i ≈ -0.5
            μ = 0.5: aperture bilanciate → cp_i ≈ 0
            μ = 1: tutte le aperture sopravento → cp_i ≈ +0.55

    Returns:
        Valore cp_i interpolato.
    """
    mu_clamped = max(0.0, min(1.0, mu))
    return round(_interpolate(mu_clamped, _MU_TABLE, _CPI_TABLE), 3)


def compute_cpi_dominant_opening(cpe_dominant: float) -> float:
    """Pressione interna per apertura dominante (EC1 §7.2.9(3-5)).

    Se un'apertura nella faccia sopravento è dominante (area > 2× area
    delle altre aperture), cp_i dipende direttamente da cp_e della faccia.

    cp_i = 0.75 · cp_e (se area dominante / area altre ≥ 3)
    cp_i = 0.90 · cp_e · √(area_dom / area_altre) (caso intermedio)

    Semplificato: cp_i = 0.75 · cp_e della faccia dominante.

    Args:
        cpe_dominant: cp_e della faccia con apertura dominante.

    Returns:
        cp_i.
    """
    return round(0.75 * cpe_dominant, 3)


def get_cpi_values(
    config: InternalPressureConfig | None = None,
    *,
    cpe_dominant: float | None = None,
) -> tuple[float, float]:
    """Calcola cp_i secondo la configurazione specificata.

    Args:
        config: Configurazione pressione interna. Se None, usa semplificato.
        cpe_dominant: cp_e della faccia con apertura dominante (se applicabile).

    Returns:
        Tupla (cp_i_caso_1, cp_i_caso_2). Per metodo semplificato: (+0.2, -0.2).
        Per metodo dettagliato: (cp_i(μ), cp_i(μ)) — singolo valore replicato.
    """
    if config is None:
        return compute_cpi_simplified()

    method = config.method.lower().strip()

    if method == "simplified":
        return compute_cpi_simplified()

    if method == "detailed":
        if config.dominant_opening and cpe_dominant is not None:
            cpi = compute_cpi_dominant_opening(cpe_dominant)
            return (cpi, cpi)

        if config.mu is not None:
            cpi = compute_cpi_detailed(config.mu)
            return (cpi, cpi)

        logger.warning(
            "Metodo 'detailed' richiede mu o dominant_opening; uso semplificato."
        )
        return compute_cpi_simplified()

    logger.warning("Metodo pressione interna '%s' non riconosciuto; uso semplificato.", method)
    return compute_cpi_simplified()
