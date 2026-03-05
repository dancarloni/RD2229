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


def check_flessione_slu(
    calc_input: CalcInput, template: VerificationTemplate
) -> SingleCheckResult:
    """Verifica a flessione semplice SLU — NTC 2018 § 4.1.2.1.3.1.

    Generalizzata per QUALSIASI tipo di sezione. Delega a check_pressoflessione_slu
    imponendo N=0, sfruttando il fiber method per tutte le geometrie.

    Args:
        calc_input: Dati di input (Mx, My, sezione, materiale, armatura)
        template: Template della verifica

    Returns:
        Risultato della verifica a flessione semplice
    """
    import dataclasses

    # Forza N=0 per flessione semplice (ignora eventuale N nel calc_input)
    ci_flessione = dataclasses.replace(calc_input, N=0.0)
    return check_pressoflessione_slu(ci_flessione, template)


# Alias per retrocompatibilità
check_flessione_slu_rett = check_flessione_slu


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
    """Verifica minimi di armatura a flessione SLU — NTC 2018 § 4.1.6.1.1.

    Generalizzata per qualsiasi tipo di sezione.
    Formula: As,min = max(0.26 * f_ctm / f_yk * b * d, 0.0013 * b * d)
    dove b = larghezza anima (b_w) per sezioni a T/I/C.

    Args:
        calc_input: Dati di input
        template: Template della verifica

    Returns:
        Risultato della verifica
    """
    from src.methods.section_fiber import get_section_height, get_web_width

    if calc_input.section is None or calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione o materiale non specificati"],
        )

    # Get geometry from any section type
    section = calc_input.section
    try:
        h = get_section_height(section)
        b = get_web_width(section)  # b_w per sezioni a T/I
    except ValueError:
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
    """Verifica a taglio SLU — NTC 2018 § 4.1.2.1.3.2.

    Generalizzata per qualsiasi tipo di sezione.
    V_Rd = min(V_Rd,s, V_Rd,max) con b = b_w (larghezza anima).

    Args:
        calc_input: Dati di input
        template: Template della verifica

    Returns:
        Risultato della verifica
    """
    from src.methods.section_fiber import get_section_height, get_web_width

    # Check required inputs
    if calc_input.section is None or calc_input.material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Sezione o materiale non specificati"],
        )

    # Get geometry from any section type
    section = calc_input.section
    try:
        h = get_section_height(section)
        b = get_web_width(section)  # b_w per taglio
    except ValueError:
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
    """Verifica minimi armatura a taglio — NTC 2018 § 4.1.6.1.1.

    Generalizzata per qualsiasi tipo di sezione.
    Formula: Asw,min/s = 0.08 * sqrt(f_ck) / f_yk * b_w

    Args:
        calc_input: Input data with section, material, stirrups data
        template: Template definition
        adjusted_material: Material properties after LC/FC adjustments (optional)

    Returns:
        SingleCheckResult with ok/non-ok
    """
    from src.methods.section_fiber import get_section_height, get_web_width

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

    try:
        b = get_web_width(section)
        h = get_section_height(section)
    except ValueError:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={},
            messages_it=["Geometria sezione non disponibile per verifica minimi armatura taglio"],
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


# ===========================================================================
# Torsione SLU — NTC 2018 § 4.1.2.1.5 / EC2 § 6.3
# ===========================================================================

