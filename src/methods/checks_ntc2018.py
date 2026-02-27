"""
NTC 2018 verification check functions.

Each function:
- Takes CalcInput and VerificationTemplate
- Returns SingleCheckResult
- Uses Italian messages
- Includes NormReference

TODO: Implement full normative checks per NTC 2018.
Current implementation is PARTIAL and PLACEHOLDER - marks clearly with Italian TODOs.
"""

from __future__ import annotations

import logging
import math

from src.core_calculus.contracts import (
    CalcInput,
    NormReference,
    SingleCheckResult,
    VerificationTemplate,
)
from src.core_calculus.lc_fc_adjustments import AdjustedMaterialProperties, apply_lc_fc_adjustments

logger = logging.getLogger(__name__)


def check_flessione_slu_rett(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica a flessione semplice SLU per sezione rettangolare - NTC 2018.

    TODO: Implementazione PARZIALE - formula semplificata.
    Richiede implementazione completa secondo NTC 2018 § 4.1.2.1.3.1.

    Args:
        calc_input: Dati di input
        template: Template della verifica

    Returns:
        Risultato della verifica
    """
    # Check required inputs
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata"],
        )

    if calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Materiale non specificato"],
        )

    # Get geometry from section
    section = calc_input.section
    if hasattr(section, "width") and hasattr(section, "height"):
        b = section.width  # mm
        h = section.height  # mm
    else:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non rettangolare o geometria non disponibile"],
        )

    # Get material properties
    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)  # MPa
    f_yk_base = getattr(material, "f_yk", None)  # MPa

    if f_ck_base is None or f_yk_base is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Proprietà materiale (f_ck, f_yk) non disponibili"],
        )

    # Apply LC/FC adjustments if structure is existing (LC/FC set)
    if calc_input.lc is not None and calc_input.fc is not None:
        try:
            adjusted = apply_lc_fc_adjustments(material, calc_input.lc, calc_input.fc)
            f_ck = adjusted.f_ck_adjusted
            f_yk = adjusted.f_yk_adjusted
        except ValueError as e:
            # LC/FC invalid - use base values and warn
            f_ck = f_ck_base
            f_yk = f_yk_base
            logger.warning(f"LC/FC adjustment failed: {e}")
    else:
        f_ck = f_ck_base
        f_yk = f_yk_base

    # Get reinforcement
    As = calc_input.As or 0.0  # cm²
    d = calc_input.d or (h * 0.9 / 10.0)  # cm (if not specified, assume d = 0.9h)

    # Convert d to mm
    d_mm = d * 10.0

    # Get bending moment
    Mx = calc_input.Mx or 0.0  # kNm
    My = calc_input.My or 0.0  # kNm
    # Use primary moment (larger of Mx, My)
    M_Ed = max(abs(Mx), abs(My))  # kNm
    M_Ed_Nmm = M_Ed * 1e6  # N·mm

    # Material safety factors - NTC 2018 § 4.1.2.1.1.2
    gamma_c = 1.5
    gamma_s = 1.15

    # Design strengths
    f_cd = 0.85 * f_ck / gamma_c  # MPa
    f_yd = f_yk / gamma_s  # MPa

    # Get compression reinforcement (if any)
    As_prime = calc_input.As_prime or 0.0  # cm²
    d_prime = calc_input.d_prime  # cm
    if d_prime is None or d_prime <= 0:
        d_prime = 4.0  # cm (typical cover + stirrup + bar_diam/2)

    # Convert to mm
    As_prime_mm2 = As_prime * 100.0  # mm²
    d_prime_mm = d_prime * 10.0  # mm

    # Parameters for rectangular stress block - NTC 2018 § 4.1.2.1.2
    lambda_factor = 0.8  # depth of equivalent rectangular stress block
    # eta_factor = 1.0 (stress efficiency factor, already included in lambda)

    # Neutral axis calculation for simple bending (N=0)
    # Equilibrium: R_c + R_s' = R_s
    # Where: R_c = lambda * x * b * f_cd (concrete compression)
    #        R_s = As * f_yd (steel tension)
    #        R_s' = As' * sigma_s' (steel compression, if x > d')

    As_mm2 = As * 100.0  # mm²

    # For singly reinforced section or when As' negligible
    if As_prime_mm2 < 0.01 or As_prime < 0.01:
        # Simplified case: only tension reinforcement
        # R_c = R_s → lambda * x * b * f_cd = As * f_yd
        x = (As_mm2 * f_yd) / (lambda_factor * b * f_cd)  # mm

        # Compression steel contribution (none for singly reinforced)
        R_s_comp = 0.0  # N

    else:
        # Doubly reinforced section - need to check if compression steel yields
        # Assumption 1: compression steel yields (sigma_s' = f_yd)
        # Then: lambda * x * b * f_cd + As' * f_yd = As * f_yd
        x_assumption = ((As_mm2 - As_prime_mm2) * f_yd) / (lambda_factor * b * f_cd)

        # Check if assumption valid (x > d' means compression steel is in compression)
        if x_assumption > d_prime_mm:
            # Compression steel yields - assumption valid
            x = x_assumption
            # sigma_s_prime = f_yd (compression steel yields)
            R_s_comp = As_prime_mm2 * f_yd
        else:
            # Compression steel may not yield - iterative solution needed
            # For now, use simplified approach: assume compression steel yields
            # and set minimum x = 1.1 * d' to ensure compression
            x = max(x_assumption, 1.1 * d_prime_mm)
            # Assume sigma_s_prime = f_yd (compression steel yields)
            R_s_comp = As_prime_mm2 * f_yd

    # Check limits on neutral axis depth
    # Maximum x to ensure ductile failure: x/d ≤ 0.45 for ductility class B
    x_max = 0.45 * d_mm
    if x > x_max:
        # Over-reinforced section - warn but continue
        x_limited = True
    else:
        x_limited = False

    # Compute lever arms
    z_c = d_mm - lambda_factor * x / 2.0  # lever arm for concrete force
    z_s_comp = d_mm - d_prime_mm  # lever arm for compression steel

    # Compute internal forces
    R_c = lambda_factor * x * b * f_cd  # N (concrete compression)
    R_s = As_mm2 * f_yd  # N (steel tension)

    # Compute moment capacity
    M_Rd = R_c * z_c + R_s_comp * z_s_comp  # N·mm
    M_Rd_kNm = M_Rd / 1e6  # kNm

    # Utilisation
    utilisazione = M_Ed_Nmm / M_Rd if M_Rd > 0 else 999.0
    ok = utilisazione <= 1.0

    # Messages
    messages_it = [
        f"Sezione: {b/10:.1f} × {h/10:.1f} cm, d = {d:.1f} cm, d' = {d_prime:.1f} cm",
        f"Armatura tesa: As = {As:.2f} cm²",
        (
            f"Armatura compressa: As' = {As_prime:.2f} cm²"
            if As_prime > 0.01
            else "Armatura compressa: As' = 0 (sezione semplicemente armata)"
        ),
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f} (f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa)",
        "",
        "Calcolo asse neutro (NTC 2018 § 4.1.2.1.3.1):",
        f"  x = {x:.1f} mm ({x/d_mm:.3f}·d)",
        f"  Braccio coppia z = {z_c:.1f} mm",
    ]

    if x_limited:
        messages_it.append(f"  ⚠️ x/d = {x/d_mm:.3f} > 0.45: sezione sovra-armata, verificare duttilità")

    messages_it.extend(
        [
            "",
            f"Momento agente: M_Ed = {M_Ed:.2f} kNm",
            f"Momento resistente: M_Rd = {M_Rd_kNm:.2f} kNm",
            f"Utilizzazione: {utilisazione:.3f} {'✓ OK' if ok else '✗ NON OK'}",
        ]
    )

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok and not x_limited,  # Fail if over-reinforced
        utilisation=utilisazione,
        details={
            "M_Ed_kNm": M_Ed,
            "M_Rd_kNm": M_Rd_kNm,
            "f_cd_MPa": f_cd,
            "f_yd_MPa": f_yd,
            "x_mm": x,
            "x_over_d": x / d_mm,
            "z_mm": z_c,
            "As_cm2": As,
            "As_prime_cm2": As_prime,
            "d_cm": d,
            "d_prime_cm": d_prime,
            "R_c_kN": R_c / 1000.0,
            "R_s_kN": R_s / 1000.0,
            "over_reinforced": x_limited,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.1",
                formula_label="(4.1)",
                description_it="Verifica a flessione semplice e composta - sezione rettangolare",
            ),
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.2",
                description_it="Parametri stress block rettangolare (λ=0.8, η=1.0)",
            ),
        ],
        messages_it=messages_it,
    )


def check_minimi_armatura_flessione_slu(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica minimi di armatura a flessione SLU - NTC 2018.

    Implementa la formula completa secondo NTC 2018 § 4.1.6.1.1:
    As,min = max(0.26 * f_ctm / f_yk * b * d, 0.0013 * b * d)

    Args:
        calc_input: Dati di input
        template: Template della verifica

    Returns:
        Risultato della verifica
    """
    if calc_input.section is None or calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione o materiale non specificati"],
        )

    # Get geometry
    section = calc_input.section
    if hasattr(section, "width") and hasattr(section, "height"):
        b = section.width  # mm
        h = section.height  # mm
    else:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Geometria sezione non disponibile"],
        )

    # Get effective depth d
    d = calc_input.d  # cm (from CalcInput)
    if d is None or d <= 0:
        # If d not specified, estimate as d ≈ h - cover
        # Use conservative estimate: d = 0.9 * h
        d = 0.9 * h / 10.0  # mm → cm
        d_estimated = True
    else:
        d_estimated = False

    d_mm = d * 10.0  # Convert to mm

    # Get material properties (after LC/FC adjustment if applicable)
    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)  # MPa
    f_yk_base = getattr(material, "f_yk", None)  # MPa

    if f_ck_base is None or f_yk_base is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Proprietà materiale (f_ck, f_yk) non disponibili"],
        )

    # Apply LC/FC adjustments if structure is existing
    if calc_input.lc is not None and calc_input.fc is not None:
        try:
            adjusted = apply_lc_fc_adjustments(material, calc_input.lc, calc_input.fc)
            f_ck = adjusted.f_ck_adjusted
            f_yk = adjusted.f_yk_adjusted
        except ValueError as e:
            f_ck = f_ck_base
            f_yk = f_yk_base
            logger.warning(f"LC/FC adjustment failed: {e}")
    else:
        f_ck = f_ck_base
        f_yk = f_yk_base

    # Extract or compute f_ctm
    # Check if material has f_ctm property
    f_ctm = getattr(material, "f_ctm", None)

    if f_ctm is None or f_ctm <= 0:
        # Compute f_ctm from f_ck using NTC 2018 Table C4.1.IV formula
        # f_ctm = 0.30 * f_ck^(2/3) for f_ck ≤ 50 MPa
        # f_ctm = 2.12 * ln(1 + (f_cm/10)) for f_ck > 50 MPa where f_cm = f_ck + 8
        if f_ck <= 50:
            f_ctm = 0.30 * (f_ck ** (2.0 / 3.0))  # MPa
        else:
            f_cm = f_ck + 8.0
            f_ctm = 2.12 * math.log(1 + (f_cm / 10.0))  # MPa
        f_ctm_computed = True
    else:
        f_ctm_computed = False

    # Get reinforcement
    As = calc_input.As or 0.0  # cm²
    As_mm2 = As * 100.0  # mm²

    # Formula NTC 2018 § 4.1.6.1.1:
    # As,min = max(0.26 * f_ctm / f_yk * b * d, 0.0013 * b * d)
    As_min_1 = 0.26 * f_ctm / f_yk * b * d_mm  # mm²
    As_min_2 = 0.0013 * b * d_mm  # mm²
    As_min_mm2 = max(As_min_1, As_min_2)  # mm²

    # Check
    ok = As_mm2 >= As_min_mm2
    utilizzazione = As_min_mm2 / As_mm2 if As_mm2 > 0 else 999.0

    # Italian messages
    messages_it = [
        f"Sezione: {b/10:.1f} × {h/10:.1f} cm, d = {d:.1f} cm" + (" (stimato)" if d_estimated else ""),
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f} (f_ctm = {f_ctm:.2f} MPa" + (" calcolato)" if f_ctm_computed else ")"),
        f"Armatura presente: As = {As:.2f} cm²",
        "",
        "Formula NTC 2018 § 4.1.6.1.1:",
        f"  As,min,1 = 0.26 * f_ctm / f_yk * b * d = {As_min_1 / 100:.2f} cm²",
        f"  As,min,2 = 0.0013 * b * d = {As_min_2 / 100:.2f} cm²",
        f"  As,min = max(As,min,1, As,min,2) = {As_min_mm2 / 100:.2f} cm²",
        "",
        f"Rapporto: As / As,min = {As / (As_min_mm2 / 100):.3f} {'✓ OK' if ok else '✗ NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilizzazione,
        details={
            "As_cm2": As,
            "As_min_cm2": As_min_mm2 / 100.0,
            "As_min_1_cm2": As_min_1 / 100.0,
            "As_min_2_cm2": As_min_2 / 100.0,
            "f_ctm_MPa": f_ctm,
            "f_ck_MPa": f_ck,
            "f_yk_MPa": f_yk,
            "b_mm": b,
            "d_mm": d_mm,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.6.1.1",
                description_it="Armature longitudinali minime",
            )
        ],
        messages_it=messages_it,
    )


