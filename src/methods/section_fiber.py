"""Motore geometrico a fibre per sezioni in c.a.

Fornisce funzioni per calcolare la larghezza della sezione a qualsiasi
profondità e integrare la risultante del calcestruzzo compresso.

Funziona con TUTTI i 12 tipi di sezione gestiti dal software, usando
duck typing su section.section_type e attributi geometrici.

Unità: mm (geometria), MPa (tensioni), N e N·mm (forze e momenti).
"""

from __future__ import annotations

import math
from typing import Any


# ---------------------------------------------------------------------------
# Altezza e larghezza totale della sezione
# ---------------------------------------------------------------------------

def get_section_height(section: Any) -> float:
    """Altezza totale della sezione [mm]."""
    st = getattr(section, "section_type", "")

    if st in ("RECTANGULAR", "RECTANGULAR_HOLLOW", "C_SECTION", "L_SECTION",
              "V_SECTION", "INVERTED_V_SECTION"):
        return float(section.height)

    if st == "CIRCULAR":
        return float(section.diameter)

    if st == "CIRCULAR_HOLLOW":
        return float(section.outer_diameter)

    if st in ("T_SECTION", "INVERTED_T_SECTION"):
        return float(section.flange_thickness + section.web_height)

    if st == "I_SECTION":
        return float(2 * section.flange_thickness + section.web_height)

    if st == "PI_SECTION":
        return float(section.flange_thickness + section.web_height)

    # Fallback: prova attributi comuni
    if hasattr(section, "height"):
        return float(section.height)
    if hasattr(section, "diameter"):
        return float(section.diameter)
    if hasattr(section, "outer_diameter"):
        return float(section.outer_diameter)

    raise ValueError(f"Impossibile determinare altezza per sezione tipo '{st}'")


def get_section_width(section: Any) -> float:
    """Larghezza totale (massima) della sezione [mm]."""
    st = getattr(section, "section_type", "")

    if st in ("RECTANGULAR", "RECTANGULAR_HOLLOW", "C_SECTION",
              "V_SECTION", "INVERTED_V_SECTION"):
        return float(section.width)

    if st == "CIRCULAR":
        return float(section.diameter)

    if st == "CIRCULAR_HOLLOW":
        return float(section.outer_diameter)

    if st in ("T_SECTION", "INVERTED_T_SECTION", "I_SECTION", "PI_SECTION"):
        return float(section.flange_width)

    if st == "L_SECTION":
        return float(section.width)

    if hasattr(section, "width"):
        return float(section.width)
    if hasattr(section, "flange_width"):
        return float(section.flange_width)
    if hasattr(section, "diameter"):
        return float(section.diameter)
    if hasattr(section, "outer_diameter"):
        return float(section.outer_diameter)

    raise ValueError(f"Impossibile determinare larghezza per sezione tipo '{st}'")


# ---------------------------------------------------------------------------
# Larghezza a profondità y (asse neutro orizzontale → flessione Mx)
# ---------------------------------------------------------------------------