def check_torsione_slu(
    calc_input: CalcInput,
    template: VerificationTemplate,
    adjusted_material: AdjustedMaterialProperties | None = None,
) -> SingleCheckResult:
    """Verifica a torsione SLU — NTC 2018 § 4.1.2.1.5.

    Modello a traliccio thin-walled (EC2 § 6.3):
    - T_Rd,max = 2 · ν · A_k · t_ef · f_cd · sinθ · cosθ
    - T_Rd,s  = 2 · A_k · (A_sw/s) · f_ywd · cotθ

    Interazione taglio-torsione (EC2 eq. 6.29):
    T_Ed/T_Rd,max + V_Ed/V_Rd,max ≤ 1.0

    Generalizzata per qualsiasi tipo di sezione.
    """
    from src.methods.section_fiber import (
        compute_torsion_properties,
        get_section_height,
        get_web_width,
    )

    section = calc_input.section
    if section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Sezione non specificata per verifica torsione"],
        )

    material = calc_input.material
    if material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Materiale non specificato per verifica torsione"],
        )

    # Momento torcente
    Mz = calc_input.Mz or 0.0
    T_Ed = abs(Mz)  # kNm

    if T_Ed < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True, utilisation=0.0,
            details={"T_Ed_kNm": 0.0, "interaction": "nessuna"},
            messages_it=["Momento torcente nullo: verifica non necessaria."],
        )

    # Material properties
    if adjusted_material is not None:
        f_ck = adjusted_material.f_ck_adjusted
        f_yk = adjusted_material.f_yk_adjusted
    else:
        f_ck = getattr(material, "f_ck", None)
        f_yk = getattr(material, "f_yk", None)

    if not f_ck or f_ck <= 0 or not f_yk or f_yk <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Resistenze materiale non valide per verifica torsione"],
        )

    gamma_c = 1.5
    gamma_s = 1.15
    f_cd = 0.85 * f_ck / gamma_c  # MPa
    f_ywd = f_yk / gamma_s  # MPa

    # Torsion section properties
    try:
        A_k, u_k, t_ef = compute_torsion_properties(section)
    except (ValueError, AttributeError):
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Impossibile calcolare proprietà torsionali della sezione"],
        )

    if A_k <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Area nucleo torsionale A_k ≤ 0"],
        )

    # Strut angle θ (conservative: θ = 21.8° → cotθ = 2.5)
    theta_deg = 21.8
    theta = math.radians(theta_deg)
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)
    cot_t = cos_t / sin_t

    # ν coefficient
    nu = 0.6 * (1.0 - f_ck / 250.0)

    # T_Rd,max — resistenza puntone compresso
    # T_Rd,max = 2 · ν · A_k · t_ef · f_cd · sinθ · cosθ
    T_Rd_max_Nmm = 2.0 * nu * A_k * t_ef * f_cd * sin_t * cos_t
    T_Rd_max_kNm = T_Rd_max_Nmm / 1e6

    # T_Rd,s — resistenza armature trasversali a torsione
    # T_Rd,s = 2 · A_k · (A_sw/s) · f_ywd · cotθ
    staffe_diametro = calc_input.staffe_diametro or 0.0  # mm
    staffe_passo = calc_input.staffe_passo or 0.0  # cm
    staffe_num_bracci = calc_input.staffe_num_bracci or 2

    if staffe_diametro > 0 and staffe_passo > 0:
        s_mm = staffe_passo * 10.0  # cm → mm
        # Per torsione: un solo braccio della staffa contribuisce (non tutti)
        A_sw_torsion = math.pi * (staffe_diametro ** 2) / 4.0  # mm² (1 braccio)
        Asw_over_s = A_sw_torsion / s_mm  # mm²/mm
        T_Rd_s_Nmm = 2.0 * A_k * Asw_over_s * f_ywd * cot_t
        T_Rd_s_kNm = T_Rd_s_Nmm / 1e6
    else:
        T_Rd_s_kNm = 0.0

    T_Rd_kNm = min(T_Rd_max_kNm, T_Rd_s_kNm) if T_Rd_s_kNm > 0 else T_Rd_max_kNm

    # Interazione taglio-torsione
    Tx = calc_input.Tx or 0.0
    V_Ed = abs(Tx)  # kN
    interaction_ratio = 0.0
    has_interaction = V_Ed > 1e-6

    if has_interaction:
        # Calcolo V_Rd,max per interazione
        try:
            b_w = get_web_width(section)
            h_sec = get_section_height(section)
        except ValueError:
            b_w = 0.0
            h_sec = 0.0
        d_mm = (calc_input.d or 0.9 * h_sec / 10.0) * 10.0
        if d_mm <= 0 and h_sec > 0:
            d_mm = 0.9 * h_sec
        z = 0.9 * d_mm

        V_Rd_max_N = b_w * z * nu * f_cd * sin_t * cos_t if (b_w > 0 and z > 0) else 1e30
        V_Rd_max_kN = V_Rd_max_N / 1e3

        # EC2 eq. 6.29: T_Ed/T_Rd,max + V_Ed/V_Rd,max ≤ 1.0
        ratio_T = T_Ed / T_Rd_max_kNm if T_Rd_max_kNm > 0 else 999.0
        ratio_V = V_Ed / V_Rd_max_kN if V_Rd_max_kN > 0 else 0.0
        interaction_ratio = ratio_T + ratio_V
    else:
        V_Rd_max_kN = 0.0

    # Utilizzazione
    util_T = T_Ed / T_Rd_kNm if T_Rd_kNm > 0 else 999.0
    utilisazione = max(util_T, interaction_ratio) if has_interaction else util_T
    ok = utilisazione <= 1.0

    messages_it = [
        "VERIFICA A TORSIONE SLU — NTC 2018 § 4.1.2.1.5",
        f"Sezione: tipo {getattr(section, 'section_type', '?')}",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa",
        "",
        f"Proprietà torsionali:",
        f"  A_k = {A_k:.0f} mm²  (area nucleo)",
        f"  u_k = {u_k:.0f} mm   (perimetro nucleo)",
        f"  t_ef = {t_ef:.1f} mm  (spessore efficace)",
        "",
        f"T_Ed = {T_Ed:.2f} kNm",
        f"T_Rd,max = {T_Rd_max_kNm:.2f} kNm  (puntone compresso, θ={theta_deg}°)",
    ]

    if T_Rd_s_kNm > 0:
        messages_it.append(
            f"T_Rd,s = {T_Rd_s_kNm:.2f} kNm  (armature, φ{staffe_diametro:.0f}/{staffe_passo:.0f}cm)"
        )
    messages_it.append(f"T_Rd = {T_Rd_kNm:.2f} kNm")

    if has_interaction:
        messages_it.extend([
            "",
            "Interazione taglio-torsione (EC2 eq. 6.29):",
            f"  T_Ed/T_Rd,max + V_Ed/V_Rd,max = {interaction_ratio:.3f}",
        ])

    messages_it.extend([
        "",
        f"Utilizzazione: {utilisazione:.3f} {'OK' if ok else 'NON OK'}",
    ])

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilisazione,
        details={
            "T_Ed_kNm": T_Ed,
            "T_Rd_kNm": T_Rd_kNm,
            "T_Rd_max_kNm": T_Rd_max_kNm,
            "T_Rd_s_kNm": T_Rd_s_kNm,
            "A_k_mm2": A_k,
            "u_k_mm": u_k,
            "t_ef_mm": t_ef,
            "theta_deg": theta_deg,
            "interaction_ratio": interaction_ratio,
            "has_interaction": has_interaction,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018", chapter="4.1", paragraph="4.1.2.1.5",
                formula_label="EC2 (6.26)-(6.29)",
                description_it="Verifica a torsione con modello a traliccio thin-walled",
            ),
        ],
        messages_it=messages_it,
    )


