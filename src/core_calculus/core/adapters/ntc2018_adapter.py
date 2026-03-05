"""
NTC2018 verification adapter.

Implements ULS bending + shear checks for RC beam/column elements
per NTC 2018 §4.1.2.
"""

from __future__ import annotations

import math

from src.core_calculus.contracts import (
    CalcInput,
    CalcOutput,
    ElementRole,
    NormReference,
    SingleCheckResult,
)

from .base import EligibilityResult, NormAdapter

_INVALID_UTILISATION = 99.0


def _safe_utilisation(demand: float, capacity: float) -> float:
    """Compute utilisation ratio safely (demand / capacity)."""
    if capacity > 0:
        return demand / capacity
    return 0.0 if demand == 0 else _INVALID_UTILISATION


class Ntc2018Adapter(NormAdapter):
    """NTC 2018 adapter for RC element verification (ULS)."""

    @property
    def norm_code(self) -> str:
        return "NTC2018"

    @property
    def description_it(self) -> str:
        return "Verifiche SLU per elementi in c.a. secondo NTC 2018"

    def applicability(self, calc_input: CalcInput) -> EligibilityResult:
        reasons: list[str] = []
        refs: list[NormReference] = []

        if calc_input.norm_code and calc_input.norm_code != "NTC2018":
            return EligibilityResult(
                eligible=False,
                reasons=[f"Norma richiesta '{calc_input.norm_code}' diversa da NTC2018"],
            )

        if calc_input.section is None:
            reasons.append("Sezione non definita")
        if calc_input.material is None:
            reasons.append("Materiale non definito")

        if reasons:
            return EligibilityResult(eligible=False, reasons=reasons)

        refs.append(
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2",
                description_it="Verifiche allo stato limite ultimo per elementi in c.a.",
            )
        )
        return EligibilityResult(
            eligible=True, reasons=["Elemento RC compatibile NTC2018"], norm_references=refs
        )

    def verify(self, calc_input: CalcInput) -> CalcOutput:
        results: dict[str, SingleCheckResult] = {}

        # --- ULS Bending (pressoflessione retta) ---
        bending_result = self._check_uls_bending(calc_input)
        results[bending_result.template_id] = bending_result

        # --- ULS Shear (taglio) ---
        shear_result = self._check_uls_shear(calc_input)
        results[shear_result.template_id] = shear_result

        all_ok = all(r.ok for r in results.values())
        max_util = max((r.utilisation or 0.0 for r in results.values()), default=0.0)

        profile = "PROFILE_PRIMARY_FULL"
        if calc_input.element_role == ElementRole.SECONDARY:
            profile = "PROFILE_SECONDARY_STABILITY"

        return CalcOutput(
            element_name=calc_input.element_name,
            norm_code="NTC2018",
            ok=all_ok,
            per_template_results=results,
            element_role=calc_input.element_role,
            profile_used=profile,
            summary_metrics={
                "status": "OK" if all_ok else "KO",
                "utilizzazione_massima": round(max_util, 4),
            },
        )

    def _check_uls_bending(self, ci: CalcInput) -> SingleCheckResult:
        """ULS bending check per NTC2018 §4.1.2.1.3."""
        b = _get_width(ci)  # mm
        h = _get_height(ci)  # mm
        d = ci.d or (h - 40.0)  # mm, effective depth
        As = ci.As or 0.0  # mm²

        fck = _get_fck(ci)  # MPa
        fyk = _get_fyk(ci)  # MPa

        # Design strengths
        fcd = 0.85 * fck / 1.5  # NTC2018 §4.1.2.1.1
        fyd = fyk / 1.15  # NTC2018 §4.1.2.1.1

        # Applied moment
        M_Ed = abs(ci.Mx or 0.0)  # kNm

        # Normal force (compression positive)
        N_Ed = ci.N or 0.0  # kN

        # Resistant moment (simplified rectangular stress block)
        if As > 0 and d > 0:
            # Lever arm from reinforcement
            x = (As * fyd - N_Ed * 1000) / (0.8 * b * fcd) if b > 0 and fcd > 0 else 0.0
            x = max(x, 0.0)
            z = d - 0.4 * x
            z = max(z, 0.0)
            M_Rd = (As * fyd * z + N_Ed * 1000 * (d / 2 - 0.4 * x)) / 1e6  # kNm
            M_Rd = max(M_Rd, 0.0)
        else:
            x = 0.0
            z = d
            M_Rd = 0.0

        utilisation = _safe_utilisation(M_Ed, M_Rd)
        ok = utilisation <= 1.0

        return SingleCheckResult(
            template_id="ntc2018_slu_pressoflessione",
            ok=ok,
            utilisation=round(utilisation, 4),
            details={
                "M_Ed_kNm": round(M_Ed, 2),
                "M_Rd_kNm": round(M_Rd, 2),
                "N_Ed_kN": round(N_Ed, 2),
                "x_mm": round(x, 2),
                "z_mm": round(z, 2),
                "fcd_MPa": round(fcd, 2),
                "fyd_MPa": round(fyd, 2),
                "b_mm": round(b, 2),
                "d_mm": round(d, 2),
            },
            norm_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="4.1",
                    paragraph="4.1.2.1.3.1",
                    description_it="Resistenza a pressoflessione retta SLU",
                ),
            ],
            messages_it=["Verifica pressoflessione retta SLU NTC2018"],
            check_category="resistenza",
            limit_state="SLU",
        )

    def _check_uls_shear(self, ci: CalcInput) -> SingleCheckResult:
        """ULS shear check per NTC2018 §4.1.2.3."""
        b = _get_width(ci)
        h = _get_height(ci)
        d = ci.d or (h - 40.0)

        fck = _get_fck(ci)

        V_Ed = abs(ci.Tx or ci.Ty or 0.0)  # kN

        # Concrete contribution (no stirrups) per §4.1.2.3.5.1
        k = min(1 + math.sqrt(200 / d), 2.0) if d > 0 else 1.0
        rho_l = min((ci.As or 0.0) / (b * d), 0.02) if (b * d) > 0 else 0.0
        v_min = 0.035 * k**1.5 * math.sqrt(fck)
        V_Rd_c = max(
            (0.18 / 1.5) * k * (100 * rho_l * fck) ** (1 / 3) * b * d / 1000,
            v_min * b * d / 1000,
        )  # kN

        utilisation = _safe_utilisation(V_Ed, V_Rd_c)
        ok = utilisation <= 1.0

        return SingleCheckResult(
            template_id="ntc2018_slu_taglio",
            ok=ok,
            utilisation=round(utilisation, 4),
            details={
                "V_Ed_kN": round(V_Ed, 2),
                "V_Rd_c_kN": round(V_Rd_c, 2),
                "k": round(k, 4),
                "rho_l": round(rho_l, 6),
                "fck_MPa": round(fck, 2),
            },
            norm_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="4.1",
                    paragraph="4.1.2.3.5.1",
                    description_it="Resistenza a taglio SLU senza armatura specifica",
                ),
            ],
            messages_it=["Verifica taglio SLU NTC2018"],
            check_category="resistenza",
            limit_state="SLU",
        )