def check_taglio_slu(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica a taglio SLU - NTC 2018 § 4.1.2.1.3.2.

    Implementa la verifica a taglio con staffe verticali:
    V_Rd = min(V_Rd,s, V_Rd,max)

    Dove:
    - V_Rd,s = (Asw/s) * 0.9 * d * f_yd (resistenza con staffe)
    - V_Rd,max = 0.9 * d * b * ν * f_cd / (cotθ + tanθ) (resistenza puntoni compressi)
    - ν = 0.6 * (1 - f_ck/250)
    - θ = 21.8° (conservativo, min allowable per NTC 2018)

    Args:
        calc_input: Dati di input
        template: Template della verifica

    Returns:
        Risultato della verifica
    """
    # Check required inputs
    if calc_input.section is None or calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione o materiale non specificati"],
        )

    # Get geometry
    section = calc_input.section
    if hasattr(section, "width") and hasattr(section, "height"):
        b = section.width  # mm
        h = section.height  # mm
    else:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Geometria sezione non disponibile"],
        )

    # Get effective depth
    d = calc_input.d  # cm
    if d is None or d <= 0:
        d = 0.9 * h / 10.0  # Estimate as 0.9*h
        d_estimated = True
    else:
        d_estimated = False
    d_mm = d * 10.0  # Convert to mm

    # Get material properties (after LC/FC adjustment)
    material = calc_input.material
    f_ck_base = getattr(material, "f_ck", None)  # MPa
    f_yk_base = getattr(material, "f_yk", None)  # MPa

    if f_ck_base is None or f_yk_base is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Proprietà materiale (f_ck, f_yk) non disponibili"],
        )

    # Apply LC/FC adjustments if structure is existing
    if calc_input.lc is not None and calc_input.fc is not None:
        try:
            adjusted = apply_lc_fc_adjustments(material, calc_input.lc, calc_input.fc)
            f_ck = adjusted.f_ck_adjusted
            f_yk = adjusted.f_yk_adjusted
        except ValueError as e:
            f_ck = f_ck_base
            f_yk = f_yk_base
            logger.warning(f"LC/FC adjustment failed: {e}")
    else:
        f_ck = f_ck_base
        f_yk = f_yk_base

    # Design strengths
    gamma_c = 1.5
    gamma_s = 1.15
    f_cd = 0.85 * f_ck / gamma_c  # MPa
    f_yd = f_yk / gamma_s  # MPa

    # Get stirrup data
    staffe_diametro = calc_input.staffe_diametro  # mm
    staffe_passo = calc_input.staffe_passo  # cm (assumed, may need unit check)
    staffe_num_bracci = calc_input.staffe_num_bracci or 2  # Default to 2 legs

    if staffe_diametro is None or staffe_diametro <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Dati staffe mancanti: diametro non specificato"],
        )

    if staffe_passo is None or staffe_passo <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Dati staffe mancanti: passo non specificato"],
        )

    # Convert passo to mm (assume input is cm)
    s_mm = staffe_passo * 10.0  # mm

    # Compute stirrup area per stirrup
    phi_mm = staffe_diametro  # mm
    A_sw_stirrup = staffe_num_bracci * math.pi * (phi_mm**2) / 4.0  # mm²

    # Compute Asw/s
    Asw_over_s = A_sw_stirrup / s_mm  # mm²/mm

    # Get shear force
    Tx = calc_input.Tx or 0.0  # kN (assumed)
    Ty = calc_input.Ty or 0.0  # kN
    V_Ed = max(abs(Tx), abs(Ty))  # kN
    V_Ed_N = V_Ed * 1000.0  # N

    if V_Ed <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Taglio agente V_Ed non specificato o nullo"],
        )

    # V_Rd,s calculation (resistance with stirrups)
    # NTC 2018 § 4.1.2.1.3.2: V_Rd,s = (Asw/s) * 0.9 * d * f_yd * (cotθ + cotα) * sinα
    # For vertical stirrups: α = 90°, so sinα = 1, cotα = 0
    # V_Rd,s = (Asw/s) * 0.9 * d * f_yd * cotθ

    # Use θ = 21.8° (most conservative, cotθ = 2.5)
    # NTC 2018 allows θ between 21.8° and 45°
    theta_deg = 21.8  # degrees
    theta_rad = theta_deg * math.pi / 180.0
    cot_theta = 1.0 / math.tan(theta_rad)
    tan_theta = math.tan(theta_rad)

    V_Rd_s = Asw_over_s * 0.9 * d_mm * f_yd * cot_theta  # N

    # V_Rd,max calculation (compressed strut resistance)
    # NTC 2018 § 4.1.2.1.3.2: V_Rd,max = 0.9 * d * b * ν * f_cd / (cotθ + tanθ)
    # where ν = 0.6 * (1 - f_ck/250) for f_ck in MPa

    nu = 0.6 * (1.0 - f_ck / 250.0)
    V_Rd_max = 0.9 * d_mm * b * nu * f_cd / (cot_theta + tan_theta)  # N

    # V_Rd = min(V_Rd,s, V_Rd,max)
    V_Rd = min(V_Rd_s, V_Rd_max)  # N
    V_Rd_kN = V_Rd / 1000.0  # kN

    # Check
    ok = V_Ed_N <= V_Rd
    utilisazione = V_Ed_N / V_Rd if V_Rd > 0 else 999.0

    # Determine limiting case
    limiting_case = "staffe" if V_Rd_s < V_Rd_max else "puntoni_compressi"

    # Italian messages
    messages_it = [
        f"Sezione: {b/10:.1f} × {h/10:.1f} cm, d = {d:.1f} cm" + (" (stimato)" if d_estimated else ""),
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f} (f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa)",
        f"Staffe: φ{phi_mm:.0f}/{staffe_passo:.0f}cm, {staffe_num_bracci} bracci",
        f"  Asw/s = {Asw_over_s:.4f} mm²/mm",
        "",
        "Calcolo V_Rd (NTC 2018 § 4.1.2.1.3.2):",
        f"  θ = {theta_deg:.1f}° (cotθ = {cot_theta:.2f})",
        f"  ν = 0.6*(1 - f_ck/250) = {nu:.3f}",
        f"  V_Rd,s (resistenza staffe) = {V_Rd_s/1000:.1f} kN",
        f"  V_Rd,max (puntoni compressi) = {V_Rd_max/1000:.1f} kN",
        f"  V_Rd = min(V_Rd,s, V_Rd,max) = {V_Rd_kN:.1f} kN (limitata da: {limiting_case})",
        "",
        f"Taglio agente: V_Ed = {V_Ed:.1f} kN",
        f"Taglio resistente: V_Rd = {V_Rd_kN:.1f} kN",
        f"Utilizzazione: {utilisazione:.3f} {'✓ OK' if ok else '✗ NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilisazione,
        details={
            "V_Ed_kN": V_Ed,
            "V_Rd_kN": V_Rd_kN,
            "V_Rd_s_kN": V_Rd_s / 1000.0,
            "V_Rd_max_kN": V_Rd_max / 1000.0,
            "Asw_over_s_mm2_mm": Asw_over_s,
            "theta_deg": theta_deg,
            "nu": nu,
            "limiting_case": limiting_case,
            "f_cd_MPa": f_cd,
            "f_yd_MPa": f_yd,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.2",
                description_it="Verifica a taglio - resistenza con staffe e puntoni compressi",
            ),
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.2",
                description_it="Coefficiente ν per resistenza puntoni",
            ),
        ],
        messages_it=messages_it,
    )


def check_minimi_armatura_taglio_slu(
    calc_input: CalcInput,
    template: VerificationTemplate,
    adjusted_material: AdjustedMaterialProperties | None = None,
) -> SingleCheckResult:
    """Check minimum shear reinforcement per NTC 2018 § 4.1.6.1.1.

    Formula: Asw,min/s = 0.08 * sqrt(f_ck) / f_yk * b

    Args:
        calc_input: Input data with section, material, stirrups data
        template: Template definition
        adjusted_material: Material properties after LC/FC adjustments (optional)

    Returns:
        SingleCheckResult with ok/non-ok
    """
    # Extract section
    section = calc_input.section
    if section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione non specificata per verifica minimi armatura taglio"],
        )

    b = getattr(section, "b", None)
    h = getattr(section, "h", None)

    if b is None or b <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[f"Larghezza sezione b non valida o mancante (b = {b})"],
        )

    if h is None or h <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[f"Altezza sezione h non valida o mancante (h = {h})"],
        )

    # Extract material
    material = calc_input.material
    if material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Materiale non specificato per verifica minimi armatura taglio"],
        )

    # Get material properties (adjusted or original)
    if adjusted_material is not None:
        f_ck = adjusted_material.f_ck_adjusted
        f_yk = adjusted_material.f_yk_adjusted
    else:
        f_ck: float | None = getattr(material, "f_ck", None)
        f_yk: float | None = getattr(material, "f_yk", None)

    if f_ck is None or f_ck <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[f"Resistenza cls f_ck non valida (f_ck = {f_ck})"],
        )

    if f_yk is None or f_yk <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[f"Tensione acciaio f_yk non valida (f_yk = {f_yk})"],
        )

    # Extract stirrup data
    staffe_diametro = calc_input.staffe_diametro  # mm
    staffe_passo = calc_input.staffe_passo  # cm (from GUI)
    staffe_num_bracci = calc_input.staffe_num_bracci  # number

    if staffe_diametro is None or staffe_diametro <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Diametro staffe mancante o non valido - impossibile verificare minimi armatura taglio"],
        )

    if staffe_passo is None or staffe_passo <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Passo staffe mancante o non valido - impossibile verificare minimi armatura taglio"],
        )

    if staffe_num_bracci is None or staffe_num_bracci < 0:
        staffe_num_bracci = 2  # Default assumption

    # Convert to consistent units
    phi_mm = staffe_diametro  # mm
    s_mm = staffe_passo * 10.0  # cm → mm

    # Compute actual Asw/s
    A_sw_stirrup = staffe_num_bracci * math.pi * (phi_mm**2) / 4.0  # mm²
    Asw_over_s_actual = A_sw_stirrup / s_mm  # mm²/mm

    # Compute minimum per NTC 2018 § 4.1.6.1.1
    # Asw,min/s = 0.08 * sqrt(f_ck) / f_yk * b
    Asw_min_over_s = 0.08 * math.sqrt(f_ck) / f_yk * b  # mm²/mm

    # Check
    ok = Asw_over_s_actual >= Asw_min_over_s
    utilisazione = Asw_min_over_s / Asw_over_s_actual if Asw_over_s_actual > 0 else 999.0

    # Italian messages
    messages_it = [
        f"Sezione: {b/10:.1f} × {h/10:.1f} cm",
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f}",
        f"Staffe: φ{phi_mm:.0f}/{staffe_passo:.0f}cm, {staffe_num_bracci} bracci",
        f"  Asw/s effettivo = {Asw_over_s_actual:.4f} mm²/mm",
        "",
        "Formula NTC 2018 § 4.1.6.1.1:",
        "  Asw,min/s = 0.08 * √f_ck / f_yk * b",
        f"  Asw,min/s = 0.08 * √{f_ck:.0f} / {f_yk:.0f} * {b:.0f}",
        f"  Asw,min/s = {Asw_min_over_s:.4f} mm²/mm",
        "",
        f"Asw/s effettivo: {Asw_over_s_actual:.4f} mm²/mm",
        f"Asw,min/s richiesto: {Asw_min_over_s:.4f} mm²/mm",
        f"Utilizzazione: {utilisazione:.3f} {'✓ OK' if ok else '✗ NON OK'}",
    ]

    if not ok:
        messages_it.append("")
        messages_it.append(f"⚠️ Armatura a taglio insufficiente: " f"serve Asw/s ≥ {Asw_min_over_s:.4f} mm²/mm")

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilisazione,
        details={
            "Asw_over_s_actual_mm2_mm": Asw_over_s_actual,
            "Asw_min_over_s_mm2_mm": Asw_min_over_s,
            "f_ck_MPa": f_ck,
            "f_yk_MPa": f_yk,
            "phi_mm": phi_mm,
            "s_cm": staffe_passo,
            "num_bracci": staffe_num_bracci,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.6.1.1",
                formula_label="Eq. implicita",
                description_it="Armatura minima a taglio: Asw,min/s = 0.08*√f_ck/f_yk*b",
            ),
        ],
        messages_it=messages_it,
    )