# ===========================================================================
# Tensioni SLE — NTC 2018 § 4.1.2.2.5
# ===========================================================================

def check_tensioni_sle(
    calc_input: CalcInput,
    template: VerificationTemplate,
    adjusted_material: AdjustedMaterialProperties | None = None,
) -> SingleCheckResult:
    """Verifica tensioni in esercizio SLE — NTC 2018 § 4.1.2.2.5.

    Limiti tensioni normali in esercizio:
    - σ_c ≤ 0.60 · f_ck  (combinazione caratteristica)
    - σ_c ≤ 0.45 · f_ck  (combinazione quasi-permanente)
    - σ_s ≤ 0.80 · f_yk  (combinazione caratteristica)

    Calcolo tensioni con metodo n-trasformata (sezione fessurata).
    Generalizzata per qualsiasi tipo di sezione.
    """
    from src.methods.section_fiber import get_section_height, get_web_width

    section = calc_input.section
    if section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Sezione non specificata per verifica tensioni SLE"],
        )

    material = calc_input.material
    if material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Materiale non specificato per verifica tensioni SLE"],
        )

    # Material properties
    if adjusted_material is not None:
        f_ck = adjusted_material.f_ck_adjusted
        f_yk = adjusted_material.f_yk_adjusted
    else:
        f_ck = getattr(material, "f_ck", None)
        f_yk = getattr(material, "f_yk", None)

    if not f_ck or f_ck <= 0 or not f_yk or f_yk <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Resistenze materiale non valide per verifica tensioni SLE"],
        )

    # Geometry
    try:
        h_mm = get_section_height(section)
        b_w_mm = get_web_width(section)
    except ValueError:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Geometria sezione non disponibile per verifica tensioni SLE"],
        )

    d_cm = calc_input.d or (0.9 * h_mm / 10.0)
    d_mm = d_cm * 10.0
    As_cm2 = calc_input.As or 0.0
    As_mm2 = As_cm2 * 100.0
    As_prime_cm2 = calc_input.As_prime or 0.0
    As_prime_mm2 = As_prime_cm2 * 100.0
    d_prime_cm = calc_input.d_prime or 4.0
    d_prime_mm = d_prime_cm * 10.0

    # Solicitations (esercizio = valori caratteristici, non fattorizzati)
    M_Ed_kNm = abs(calc_input.Mx or 0.0)
    N_Ed_kN = calc_input.N or 0.0
    M_Ed_Nmm = M_Ed_kNm * 1e6
    N_Ed_N = N_Ed_kN * 1e3

    if M_Ed_kNm < 1e-6 and abs(N_Ed_kN) < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True, utilisation=0.0,
            details={"sigma_c_MPa": 0.0, "sigma_s_MPa": 0.0},
            messages_it=["Sollecitazioni nulle: verifica non necessaria."],
        )

    # Modular ratio
    E_s = 200000.0  # MPa
    E_cm = 22000.0 * (f_ck / 10.0) ** 0.3  # EC2 Table 3.1
    n = E_s / E_cm

    # Calcolo asse neutro sezione fessurata (metodo semplificato)
    # Per sezione con anima b_w e armature As, As':
    # b_w · x²/2 + n·As'·(x - d') = n·As·(d - x)
    # b_w · x²/2 + (n·As' + n·As)·x = n·As·d + n·As'·d'
    b = b_w_mm
    a_coeff = b / 2.0
    b_coeff = n * (As_mm2 + As_prime_mm2)
    c_coeff = -(n * As_mm2 * d_mm + n * As_prime_mm2 * d_prime_mm)

    disc = b_coeff ** 2 - 4.0 * a_coeff * c_coeff
    if disc < 0 or a_coeff <= 0:
        x_cr = d_mm * 0.4  # fallback
    else:
        x_cr = (-b_coeff + math.sqrt(disc)) / (2.0 * a_coeff)
        x_cr = max(0.0, min(x_cr, d_mm))

    # Momento d'inerzia sezione fessurata
    I_cr = (b * x_cr ** 3 / 3.0
            + n * As_mm2 * (d_mm - x_cr) ** 2
            + n * As_prime_mm2 * (x_cr - d_prime_mm) ** 2)

    if I_cr <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Inerzia sezione fessurata non calcolabile"],
        )

    # Eccentricità per N
    M_tot_Nmm = M_Ed_Nmm
    if abs(N_Ed_N) > 1e-3:
        # Momento totale rispetto al baricentro armatura tesa
        e_mm = M_Ed_Nmm / N_Ed_N if abs(N_Ed_N) > 1e-3 else 0.0
        # Semplificazione: somma momento + N·(d - h/2)
        M_tot_Nmm = M_Ed_Nmm + N_Ed_N * (d_mm - h_mm / 2.0)

    # Tensioni
    sigma_c = abs(M_tot_Nmm) * x_cr / I_cr  # MPa (compressione al lembo)
    sigma_s = n * abs(M_tot_Nmm) * (d_mm - x_cr) / I_cr  # MPa (trazione armatura)

    # Se c'è compressione centrata, aggiungi contributo diretto
    if N_Ed_N > 0:
        A_cr = b * x_cr + n * As_mm2 + n * As_prime_mm2  # area trasformata approssimata
        if A_cr > 0:
            sigma_c += N_Ed_N / A_cr

    # Limiti NTC2018 § 4.1.2.2.5
    sigma_c_lim_car = 0.60 * f_ck  # combinazione caratteristica
    sigma_c_lim_qp = 0.45 * f_ck   # combinazione quasi-permanente
    sigma_s_lim = 0.80 * f_yk       # acciaio

    # Combinazione: usa caratteristica come default (conservativa)
    combo = calc_input.extra.get("combinazione_sle", "caratteristica")
    sigma_c_lim = sigma_c_lim_qp if combo == "quasi_permanente" else sigma_c_lim_car

    ok_c = sigma_c <= sigma_c_lim
    ok_s = sigma_s <= sigma_s_lim
    ok = ok_c and ok_s

    util_c = sigma_c / sigma_c_lim if sigma_c_lim > 0 else 0.0
    util_s = sigma_s / sigma_s_lim if sigma_s_lim > 0 else 0.0
    utilisazione = max(util_c, util_s)

    messages_it = [
        "VERIFICA TENSIONI IN ESERCIZIO SLE — NTC 2018 § 4.1.2.2.5",
        f"Sezione: tipo {getattr(section, 'section_type', '?')}",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa, n={n:.1f}",
        f"Combinazione: {combo}",
        "",
        f"M_Ed = {M_Ed_kNm:.2f} kNm, N_Ed = {N_Ed_kN:.2f} kN",
        f"d = {d_cm:.1f} cm, As = {As_cm2:.2f} cm², As' = {As_prime_cm2:.2f} cm²",
        "",
        f"Asse neutro fessurato: x = {x_cr:.1f} mm",
        "",
        f"Tensione cls:    σ_c = {sigma_c:.2f} MPa  ≤  {sigma_c_lim:.2f} MPa  "
        f"{'OK' if ok_c else 'NON OK'}",
        f"Tensione acciaio: σ_s = {sigma_s:.2f} MPa  ≤  {sigma_s_lim:.2f} MPa  "
        f"{'OK' if ok_s else 'NON OK'}",
        "",
        f"Utilizzazione: {utilisazione:.3f} {'OK' if ok else 'NON OK'}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilisazione,
        details={
            "sigma_c_MPa": round(sigma_c, 2),
            "sigma_s_MPa": round(sigma_s, 2),
            "sigma_c_lim_MPa": sigma_c_lim,
            "sigma_s_lim_MPa": sigma_s_lim,
            "x_cr_mm": round(x_cr, 1),
            "n_modular": round(n, 2),
            "I_cr_mm4": round(I_cr, 0),
            "combinazione": combo,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018", chapter="4.1", paragraph="4.1.2.2.5",
                description_it="Limiti tensioni in esercizio: σ_c ≤ 0.60·f_ck, σ_s ≤ 0.80·f_yk",
            ),
        ],
        messages_it=messages_it,
    )


