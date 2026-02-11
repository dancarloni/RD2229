DEFAULT_SHEAR_FACTORS = {
    "RECTANGULAR": 5.0 / 6.0,
    "CIRCULAR": 10.0 / 9.0,
    "CIRCULAR_HOLLOW": 1.0,
    "RECTANGULAR_HOLLOW": 5.0 / 6.0,
    "T_SECTION": 1.0,
    "I_SECTION": 1.0,
    "C_SECTION": 1.0,
    "L_SECTION": 5.0 / 6.0,
    "INVERTED_T_SECTION": 1.0,
    "PI_SECTION": 1.0,
    "V_SECTION": 5.0 / 6.0,
    "INVERTED_V_SECTION": 5.0 / 6.0,
}


def get_default_shear_factor(section_type: str) -> float:
    return DEFAULT_SHEAR_FACTORS.get(section_type.upper(), 1.0)
