"""Costanti e configurazioni condivise per le sezioni."""

# Intestazioni CSV per esportazione/importazione sezioni
CSV_HEADERS = [
    "id",
    "name",
    "section_type",
    "width",
    "height",
    "diameter",
    "flange_width",
    "flange_thickness",
    "web_thickness",
    "web_height",
    "t_horizontal",
    "t_vertical",
    "outer_diameter",
    "thickness",
    "rotation_angle_deg",
    "area",
    "A_y",
    "A_z",
    "kappa_y",
    "kappa_z",
    "x_G",
    "y_G",
    "Ix",
    "Iy",
    "Ixy",
    "I1",
    "I2",
    "principal_angle_deg",
    "principal_rx",
    "principal_ry",
    "Qx",
    "Qy",
    "rx",
    "ry",
    "core_x",
    "core_y",
    "ellipse_a",
    "ellipse_b",
    "note",
]

# Default shear correction factors (kappa) for common section types
# Centralized values (literature-based / engineering practice approximations):
# - RECTANGULAR: 5/6
# - CIRCULAR (solid): 10/9
# - HOLLOW circular/rectangular: 1.0 (approx)
# - T/I: web-dominated shear -> kappa_y ~ 1.0 on web direction
DEFAULT_SHEAR_KAPPAS = {
    "RECTANGULAR": (5.0 / 6.0, 5.0 / 6.0),
    "CIRCULAR": (10.0 / 9.0, 10.0 / 9.0),
    "CIRCULAR_HOLLOW": (1.0, 1.0),
    "RECTANGULAR_HOLLOW": (5.0 / 6.0, 5.0 / 6.0),
    "T_SECTION": (1.0, 0.9),
    "I_SECTION": (1.0, 0.9),
    "INVERTED_T_SECTION": (1.0, 0.9),
    "C_SECTION": (1.0, 0.9),
}

# Tutte le possibili chiavi dimensionali supportate (garantire presenza nella dict dimensions)
DIMENSION_KEYS = [
    "width",
    "height",
    "diameter",
    "flange_width",
    "flange_thickness",
    "web_thickness",
    "web_height",
    "t_horizontal",
    "t_vertical",
    "outer_diameter",
    "thickness",
]

# Mapping tipo sezione -> classe per factory
SECTION_CLASS_MAP = {
    "RECTANGULAR": "RectangularSection",
    "CIRCULAR": "CircularSection",
    "CIRCULAR_HOLLOW": "CircularHollowSection",
    "RECTANGULAR_HOLLOW": "RectangularHollowSection",
    "T_SECTION": "TSection",
    "I_SECTION": "ISection",
    "L_SECTION": "LSection",
    "PI_SECTION": "PiSection",
    "INVERTED_T_SECTION": "InvertedTSection",
    "C_SECTION": "CSection",
    "V_SECTION": "VSection",
    "INVERTED_V_SECTION": "InvertedVSection",
}
