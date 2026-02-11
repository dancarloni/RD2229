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
        # Future: *get_rd2229_templates(),
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

    TODO: Implementare templates TA secondo RD 2229/39.
    """
    return [
        # TODO: Implementare templates per RD 2229/39
    ]


def get_ntc2008_templates() -> list[VerificationTemplate]:
    """Get NTC 2008 templates.

    TODO: Implementare templates secondo NTC 2008.
    """
    return [
        # TODO: Implementare templates per NTC 2008
    ]
