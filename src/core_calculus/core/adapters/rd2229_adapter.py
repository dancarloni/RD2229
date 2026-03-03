"""
RD 2229/1939 verification adapter.

Implements TA (Tensioni Ammissibili) bending + shear checks for RC elements
per Regio Decreto 2229/1939.
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


class Rd2229Adapter(NormAdapter):
    """RD 2229/1939 adapter for RC element verification (TA)."""

    @property
    def norm_code(self) -> str:
        return "RD2229"

    @property
    def description_it(self) -> str:
        return "Verifiche con metodo Tensioni Ammissibili (TA) secondo R.D. 2229/1939"

    def applicability(self, calc_input: CalcInput) -> EligibilityResult:
        reasons: list[str] = []
        refs: list[NormReference] = []

        if calc_input.norm_code and calc_input.norm_code != "RD2229":
            return EligibilityResult(
                eligible=False,
                reasons=[f"Norma richiesta '{calc_input.norm_code}' diversa da RD2229"],
            )

        if calc_input.section is None:
            reasons.append("Sezione non definita")
        if calc_input.material is None:
            reasons.append("Materiale non definito")

        if reasons:
            return EligibilityResult(eligible=False, reasons=reasons)

        refs.append(NormReference(
            norm_code="RD2229", chapter="Art. 7-9",
            paragraph="Art. 7",
            description_it="Verifica sezioni in c.a. con metodo tensioni ammissibili",
        ))
        return EligibilityResult(eligible=True, reasons=["Elemento RC compatibile RD2229"], norm_references=refs)

    def verify(self, calc_input: CalcInput) -> CalcOutput:
        results: dict[str, SingleCheckResult] = {}

        # --- TA Bending (flessione/pressoflessione retta) ---
        bending_result = self._check_ta_bending(calc_input)
        results[bending_result.template_id] = bending_result

        # --- TA Shear (taglio) ---
        shear_result = self._check_ta_shear(calc_input)
        results[shear_result.template_id] = shear_result

        all_ok = all(r.ok for r in results.values())
        max_util = max((r.utilisation or 0.0 for r in results.values()), default=0.0)

        profile = "PROFILE_PRIMARY_FULL"
        if calc_input.element_role == ElementRole.SECONDARY:
            profile = "PROFILE_SECONDARY_STABILITY"

        return CalcOutput(
            element_name=calc_input.element_name,
            norm_code="RD2229",
            ok=all_ok,
            per_template_results=results,
            element_role=calc_input.element_role,
            profile_used=profile,
            summary_metrics={
                "status": "OK" if all_ok else "KO",
                "utilizzazione_massima": round(max_util, 4),
            },
        )

    def _check_ta_bending(self, ci: CalcInput) -> SingleCheckResult:
        """TA bending/axial-bending check per RD2229 Art. 7-8."""
        b = _get_width_cm(ci)  # cm
        h = _get_height_cm(ci)  # cm
        d = (ci.d or (h * 10 - 40)) / 10  # convert mm to cm if needed
        As = (ci.As or 0.0)  # cm²

        sigma_c28 = _get_sigma_c28(ci)  # kg/cm²
        sigma_sn = _get_sigma_sn(ci)  # kg/cm²

        # Allowable stresses (TA method)
        sigma_c_adm = sigma_c28 / 2.0  # Art. 7
        sigma_s_adm = sigma_sn / 2.0  # Art. 7

        n = _get_modular_ratio(ci)  # Es/Ec ratio

        # Applied moment (convert kNm to kgcm)
        M = abs(ci.Mx or 0.0) * 10197.16  # 1 kNm = 10197.16 kgcm
        N = (ci.N or 0.0) * 101.972  # 1 kN = 101.972 kg

        # Find neutral axis position (section cracked, elastic method)
        if As > 0 and b > 0 and d > 0:
            # Quadratic for x: (b/2)x² + n*As*x - n*As*d = 0
            a_coeff = b / 2.0
            b_coeff = n * As
            c_coeff = -n * As * d
            disc = b_coeff ** 2 - 4 * a_coeff * c_coeff
            x = (-b_coeff + math.sqrt(max(disc, 0))) / (2 * a_coeff)
            x = max(x, 0.0)
        else:
            x = 0.0

        # Stresses
        z = d - x / 3 if x > 0 else d
        if z > 0 and As > 0:
            sigma_s = (M + N * (d / 2 - x / 3)) / (As * z) if z > 0 else 0.0
            sigma_c = 2 * (M + N * (d - x / 3)) / (b * x * z) if x > 0 and b > 0 else 0.0
        else:
            sigma_s = 0.0
            sigma_c = 0.0

        sigma_c = abs(sigma_c)
        sigma_s = abs(sigma_s)

        util_c = sigma_c / sigma_c_adm if sigma_c_adm > 0 else 0.0
        util_s = sigma_s / sigma_s_adm if sigma_s_adm > 0 else 0.0
        utilisation = max(util_c, util_s)
        ok = utilisation <= 1.0

        return SingleCheckResult(
            template_id="rd2229_ta_pressoflessione",
            ok=ok,
            utilisation=round(utilisation, 4),
            details={
                "sigma_c_kgcm2": round(sigma_c, 2),
                "sigma_s_kgcm2": round(sigma_s, 2),
                "sigma_c_adm_kgcm2": round(sigma_c_adm, 2),
                "sigma_s_adm_kgcm2": round(sigma_s_adm, 2),
                "x_cm": round(x, 3),
                "z_cm": round(z, 3),
                "M_kgcm": round(M, 1),
                "n": round(n, 2),
            },
            norm_references=[
                NormReference(
                    norm_code="RD2229", chapter="Art. 7-8",
                    paragraph="Art. 7",
                    description_it="Tensioni ammissibili: flessione e pressoflessione",
                ),
            ],
            messages_it=["Verifica TA pressoflessione retta RD2229"],
            check_category="resistenza",
            limit_state="TA",
        )

    def _check_ta_shear(self, ci: CalcInput) -> SingleCheckResult:
        """TA shear check per RD2229 Art. 9."""
        b = _get_width_cm(ci)  # cm
        h = _get_height_cm(ci)  # cm
        d = (ci.d or (h * 10 - 40)) / 10  # cm

        sigma_c28 = _get_sigma_c28(ci)
        # Allowable shear stress without stirrups
        tau_c0 = 0.06 * sigma_c28  # simplified RD2229

        V = abs(ci.Tx or ci.Ty or 0.0) * 101.972  # kN -> kg

        tau = V / (b * d) if (b * d) > 0 else 0.0
        utilisation = tau / tau_c0 if tau_c0 > 0 else (0.0 if tau == 0 else _INVALID_UTILISATION)
        ok = utilisation <= 1.0

        return SingleCheckResult(
            template_id="rd2229_ta_taglio",
            ok=ok,
            utilisation=round(utilisation, 4),
            details={
                "tau_kgcm2": round(tau, 2),
                "tau_c0_kgcm2": round(tau_c0, 2),
                "V_kg": round(V, 1),
            },
            norm_references=[
                NormReference(
                    norm_code="RD2229", chapter="Art. 9",
                    paragraph="Art. 9",
                    description_it="Tensioni tangenziali ammissibili senza armatura specifica",
                ),
            ],
            messages_it=["Verifica TA taglio RD2229"],
            check_category="resistenza",
            limit_state="TA",
        )


# --- Helper functions ---

def _get_width_cm(ci: CalcInput) -> float:
    """Extract width in cm."""
    if ci.section and hasattr(ci.section, "b"):
        return float(ci.section.b) / 10  # mm -> cm
    if ci.section and hasattr(ci.section, "width"):
        return float(ci.section.width) / 10
    return float(ci.extra.get("b_cm", 30.0))


def _get_height_cm(ci: CalcInput) -> float:
    """Extract height in cm."""
    if ci.section and hasattr(ci.section, "h"):
        return float(ci.section.h) / 10
    if ci.section and hasattr(ci.section, "height"):
        return float(ci.section.height) / 10
    return float(ci.extra.get("h_cm", 50.0))


def _get_sigma_c28(ci: CalcInput) -> float:
    """Extract sigma_c28 in kg/cm²."""
    if ci.material and hasattr(ci.material, "sigma_c28"):
        return float(ci.material.sigma_c28)
    return float(ci.extra.get("sigma_c28", 160.0))


def _get_sigma_sn(ci: CalcInput) -> float:
    """Extract sigma_sn in kg/cm²."""
    if ci.material and hasattr(ci.material, "sigma_sn"):
        return float(ci.material.sigma_sn)
    return float(ci.extra.get("sigma_sn", 3800.0))


def _get_modular_ratio(ci: CalcInput) -> float:
    """Extract modular ratio n=Es/Ec."""
    if ci.material and hasattr(ci.material, "n"):
        return float(ci.material.n)
    return float(ci.extra.get("n", 15.0))
