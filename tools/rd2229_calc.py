"""Routines basate sui valori estratti da COPILOT_SEARCH_2229.md (R.D. 2229/1939)
Fornisce funzioni utili per calcoli elementari secondo la norma storica.
Unità: kg/cm2 per tensioni, cm per copriferri.
"""

def sigma_c_amm_from_r28(sigma_r28, mode='compression'):
    """Calcola la tensione ammissibile del calcestruzzo data la resistenza a 28gg (sigma_r28).
    mode: 'compression' o 'flexure'
    Regola: sigma_c_amm = sigma_r28 / 3
    Massimi: compression -> 60 kg/cm2, flexure -> 75 kg/cm2
    """
    if sigma_r28 is None:
        raise ValueError('sigma_r28 required')
    sigma = float(sigma_r28) / 3.0
    if mode == 'compression':
        return min(sigma, 60.0)
    elif mode == 'flexure':
        return min(sigma, 75.0)
    else:
        raise ValueError("mode must be 'compression' or 'flexure'")


def steel_sigma_amm(category='soft'):
    """Restituisce la tensione ammissibile per l'acciaio in kg/cm2.
    category: 'soft' -> 1400, 'hard' -> 2000
    """
    if category == 'soft':
        return 1400.0
    elif category == 'hard':
        return 2000.0
    else:
        raise ValueError("category must be 'soft' or 'hard'")


def n_modulus_ratio(concrete_type='common'):
    """Restituisce il coefficiente n = Es/Ec in funzione del tipo di conglomerato.
    concrete_type: 'common'->10, 'high'->8, 'aluminous'->6
    """
    mapping = {'common':10.0, 'high':8.0, 'aluminous':6.0}
    return mapping.get(concrete_type, 10.0)


def shear_allowable(with_stirrups=False, concrete_type='ordinary'):
    """Ritorna la tensione tangenziale ammissibile del calcestruzzo (kg/cm2).
    without stirrups: tau_c0 = 4 (ordinary) or 6 (high)
    with stirrups: tau_c1 = 14 (ordinary) or 16 (high)
    """
    if with_stirrups:
        return 16.0 if concrete_type == 'high' else 14.0
    else:
        return 6.0 if concrete_type == 'high' else 4.0


def check_cube_requirement(f_cub28, sigma_c_amm):
    """Verifica la prescrizione f_cub28 >= 3 * sigma_c_amm e i minimi assoluti (120/160).
    Restituisce tuple (ok_bool, message)
    """
    if f_cub28 is None or sigma_c_amm is None:
        return (False, 'Inputs required')
    req = 3.0 * float(sigma_c_amm)
    min_abs = 160.0 if float(sigma_c_amm) > 40.0 else 120.0
    if float(f_cub28) >= req and float(f_cub28) >= min_abs:
        return (True, f'f_cub28={f_cub28} OK (>= {req} and >= {min_abs})')
    else:
        return (False, f'f_cub28={f_cub28} NOT OK (required >= {req} and >= {min_abs})')


if __name__ == '__main__':
    # Esempi rapidi
    print('Esempio: sigma_c_amm da sigma_r28=180 (compression):', sigma_c_amm_from_r28(180,'compression'))
    print('Esempio: steel sigma amm (soft):', steel_sigma_amm('soft'))
    print('Esempio: shear without stirrups (ordinary):', shear_allowable(False,'ordinary'))
    print('Check cube 200 vs sigma amm 60:', check_cube_requirement(200,60))
