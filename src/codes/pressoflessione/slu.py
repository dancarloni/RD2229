"""Wrapper SLU per pressoflessione deviata NTC2018/NTC2008/EC2 (FASE J).

Delega a src.methods.checks_ntc2018.check_pressoflessione_slu per il
calcolo fiber + Bresler SLU. Converte unita' (cm/kg -> mm/kN).

Non duplica codice: riusa interamente il motore fiber esistente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import PressoflessResult, PressoflessSpec

# Riferimenti normativi
_NORM_REFS_SLU: dict[str, list[str]] = {
    "NTC2018": ["NTC2018 §4.1.2.1.3.1 — Pressoflessione deviata SLU"],
    "NTC2008": ["NTC2008 §4.1.2.1.3.1 — Pressoflessione deviata SLU"],
    "EC2": ["EC2 §5.8.9 — Interazione biassiale (Mx/Mx_Rd)^alpha + (My/My_Rd)^alpha <= 1"],
}


@dataclass
class _MockCalcInput:
    """Adapter minimo per CalcInput da PressoflessSpec."""

    element_name: str = ""
    section: Any = None
    material: Any = None
    norm_code: str = ""
    limit_states_enabled: list = None
    N: float = 0.0
    Mx: float = 0.0
    My: float = 0.0
    d: float | None = None
    extra: dict | None = None
    lc: str = ""
    fc: float = 1.0

    def __post_init__(self):
        if self.limit_states_enabled is None:
            self.limit_states_enabled = ["SLU"]


@dataclass
class _MockMaterial:
    """Adapter materiale per checks_ntc2018 (MPa)."""

    f_ck: float = 25.0
    f_yk: float = 450.0
    gamma_c: float = 1.5
    gamma_s: float = 1.15
    E_s: float = 200000.0


@dataclass
class _MockTemplate:
    """Template minimo per checks_ntc2018."""

    template_id: str = "pressoflessione_slu"
    check_category: str = "RESISTANCE"
    limit_state: str = "SLU"


def verifica_pressofless_slu(spec: PressoflessSpec) -> PressoflessResult:
    """Verifica SLU pressoflessione deviata.

    Converte PressoflessSpec in CalcInput e delega a check_pressoflessione_slu.
    Unita' in ingresso: cm/kg/kg·cm. Conversione a mm/kN/kNm per il fiber method.

    Args:
        spec: input pressoflessione deviata

    Returns:
        PressoflessResult con bresler_value SLU.
    """
    from src.methods.checks_ntc2018 import check_pressoflessione_slu

    if spec.f_ck_MPa is None or spec.f_yk_MPa is None:
        return PressoflessResult(
            esito="ERRORE", utilisation=0.0,
            metodo="BRESLER_SLU", norma=spec.norma,
            decision_log=["f_ck_MPa e f_yk_MPa richiesti per verifica SLU"],
        )

    material = _MockMaterial(f_ck=spec.f_ck_MPa, f_yk=spec.f_yk_MPa)

    # Conversione unita': kg -> kN, kg·cm -> kN·m
    N_kN = spec.N_kg / 102.0   # 1 kN = 102 kgf
    Mx_kNm = spec.Mx_kgcm / 10200.0  # 1 kN·m = 10200 kg·cm
    My_kNm = spec.My_kgcm / 10200.0

    # Armatura: somma barre per As totale
    As_tesa = sum(b.A for b in spec.barre if b.zona == "tesa")
    As_comp = sum(b.A for b in spec.barre if b.zona == "compressa")

    calc_input = _MockCalcInput(
        element_name="pressoflessione_deviata_slu",
        section=spec.section,
        material=material,
        norm_code=spec.norma,
        N=N_kN,
        Mx=Mx_kNm,
        My=My_kNm,
        extra={
            "As_tesa_cm2": As_tesa,
            "As_comp_cm2": As_comp,
        },
    )
    template = _MockTemplate()

    try:
        result = check_pressoflessione_slu(calc_input, template)
    except Exception as exc:
        return PressoflessResult(
            esito="ERRORE", utilisation=0.0,
            metodo="BRESLER_SLU", norma=spec.norma,
            decision_log=[f"Errore check_pressoflessione_slu: {exc}"],
        )

    details = result.details if hasattr(result, "details") else {}
    bresler = details.get("bresler_value", result.utilisation)

    return PressoflessResult(
        esito="OK" if result.ok else "NON_OK",
        utilisation=round(result.utilisation, 6),
        metodo="BRESLER_SLU",
        norma=spec.norma,
        bresler_value=round(bresler, 6) if bresler is not None else None,
        alpha_bresler=details.get("alpha_bresler"),
        M_Rdx_kgcm=round(details["Mx_Rd_kNm"] * 10200.0, 4) if "Mx_Rd_kNm" in details else None,
        M_Rdy_kgcm=round(details["My_Rd_kNm"] * 10200.0, 4) if "My_Rd_kNm" in details else None,
        norm_references=_NORM_REFS_SLU.get(spec.norma, []),
        passaggi_calcolo=result.messages_it if hasattr(result, "messages_it") else [],
        details=details,
    )