def width_at_depth(section: Any, y: float) -> float:
    """Larghezza della sezione alla profondità *y* dal lembo superiore [mm].

    y = 0 è il lembo compresso superiore, y = h il lembo inferiore.
    Restituisce 0.0 se y è fuori dalla sezione.
    """
    st = getattr(section, "section_type", "")

    # --- Sezioni semplici ---
    if st == "RECTANGULAR":
        h = section.height
        return float(section.width) if 0.0 <= y <= h else 0.0

    if st == "CIRCULAR":
        R = section.diameter / 2.0
        if y < 0.0 or y > 2.0 * R:
            return 0.0
        val = R * R - (y - R) * (y - R)
        return 2.0 * math.sqrt(max(0.0, val))

    if st == "CIRCULAR_HOLLOW":
        R_out = section.outer_diameter / 2.0
        R_in = R_out - section.thickness
        if y < 0.0 or y > 2.0 * R_out:
            return 0.0
        w_out = 2.0 * math.sqrt(max(0.0, R_out ** 2 - (y - R_out) ** 2))
        dy_in = y - R_out
        if abs(dy_in) <= R_in and R_in > 0:
            w_in = 2.0 * math.sqrt(max(0.0, R_in ** 2 - dy_in ** 2))
        else:
            w_in = 0.0
        return max(0.0, w_out - w_in)

    # --- Sezioni cave rettangolari ---
    if st == "RECTANGULAR_HOLLOW":
        h = section.height
        t = section.thickness
        w = section.width
        if y < 0.0 or y > h:
            return 0.0
        if y <= t or y >= h - t:
            return float(w)
        return 2.0 * t

    # --- Sezioni a T ---
    if st == "T_SECTION":
        tf = section.flange_thickness
        hw = section.web_height
        h_tot = tf + hw
        if y < 0.0 or y > h_tot:
            return 0.0
        if y <= tf:
            return float(section.flange_width)
        return float(section.web_thickness)

    if st == "INVERTED_T_SECTION":
        hw = section.web_height
        tf = section.flange_thickness
        h_tot = hw + tf
        if y < 0.0 or y > h_tot:
            return 0.0
        if y <= hw:
            return float(section.web_thickness)
        return float(section.flange_width)

    # --- Sezione a I (doppia T) ---
    if st == "I_SECTION":
        tf = section.flange_thickness
        hw = section.web_height
        h_tot = 2.0 * tf + hw
        if y < 0.0 or y > h_tot:
            return 0.0
        if y <= tf or y >= h_tot - tf:
            return float(section.flange_width)
        return float(section.web_thickness)

    # --- Pi-greco (soletta + 2 anime) ---
    if st == "PI_SECTION":
        tf = section.flange_thickness
        hw = section.web_height
        h_tot = tf + hw
        if y < 0.0 or y > h_tot:
            return 0.0
        if y <= tf:
            return float(section.flange_width)
        return 2.0 * section.web_thickness

    # --- C (UPN) ---
    if st == "C_SECTION":
        tf = section.flange_thickness
        h = section.height
        if y < 0.0 or y > h:
            return 0.0
        if y <= tf or y >= h - tf:
            return float(section.width)
        return float(section.web_thickness)

    # --- L (angolare) ---
    if st == "L_SECTION":
        th = section.t_horizontal
        h = section.height
        if y < 0.0 or y > h:
            return 0.0
        if y <= th:
            return float(section.width)
        return float(section.t_vertical)

    # --- V e V rovescia (thin-walled) ---
    if st == "V_SECTION":
        h = section.height
        w = section.width
        if y < 0.0 or y > h:
            return 0.0
        # Sezione a V: larga in alto, stretta in basso
        # Larghezza esterna varia linearmente
        w_ext = w * (1.0 - y / h) if h > 0 else 0.0
        t = section.thickness
        # Thin-walled: larghezza interna parallela
        w_int = max(0.0, (w - 2.0 * t) * (1.0 - y / h)) if h > 0 else 0.0
        return max(0.0, w_ext - w_int) if w_ext > 0 else 0.0

    if st == "INVERTED_V_SECTION":
        h = section.height
        w = section.width
        if y < 0.0 or y > h:
            return 0.0
        w_ext = w * (y / h) if h > 0 else 0.0
        t = section.thickness
        w_int = max(0.0, (w - 2.0 * t) * (y / h)) if h > 0 else 0.0
        return max(0.0, w_ext - w_int) if w_ext > 0 else 0.0

    # --- Fallback per sezioni con width/height ---
    if hasattr(section, "width") and hasattr(section, "height"):
        h = section.height
        return float(section.width) if 0.0 <= y <= h else 0.0

    return 0.0


# ---------------------------------------------------------------------------
# Larghezza a coordinata orizzontale x (asse neutro verticale → flessione My)
# ---------------------------------------------------------------------------

