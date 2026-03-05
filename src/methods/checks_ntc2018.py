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


def check_flessione_slu_rett(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
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
        f"Sezione: {b / 10:.1f} × {h / 10:.1f} cm, d = {d:.1f} cm, d' = {d_prime:.1f} cm",
        f"Armatura tesa: As = {As:.2f} cm²",
        (
            f"Armatura compressa: As' = {As_prime:.2f} cm²"
            if As_prime > 0.01
            else "Armatura compressa: As' = 0 (sezione semplicemente armata)"
        ),
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f} (f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa)",
        "",
        "Calcolo asse neutro (NTC 2018 § 4.1.2.1.3.1):",
        f"  x = {x:.1f} mm ({x / d_mm:.3f}·d)",
        f"  Braccio coppia z = {z_c:.1f} mm",
    ]

    if x_limited:
        messages_it.append(
            f"  ⚠️ x/d = {x / d_mm:.3f} > 0.45: sezione sovra-armata, verificare duttilità"
        )

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


def check_pressoflessione_slu(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a presso/tenso-flessione retta e deviata SLU — NTC 2018 § 4.1.2.1.3.1.

    Modello generalizzato per QUALSIASI tipo di sezione gestito dal software.
    Copre tutti i casi di interazione N + M:
    - Compressione centrata (N > 0, M = 0)
    - Trazione centrata (N < 0, M = 0)
    - Flessione semplice retta (N = 0, Mx o My)
    - Presso-flessione retta (N > 0, Mx o My)
    - Tenso-flessione retta (N < 0, Mx o My)
    - Flessione deviata (N + Mx + My, formula di Bresler)

    Metodo: fiber method con stress block rettangolare (λ=0.8).
    Convenzione: N > 0 = compressione, N < 0 = trazione.

    Args:
        calc_input: Dati di input (N, Mx, My, sezione, materiale, armatura)
        template: Template della verifica

    Returns:
        Risultato della verifica con interazione N-M
    """
    from src.methods.section_fiber import (
        compute_concrete_resultant,
        get_section_height,
        get_section_width,
    )

    # --- Validazione input ---
    if calc_input.section is None:
        return SingleCheckResult(
            template_id=template.template_id, ok=False, utilisation=None,
            details={}, messages_it=["Sezione non specificata"],
        )
    if calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id, ok=False, utilisation=None,
            details={}, messages_it=["Materiale non specificato"],
        )

    section = calc_input.section
    material = calc_input.material

    # Verifica che la sezione abbia un tipo riconosciuto
    section_type = getattr(section, "section_type", None)
    try:
        h = get_section_height(section)
        w = get_section_width(section)
    except ValueError:
        return SingleCheckResult(
            template_id=template.template_id, ok=False, utilisation=None,
            details={},
            messages_it=[f"Geometria sezione non disponibile (tipo: {section_type})"],
        )

    f_ck_base = getattr(material, "f_ck", None)
    f_yk_base = getattr(material, "f_yk", None)
    if f_ck_base is None or f_yk_base is None:
        return SingleCheckResult(
            template_id=template.template_id, ok=False, utilisation=None,
            details={}, messages_it=["Proprietà materiale (f_ck, f_yk) non disponibili"],
        )

    # --- LC/FC per edifici esistenti ---
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

    # --- Parametri di calcolo ---
    gamma_c = 1.5
    gamma_s = 1.15
    f_cd = 0.85 * f_ck / gamma_c   # MPa
    f_yd = f_yk / gamma_s           # MPa
    lambda_f = 0.8                  # profondità stress block
    Es = 200000.0                   # MPa, modulo elastico acciaio
    eps_cu = 0.0035                 # deformazione ultima cls NTC2018 §4.1.2.1.2
    eps_yd = f_yd / Es

    # Armatura
    As = calc_input.As or 0.0               # cm² (tesa)
    As_prime = calc_input.As_prime or 0.0    # cm² (compressa)
    d = calc_input.d or (h * 0.9 / 10.0)    # cm (profondità utile)
    d_prime = calc_input.d_prime or 4.0      # cm

    d_mm = d * 10.0
    d_prime_mm = d_prime * 10.0
    As_mm2 = As * 100.0
    As_prime_mm2 = As_prime * 100.0

    # Sollecitazioni
    N_Ed = calc_input.N or 0.0    # kN (positivo = compressione)
    Mx_Ed = calc_input.Mx or 0.0  # kNm
    My_Ed = calc_input.My or 0.0  # kNm
    N_Ed_N = N_Ed * 1000.0        # N

    # --- Casi limite: sollecitazioni nulle ---
    if abs(N_Ed_N) < 1.0 and abs(Mx_Ed) < 1e-6 and abs(My_Ed) < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id, ok=True, utilisation=0.0,
            details={"N_Ed_kN": N_Ed, "Mx_Ed_kNm": Mx_Ed, "My_Ed_kNm": My_Ed},
            messages_it=["Sollecitazioni nulle (N≈0, Mx≈0, My≈0): verifica soddisfatta."],
            norm_references=[],
        )

    # --- Funzione ausiliaria: verifica uniassiale su un asse ---

    def _uniaxial_check(M_Ed_kNm: float, axis: str) -> dict:
        """Esegue verifica uniassiale N + M su un asse.

        Args:
            M_Ed_kNm: momento agente [kNm]
            axis: "x" o "y"

        Returns:
            dict con chiavi: M_Rd_kNm, x_eq_mm, x_over_d, over_reinforced,
                             ok, utilisazione, messages
        """
        M_Ed_Nmm = abs(M_Ed_kNm) * 1e6
        h_axis = h if axis == "x" else w
        h_2 = h_axis / 2.0
        # Per asse y, d si riferisce alla dimensione orizzontale
        d_ax_mm = d_mm if axis == "x" else (w * 0.9 if calc_input.d is None else d_mm)

        def _sigma_s(eps: float) -> float:
            if abs(eps) >= eps_yd:
                return f_yd if eps >= 0 else -f_yd
            return eps * Es

        def _equilibrium_N(x_na: float) -> float:
            """Sforzo normale interno per dato asse neutro x_na [mm]."""
            R_c, _ = compute_concrete_resultant(
                section, x_na, f_cd, axis=axis, lambda_f=lambda_f
            )
            # Deformazione armature
            if x_na > 0:
                eps_s_comp = eps_cu * (x_na - d_prime_mm) / x_na
                eps_s_tens = eps_cu * (x_na - d_ax_mm) / x_na
            else:
                eps_s_comp = -eps_cu
                eps_s_tens = -eps_cu

            R_s_comp = As_prime_mm2 * _sigma_s(eps_s_comp)
            R_s_tens = As_mm2 * _sigma_s(eps_s_tens)
            return R_c + R_s_comp + R_s_tens

        def _moment_about_center(x_na: float) -> float:
            """Momento interno rispetto al baricentro geometrico [N·mm]."""
            _, M_c = compute_concrete_resultant(
                section, x_na, f_cd, axis=axis, lambda_f=lambda_f
            )
            if x_na > 0:
                eps_s_comp = eps_cu * (x_na - d_prime_mm) / x_na
                eps_s_tens = eps_cu * (x_na - d_ax_mm) / x_na
            else:
                eps_s_comp = -eps_cu
                eps_s_tens = -eps_cu

            R_s_comp = As_prime_mm2 * _sigma_s(eps_s_comp)
            R_s_tens = As_mm2 * _sigma_s(eps_s_tens)

            M_int = M_c + R_s_comp * (h_2 - d_prime_mm) - R_s_tens * (d_ax_mm - h_2)
            return M_int

        # Bisezione su asse neutro
        x_lo = -h_axis
        x_hi = 3.0 * h_axis

        N_lo = _equilibrium_N(x_lo)
        N_hi = _equilibrium_N(x_hi)

        if N_Ed_N < N_lo or N_Ed_N > N_hi:
            return {
                "M_Rd_kNm": 0.0, "x_eq_mm": 0.0, "x_over_d": 0.0,
                "over_reinforced": False, "ok": False, "utilisazione": 999.0,
                "messages": [
                    f"N_Ed = {N_Ed:.1f} kN fuori dal dominio di resistenza.",
                    f"N_Rd,min = {N_lo / 1000:.1f} kN, N_Rd,max = {N_hi / 1000:.1f} kN",
                ],
            }

        for _ in range(100):
            x_mid = (x_lo + x_hi) / 2.0
            N_mid = _equilibrium_N(x_mid)
            if abs(N_mid - N_Ed_N) < 0.1:
                break
            if N_mid < N_Ed_N:
                x_lo = x_mid
            else:
                x_hi = x_mid
        x_eq = (x_lo + x_hi) / 2.0

        M_Rd_Nmm = abs(_moment_about_center(x_eq))
        M_Rd_kNm_val = M_Rd_Nmm / 1e6

        if M_Rd_Nmm > 0:
            util = M_Ed_Nmm / M_Rd_Nmm
        elif M_Ed_Nmm < 1.0:
            util = 0.0
        else:
            util = 999.0

        x_over_d_val = x_eq / d_ax_mm if d_ax_mm > 0 else 0.0
        over_reinf = x_over_d_val > 0.45

        return {
            "M_Rd_kNm": M_Rd_kNm_val,
            "x_eq_mm": x_eq,
            "x_over_d": x_over_d_val,
            "over_reinforced": over_reinf,
            "ok": util <= 1.0 and not over_reinf,
            "utilisazione": util,
            "messages": [],
        }

    # --- Determinazione tipo verifica ---
    has_Mx = abs(Mx_Ed) > 1e-6
    has_My = abs(My_Ed) > 1e-6
    biaxial = has_Mx and has_My

    if biaxial:
        # ---------------------------------------------------------------
        # FLESSIONE DEVIATA: Formula di Bresler (NTC2018 / EC2 §5.8.9)
        # (Mx_Ed/Mx_Rd)^α + (My_Ed/My_Rd)^α ≤ 1.0
        # ---------------------------------------------------------------
        res_x = _uniaxial_check(Mx_Ed, axis="x")
        res_y = _uniaxial_check(My_Ed, axis="y")

        Mx_Rd = res_x["M_Rd_kNm"]
        My_Rd = res_y["M_Rd_kNm"]

        # N_Rd per compressione centrata (tutta sezione + armatura)
        # Approssimazione: area cls = h * w_medio (media larghezza)
        # Per maggiore precisione usiamo integrazione fiber
        R_c_full, _ = compute_concrete_resultant(
            section, h / lambda_f, f_cd, axis="x", lambda_f=lambda_f
        )
        N_Rd_N = R_c_full + (As_mm2 + As_prime_mm2) * f_yd
        N_Rd_kN = N_Rd_N / 1000.0

        # Esponente α (interpolazione lineare)
        n_rel = abs(N_Ed_N) / N_Rd_N if N_Rd_N > 0 else 0.0
        if n_rel <= 0.1:
            alpha = 1.0
        elif n_rel >= 1.0:
            alpha = 2.0
        else:
            # Interpolazione lineare 0.1→1.0: α da 1.0→2.0
            alpha = 1.0 + (n_rel - 0.1) / 0.9
        alpha = min(alpha, 2.0)

        # Verifica Bresler
        if Mx_Rd > 0 and My_Rd > 0:
            ratio_x = abs(Mx_Ed) / Mx_Rd
            ratio_y = abs(My_Ed) / My_Rd
            bresler = ratio_x ** alpha + ratio_y ** alpha
        elif Mx_Rd <= 0 and My_Rd <= 0:
            bresler = 999.0
        elif Mx_Rd <= 0:
            bresler = 999.0 if abs(Mx_Ed) > 1e-6 else (abs(My_Ed) / My_Rd) ** alpha
        else:
            bresler = 999.0 if abs(My_Ed) > 1e-6 else (abs(Mx_Ed) / Mx_Rd) ** alpha

        over_reinf = res_x["over_reinforced"] or res_y["over_reinforced"]
        ok = bresler <= 1.0 and not over_reinf

        messages_it = [
            f"Sezione: {section_type}, h = {h / 10:.1f} cm, b = {w / 10:.1f} cm",
            f"d = {d:.1f} cm, d' = {d_prime:.1f} cm",
            f"Armatura tesa: As = {As:.2f} cm², compressa: As' = {As_prime:.2f} cm²",
            f"Materiali: f_ck = {f_ck:.0f} MPa, f_yk = {f_yk:.0f} MPa "
            f"(f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa)",
            "",
            "Sollecitazioni di calcolo:",
            f"  N_Ed = {N_Ed:.1f} kN ({'compressione' if N_Ed > 0 else 'trazione'})",
            f"  Mx_Ed = {Mx_Ed:.2f} kNm",
            f"  My_Ed = {My_Ed:.2f} kNm",
            "",
            "FLESSIONE DEVIATA — Formula di Bresler (NTC2018 / EC2 §5.8.9):",
            f"  Mx_Rd = {Mx_Rd:.2f} kNm (per N_Ed = {N_Ed:.1f} kN, asse x)",
            f"  My_Rd = {My_Rd:.2f} kNm (per N_Ed = {N_Ed:.1f} kN, asse y)",
            f"  N_Rd = {N_Rd_kN:.1f} kN, n = N_Ed/N_Rd = {n_rel:.3f}",
            f"  α = {alpha:.2f}",
            f"  (Mx/Mx_Rd)^α + (My/My_Rd)^α = {bresler:.3f} {'≤ 1.0 ✓ OK' if ok else '> 1.0 ✗ NON OK'}",
        ]

        if over_reinf:
            messages_it.append("")
            messages_it.append(
                f"  ⚠️ Sezione sovra-armata: x/d_x = {res_x['x_over_d']:.3f}, "
                f"x/d_y = {res_y['x_over_d']:.3f}"
            )

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=bresler,
            details={
                "N_Ed_kN": N_Ed,
                "Mx_Ed_kNm": Mx_Ed,
                "My_Ed_kNm": My_Ed,
                "Mx_Rd_kNm": Mx_Rd,
                "My_Rd_kNm": My_Rd,
                "N_Rd_kN": N_Rd_kN,
                "alpha_bresler": alpha,
                "bresler_value": bresler,
                "x_eq_x_mm": res_x["x_eq_mm"],
                "x_eq_y_mm": res_y["x_eq_mm"],
                "x_over_d_x": res_x["x_over_d"],
                "x_over_d_y": res_y["x_over_d"],
                "f_cd_MPa": f_cd,
                "f_yd_MPa": f_yd,
                "section_type": section_type,
                "over_reinforced": over_reinf,
                "biaxial": True,
            },
            norm_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="4.1",
                    paragraph="4.1.2.1.3.1",
                    formula_label="(4.1)",
                    description_it=(
                        "Verifica a presso/tenso-flessione deviata — "
                        "Formula di Bresler per interazione biassiale"
                    ),
                ),
                NormReference(
                    norm_code="EC2",
                    chapter="5.8",
                    paragraph="5.8.9",
                    description_it="Formula di interazione biassiale (Mx/Mx_Rd)^α + (My/My_Rd)^α ≤ 1",
                ),
            ],
            messages_it=messages_it,
        )

    else:
        # ---------------------------------------------------------------
        # FLESSIONE RETTA (uniassiale): N + Mx oppure N + My
        # ---------------------------------------------------------------
        if has_My and not has_Mx:
            axis = "y"
            M_Ed = abs(My_Ed)
        else:
            axis = "x"
            M_Ed = abs(Mx_Ed) if has_Mx else 0.0

        M_Ed_Nmm = M_Ed * 1e6
        res = _uniaxial_check(M_Ed, axis=axis)

        # Per compressione/trazione centrata (M=0), verifica N solo
        if M_Ed < 1e-6 and abs(N_Ed_N) >= 1.0:
            # Compressione o trazione centrata
            R_c_full, _ = compute_concrete_resultant(
                section, h / lambda_f, f_cd, axis="x", lambda_f=lambda_f
            )
            if N_Ed > 0:
                # Compressione centrata
                N_Rd_N = R_c_full + (As_mm2 + As_prime_mm2) * f_yd
                util = N_Ed_N / N_Rd_N if N_Rd_N > 0 else 999.0
                ok = util <= 1.0
                messages_it = [
                    f"Sezione: {section_type}, h = {h / 10:.1f} cm, b = {w / 10:.1f} cm",
                    f"Armatura: As = {As:.2f} cm², As' = {As_prime:.2f} cm²",
                    f"Materiali: f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa",
                    "",
                    "COMPRESSIONE CENTRATA:",
                    f"  N_Ed = {N_Ed:.1f} kN",
                    f"  N_Rd = {N_Rd_N / 1000:.1f} kN",
                    f"  Utilizzazione: {util:.3f} {'✓ OK' if ok else '✗ NON OK'}",
                ]
            else:
                # Trazione centrata
                N_Rd_t_N = (As_mm2 + As_prime_mm2) * f_yd
                util = abs(N_Ed_N) / N_Rd_t_N if N_Rd_t_N > 0 else 999.0
                ok = util <= 1.0
                messages_it = [
                    f"Sezione: {section_type}, h = {h / 10:.1f} cm, b = {w / 10:.1f} cm",
                    f"Armatura: As = {As:.2f} cm², As' = {As_prime:.2f} cm²",
                    f"Materiali: f_yd = {f_yd:.0f} MPa",
                    "",
                    "TRAZIONE CENTRATA:",
                    f"  N_Ed = {N_Ed:.1f} kN (trazione)",
                    f"  N_Rd,t = {N_Rd_t_N / 1000:.1f} kN",
                    f"  Utilizzazione: {util:.3f} {'✓ OK' if ok else '✗ NON OK'}",
                ]

            return SingleCheckResult(
                template_id=template.template_id,
                ok=ok,
                utilisation=util,
                details={
                    "N_Ed_kN": N_Ed,
                    "N_Rd_kN": (N_Rd_N if N_Ed > 0 else N_Rd_t_N) / 1000,
                    "f_cd_MPa": f_cd,
                    "f_yd_MPa": f_yd,
                    "section_type": section_type,
                },
                norm_references=[
                    NormReference(
                        norm_code="NTC2018",
                        chapter="4.1",
                        paragraph="4.1.2.1.3.1",
                        description_it="Verifica a compressione/trazione centrata",
                    ),
                ],
                messages_it=messages_it,
            )

        # Flessione retta (con o senza N)
        M_Rd_kNm = res["M_Rd_kNm"]
        x_eq = res["x_eq_mm"]
        x_over_d = res["x_over_d"]
        over_reinforced = res["over_reinforced"]
        utilisazione = res["utilisazione"]
        ok = res["ok"]

        # Tipo sollecitazione per messaggi
        if abs(N_Ed) < 0.01:
            tipo_soll = "FLESSIONE SEMPLICE"
        elif N_Ed > 0:
            tipo_soll = "PRESSO-FLESSIONE"
        else:
            tipo_soll = "TENSO-FLESSIONE"

        asse_label = "Mx" if axis == "x" else "My"

        messages_it = [
            f"Sezione: {section_type}, h = {h / 10:.1f} cm, b = {w / 10:.1f} cm",
            f"d = {d:.1f} cm, d' = {d_prime:.1f} cm",
            f"Armatura tesa: As = {As:.2f} cm², compressa: As' = {As_prime:.2f} cm²",
            f"Materiali: f_ck = {f_ck:.0f} MPa, f_yk = {f_yk:.0f} MPa "
            f"(f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa)",
            "",
            "Sollecitazioni di calcolo:",
            f"  N_Ed = {N_Ed:.1f} kN ({'compressione' if N_Ed >= 0 else 'trazione'})",
            f"  {asse_label}_Ed = {M_Ed:.2f} kNm",
            "",
            f"{tipo_soll} — Equilibrio sezione (NTC 2018 § 4.1.2.1.3.1):",
            f"  Asse neutro: x = {x_eq:.1f} mm (x/d = {x_over_d:.3f})",
        ]

        if res["messages"]:
            messages_it.extend(["  " + m for m in res["messages"]])

        if over_reinforced:
            messages_it.append(f"  ⚠️ x/d = {x_over_d:.3f} > 0.45: sezione sovra-armata")

        messages_it.extend([
            "",
            f"Momento resistente: {asse_label}_Rd = {M_Rd_kNm:.2f} kNm "
            f"(per N_Ed = {N_Ed:.1f} kN)",
            f"Momento agente: {asse_label}_Ed = {M_Ed:.2f} kNm",
            f"Utilizzazione: {utilisazione:.3f} {'✓ OK' if ok else '✗ NON OK'}",
        ])

        return SingleCheckResult(
            template_id=template.template_id,
            ok=ok,
            utilisation=utilisazione,
            details={
                "N_Ed_kN": N_Ed,
                "M_Ed_kNm": M_Ed,
                "M_Rd_kNm": M_Rd_kNm,
                "x_mm": x_eq,
                "x_over_d": x_over_d,
                "f_cd_MPa": f_cd,
                "f_yd_MPa": f_yd,
                "As_cm2": As,
                "As_prime_cm2": As_prime,
                "d_cm": d,
                "d_prime_cm": d_prime,
                "over_reinforced": over_reinforced,
                "section_type": section_type,
                "axis": axis,
                "biaxial": False,
            },
            norm_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="4.1",
                    paragraph="4.1.2.1.3.1",
                    formula_label="(4.1)",
                    description_it=(
                        f"Verifica a {tipo_soll.lower()} — "
                        f"sezione {section_type}"
                    ),
                ),
                NormReference(
                    norm_code="Circolare7",
                    chapter="C4.1",
                    paragraph="C4.1.2.1.3.1",
                    description_it="Istruzioni per verifica a pressoflessione",
                ),
            ],
            messages_it=messages_it,
        )


def check_minimi_armatura_flessione_slu(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
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
        f"Sezione: {b / 10:.1f} × {h / 10:.1f} cm, d = {d:.1f} cm"
        + (" (stimato)" if d_estimated else ""),
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f} (f_ctm = {f_ctm:.2f} MPa"
        + (" calcolato)" if f_ctm_computed else ")"),
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
        f"Sezione: {b / 10:.1f} × {h / 10:.1f} cm, d = {d:.1f} cm"
        + (" (stimato)" if d_estimated else ""),
        f"Materiali: C{f_ck:.0f}/{f_yk:.0f} (f_cd = {f_cd:.1f} MPa, f_yd = {f_yd:.0f} MPa)",
        f"Staffe: φ{phi_mm:.0f}/{staffe_passo:.0f}cm, {staffe_num_bracci} bracci",
        f"  Asw/s = {Asw_over_s:.4f} mm²/mm",
        "",
        "Calcolo V_Rd (NTC 2018 § 4.1.2.1.3.2):",
        f"  θ = {theta_deg:.1f}° (cotθ = {cot_theta:.2f})",
        f"  ν = 0.6*(1 - f_ck/250) = {nu:.3f}",
        f"  V_Rd,s (resistenza staffe) = {V_Rd_s / 1000:.1f} kN",
        f"  V_Rd,max (puntoni compressi) = {V_Rd_max / 1000:.1f} kN",
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
            messages_it=[
                "Diametro staffe mancante o non valido - impossibile verificare minimi armatura taglio"
            ],
        )

    if staffe_passo is None or staffe_passo <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=[
                "Passo staffe mancante o non valido - impossibile verificare minimi armatura taglio"
            ],
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
        f"Sezione: {b / 10:.1f} × {h / 10:.1f} cm",
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
        messages_it.append(
            f"⚠️ Armatura a taglio insufficiente: serve Asw/s ≥ {Asw_min_over_s:.4f} mm²/mm"
        )

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
