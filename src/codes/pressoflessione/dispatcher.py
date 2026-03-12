"""Dispatcher multinorma pressoflessione deviata (FASE J).

Entry-point unico: calcola_pressoflessione_deviata(spec).
Routing su spec.norma: TA per RD2229/DM92/DM96, SLU per NTC2018/NTC2008/EC2.
"""

from __future__ import annotations

from .base import PressoflessResult, PressoflessSpec
from .instabilita_biassiale import amplifica_momenti_biassiale
from .slu import verifica_pressofless_slu
from .ta_cls import verifica_pressofless_ta_cls

NORME_TA = frozenset({"RD2229", "DM92", "DM96"})
NORME_SLU = frozenset({"NTC2008", "NTC2018", "EC2"})
NORME = NORME_TA | NORME_SLU


def calcola_pressoflessione_deviata(spec: PressoflessSpec) -> PressoflessResult:
    """Entry-point multinorma per pressoflessione deviata.

    Routing:
      - RD2229, DM92, DM96 -> TA (sovrapposizione elastica o Bresler TA)
      - NTC2018, NTC2008, EC2 -> SLU (Bresler fiber)

    Se spec.amplifica_instabilita e' True, amplifica Mx e My prima della verifica.

    Args:
        spec: input completo con norma, sezione, sollecitazioni, materiale.

    Returns:
        PressoflessResult con esito, utilizzazione, passaggi.

    Raises:
        ValueError: se spec.norma non e' supportata.
    """
    if spec.norma not in NORME:
        raise ValueError(
            f"Norma '{spec.norma}' non supportata. " f"Norme disponibili: {sorted(NORME)}"
        )

    # Amplificazione instabilita' (opzionale)
    Mx_eff = spec.Mx_kgcm
    My_eff = spec.My_kgcm
    omega_x = None
    omega_y = None
    instab_details: dict = {}

    if spec.amplifica_instabilita and spec.l0_x_cm and spec.l0_y_cm:
        omega_x, omega_y, Mx_eff, My_eff, instab_details = amplifica_momenti_biassiale(
            spec.N_kg,
            spec.Mx_kgcm,
            spec.My_kgcm,
            spec.section,
            spec.barre,
            spec.n,
            spec.l0_x_cm,
            spec.l0_y_cm,
            spec.sigma_c_adm_kgcm2,
            spec.E_c_kgcm2,
        )
        # Crea spec con momenti amplificati
        spec = PressoflessSpec(
            section=spec.section,
            barre=spec.barre,
            N_kg=spec.N_kg,
            Mx_kgcm=Mx_eff,
            My_kgcm=My_eff,
            sigma_c_adm_kgcm2=spec.sigma_c_adm_kgcm2,
            sigma_s_adm_kgcm2=spec.sigma_s_adm_kgcm2,
            n=spec.n,
            norma=spec.norma,
            metodo=spec.metodo,
            alpha_bresler=spec.alpha_bresler,
            amplifica_instabilita=False,  # gia' amplificato
            E_c_kgcm2=spec.E_c_kgcm2,
            f_ck_MPa=spec.f_ck_MPa,
            f_yk_MPa=spec.f_yk_MPa,
        )

    # Routing
    if spec.norma in NORME_TA:
        result = verifica_pressofless_ta_cls(spec)
    else:
        result = verifica_pressofless_slu(spec)

    # Aggiungi info instabilita'
    if omega_x is not None:
        result.omega_x = omega_x
        result.omega_y = omega_y
        result.Mx_amplificato_kgcm = round(Mx_eff, 4)
        result.My_amplificato_kgcm = round(My_eff, 4)
        result.details.update(instab_details)
        result.passaggi_calcolo.insert(
            0,
            f"Instabilita' biassiale: omega_x={omega_x:.4f}, omega_y={omega_y:.4f}, "
            f"Mx_amp={Mx_eff:.1f}, My_amp={My_eff:.1f}",
        )

    return result