def height_at_horizontal(section: Any, x: float) -> float:
    """Altezza della sezione alla coordinata orizzontale *x* dal lembo sinistro [mm].

    x = 0 è il lembo sinistro, x = W il lembo destro.
    Per flessione attorno a y (My), la compressione agisce lateralmente.
    Restituisce 0.0 se x è fuori dalla sezione.
    """
    st = getattr(section, "section_type", "")

    if st == "RECTANGULAR":
        w = section.width
        return float(section.height) if 0.0 <= x <= w else 0.0

    if st == "CIRCULAR":
        R = section.diameter / 2.0
        if x < 0.0 or x > 2.0 * R:
            return 0.0
        val = R * R - (x - R) * (x - R)
        return 2.0 * math.sqrt(max(0.0, val))

    if st == "CIRCULAR_HOLLOW":
        R_out = section.outer_diameter / 2.0
        R_in = R_out - section.thickness
        if x < 0.0 or x > 2.0 * R_out:
            return 0.0
        h_out = 2.0 * math.sqrt(max(0.0, R_out ** 2 - (x - R_out) ** 2))
        dx_in = x - R_out
        if abs(dx_in) <= R_in and R_in > 0:
            h_in = 2.0 * math.sqrt(max(0.0, R_in ** 2 - dx_in ** 2))
        else:
            h_in = 0.0
        return max(0.0, h_out - h_in)

    if st == "RECTANGULAR_HOLLOW":
        w = section.width
        h = section.height
        t = section.thickness
        if x < 0.0 or x > w:
            return 0.0
        if x <= t or x >= w - t:
            return float(h)
        return 2.0 * t

    if st in ("T_SECTION", "I_SECTION", "PI_SECTION", "INVERTED_T_SECTION"):
        bf = section.flange_width
        tw = section.web_thickness
        h_tot = get_section_height(section)
        tf = section.flange_thickness
        # Centro dell'anima rispetto alla flangia (flangia centrata)
        web_left = (bf - tw) / 2.0
        web_right = web_left + tw
        if x < 0.0 or x > bf:
            return 0.0
        if web_left <= x <= web_right:
            return float(h_tot)
        # Solo flangia
        if st == "T_SECTION":
            return float(tf) if 0.0 <= x <= bf else 0.0
        if st == "INVERTED_T_SECTION":
            return float(tf) if 0.0 <= x <= bf else 0.0
        if st == "I_SECTION":
            return 2.0 * tf if 0.0 <= x <= bf else 0.0
        if st == "PI_SECTION":
            return float(tf) if 0.0 <= x <= bf else 0.0

    if st == "C_SECTION":
        w = section.width
        h = section.height
        tf = section.flange_thickness
        tw = section.web_thickness
        if x < 0.0 or x > w:
            return 0.0
        if x <= tw:
            return float(h)  # anima
        return 2.0 * tf  # solo flangie

    if st == "L_SECTION":
        w = section.width
        h = section.height
        th = section.t_horizontal
        tv = section.t_vertical
        if x < 0.0 or x > w:
            return 0.0
        if x <= tv:
            return float(h)  # braccio verticale
        return float(th)  # solo braccio orizzontale

    # Fallback
    if hasattr(section, "width") and hasattr(section, "height"):
        w = section.width
        return float(section.height) if 0.0 <= x <= w else 0.0

    return 0.0


# ---------------------------------------------------------------------------
# Risultante calcestruzzo compresso
# ---------------------------------------------------------------------------

def compute_concrete_resultant(
    section: Any,
    x_na: float,
    f_cd: float,
    axis: str = "x",
    lambda_f: float = 0.8,
    n_strips: int = 100,
) -> tuple[float, float]:
    """Risultante e momento del calcestruzzo compresso per stress block rettangolare.

    Args:
        section: oggetto sezione (qualsiasi tipo)
        x_na: profondità asse neutro dal lembo compresso [mm]
        f_cd: resistenza di calcolo a compressione cls [MPa]
        axis: "x" per flessione attorno a x (asse neutro orizzontale),
              "y" per flessione attorno a y (asse neutro verticale)
        lambda_f: fattore profondità stress block (NTC2018: 0.8)
        n_strips: numero di strisce per integrazione numerica

    Returns:
        (R_c [N], M_c [N·mm]):
            R_c = risultante compressione cls (positiva)
            M_c = momento di R_c rispetto al baricentro geometrico (positivo
                  se la compressione è sopra/a sinistra del baricentro)
    """
    if axis == "x":
        h = get_section_height(section)
        width_func = lambda pos: width_at_depth(section, pos)
    else:
        h = get_section_width(section)
        width_func = lambda pos: height_at_horizontal(section, pos)

    h_2 = h / 2.0

    # Profondità effettiva dello stress block
    x_block = min(lambda_f * max(x_na, 0.0), h)
    if x_block <= 0.0:
        return (0.0, 0.0)

    dy = x_block / n_strips
    R_c = 0.0
    M_c = 0.0

    for i in range(n_strips):
        y_mid = (i + 0.5) * dy
        b_y = width_func(y_mid)
        dF = b_y * dy * f_cd  # N
        R_c += dF
        M_c += dF * (h_2 - y_mid)  # positivo se sopra/sinistra baricentro

    return (R_c, M_c)


# ---------------------------------------------------------------------------
# Area totale della sezione (per integrazione di verifica)
# ---------------------------------------------------------------------------

def compute_section_area(section: Any, n_strips: int = 200) -> float:
    """Area della sezione per integrazione numerica [mm²].

    Utile per verificare la correttezza di width_at_depth.
    """
    h = get_section_height(section)
    dy = h / n_strips
    area = 0.0
    for i in range(n_strips):
        y_mid = (i + 0.5) * dy
        area += width_at_depth(section, y_mid) * dy
    return area
