"""Topography – fattore topografico ct per il calcolo del vento.

Implementa il calcolo del fattore di orografia ct secondo:
- NTC2018 §3.3.3
- EN 1991-1-4 §4.3.3 / Annex A.3
- CNR-DT 207 R1/2018

Tipologie topografiche supportate:
- flat: terreno piano (ct = 1.0)
- hill: collina isolata
- ridge: cresta allungata
- escarpment: scarpata/falesia
- valley: valle (speed-up per effetto imbuto)
"""

from __future__ import annotations

import math
import logging

from src.wind.models import TopographyParams

logger = logging.getLogger(__name__)


def compute_topography_factor(
    z_m: float,
    topo: TopographyParams | None = None,
) -> float:
    """Calcola il fattore topografico ct a quota z.

    ct amplifica la velocità media del vento per effetto di orografia
    (colline, creste, scarpate). Per terreno piano ct = 1.0.

    Formula generale (EC1 Annex A.3):
        ct(z) = 1 + s(z)  dove s è il fattore orografico di speed-up.

    Args:
        z_m: Quota dal suolo [m].
        topo: Parametri topografici. Se None, terreno piano.

    Returns:
        Fattore topografico ct ≥ 1.0.
    """
    if topo is None:
        return 1.0

    topo_type = topo.topo_type.lower().strip()

    if topo_type == "flat":
        return 1.0

    if topo_type in ("hill", "ridge"):
        return _ct_hill_ridge(z_m, topo)

    if topo_type == "escarpment":
        return _ct_escarpment(z_m, topo)

    if topo_type == "valley":
        return _ct_valley(z_m, topo)

    logger.warning(
        "Tipo topografico '%s' non riconosciuto; uso ct=1.0.", topo_type
    )
    return 1.0


def _ct_hill_ridge(z_m: float, topo: TopographyParams) -> float:
    """Fattore ct per colline e creste (EC1 Annex A.3, Fig. A.2/A.3).

    Il fattore di speed-up s dipende dalla posizione rispetto alla sommità
    e decade con la quota z e la distanza orizzontale x dalla cresta.

    Modello semplificato:
        s(z) = s_max · ψ_s(x) · ψ_z(z)

    dove:
        s_max = fattore di speed-up massimo alla sommità (dipende da pendenza)
        ψ_s(x) = decay orizzontale (funzione della distanza dalla sommità)
        ψ_z(z) = decay verticale (funzione della quota)
    """
    H = topo.crest_height_m
    if H <= 0:
        return 1.0

    # Lunghezze caratteristiche
    Lu = topo.lu_m if topo.lu_m > 0 else max(H / math.tan(math.radians(max(topo.slope_upwind_deg, 1.0))), 1.0)
    Le = min(Lu, H)  # Lunghezza effettiva

    # Pendenza φ = H / Lu
    phi = H / Lu if Lu > 0 else 0.0

    # EC1 Annex A.3: s_max per colline/creste
    # Per pendenze moderate (0.05 ≤ φ ≤ 0.3): s_max ≈ 2 · φ (hill), ≈ 1.2 · φ (ridge)
    # Per pendenze > 0.3: s_max converge
    if phi < 0.05:
        return 1.0  # Effetto trascurabile

    if topo.topo_type.lower() == "hill":
        s_max = min(2.0 * phi, 0.6)
    else:  # ridge
        s_max = min(1.2 * phi, 0.36)

    # Decay orizzontale ψ_s(x)
    x = topo.x_from_crest_m
    if x >= 0:
        # Sottovento
        Ld = topo.ld_m if topo.ld_m > 0 else 2.0 * Le
        psi_s = max(0.0, 1.0 - abs(x) / Ld) if Ld > 0 else 0.0
    else:
        # Sopravento
        psi_s = max(0.0, 1.0 - abs(x) / (1.5 * Lu)) if Lu > 0 else 0.0

    # Decay verticale ψ_z(z)
    # ψ_z = 1.0 per z ≤ 0.6·Le, poi decadimento esponenziale
    z_eff = max(z_m, 0.1)
    if Le > 0:
        psi_z = math.exp(-1.5 * max(0, z_eff - 0.6 * Le) / Le) if z_eff > 0.6 * Le else 1.0
    else:
        psi_z = 1.0

    s = s_max * psi_s * psi_z
    ct = 1.0 + s
    return max(ct, 1.0)


def _ct_escarpment(z_m: float, topo: TopographyParams) -> float:
    """Fattore ct per scarpate (EC1 Annex A.3, Fig. A.4).

    Modello analogo a hill/ridge ma con speed-up asimmetrico:
    - sopravento: speed-up crescente verso la cresta
    - sottovento: plateau, lento decadimento
    """
    H = topo.crest_height_m
    if H <= 0:
        return 1.0

    Lu = topo.lu_m if topo.lu_m > 0 else max(H / math.tan(math.radians(max(topo.slope_upwind_deg, 1.0))), 1.0)
    Le = min(Lu, H)

    phi = H / Lu if Lu > 0 else 0.0
    if phi < 0.05:
        return 1.0

    # Speed-up massimo per scarpate: circa 1.3·φ (inferiore a colline)
    s_max = min(1.3 * phi, 0.4)

    x = topo.x_from_crest_m
    if x >= 0:
        # Sottovento: decadimento più lento
        Ld = topo.ld_m if topo.ld_m > 0 else 3.0 * Le
        psi_s = max(0.0, 1.0 - abs(x) / Ld) if Ld > 0 else 0.0
    else:
        # Sopravento: crescita verso la cresta
        psi_s = max(0.0, 1.0 - abs(x) / (2.0 * Lu)) if Lu > 0 else 0.0

    z_eff = max(z_m, 0.1)
    if Le > 0:
        psi_z = math.exp(-1.5 * max(0, z_eff - 0.6 * Le) / Le) if z_eff > 0.6 * Le else 1.0
    else:
        psi_z = 1.0

    s = s_max * psi_s * psi_z
    return max(1.0 + s, 1.0)


def _ct_valley(z_m: float, topo: TopographyParams) -> float:
    """Fattore ct per valli (effetto imbuto / speed-up laterale).

    Le valli possono causare accelerazione del vento per effetto
    Venturi se strette e orientate con la direzione del vento.

    Modello semplificato:
        ct = 1 + s_valley
        s_valley dipende dal rapporto H_valley/W_valley
    """
    H = topo.crest_height_m  # profondità della valle
    if H <= 0:
        return 1.0

    # Larghezza caratteristica della valle
    W = topo.lu_m if topo.lu_m > 0 else 4.0 * H

    # Rapporto di restringimento
    ratio = H / W if W > 0 else 0.0

    if ratio < 0.05:
        return 1.0

    # Speed-up per effetto imbuto (massimo ~20% per valli strette)
    s_valley = min(0.8 * ratio, 0.20)

    # Decadimento con l'altezza
    z_eff = max(z_m, 0.1)
    decay = math.exp(-z_eff / (2.0 * H)) if H > 0 else 1.0

    return max(1.0 + s_valley * decay, 1.0)