# --- Helper functions ---


def _get_width(ci: CalcInput) -> float:
    """Extract width in mm from section or extra."""
    if ci.section and hasattr(ci.section, "b"):
        return float(ci.section.b)
    if ci.section and hasattr(ci.section, "width"):
        return float(ci.section.width)
    return float(ci.extra.get("b_mm", ci.extra.get("width", 300.0)))


def _get_height(ci: CalcInput) -> float:
    """Extract height in mm from section or extra."""
    if ci.section and hasattr(ci.section, "h"):
        return float(ci.section.h)
    if ci.section and hasattr(ci.section, "height"):
        return float(ci.section.height)
    return float(ci.extra.get("h_mm", ci.extra.get("height", 500.0)))


def _get_fck(ci: CalcInput) -> float:
    """Extract fck in MPa from material or extra."""
    if ci.material and hasattr(ci.material, "fck"):
        return float(ci.material.fck)
    if ci.material and hasattr(ci.material, "f_ck"):
        return float(ci.material.f_ck)
    return float(ci.extra.get("fck", 25.0))


def _get_fyk(ci: CalcInput) -> float:
    """Extract fyk in MPa from material or extra."""
    if ci.material and hasattr(ci.material, "fyk"):
        return float(ci.material.fyk)
    if ci.material and hasattr(ci.material, "f_yk"):
        return float(ci.material.f_yk)
    return float(ci.extra.get("fyk", 450.0))