# ===========================================================================
# Fessurazione SLE — NTC 2018 § 4.1.2.2.4 / EC2 § 7.3
# ===========================================================================

def check_fessurazione_sle(
    calc_input: CalcInput,
    template: VerificationTemplate,
    adjusted_material: AdjustedMaterialProperties | None = None,
) -> SingleCheckResult:
    """Verifica fessurazione SLE — NTC 2018 § 4.1.2.2.4.

    Calcolo ampiezza fessure w_k e confronto con w_amm.

    EC2 § 7.3.4:
    w_k = s_r,max · (ε_sm - ε_cm)

    dove:
    s_r,max = 3.4·c + 0.425·k1·k2·φ/ρ_p,eff
    ε_sm - ε_cm = [σ_s - kt·f_ct,eff/ρ_p,eff·(1+αe·ρ_p,eff)] / E_s ≥ 0.6·σ_s/E_s

    Generalizzata per qualsiasi tipo di sezione.
    """
    from src.methods.section_fiber import get_section_height, get_web_width

    section = calc_input.section
    if section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Sezione non specificata per verifica fessurazione"],
        )

    material = calc_input.material
    if material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Materiale non specificato per verifica fessurazione"],
        )

    # Material properties
    if adjusted_material is not None:
        f_ck = adjusted_material.f_ck_adjusted
        f_yk = adjusted_material.f_yk_adjusted
    else:
        f_ck = getattr(material, "f_ck", None)
        f_yk = getattr(material, "f_yk", None)

    if not f_ck or f_ck <= 0 or not f_yk or f_yk <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Resistenze materiale non valide per verifica fessurazione"],
        )

    # Geometry
    try:
        h_mm = get_section_height(section)
        b_w_mm = get_web_width(section)
    except ValueError:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Geometria sezione non disponibile per verifica fessurazione"],
        )

    d_cm = calc_input.d or (0.9 * h_mm / 10.0)
    d_mm = d_cm * 10.0
    As_cm2 = calc_input.As or 0.0
    As_mm2 = As_cm2 * 100.0

    if As_mm2 <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Armatura As non specificata per verifica fessurazione"],
        )

    # Solicitations
    M_Ed_kNm = abs(calc_input.Mx or 0.0)
    if M_Ed_kNm < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True, utilisation=0.0,
            details={"w_k_mm": 0.0},
            messages_it=["Sollecitazione nulla: verifica fessurazione non necessaria."],
        )

    # Material derived
    E_s = 200000.0  # MPa
    E_cm = 22000.0 * (f_ck / 10.0) ** 0.3
    n = E_s / E_cm
    f_ctm = 0.30 * f_ck ** (2.0 / 3.0) if f_ck <= 50 else 2.12 * math.log(1 + f_ck / 10.0)
    f_ct_eff = f_ctm  # per fessurazione

    # Copriferro netto e diametro barre
    c_nom_mm = calc_input.extra.get("copriferro_mm", 30.0)
    phi_long_mm = calc_input.extra.get("phi_long_mm", 16.0)

    # Asse neutro fessurato (semplificato)
    b = b_w_mm
    a_c = b / 2.0
    b_c = n * As_mm2
    c_c = -n * As_mm2 * d_mm
    disc = b_c ** 2 - 4.0 * a_c * c_c
    x_cr = (-b_c + math.sqrt(max(disc, 0.0))) / (2.0 * a_c) if a_c > 0 else d_mm * 0.4
    x_cr = max(0.0, min(x_cr, d_mm))

    # Inerzia fessurata e tensione acciaio
    I_cr = b * x_cr ** 3 / 3.0 + n * As_mm2 * (d_mm - x_cr) ** 2
    M_Ed_Nmm = M_Ed_kNm * 1e6
    sigma_s = n * M_Ed_Nmm * (d_mm - x_cr) / I_cr if I_cr > 0 else 0.0

    # Altezza efficace della zona tesa
    h_c_eff = min(2.5 * (h_mm - d_mm), (h_mm - x_cr) / 3.0, h_mm / 2.0)
    h_c_eff = max(h_c_eff, 0.0)
    A_c_eff = b * h_c_eff  # mm²
    rho_p_eff = As_mm2 / A_c_eff if A_c_eff > 0 else 0.01

    # Coefficienti EC2 § 7.3.4
    k1 = 0.8  # barre ad aderenza migliorata
    k2 = 0.5  # flessione
    kt = 0.4  # lungo termine (quasi-permanente); 0.6 per breve termine
    combo = calc_input.extra.get("combinazione_sle", "quasi_permanente")
    if combo == "frequente":
        kt = 0.6

    alpha_e = n

    # s_r,max — distanza massima tra fessure
    s_r_max = 3.4 * c_nom_mm + 0.425 * k1 * k2 * phi_long_mm / rho_p_eff

    # ε_sm - ε_cm
    eps_diff = (sigma_s - kt * f_ct_eff / rho_p_eff * (1 + alpha_e * rho_p_eff)) / E_s
    eps_min = 0.6 * sigma_s / E_s
    eps_diff = max(eps_diff, eps_min)

    # w_k
    w_k = s_r_max * eps_diff  # mm

    # Limite ammissibile
    w_amm = calc_input.extra.get("w_amm_mm", 0.3)  # default 0.3 mm

    ok = w_k <= w_amm
    utilisazione = w_k / w_amm if w_amm > 0 else 999.0

    messages_it = [
        "VERIFICA FESSURAZIONE SLE — NTC 2018 § 4.1.2.2.4 / EC2 § 7.3",
        f"Sezione: tipo {getattr(section, 'section_type', '?')}",
        f"Materiali: f_ck={f_ck:.0f} MPa, f_yk={f_yk:.0f} MPa",
        f"Copriferro: c={c_nom_mm:.0f} mm, φ_long={phi_long_mm:.0f} mm",
        f"Combinazione: {combo} (kt={kt})",
        "",
        f"M_Ed = {M_Ed_kNm:.2f} kNm",
        f"σ_s = {sigma_s:.1f} MPa  (tensione acciaio in esercizio)",
        "",
        f"h_c,eff = {h_c_eff:.1f} mm, ρ_p,eff = {rho_p_eff:.4f}",
        f"s_r,max = {s_r_max:.1f} mm",
        f"ε_sm - ε_cm = {eps_diff:.6f}",
        "",
        f"w_k = {w_k:.3f} mm  ≤  w_amm = {w_amm:.2f} mm  {'OK' if ok else 'NON OK'}",
        f"Utilizzazione: {utilisazione:.3f}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilisazione,
        details={
            "w_k_mm": round(w_k, 3),
            "w_amm_mm": w_amm,
            "sigma_s_MPa": round(sigma_s, 1),
            "s_r_max_mm": round(s_r_max, 1),
            "eps_diff": round(eps_diff, 6),
            "h_c_eff_mm": round(h_c_eff, 1),
            "rho_p_eff": round(rho_p_eff, 5),
            "x_cr_mm": round(x_cr, 1),
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018", chapter="4.1", paragraph="4.1.2.2.4",
                formula_label="EC2 (7.8)-(7.11)",
                description_it="Verifica ampiezza fessure: w_k = s_r,max · (ε_sm - ε_cm)",
            ),
        ],
        messages_it=messages_it,
    )


