"""Verifiche EC8 (EN 1998-1) per duttilita e gerarchia delle resistenze."""

from typing import Any


def verifica_duttilita_ec8(
    q: float,
    T_1: float,
    T_C: float,
    mu_phi_richiesto: float,
    classe_duttilita: str = "CD-M",
) -> dict[str, Any]:
    """Verifica domanda di duttilita in curvatura (§5.2.3.4)."""
    if min(q, T_1, T_C, mu_phi_richiesto) <= 0:
        raise ValueError("q, T_1, T_C e mu_phi_richiesto devono essere > 0")

    if T_1 < T_C:
        mu_min = 1.0 + 2.0 * (q - 1.0) * T_C / T_1
    else:
        mu_min = 2.0 * q - 1.0

    if classe_duttilita.upper() == "CD-H":
        mu_min = max(mu_min, 13.0)

    esito = mu_phi_richiesto >= mu_min
    return {
        "esito": esito,
        "mu_phi_richiesto": mu_phi_richiesto,
        "mu_phi_min": mu_min,
        "rateo": mu_min / mu_phi_richiesto,
        "classe_duttilita": classe_duttilita,
        "riferimento_normativo": "EC8 EN1998-1 §5.2.3.4",
    }


def verifica_duttilita_disponibile_ec8(
    eps_cu: float,
    eps_y: float,
    x_su_d: float,
    mu_phi_richiesto: float | None = None,
) -> dict[str, Any]:
    """Verifica duttilita disponibile in curvatura con formula semplificata (§5.2.3.4)."""
    if min(eps_cu, eps_y, x_su_d) <= 0:
        raise ValueError("eps_cu, eps_y e x_su_d devono essere > 0")

    mu_phi_disponibile = (eps_cu / eps_y) / x_su_d
    esito = True if mu_phi_richiesto is None else mu_phi_disponibile >= mu_phi_richiesto
    rateo = 1.0 if mu_phi_richiesto is None else mu_phi_richiesto / mu_phi_disponibile

    return {
        "esito": esito,
        "mu_phi_disponibile": mu_phi_disponibile,
        "mu_phi_richiesto": mu_phi_richiesto,
        "rateo": rateo,
        "riferimento_normativo": "EC8 EN1998-1 §5.2.3.4",
    }


def calcola_armatura_confinamento_ec8(
    A_c_cm2: float,
    A_cc_cm2: float,
    f_cd: float,
    f_yd: float,
    b0_cm: float,
    s_cm: float,
    A_sw_prov_cm2: float | None = None,
) -> dict[str, Any]:
    """Stima minima armatura di confinamento (staffe) per pilastri EC8 §5.4.3.2.2."""
    if min(A_c_cm2, A_cc_cm2, f_cd, f_yd, b0_cm, s_cm) <= 0:
        raise ValueError("Parametri di confinamento devono essere > 0")
    if A_c_cm2 <= A_cc_cm2:
        raise ValueError("A_c_cm2 deve essere maggiore di A_cc_cm2")

    rho_wd_min = 0.08 * ((A_c_cm2 / A_cc_cm2) - 1.0) * (f_cd / f_yd)
    A_sw_req_cm2 = rho_wd_min * b0_cm * s_cm

    esito = True if A_sw_prov_cm2 is None else A_sw_prov_cm2 >= A_sw_req_cm2
    rateo = 1.0 if A_sw_prov_cm2 is None else A_sw_prov_cm2 / A_sw_req_cm2

    return {
        "esito": esito,
        "rho_wd_min": rho_wd_min,
        "A_sw_req_cm2": A_sw_req_cm2,
        "A_sw_prov_cm2": A_sw_prov_cm2,
        "rateo": rateo,
        "riferimento_normativo": "EC8 EN1998-1 §5.4.3.2.2",
    }


def verifica_gerarchia_nodo_ec8(
    somma_MRc: float,
    somma_MRb: float,
    coeff_gerarchia: float = 1.3,
) -> dict[str, Any]:
    """Verifica strong-column weak-beam al nodo (§5.4.2.3)."""
    if min(somma_MRc, somma_MRb, coeff_gerarchia) <= 0:
        raise ValueError("Momenti e coefficiente devono essere > 0")

    limite = coeff_gerarchia * somma_MRb
    esito = somma_MRc >= limite
    return {
        "esito": esito,
        "somma_MRc": somma_MRc,
        "somma_MRb": somma_MRb,
        "limite": limite,
        "rateo": somma_MRc / limite,
        "riferimento_normativo": "EC8 EN1998-1 §5.4.2.3",
    }


def verifica_taglio_trave_gerarchia_ec8(
    M_rb_left: float,
    M_rb_right: float,
    L_cm: float,
    V_g: float,
    V_ed: float,
) -> dict[str, Any]:
    """Taglio di progetto trave da gerarchia (§5.4.3.1.2)."""
    if L_cm <= 0:
        raise ValueError("L_cm deve essere > 0")

    V_cd = (M_rb_left + M_rb_right) / L_cm + V_g
    return {
        "esito": V_ed <= V_cd * 1.001,
        "rateo": V_ed / V_cd if V_cd > 0 else 0.0,
        "V_ed": V_ed,
        "V_cd": V_cd,
        "riferimento_normativo": "EC8 EN1998-1 §5.4.3.1.2",
    }


def verifica_taglio_pilastro_gerarchia_ec8(
    M_rc_top: float,
    M_rc_bot: float,
    H_cl_cm: float,
    V_ed: float,
) -> dict[str, Any]:
    """Taglio di progetto pilastro da gerarchia (§5.4.3.2.1)."""
    if H_cl_cm <= 0:
        raise ValueError("H_cl_cm deve essere > 0")

    V_cd = (M_rc_top + M_rc_bot) / H_cl_cm
    return {
        "esito": V_ed <= V_cd * 1.001,
        "rateo": V_ed / V_cd if V_cd > 0 else 0.0,
        "V_ed": V_ed,
        "V_cd": V_cd,
        "riferimento_normativo": "EC8 EN1998-1 §5.4.3.2.1",
    }


def verifica_nodo_compressione_diagonale_ec8(
    V_jhd: float,
    eta: float,
    f_cd: float,
    b_j: float,
    h_jc: float,
) -> dict[str, Any]:
    """Check compressione diagonale nodo (§5.5.3.3)."""
    if min(eta, f_cd, b_j, h_jc) <= 0:
        raise ValueError("eta, f_cd, b_j, h_jc devono essere > 0")

    V_lim = eta * f_cd * b_j * h_jc
    return {
        "esito": V_jhd <= V_lim * 1.001,
        "rateo": V_jhd / V_lim if V_lim > 0 else 0.0,
        "V_jhd": V_jhd,
        "V_lim": V_lim,
        "riferimento_normativo": "EC8 EN1998-1 §5.5.3.3",
    }
