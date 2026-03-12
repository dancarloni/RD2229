"""
Normative templates registry.

Provides templates for verification checks across different norms:
- RD 2229/39
- DM 14/02/1992, DM 9/1/1996
- NTC 2008
- NTC 2018
- EC2

Each template defines:
- Which check to run
- Which norm paragraph it comes from
- Which function implements it
- Applicability criteria

Future: Load from JSON/CSV for easier configuration.
"""

from __future__ import annotations

from src.core_calculus.contracts import NormReference, VerificationTemplate


def get_all_templates() -> list[VerificationTemplate]:
    """Get all available verification templates.

    Returns:
        List of all templates across all norms
    """
    return [
        *get_ntc2018_templates(),
        *get_rd2229_templates(),
        *get_dm96_templates(),
        *get_fire_templates(),
        # Future: *get_ntc2008_templates(),
        # Future: *get_ec2_templates(),
    ]


def get_templates_for_norm(norm_code: str) -> list[VerificationTemplate]:
    """Get templates for a specific norm.

    Args:
        norm_code: Norm code (e.g., "NTC2018", "RD2229")

    Returns:
        List of templates for that norm
    """
    all_templates = get_all_templates()
    return [t for t in all_templates if t.norm_code == norm_code]


def get_ntc2018_templates() -> list[VerificationTemplate]:
    """Get NTC 2018 templates.

    Currently PARTIAL implementation:
    - Flessione semplice SLU (simplified)
    - Minimi armatura flessione
    - Taglio (placeholder only)

    TODO: Complete implementation for all check families per NTC 2018.
    """
    return [
        # Flessione semplice SLU
        VerificationTemplate(
            template_id="ntc2018_slu_flessione_rett",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="flessione",
            limit_state="SLU",
            description_it="Verifica a flessione semplice SLU — qualsiasi tipo di sezione",
            check_category="resistenza",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=["M_Ed_kNm", "M_Rd_kNm", "x_mm", "x_over_d", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.1",
                formula_label="(4.1)",
                description_it="Verifica a flessione semplice e composta — qualsiasi tipo di sezione",
                notes_it=(
                    "Implementazione completa con calcolo asse neutro per sezioni semplicemente e "
                    "doppiamente armate. Stress block rettangolare λ=0.8, η=1.0."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="4.1",
                    paragraph="4.1.2.1.2",
                    description_it="Parametri stress block rettangolare",
                )
            ],
            function_path="src.methods.ntc2018.checks.check_flessione_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Minimi armatura flessione
        VerificationTemplate(
            template_id="ntc2018_slu_minimi_armatura_fless",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="minimi_armatura",
            limit_state="SLU",
            description_it="Verifica minimi di armatura a flessione",
            check_category="minimi_armatura",
            required_inputs=["section", "material", "As"],
            optional_inputs=["d"],
            output_metrics=[
                "As_min_cm2",
                "As_min_1_cm2",
                "As_min_2_cm2",
                "f_ctm_MPa",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.6.1.1",
                description_it="Armature longitudinali minime",
                notes_it=(
                    "Implementazione completa formula NTC 2018: As,min = max(0.26*f_ctm/f_yk*b*d, "
                    "0.0013*b*d). f_ctm calcolato automaticamente se non disponibile."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="C4.1",
                    paragraph="Tabella C4.1.IV",
                    description_it="Formula per f_ctm in funzione di f_ck",
                )
            ],
            function_path="src.methods.ntc2018.checks.check_minimi_armatura_flessione_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Taglio SLU
        VerificationTemplate(
            template_id="ntc2018_slu_taglio",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="taglio",
            limit_state="SLU",
            description_it="Verifica a taglio SLU — staffe verticali, qualsiasi tipo di sezione",
            check_category="resistenza",
            required_inputs=[
                "section",
                "material",
                "Tx",
                "staffe_passo",
                "staffe_diametro",
                "staffe_num_bracci",
            ],
            optional_inputs=["Ty", "N", "d"],
            output_metrics=[
                "V_Ed_kN",
                "V_Rd_kN",
                "V_Rd_s_kN",
                "V_Rd_max_kN",
                "theta_deg",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.2",
                formula_label="(4.1.23), (4.1.24)",
                description_it="Verifica a taglio con armature trasversali",
                notes_it=(
                    "Implementazione completa con staffe verticali: V_Rd = min(V_Rd,s, V_Rd,max). "
                    "Inclinazione puntone θ=21.8° (conservativa). V_Rd,s per staffe verticali, "
                    "V_Rd,max per puntone compresso con ν=0.6*(1-f_ck/250)."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="NTC2018",
                    chapter="4.1",
                    paragraph="4.1.2.1.2",
                    description_it="Coefficiente di riduzione resistenza cls ν",
                )
            ],
            function_path="src.methods.ntc2018.checks.check_taglio_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Minimi armatura taglio
        VerificationTemplate(
            template_id="ntc2018_slu_minimi_armatura_taglio",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="minimi_armatura",
            limit_state="SLU",
            description_it="Verifica minimi di armatura a taglio",
            check_category="minimi_armatura",
            required_inputs=["section", "material", "staffe_passo", "staffe_diametro"],
            optional_inputs=["staffe_num_bracci"],
            output_metrics=[
                "Asw_over_s_actual_mm2_mm",
                "Asw_min_over_s_mm2_mm",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.6.1.1",
                description_it="Armatura minima a taglio",
                notes_it=(
                    "Implementazione completa formula NTC 2018: Asw,min/s = 0.08*√f_ck/f_yk*b."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.ntc2018.checks.check_minimi_armatura_taglio_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Presso/tenso-flessione retta e deviata SLU (generalizzata per tutte le sezioni)
        VerificationTemplate(
            template_id="ntc2018_slu_pressoflessione",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="pressoflessione",
            limit_state="SLU",
            description_it=(
                "Verifica a presso/tenso-flessione retta e deviata SLU — "
                "qualsiasi tipo di sezione"
            ),
            check_category="resistenza",
            required_inputs=["section", "material", "As", "d"],
            optional_inputs=["N", "Mx", "My", "As_prime", "d_prime"],
            output_metrics=[
                "N_Ed_kN",
                "M_Ed_kNm",
                "M_Rd_kNm",
                "x_mm",
                "x_over_d",
                "utilizzazione",
                "bresler_value",
                "alpha_bresler",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.1",
                formula_label="(4.1)",
                description_it=(
                    "Verifica a presso/tenso-flessione retta e deviata. "
                    "Fiber method con stress block rettangolare λ=0.8, εcu=0.0035. "
                    "Flessione deviata: formula di Bresler."
                ),
                notes_it=(
                    "Modello generalizzato: copre compressione/trazione centrata, "
                    "flessione semplice, presso-flessione, tenso-flessione retta e "
                    "deviata. Applicabile a tutte le sezioni gestite dal software."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="EC2",
                    chapter="5.8",
                    paragraph="5.8.9",
                    description_it=(
                        "Formula di Bresler per flessione deviata: "
                        "(Mx/Mx_Rd)^α + (My/My_Rd)^α ≤ 1.0"
                    ),
                ),
                NormReference(
                    norm_code="Circolare7",
                    chapter="C4.1",
                    paragraph="C4.1.2.1.3.1",
                    description_it="Istruzioni per verifica a pressoflessione",
                ),
            ],
            function_path="src.methods.ntc2018.checks.check_pressoflessione_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "rectangular",
                "RECTANGULAR",
                "circular",
                "CIRCULAR",
                "circular_hollow",
                "CIRCULAR_HOLLOW",
                "rectangular_hollow",
                "RECTANGULAR_HOLLOW",
                "t_section",
                "T_SECTION",
                "inverted_t_section",
                "INVERTED_T_SECTION",
                "i_section",
                "I_SECTION",
                "pi_section",
                "PI_SECTION",
                "c_section",
                "C_SECTION",
                "l_section",
                "L_SECTION",
                "v_section",
                "V_SECTION",
                "inverted_v_section",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Torsione SLU
        VerificationTemplate(
            template_id="ntc2018_slu_torsione",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="torsione",
            limit_state="SLU",
            description_it=(
                "Verifica a torsione SLU — modello traliccio thin-walled, "
                "qualsiasi tipo di sezione"
            ),
            check_category="resistenza",
            required_inputs=["section", "material", "Mz"],
            optional_inputs=[
                "Tx",
                "staffe_passo",
                "staffe_diametro",
                "staffe_num_bracci",
                "d",
            ],
            output_metrics=[
                "T_Ed_kNm",
                "T_Rd_kNm",
                "T_Rd_max_kNm",
                "T_Rd_s_kNm",
                "A_k_mm2",
                "interaction_ratio",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.5",
                formula_label="EC2 (6.26)-(6.29)",
                description_it="Verifica a torsione con modello a traliccio thin-walled",
                notes_it=(
                    "T_Rd,max = 2·ν·A_k·t_ef·f_cd·sinθ·cosθ (puntone compresso). "
                    "T_Rd,s = 2·A_k·(Asw/s)·f_ywd·cotθ (armature). "
                    "Interazione taglio-torsione: T_Ed/T_Rd,max + V_Ed/V_Rd,max ≤ 1.0."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="EC2",
                    chapter="6.3",
                    paragraph="6.3.2",
                    description_it="Modello a traliccio per torsione",
                ),
            ],
            function_path="src.methods.ntc2018.checks.check_torsione_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Tensioni SLE
        VerificationTemplate(
            template_id="ntc2018_sle_tensioni",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="tensioni_esercizio",
            limit_state="SLE",
            description_it=("Verifica tensioni in esercizio SLE — " "qualsiasi tipo di sezione"),
            check_category="tensioni_esercizio",
            required_inputs=["section", "material", "As", "d"],
            optional_inputs=["Mx", "N", "As_prime", "d_prime"],
            output_metrics=[
                "sigma_c_MPa",
                "sigma_s_MPa",
                "sigma_c_lim_MPa",
                "sigma_s_lim_MPa",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.2.5",
                description_it="Limiti tensioni in esercizio",
                notes_it=(
                    "σ_c ≤ 0.60·f_ck (comb. caratteristica), "
                    "σ_c ≤ 0.45·f_ck (comb. quasi-permanente), "
                    "σ_s ≤ 0.80·f_yk. Sezione fessurata n-trasformata."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.ntc2018.checks.check_tensioni_sle",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # Fessurazione SLE
        VerificationTemplate(
            template_id="ntc2018_sle_fessurazione",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="fessurazione",
            limit_state="SLE",
            description_it=(
                "Verifica fessurazione SLE — ampiezza fessure w_k, " "qualsiasi tipo di sezione"
            ),
            check_category="fessurazione",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["As_prime", "d_prime"],
            output_metrics=[
                "w_k_mm",
                "w_amm_mm",
                "sigma_s_MPa",
                "s_r_max_mm",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.2.4",
                formula_label="EC2 (7.8)-(7.11)",
                description_it="Verifica ampiezza fessure",
                notes_it=(
                    "w_k = s_r,max · (ε_sm - ε_cm). "
                    "s_r,max = 3.4·c + 0.425·k1·k2·φ/ρ_p,eff. "
                    "Limite w_amm configurabile (default 0.3 mm)."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="EC2",
                    chapter="7.3",
                    paragraph="7.3.4",
                    description_it="Calcolo ampiezza fessure",
                ),
            ],
            function_path="src.methods.ntc2018.checks.check_fessurazione_sle",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete", "w_amm_mm": 0.3},
        ),
        # Deformazioni SLE
        VerificationTemplate(
            template_id="ntc2018_sle_deformazioni",
            norm_code="NTC2018",
            norm_version="2018",
            verification_type="deformazioni",
            limit_state="SLE",
            description_it=(
                "Verifica deformazioni SLE — freccia con rigidezza interpolata, "
                "qualsiasi tipo di sezione"
            ),
            check_category="deformazioni",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["As_prime", "d_prime"],
            output_metrics=[
                "delta_mm",
                "delta_amm_mm",
                "M_cr_kNm",
                "zeta",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.2.2",
                formula_label="EC2 (7.18)-(7.19)",
                description_it="Verifica frecce con rigidezza interpolata",
                notes_it=(
                    "1/r = ζ·1/r_II + (1-ζ)·1/r_I. "
                    "ζ = 1 - β·(M_cr/M_Ed)². "
                    "Richiede span_mm in CalcInput.extra. "
                    "Limite: L/250 (aspetto) o L/500 (danni)."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="EC2",
                    chapter="7.4",
                    paragraph="7.4.3",
                    description_it="Metodo rigidezza interpolata per frecce",
                ),
            ],
            function_path="src.methods.ntc2018.checks.check_deformazioni_sle",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=[
                "RECTANGULAR",
                "CIRCULAR",
                "CIRCULAR_HOLLOW",
                "RECTANGULAR_HOLLOW",
                "T_SECTION",
                "INVERTED_T_SECTION",
                "I_SECTION",
                "PI_SECTION",
                "C_SECTION",
                "L_SECTION",
                "V_SECTION",
                "INVERTED_V_SECTION",
            ],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={
                "implementation_status": "complete",
                "deflection_limit_ratio": 250.0,
            },
        ),
    ]


def get_rd2229_templates() -> list[VerificationTemplate]:
    """Get RD 2229/39 templates (Tensioni Ammissibili storiche).

    Implementazione Session 5:
    - 1 template COMPLETE (flessione TA)
    - 3 templates PARTIAL (pressoflessione, taglio, minimi armatura)

    Tutti con messaggi in italiano e TODOs chiari per parti mancanti.
    """
    return [
        # Flessione TA (COMPLETE)
        VerificationTemplate(
            template_id="rd2229_ta_flessione_rett",
            norm_code="RD2229",
            norm_version="1939",
            verification_type="flessione",
            limit_state="TA",
            description_it="Verifica a flessione metodo Tensioni Ammissibili - RD 2229/39",
            check_category="resistenza",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=[
                "sigma_c_max_kg_cm2",
                "sigma_s_max_kg_cm2",
                "sigma_c_adm_kg_cm2",
                "sigma_s_adm_kg_cm2",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="RD2229",
                chapter="Art. 16",
                paragraph="Tensioni ammissibili",
                description_it="Tensioni ammissibili per calcestruzzo e acciaio",
                notes_it=(
                    "Implementazione completa con calcolo tensioni normali metodo TA. "
                    "σ_c,adm = 0.5 × σ_c,28, σ_s,adm = 0.5 × σ_sn. "
                    "Utilizza historical_ta.stress.compute_normal_stresses_ta() per calcolo completo."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="RD2229",
                    chapter="Art. 14",
                    paragraph="Coefficiente di omogeneizzazione",
                    description_it="n = Es / Ec per sezioni omogeneizzate",
                )
            ],
            function_path="src.methods.rd2229.checks.check_flessione_ta_rett",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={"implementation_status": "complete"},
        ),
        # Pressoflessione TA (PARTIAL)
        VerificationTemplate(
            template_id="rd2229_ta_pressoflessione_rett",
            norm_code="RD2229",
            norm_version="1939",
            verification_type="pressoflessione",
            limit_state="TA",
            description_it="Verifica a pressoflessione metodo Tensioni Ammissibili - RD 2229/39",
            check_category="resistenza",
            required_inputs=["section", "material", "N", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=[
                "sigma_c_max_kg_cm2",
                "sigma_s_max_kg_cm2",
                "N_kg",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="RD2229",
                chapter="Art. 16",
                paragraph="Tensioni ammissibili - Pressoflessione",
                description_it="Tensioni ammissibili per presso/tensioflessione",
                notes_it=(
                    "Implementazione MIGLIORATA: calcolo tensioni completo + riduzione snellezza. "
                    "✓ IMPLEMENTATO: Riduzione σ_c,adm per sezioni snelle (Art. 16): "
                    "σ_c,adm,rid = σ_c,adm × (1 - 0.03 × (25 - A_min)) per A_min < 25 cm. "
                    "TODO: Controllo instabilità pilastri snelli (λ > 15) - richiede l₀. "
                    "Riferimento normativo: RD 2229/39 Art. 16."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.rd2229.checks.check_pressoflessione_ta_rett",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={
                "implementation_status": "improved_partial",
                "missing_features": ["instabilita_pilastri"],
            },
        ),
        # Taglio TA (PARTIAL)
        VerificationTemplate(
            template_id="rd2229_ta_taglio_rett",
            norm_code="RD2229",
            norm_version="1939",
            verification_type="taglio",
            limit_state="TA",
            description_it="Verifica a taglio metodo Tensioni Ammissibili - RD 2229/39",
            check_category="resistenza",
            required_inputs=["section", "material", "Tx", "d"],
            optional_inputs=["Ty", "staffe_passo", "staffe_diametro"],
            output_metrics=[
                "tau_kg_cm2",
                "tau_c0_kg_cm2",
                "tau_c1_kg_cm2",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="RD2229",
                chapter="Art. 21",
                paragraph="Tensioni tangenziali ammissibili",
                description_it="Verifica a taglio",
                notes_it=(
                    "Implementazione PARZIALE: formula base τ = V/(b·d) conservativa. "
                    "τ_c0 = 0.06 × σ_c,28 (senza staffe), τ_c1 = 0.14 × σ_c,28 (con staffe) da RD2229.jsoncode. "
                    "TODO: Formula completa Art. 21 (richiede ricerca storica su manuali RD 2229/Santarella). "
                    "TODO: Calcolo contributo staffe metodo TA storico. "
                    "TODO: Verifica biella compressa. "
                    "Nota: Verifica attuale utilizzabile per valutazioni preliminari conservative."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.rd2229.checks.check_taglio_ta_rett",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={
                "implementation_status": "partial",
                "missing_features": [
                    "formula_completa_art21",
                    "contributo_staffe_ta",
                    "minimi_armatura_taglio",
                ],
            },
        ),
        # Minimi armatura TA (PARTIAL)
        VerificationTemplate(
            template_id="rd2229_ta_minimi_armatura_long",
            norm_code="RD2229",
            norm_version="1939",
            verification_type="minimi_armatura",
            limit_state="TA",
            description_it="Verifica minimi armatura longitudinale - RD 2229/39",
            check_category="minimi_armatura",
            required_inputs=["section", "material", "As"],
            optional_inputs=["element_type"],  # "trave" or "pilastro"
            output_metrics=[
                "As_cm2",
                "As_min_cm2",
                "As_max_cm2",
                "percentuale_armatura",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="RD2229",
                chapter="Art. 16",
                paragraph="Armature minime e massime",
                description_it="Percentuali armatura longitudinale",
                notes_it=(
                    "Implementazione COMPLETA con compute_long_rebar_limits_ta(). "
                    "Distinzione automatica travi (As,min = 0.15% A_sez) / "
                    "pilastri (As,min = 0.30% A_sez). "
                    "As,max = 6% A_sez per entrambi. Riferimento: Art. 16 RD 2229/39."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.rd2229.checks.check_minimi_armatura_ta",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={
                "implementation_status": "complete",
            },
        ),
        # Pressoflessione deviata TA - Concrete (COMPLETE)
        VerificationTemplate(
            template_id="rd2229_ta_pressoflessione_deviata_concrete",
            norm_code="RD2229",
            norm_version="1939",
            verification_type="pressoflessione_deviata",
            limit_state="TA",
            description_it="Verifica cls pressoflessione deviata N-Mx-My - RD 2229/39",
            check_category="resistenza",
            required_inputs=["section", "material"],
            optional_inputs=["N", "Mx", "My"],
            output_metrics=["sigma_c_max_kg_cm2", "sigma_c_adm_kg_cm2", "utilisazione"],
            primary_reference=NormReference(
                norm_code="RD2229",
                chapter="Art. 18",
                paragraph="Tensioni ammissibili calcestruzzo",
                description_it="Carichi di sicurezza per flessione e compressione",
                notes_it=(
                    "Implementazione COMPLETA con sovrapposizione elastica (Art. 29). "
                    "σ_c,max = N/A + |Mx|/Wx + |My|/Wy. "
                    "Riduzione sezioni snelle (A_min < 25 cm) integrata. "
                    "TODO: Instabilità λ > 15 (richiede l₀)."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="RD2229",
                    chapter="Art. 29",
                    paragraph="Metodo elastico",
                    description_it="Sovrapposizione lineare effetti",
                ),
                NormReference(
                    norm_code="RD2229",
                    chapter="Art. 30",
                    paragraph="Pilastri snelli",
                    description_it="Verifica stabilità λ > 15 (OUT OF SCOPE)",
                ),
            ],
            function_path="src.methods.rd2229.checks.check_pressoflessione_deviata_ta_concrete",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={"implementation_status": "complete"},
        ),
        # Pressoflessione deviata TA - Steel (PARTIAL)
        VerificationTemplate(
            template_id="rd2229_ta_pressoflessione_deviata_steel",
            norm_code="RD2229",
            norm_version="1939",
            verification_type="pressoflessione_deviata",
            limit_state="TA",
            description_it="Verifica acciaio pressoflessione deviata N-Mx-My - RD 2229/39",
            check_category="resistenza",
            required_inputs=["section", "material"],
            optional_inputs=["N", "Mx", "My", "As", "d"],
            output_metrics=["sigma_s_max_kg_cm2", "sigma_s_adm_kg_cm2", "utilisazione"],
            primary_reference=NormReference(
                norm_code="RD2229",
                chapter="Art. 19",
                paragraph="Tensioni ammissibili acciaio",
                description_it="Limiti tensioni acciaio in flessione",
                notes_it=(
                    "Implementazione PARZIALE: richiede W_sx, W_sy in calc_input.extra. "
                    "TODO: Calcolo automatico moduli resistenza acciaio da geometria barre."
                ),
            ),
            secondary_references=[
                NormReference(
                    norm_code="RD2229",
                    chapter="Art. 29",
                    paragraph="Metodo elastico",
                    description_it="Sovrapposizione lineare effetti",
                ),
            ],
            function_path="src.methods.rd2229.checks.check_pressoflessione_deviata_ta_steel",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={
                "implementation_status": "partial",
                "missing_features": ["automatic_steel_moduli_calculation"],
            },
        ),
    ]


def get_dm96_templates() -> list[VerificationTemplate]:
    """Get DM 9/1/1996 templates (TA + SLU + SLE + c.a.p.).

    DM 9/1/1996 consente sia il metodo TA (DM 14/02/1992) sia il metodo
    agli Stati Limite (SLU/SLE) con gamma_c = 1.6 e gamma_s = 1.15.

    Templates:
    - 4 TA: flessione, pressoflessione, taglio, minimi armatura
    - 4 SLU base: flessione, taglio, minimi armatura flessione, minimi armatura taglio
    - 2 SLE: fessurazione, deformazioni
    - 3 SLU aggiuntivi: torsione, punzonamento, instabilita
    - 2 c.a.p. placeholder: tensioni TA, SLU precompressione
    """
    _dm96_ref_ta = NormReference(
        norm_code="DM96",
        chapter="DM 14/02/1992",
        paragraph="Tensioni ammissibili",
        description_it="Metodo delle tensioni ammissibili (DM 14/02/1992)",
    )
    _dm96_ref_slu = NormReference(
        norm_code="DM96",
        chapter="DM 9/1/1996",
        paragraph="Stati Limite Ultimo",
        description_it="Metodo agli stati limite ultimo (DM 9/1/1996)",
    )
    _dm96_ref_sle = NormReference(
        norm_code="DM96",
        chapter="DM 9/1/1996",
        paragraph="Stati Limite Esercizio",
        description_it="Metodo agli stati limite di esercizio (DM 9/1/1996)",
    )
    _dm96_ref_cap = NormReference(
        norm_code="DM96",
        chapter="DM 9/1/1996",
        paragraph="Precompressione",
        description_it="Verifiche cemento armato precompresso (DM 9/1/1996, DM 14/02/1992)",
    )

    return [
        # =====================================================================
        # TA - Tensioni Ammissibili (DM 14/02/1992)
        # =====================================================================
        VerificationTemplate(
            template_id="dm96_ta_flessione_rett",
            norm_code="DM96",
            norm_version="1996",
            verification_type="flessione",
            limit_state="TA",
            description_it="Verifica a flessione semplice TA - DM 14/02/1992",
            check_category="resistenza",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=[
                "sigma_c_max_kg_cm2",
                "sigma_s_max_kg_cm2",
                "sigma_c_adm_kg_cm2",
                "sigma_s_adm_kg_cm2",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 14/02/1992",
                paragraph="Tensioni ammissibili - Flessione",
                description_it="Verifica a flessione semplice metodo TA",
                notes_it=(
                    "sigma_c_adm = 0.30 * Rck (DM 14/02/1992). "
                    "Utilizza historical_ta per calcolo tensioni normali."
                ),
            ),
            secondary_references=[_dm96_ref_ta],
            function_path="src.methods.dm96.checks.check_flessione_ta_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={"implementation_status": "complete"},
        ),
        VerificationTemplate(
            template_id="dm96_ta_pressoflessione_rett",
            norm_code="DM96",
            norm_version="1996",
            verification_type="pressoflessione",
            limit_state="TA",
            description_it="Verifica a pressoflessione TA - DM 14/02/1992",
            check_category="resistenza",
            required_inputs=["section", "material", "N", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=[
                "sigma_c_max_kg_cm2",
                "sigma_s_max_kg_cm2",
                "N_kg",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 14/02/1992",
                paragraph="Tensioni ammissibili - Pressoflessione",
                description_it="Verifica a pressoflessione metodo TA con riduzione snellezza",
                notes_it=(
                    "Include riduzione sigma_c_adm per sezioni snelle (dimensione minima < 25 cm)."
                ),
            ),
            secondary_references=[_dm96_ref_ta],
            function_path="src.methods.dm96.checks.check_pressoflessione_ta_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={"implementation_status": "complete"},
        ),
        VerificationTemplate(
            template_id="dm96_ta_taglio_rett",
            norm_code="DM96",
            norm_version="1996",
            verification_type="taglio",
            limit_state="TA",
            description_it="Verifica a taglio TA - DM 14/02/1992",
            check_category="resistenza",
            required_inputs=["section", "material", "Tx", "d"],
            optional_inputs=["Ty", "staffe_passo", "staffe_diametro"],
            output_metrics=[
                "tau_kg_cm2",
                "tau_c0_kg_cm2",
                "tau_c1_kg_cm2",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 14/02/1992",
                paragraph="Tensioni tangenziali ammissibili",
                description_it="Verifica a taglio metodo TA",
                notes_it=(
                    "tau = V/(b*d), tau_c0 e tau_c1 da DM92.jsoncode. "
                    "tau < tau_c0: nessuna armatura richiesta; "
                    "tau_c0 < tau < tau_c1: staffe richieste; tau > tau_c1: NON verificato."
                ),
            ),
            secondary_references=[_dm96_ref_ta],
            function_path="src.methods.dm96.checks.check_taglio_ta_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={"implementation_status": "complete"},
        ),
        VerificationTemplate(
            template_id="dm96_ta_minimi_armatura_long",
            norm_code="DM96",
            norm_version="1996",
            verification_type="minimi_armatura",
            limit_state="TA",
            description_it="Verifica minimi armatura longitudinale TA - DM 14/02/1992",
            check_category="minimi_armatura",
            required_inputs=["section", "material", "As"],
            optional_inputs=["element_type"],
            output_metrics=["As_cm2", "As_min_cm2", "As_max_cm2", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 14/02/1992",
                paragraph="Armature minime e massime",
                description_it="Percentuali armatura longitudinale",
                notes_it=(
                    "Travi: As,min = 0.15% A_sez; Pilastri: As,min = 0.30% A_sez. "
                    "As,max = 6% A_sez."
                ),
            ),
            secondary_references=[_dm96_ref_ta],
            function_path="src.methods.dm96.checks.check_minimi_armatura_ta_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={"implementation_status": "complete"},
        ),
        # =====================================================================
        # SLU - Stati Limite Ultimo (DM 9/1/1996) - gamma_c = 1.6
        # =====================================================================
        VerificationTemplate(
            template_id="dm96_slu_flessione_rett",
            norm_code="DM96",
            norm_version="1996",
            verification_type="flessione",
            limit_state="SLU",
            description_it="Verifica a flessione semplice SLU - DM 9/1/1996",
            check_category="resistenza",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=[
                "M_Ed_kNm",
                "M_Rd_kNm",
                "x_mm",
                "x_over_d",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Verifica a flessione SLU",
                description_it="Flessione semplice e composta SLU",
                notes_it=(
                    "Stress block rettangolare lambda=0.8, eta=1.0. "
                    "gamma_c = 1.6 (DM96, default); gamma_s = 1.15. "
                    "Limite x/d configurabile (default 0.45)."
                ),
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_flessione_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={
                "implementation_status": "complete",
                "gamma_c": 1.6,
                "gamma_s": 1.15,
                "lambda_factor": 0.8,
                "x_d_limit": 0.45,
            },
        ),
        VerificationTemplate(
            template_id="dm96_slu_taglio",
            norm_code="DM96",
            norm_version="1996",
            verification_type="taglio",
            limit_state="SLU",
            description_it="Verifica a taglio SLU - DM 9/1/1996",
            check_category="resistenza",
            required_inputs=[
                "section",
                "material",
                "Tx",
                "staffe_passo",
                "staffe_diametro",
                "staffe_num_bracci",
            ],
            optional_inputs=["Ty", "N", "d"],
            output_metrics=[
                "V_Ed_kN",
                "V_Rd_kN",
                "V_Rd_s_kN",
                "V_Rd_max_kN",
                "theta_deg",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Verifica a taglio SLU",
                description_it="Taglio con armature trasversali SLU",
                notes_it=(
                    "V_Rd = min(V_Rd,s, V_Rd,max). gamma_c = 1.6 (DM96). "
                    "Angolo puntone theta configurabile (default 21.8 gradi)."
                ),
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_taglio_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={
                "implementation_status": "complete",
                "gamma_c": 1.6,
                "gamma_s": 1.15,
                "theta_deg": 21.8,
            },
        ),
        VerificationTemplate(
            template_id="dm96_slu_minimi_armatura_fless",
            norm_code="DM96",
            norm_version="1996",
            verification_type="minimi_armatura",
            limit_state="SLU",
            description_it="Verifica minimi armatura a flessione SLU - DM 9/1/1996",
            check_category="minimi_armatura",
            required_inputs=["section", "material", "As"],
            optional_inputs=["d"],
            output_metrics=["As_min_cm2", "As_effettiva_cm2", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Armature minime flessione",
                description_it="Armatura longitudinale minima SLU",
                notes_it="As,min = max(0.26*fctm/fyk*b*d, 0.0013*b*d).",
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_minimi_armatura_flessione_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        VerificationTemplate(
            template_id="dm96_slu_minimi_armatura_taglio",
            norm_code="DM96",
            norm_version="1996",
            verification_type="minimi_armatura",
            limit_state="SLU",
            description_it="Verifica minimi armatura a taglio SLU - DM 9/1/1996",
            check_category="minimi_armatura",
            required_inputs=["section", "material", "staffe_passo", "staffe_diametro"],
            optional_inputs=["staffe_num_bracci"],
            output_metrics=[
                "Asw_over_s_actual_mm2_mm",
                "Asw_min_over_s_mm2_mm",
                "utilizzazione",
            ],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Armature minime taglio",
                description_it="Armatura trasversale minima SLU",
                notes_it="Asw,min/s = 0.08*sqrt(fck)/fyk*b.",
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_minimi_armatura_taglio_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={
                "implementation_status": "complete",
                "gamma_c": 1.6,
                "gamma_s": 1.15,
            },
        ),
        # =====================================================================
        # SLE - Stati Limite Esercizio (DM 9/1/1996)
        # =====================================================================
        VerificationTemplate(
            template_id="dm96_sle_fessurazione",
            norm_code="DM96",
            norm_version="1996",
            verification_type="fessurazione",
            limit_state="SLE",
            description_it="Verifica fessurazione SLE - DM 9/1/1996",
            check_category="fessurazione",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["N", "As_prime"],
            output_metrics=["w_k_mm", "w_amm_mm", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Stato limite di fessurazione",
                description_it="Verifica ampiezza fessure SLE",
                notes_it=(
                    "Limite w_amm configurabile via extra_params (default 0.3 mm). "
                    "Implementato: formula EC2 §7.3.4 per calcolo w_k."
                ),
            ),
            secondary_references=[_dm96_ref_sle],
            function_path="src.methods.dm96.checks.check_fessurazione_sle_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={
                "implementation_status": "implemented",
                "w_amm_mm": 0.3,
            },
        ),
        VerificationTemplate(
            template_id="dm96_sle_deformazioni",
            norm_code="DM96",
            norm_version="1996",
            verification_type="deformazioni",
            limit_state="SLE",
            description_it="Verifica deformazioni SLE - DM 9/1/1996",
            check_category="deformazioni",
            required_inputs=["section", "material"],
            optional_inputs=["Mx", "N"],
            output_metrics=["delta_mm", "delta_amm_mm", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Stato limite di deformazione",
                description_it="Verifica frecce e deformazioni SLE",
                notes_it=(
                    "Limite L/250 configurabile via extra_params. "
                    "Richiede span_mm e deflection_limit_ratio in CalcInput.extra. "
                    "Implementato: metodo Branson per I_eff con fluage."
                ),
            ),
            secondary_references=[_dm96_ref_sle],
            function_path="src.methods.dm96.checks.check_deformazioni_sle_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={
                "implementation_status": "implemented",
                "deflection_limit_ratio": 250.0,
            },
        ),
        # =====================================================================
        # SLU aggiuntivi (DM 9/1/1996)
        # =====================================================================
        VerificationTemplate(
            template_id="dm96_slu_torsione",
            norm_code="DM96",
            norm_version="1996",
            verification_type="torsione",
            limit_state="SLU",
            description_it="Verifica a torsione SLU - DM 9/1/1996",
            check_category="resistenza",
            required_inputs=["section", "material", "Mz"],
            optional_inputs=["Tx", "staffe_passo", "staffe_diametro"],
            output_metrics=["T_Ed_kNm", "T_Rd_kNm", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Verifica a torsione SLU",
                description_it="Torsione e interazione taglio-torsione",
                notes_it="Implementato: modello traliccio thin-walled EC2 §6.3.",
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_torsione_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "implemented", "gamma_c": 1.6},
        ),
        VerificationTemplate(
            template_id="dm96_slu_punzonamento",
            norm_code="DM96",
            norm_version="1996",
            verification_type="punzonamento",
            limit_state="SLU",
            description_it="Verifica a punzonamento SLU - DM 9/1/1996",
            check_category="resistenza",
            required_inputs=["section", "material", "N"],
            optional_inputs=["d"],
            output_metrics=["v_Ed_MPa", "v_Rd_MPa", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Verifica a punzonamento SLU",
                description_it="Punzonamento piastre e plinti",
                notes_it="Implementato: perimetro critico u_1, v_Rd,c EC2 §6.4.",
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_punzonamento_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "implemented", "gamma_c": 1.6},
        ),
        VerificationTemplate(
            template_id="dm96_slu_instabilita",
            norm_code="DM96",
            norm_version="1996",
            verification_type="instabilita",
            limit_state="SLU",
            description_it="Verifica instabilita a compressione SLU - DM 9/1/1996",
            check_category="resistenza",
            required_inputs=["section", "material", "N"],
            optional_inputs=["Mx", "My"],
            output_metrics=["lambda_", "N_Ed_kN", "N_cr_kN", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="Verifica instabilita compressione",
                description_it="Instabilita pilastri snelli",
                notes_it=(
                    "Calcolo snellezza lambda = l_0 / i_min. "
                    "l_0 da CalcInput.extra['l_0_mm']. "
                    "Implementato: amplificazione momento EC2 §5.8."
                ),
            ),
            secondary_references=[_dm96_ref_slu],
            function_path="src.methods.dm96.checks.check_instabilita_compressione_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "implemented", "gamma_c": 1.6},
        ),
        # =====================================================================
        # C.A.P. - Precompressione (DM 9/1/1996 + DM 14/02/1992)
        # =====================================================================
        VerificationTemplate(
            template_id="dm96_ta_prestress_stresses",
            norm_code="DM96",
            norm_version="1996",
            verification_type="prestress_stresses",
            limit_state="TA",
            description_it="Verifica tensioni c.a.p. metodo TA - DM 14/02/1992",
            check_category="resistenza",
            required_inputs=["section", "material"],
            optional_inputs=["N", "Mx"],
            output_metrics=["sigma_c_top", "sigma_c_bottom", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 14/02/1992",
                paragraph="Tensioni ammissibili c.a.p.",
                description_it="Verifica tensioni nel calcestruzzo e nell'acciaio da precompressione",
                notes_it=(
                    "TODO: richiede integrazione PrecompressionData in CalcInput. "
                    "Placeholder funzionale."
                ),
            ),
            secondary_references=[_dm96_ref_cap],
            function_path="src.methods.dm96.checks.check_precompression_stresses_ta_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC", "prestressed"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "TODO"},
        ),
        VerificationTemplate(
            template_id="dm96_slu_prestress",
            norm_code="DM96",
            norm_version="1996",
            verification_type="prestress_slu",
            limit_state="SLU",
            description_it="Verifica SLU c.a.p. - DM 9/1/1996",
            check_category="resistenza",
            required_inputs=["section", "material", "Mx"],
            optional_inputs=["N", "As"],
            output_metrics=["M_Rd_kNm", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="DM96",
                chapter="DM 9/1/1996",
                paragraph="SLU c.a.p.",
                description_it="Verifica a flessione SLU per sezioni precompresse",
                notes_it=(
                    "TODO: richiede integrazione PrecompressionData in CalcInput. "
                    "Placeholder funzionale. gamma_c = 1.6."
                ),
            ),
            secondary_references=[_dm96_ref_cap],
            function_path="src.methods.dm96.checks.check_precompression_slu_dm96",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC", "prestressed"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "TODO", "gamma_c": 1.6},
        ),
    ]


def get_fire_templates() -> list[VerificationTemplate]:
    """Get fire resistance templates (DM 9/3/2007, DM 16/2/2007).

    4 template per verifiche incendio:
    - Trave c.a.
    - Pilastro c.a.
    - Solaio c.a.
    - Trave c.a.p. (gancio per futuro)

    Tutti con norm_code="FIRE_DM2007" e limit_state="FIRE".
    """
    _fire_ref = NormReference(
        norm_code="FIRE_DM2007",
        chapter="DM 9/3/2007",
        paragraph="Resistenza al fuoco",
        description_it="Verifica di resistenza al fuoco secondo DM 9/3/2007 e DM 16/2/2007",
    )

    return [
        VerificationTemplate(
            template_id="dm_fire_trave_ca",
            norm_code="FIRE_DM2007",
            norm_version="2007",
            verification_type="fire_resistance",
            limit_state="FIRE",
            description_it="Verifica resistenza al fuoco - Trave c.a.",
            check_category="resistenza_fuoco",
            required_inputs=["section", "material"],
            optional_inputs=["d"],
            output_metrics=["required_class", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="FIRE_DM2007",
                chapter="DM 9/3/2007",
                paragraph="Travi in c.a.",
                description_it="Resistenza al fuoco travi c.a. (metodo tabellare/semplificato)",
                notes_it=(
                    "TODO: implementare tabelle DM 9/3/2007 per spessori minimi "
                    "e copriferri in funzione di classe R e lati esposti."
                ),
            ),
            secondary_references=[_fire_ref],
            function_path="src.methods.dm96.fire.check_fire_resistance_beam_rc",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "TODO"},
        ),
        VerificationTemplate(
            template_id="dm_fire_pilastro_ca",
            norm_code="FIRE_DM2007",
            norm_version="2007",
            verification_type="fire_resistance",
            limit_state="FIRE",
            description_it="Verifica resistenza al fuoco - Pilastro c.a.",
            check_category="resistenza_fuoco",
            required_inputs=["section", "material"],
            optional_inputs=["N", "d"],
            output_metrics=["required_class", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="FIRE_DM2007",
                chapter="DM 9/3/2007",
                paragraph="Pilastri in c.a.",
                description_it="Resistenza al fuoco pilastri c.a. (metodo tabellare)",
                notes_it=(
                    "TODO: implementare tabelle DM 9/3/2007 per dimensioni minime "
                    "e copriferri in funzione di classe R."
                ),
            ),
            secondary_references=[_fire_ref],
            function_path="src.methods.dm96.fire.check_fire_resistance_column_rc",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "TODO"},
        ),
        VerificationTemplate(
            template_id="dm_fire_solaio_ca",
            norm_code="FIRE_DM2007",
            norm_version="2007",
            verification_type="fire_resistance",
            limit_state="FIRE",
            description_it="Verifica resistenza al fuoco - Solaio c.a.",
            check_category="resistenza_fuoco",
            required_inputs=["section", "material"],
            optional_inputs=["d"],
            output_metrics=["required_class", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="FIRE_DM2007",
                chapter="DM 9/3/2007",
                paragraph="Solai in c.a.",
                description_it="Resistenza al fuoco solai c.a. (metodo tabellare)",
                notes_it=(
                    "TODO: implementare tabelle DM 9/3/2007 per spessore minimo "
                    "e copriferro in funzione di classe R."
                ),
            ),
            secondary_references=[_fire_ref],
            function_path="src.methods.dm96.fire.check_fire_resistance_slab_rc",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "TODO"},
        ),
        VerificationTemplate(
            template_id="dm_fire_trave_cap",
            norm_code="FIRE_DM2007",
            norm_version="2007",
            verification_type="fire_resistance",
            limit_state="FIRE",
            description_it="Verifica resistenza al fuoco - Trave c.a.p.",
            check_category="resistenza_fuoco",
            required_inputs=["section", "material"],
            optional_inputs=["d"],
            output_metrics=["required_class", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="FIRE_DM2007",
                chapter="DM 9/3/2007",
                paragraph="Elementi in c.a.p.",
                description_it="Resistenza al fuoco elementi precompressi",
                notes_it=(
                    "GANCIO: richiede integrazione PrecompressionData. "
                    "Temperature critiche acciaio da precompressione tipicamente "
                    "350-400 gradi C (inferiori a 500 gradi C acciaio ordinario)."
                ),
            ),
            secondary_references=[_fire_ref],
            function_path="src.methods.dm96.fire.check_fire_resistance_beam_cap",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC", "prestressed"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "TODO"},
        ),
    ]


def get_ntc2008_templates() -> list[VerificationTemplate]:
    """Get NTC 2008 templates.

    TODO: Implementare templates secondo NTC 2008.
    """
    return [
        # TODO: Implementare templates per NTC 2008
    ]