# ===========================================================================
# Deformazioni SLE — NTC 2018 § 4.1.2.2.2 / EC2 § 7.4
# ===========================================================================

def check_deformazioni_sle(
    calc_input: CalcInput,
    template: VerificationTemplate,
    adjusted_material: AdjustedMaterialProperties | None = None,
) -> SingleCheckResult:
    """Verifica deformazioni SLE — NTC 2018 § 4.1.2.2.2.

    Calcolo freccia con metodo della rigidezza interpolata (EC2 § 7.4.3):
    1/r = ζ · 1/r_II + (1-ζ) · 1/r_I

    dove ζ = 1 - β · (M_cr / M_Ed)²  (coefficiente di distribuzione)

    Limite: δ ≤ L / 250 (aspetto) o L / 500 (danni elementi non strutturali)

    Richiede luce della trave in CalcInput.extra["span_mm"].
    Generalizzata per qualsiasi tipo di sezione.
    """
    from src.methods.section_fiber import get_section_height, get_web_width

    section = calc_input.section
    if section is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Sezione non specificata per verifica deformazioni"],
        )

    material = calc_input.material
    if material is None:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Materiale non specificato per verifica deformazioni"],
        )

    # Luce trave
    span_mm = calc_input.extra.get("span_mm", None)
    if span_mm is None or span_mm <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Luce trave (span_mm) non specificata in CalcInput.extra"],
        )

    # Material properties
    if adjusted_material is not None:
        f_ck = adjusted_material.f_ck_adjusted
        f_yk = adjusted_material.f_yk_adjusted
    else:
        f_ck = getattr(material, "f_ck", None)
        f_yk = getattr(material, "f_yk", None)

    if not f_ck or f_ck <= 0:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["f_ck non valido per verifica deformazioni"],
        )

    # Geometry
    try:
        h_mm = get_section_height(section)
        b_w_mm = get_web_width(section)
    except ValueError:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False, utilisation=None, details={},
            messages_it=["Geometria sezione non disponibile per verifica deformazioni"],
        )

    d_cm = calc_input.d or (0.9 * h_mm / 10.0)
    d_mm = d_cm * 10.0
    As_cm2 = calc_input.As or 0.0
    As_mm2 = As_cm2 * 100.0
    As_prime_cm2 = calc_input.As_prime or 0.0
    As_prime_mm2 = As_prime_cm2 * 100.0
    d_prime_mm = (calc_input.d_prime or 4.0) * 10.0

    # Solicitations
    M_Ed_kNm = abs(calc_input.Mx or 0.0)
    M_Ed_Nmm = M_Ed_kNm * 1e6

    if M_Ed_kNm < 1e-6:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=True, utilisation=0.0,
            details={"delta_mm": 0.0},
            messages_it=["Sollecitazione nulla: verifica deformazioni non necessaria."],
        )

    # Material derived
    E_s = 200000.0
    E_cm = 22000.0 * (f_ck / 10.0) ** 0.3
    n = E_s / E_cm
    f_ctm = 0.30 * f_ck ** (2.0 / 3.0) if f_ck <= 50 else 2.12 * math.log(1 + f_ck / 10.0)

    b = b_w_mm

    # Inerzia sezione integra (stadio I)
    # Approssimazione: sezione rettangolare equivalente b × h
    I_I = b * h_mm ** 3 / 12.0 + n * As_mm2 * (d_mm - h_mm / 2.0) ** 2
    if As_prime_mm2 > 0:
        I_I += n * As_prime_mm2 * (h_mm / 2.0 - d_prime_mm) ** 2

    # Momento di fessurazione
    W_I = I_I / (h_mm / 2.0) if h_mm > 0 else 1.0
    M_cr_Nmm = f_ctm * W_I
    M_cr_kNm = M_cr_Nmm / 1e6

    # Inerzia sezione fessurata (stadio II)
    a_c = b / 2.0
    b_c = n * (As_mm2 + As_prime_mm2)
    c_c = -(n * As_mm2 * d_mm + n * As_prime_mm2 * d_prime_mm)
    disc = b_c ** 2 - 4.0 * a_c * c_c
    x_cr = (-b_c + math.sqrt(max(disc, 0.0))) / (2.0 * a_c) if a_c > 0 else d_mm * 0.4
    x_cr = max(0.0, min(x_cr, d_mm))

    I_II = (b * x_cr ** 3 / 3.0
            + n * As_mm2 * (d_mm - x_cr) ** 2
            + n * As_prime_mm2 * (x_cr - d_prime_mm) ** 2)

    # Coefficiente di distribuzione (EC2 eq. 7.19)
    beta = 1.0  # carico di lunga durata (0.5 per breve durata)
    combo = calc_input.extra.get("combinazione_sle", "quasi_permanente")
    if combo == "caratteristica":
        beta = 0.5

    if M_Ed_Nmm > M_cr_Nmm:
        zeta = 1.0 - beta * (M_cr_Nmm / M_Ed_Nmm) ** 2
        zeta = max(0.0, min(zeta, 1.0))
    else:
        zeta = 0.0  # sezione non fessurata

    # Rigidezza interpolata
    # 1/r = ζ · M/(E·I_II) + (1-ζ) · M/(E·I_I)
    if I_I > 0 and I_II > 0:
        curv_I = M_Ed_Nmm / (E_cm * I_I)
        curv_II = M_Ed_Nmm / (E_cm * I_II)
        curv = zeta * curv_II + (1.0 - zeta) * curv_I
    else:
        curv = M_Ed_Nmm / (E_cm * max(I_I, I_II, 1.0))

    # Freccia per trave semplicemente appoggiata: δ = 5/48 · 1/r · L²
    # (per carico uniforme equivalente)
    k_defl = calc_input.extra.get("k_deflection", 5.0 / 48.0)
    delta_mm = k_defl * curv * span_mm ** 2

    # Creep: amplificazione
    phi_creep = calc_input.extra.get("phi_creep", 2.0)  # EC2 default ≈ 2.0
    delta_mm *= (1.0 + phi_creep)

    # Limite
    limit_ratio = calc_input.extra.get("deflection_limit_ratio", 250.0)
    delta_amm_mm = span_mm / limit_ratio

    ok = delta_mm <= delta_amm_mm
    utilisazione = delta_mm / delta_amm_mm if delta_amm_mm > 0 else 999.0

    messages_it = [
        "VERIFICA DEFORMAZIONI SLE — NTC 2018 § 4.1.2.2.2 / EC2 § 7.4",
        f"Sezione: tipo {getattr(section, 'section_type', '?')}",
        f"Materiali: f_ck={f_ck:.0f} MPa, E_cm={E_cm:.0f} MPa",
        f"Luce: L = {span_mm:.0f} mm ({span_mm / 1000:.2f} m)",
        f"Combinazione: {combo} (β={beta})",
        "",
        f"M_Ed = {M_Ed_kNm:.2f} kNm",
        f"M_cr = {M_cr_kNm:.2f} kNm",
        f"ζ = {zeta:.3f}  (coefficiente distribuzione)",
        "",
        f"I_I = {I_I:.0f} mm⁴  (sezione integra)",
        f"I_II = {I_II:.0f} mm⁴  (sezione fessurata)",
        f"φ_creep = {phi_creep:.1f}",
        "",
        f"Freccia: δ = {delta_mm:.2f} mm  ≤  L/{limit_ratio:.0f} = {delta_amm_mm:.2f} mm  "
        f"{'OK' if ok else 'NON OK'}",
        f"Utilizzazione: {utilisazione:.3f}",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=ok,
        utilisation=utilisazione,
        details={
            "delta_mm": round(delta_mm, 2),
            "delta_amm_mm": round(delta_amm_mm, 2),
            "M_cr_kNm": round(M_cr_kNm, 2),
            "I_I_mm4": round(I_I, 0),
            "I_II_mm4": round(I_II, 0),
            "zeta": round(zeta, 3),
            "phi_creep": phi_creep,
            "span_mm": span_mm,
            "limit_ratio": limit_ratio,
        },
        norm_references=[
            NormReference(
                norm_code="NTC2018", chapter="4.1", paragraph="4.1.2.2.2",
                formula_label="EC2 (7.18)-(7.19)",
                description_it="Verifica frecce con rigidezza interpolata",
            ),
        ],
        messages_it=messages_it,
    )
