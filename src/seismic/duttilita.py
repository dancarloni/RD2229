"""Fase U.2 - Verifiche di duttilita in curvatura e rotazione plastica.

Formula principali implementate:
- mu_phi_req: domanda di duttilita (EC8)
- mu_phi_avail: capacita di duttilita in curvatura
- epsilon_cu,c: deformazione ultima confinata
- rho_sx,min: armatura trasversale minima
- theta_u: rotazione plastica ultima (Circ. 7/2019, semplificata)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RisultatoDuttilita:
    """Risultato sintetico verifica duttilita."""

    mu_phi_richiesta: float
    mu_phi_disponibile: float
    verifica_ok: bool
    rho_sx_minimo: float
    epsilon_cu_confinata: float
    warning_zona_tc: bool
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, float | bool | list[str]]:
        return {
            "mu_phi_richiesta": round(self.mu_phi_richiesta, 3),
            "mu_phi_disponibile": round(self.mu_phi_disponibile, 3),
            "verifica_ok": self.verifica_ok,
            "rho_sx_minimo": round(self.rho_sx_minimo, 5),
            "epsilon_cu_confinata": round(self.epsilon_cu_confinata, 6),
            "warning_zona_tc": self.warning_zona_tc,
            "passaggi": self.passaggi,
        }


def calcola_mu_phi_richiesta(q: float, t_1: float, t_c: float) -> tuple[float, bool]:
    """Calcola mu_phi richiesta secondo EC8.

    Returns:
        tuple(mu_phi, warning_zona_tc)
    """

    if q <= 0.0:
        raise ValueError("q deve essere > 0")
    if t_1 <= 0.0 or t_c <= 0.0:
        raise ValueError("t_1 e t_c devono essere > 0")

    warning_zona_tc = 0.9 * t_c <= t_1 <= 1.1 * t_c

    if t_1 < t_c:
        mu_phi = 1.0 + 2.0 * (q - 1.0) * (t_c / t_1)
    else:
        mu_phi = 2.0 * q - 1.0

    return mu_phi, warning_zona_tc


def calcola_epsilon_cu_confinata(
    alpha_confinamento: float, rho_sx: float, f_yw: float, f_c: float
) -> float:
    """Calcola epsilon_cu confinata.

    epsilon_cu,c = 0.0035 + 0.1 * alpha * rho_sx * f_yw / f_c
    """

    if alpha_confinamento < 0.0:
        raise ValueError("alpha_confinamento deve essere >= 0")
    if rho_sx < 0.0:
        raise ValueError("rho_sx deve essere >= 0")
    if f_yw <= 0.0 or f_c <= 0.0:
        raise ValueError("f_yw e f_c devono essere > 0")

    return 0.0035 + 0.1 * alpha_confinamento * rho_sx * f_yw / f_c


def calcola_mu_phi_disponibile(epsilon_cu: float, epsilon_y: float, x_su_d: float) -> float:
    """Calcola mu_phi disponibile.

    mu_phi,avail = epsilon_cu / (epsilon_y * x/d)
    """

    if epsilon_cu <= 0.0 or epsilon_y <= 0.0:
        raise ValueError("epsilon_cu e epsilon_y devono essere > 0")
    if x_su_d <= 0.0:
        raise ValueError("x_su_d deve essere > 0")

    return epsilon_cu / (epsilon_y * x_su_d)


def calcola_rho_sx_minimo(
    f_cd: float,
    f_yd: float,
    nu_d: float,
    mu_phi_richiesta: float,
    epsilon_sy_d: float,
    d_s: float,
    b_0: float,
) -> float:
    """Calcola rho_sx minimo con limite inferiore 0.01."""

    if f_cd <= 0.0 or f_yd <= 0.0:
        raise ValueError("f_cd e f_yd devono essere > 0")
    if nu_d < 0.0:
        raise ValueError("nu_d deve essere >= 0")
    if mu_phi_richiesta <= 0.0 or epsilon_sy_d <= 0.0:
        raise ValueError("mu_phi_richiesta e epsilon_sy_d devono essere > 0")
    if d_s <= 0.0 or b_0 <= 0.0:
        raise ValueError("d_s e b_0 devono essere > 0")

    valore = 0.08 * (f_cd / f_yd) * nu_d * (mu_phi_richiesta * epsilon_sy_d * (d_s / b_0) - 0.035)
    return max(valore, 0.01)


def calcola_theta_u_circolare(
    f_c: float,
    nu_d: float,
    rho_tot: float,
    rho_b: float,
    d_l: float,
    l_p: float,
) -> float:
    """Calcola theta_u (forma semplificata da Circ. 7/2019)."""

    if f_c <= 0.0:
        raise ValueError("f_c deve essere > 0")
    if nu_d <= 0.0:
        raise ValueError("nu_d deve essere > 0")
    if rho_b <= 0.0:
        raise ValueError("rho_b deve essere > 0")
    if d_l <= 0.0 or l_p <= 0.0:
        raise ValueError("d_l e l_p devono essere > 0")

    fattore_diametro = min(1.0, (d_l / l_p) ** 0.5)
    return (f_c / (165.0 * nu_d) - 0.002) * (1.0 + rho_tot / rho_b) * fattore_diametro


def verifica_duttilita(
    *,
    q: float,
    t_1: float,
    t_c: float,
    alpha_confinamento: float,
    rho_sx: float,
    f_yw: float,
    f_c: float,
    epsilon_y: float,
    x_su_d: float,
    f_cd: float,
    f_yd: float,
    nu_d: float,
    epsilon_sy_d: float,
    d_s: float,
    b_0: float,
) -> RisultatoDuttilita:
    """Esegue una verifica completa richiesta/disponibile di duttilita."""

    passaggi: list[str] = []

    mu_req, warning_zona_tc = calcola_mu_phi_richiesta(q=q, t_1=t_1, t_c=t_c)
    passaggi.append(f"mu_phi_richiesta = {mu_req:.3f}")

    epsilon_cu_conf = calcola_epsilon_cu_confinata(
        alpha_confinamento=alpha_confinamento,
        rho_sx=rho_sx,
        f_yw=f_yw,
        f_c=f_c,
    )
    passaggi.append(f"epsilon_cu_confinata = {epsilon_cu_conf:.6f}")

    mu_avail = calcola_mu_phi_disponibile(
        epsilon_cu=epsilon_cu_conf,
        epsilon_y=epsilon_y,
        x_su_d=x_su_d,
    )
    passaggi.append(f"mu_phi_disponibile = {mu_avail:.3f}")

    rho_sx_min = calcola_rho_sx_minimo(
        f_cd=f_cd,
        f_yd=f_yd,
        nu_d=nu_d,
        mu_phi_richiesta=mu_req,
        epsilon_sy_d=epsilon_sy_d,
        d_s=d_s,
        b_0=b_0,
    )
    passaggi.append(f"rho_sx_minimo = {rho_sx_min:.5f}")

    verifica_ok = mu_avail >= mu_req
    passaggi.append("Verifica duttilita: OK" if verifica_ok else "Verifica duttilita: NON OK")

    return RisultatoDuttilita(
        mu_phi_richiesta=mu_req,
        mu_phi_disponibile=mu_avail,
        verifica_ok=verifica_ok,
        rho_sx_minimo=rho_sx_min,
        epsilon_cu_confinata=epsilon_cu_conf,
        warning_zona_tc=warning_zona_tc,
        passaggi=passaggi,
    )
