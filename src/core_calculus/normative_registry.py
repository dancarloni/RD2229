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
            description_it="Verifica a flessione semplice SLU - sezione rettangolare",
            check_category="resistenza",
            required_inputs=["section", "material", "Mx", "As", "d"],
            optional_inputs=["My", "As_prime", "d_prime"],
            output_metrics=["M_Ed_kNm", "M_Rd_kNm", "x_mm", "x_over_d", "utilizzazione"],
            primary_reference=NormReference(
                norm_code="NTC2018",
                chapter="4.1",
                paragraph="4.1.2.1.3.1",
                formula_label="(4.1)",
                description_it="Verifica a flessione semplice e composta - sezione rettangolare",
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
            function_path="src.methods.checks_ntc2018.check_flessione_slu_rett",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
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
            function_path="src.methods.checks_ntc2018.check_minimi_armatura_flessione_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
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
            description_it="Verifica a taglio SLU - staffe verticali",
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
            function_path="src.methods.checks_ntc2018.check_taglio_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
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
                    "Implementazione completa formula NTC 2018: " "Asw,min/s = 0.08*√f_ck/f_yk*b."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.checks_ntc2018.check_minimi_armatura_taglio_slu",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=False,
            extra_params={"implementation_status": "complete"},
        ),
        # TODO: Add more templates:
        # - Presso-flessione SLU
        # - Compressione/trazione SLU
        # - Torsione SLU
        # - Taglio + torsione SLU
        # - Tensioni SLE
        # - Fessurazione SLE
        # - Deformazioni SLE
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
            function_path="src.methods.checks_rd2229.check_flessione_ta_rett",
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
            function_path="src.methods.checks_rd2229.check_pressoflessione_ta_rett",
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
                    "Implementazione PARZIALE: verifica tensione tangenziale base τ = V / (b·d). "
                    "TODO: Formula completa secondo Art. 21 RD 2229/39. "
                    "TODO: Calcolo contributo staffe metodo TA storico. "
                    "TODO: Minimi armatura a taglio secondo RD 2229/39. "
                    "τ_c0 = 0.06 × σ_c,28 (senza staffe), τ_c1 = 0.14 × σ_c,28 (con staffe)."
                ),
            ),
            secondary_references=[],
            function_path="src.methods.checks_rd2229.check_taglio_ta_rett",
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
            function_path="src.methods.checks_rd2229.check_minimi_armatura_ta",
            can_batch=True,
            supports_real_time=True,
            applicable_section_types=["rectangular", "RECTANGULAR"],
            applicable_material_tags=["concrete", "RC"],
            requires_existing_structure=True,
            extra_params={
                "implementation_status": "complete",
            },
        ),
    ]


def get_ntc2008_templates() -> list[VerificationTemplate]:
    """Get NTC 2008 templates.

    TODO: Implementare templates secondo NTC 2008.
    """
    return [
        # TODO: Implementare templates per NTC 2008
    ]
