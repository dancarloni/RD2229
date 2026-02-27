"""
Validation engine for CalcInput.

Checks input data for:
- Geometric consistency (d > d', As >= 0, etc.)
- Material parameter ranges (f_ck > 0, f_yk > 0, etc.)
- LC/FC coherence (valid LC values, typical FC ranges)
- Basic limit state coherence

Returns ValidationResult with Italian messages.

DOES NOT:
- Select templates (that's verification service responsibility)
- Execute normative checks (that's verification service responsibility)
"""

from __future__ import annotations

from src.core_calculus.contracts import (
    CalcInput,
    NormReference,
    ValidationIssue,
    ValidationResult,
    VerificationTemplate,
)


def validate_calc_input(
    calc_input: CalcInput,
    active_norm: str,
    templates: list[VerificationTemplate] | None = None,
) -> ValidationResult:
    """Validate CalcInput before verification.

    Checks:
    - Geometric consistency
    - Material parameter ranges
    - LC/FC coherence
    - Basic data completeness

    Returns ValidationResult with issues.
    If result.has_errors is True, verification MUST NOT run.

    Args:
        calc_input: Input data to validate
        active_norm: Active norm code (e.g., "NTC2018")
        templates: Optional list of templates (for future norm-specific validation)

    Returns:
        ValidationResult with list of issues
    """
    issues: list[ValidationIssue] = []

    # 1. Check basic fields
    if not calc_input.element_name or calc_input.element_name.strip() == "":
        issues.append(
            ValidationIssue(
                severity="warning",
                field="element_name",
                code="EMPTY_ELEMENT_NAME",
                message_it="Nome elemento vuoto o mancante",
            )
        )

    if calc_input.section is None:
        issues.append(
            ValidationIssue(
                severity="error",
                field="section",
                code="MISSING_SECTION",
                message_it="Sezione non specificata o non trovata nel repository",
            )
        )

    if calc_input.material is None:
        issues.append(
            ValidationIssue(
                severity="error",
                field="material",
                code="MISSING_MATERIAL",
                message_it="Materiale non specificato o non trovato nel repository",
            )
        )

    if not calc_input.norm_code or calc_input.norm_code.strip() == "":
        issues.append(
            ValidationIssue(
                severity="error",
                field="norm_code",
                code="MISSING_NORM_CODE",
                message_it="Normativa non specificata",
            )
        )

    # 2. Geometric consistency checks
    if calc_input.d is not None and calc_input.d <= 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="d",
                code="INVALID_D",
                message_it=f"Altezza utile d deve essere positiva (valore: {calc_input.d})",
            )
        )

    if calc_input.d_prime is not None and calc_input.d_prime < 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="d_prime",
                code="NEGATIVE_D_PRIME",
                message_it=f"Altezza d' non può essere negativa (valore: {calc_input.d_prime})",
            )
        )

    if calc_input.d is not None and calc_input.d_prime is not None and calc_input.d_prime >= calc_input.d:
        issues.append(
            ValidationIssue(
                severity="error",
                field="d_prime",
                code="D_PRIME_GE_D",
                message_it=f"d' ({calc_input.d_prime}) deve essere minore di d ({calc_input.d})",
            )
        )

    if calc_input.As is not None and calc_input.As < 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="As",
                code="NEGATIVE_AS",
                message_it=f"Area armatura tesa As non può essere negativa (valore: {calc_input.As})",
            )
        )

    if calc_input.As_prime is not None and calc_input.As_prime < 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="As_prime",
                code="NEGATIVE_AS_PRIME",
                message_it=f"Area armatura compressa As' non può essere negativa (valore: {calc_input.As_prime})",
            )
        )

    # 3. Stirrup/shear reinforcement checks
    if calc_input.staffe_passo is not None and calc_input.staffe_passo <= 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="staffe_passo",
                code="INVALID_STAFFE_PASSO",
                message_it=f"Passo staffe deve essere positivo (valore: {calc_input.staffe_passo})",
            )
        )

    if calc_input.staffe_diametro is not None and calc_input.staffe_diametro <= 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="staffe_diametro",
                code="INVALID_STAFFE_DIAMETRO",
                message_it=f"Diametro staffe deve essere positivo (valore: {calc_input.staffe_diametro})",
            )
        )

    if calc_input.staffe_num_bracci is not None and calc_input.staffe_num_bracci < 0:
        issues.append(
            ValidationIssue(
                severity="error",
                field="staffe_num_bracci",
                code="INVALID_STAFFE_NUM_BRACCI",
                message_it=f"Numero bracci staffe non può essere negativo (valore: {calc_input.staffe_num_bracci})",
            )
        )

    # 4. Material parameter validation (if material object has properties)
    if calc_input.material is not None:
        material = calc_input.material
        # Check f_ck (concrete compressive strength)
        if hasattr(material, "f_ck") and material.f_ck is not None:
            if material.f_ck <= 0:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="material.f_ck",
                        code="INVALID_F_CK",
                        message_it=f"Resistenza caratteristica cls f_ck deve essere positiva (valore: {material.f_ck})",
                    )
                )
        # Check f_yk (steel yield strength)
        if hasattr(material, "f_yk") and material.f_yk is not None:
            if material.f_yk <= 0:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="material.f_yk",
                        code="INVALID_F_YK",
                        message_it=f"Tensione caratteristica acciaio f_yk deve essere positiva (valore: {material.f_yk})",
                    )
                )

    # 5. LC/FC validation for existing structures
    if calc_input.lc is not None:
        valid_lc = ["LC1", "LC2", "LC3"]
        if calc_input.lc not in valid_lc:
            issues.append(
                ValidationIssue(
                    severity="error",
                    field="lc",
                    code="INVALID_LC",
                    message_it=f"Livello di Conoscenza non valido: '{calc_input.lc}'. Valori ammessi: {', '.join(valid_lc)}",
                    norm_reference=NormReference(
                        norm_code="NTC2018",
                        chapter="8",
                        paragraph="8.5.4",
                        description_it="Livelli di Conoscenza per strutture esistenti",
                    ),
                )
            )

    if calc_input.fc is not None:
        # Typical FC range per NTC 2018 Table 8.2
        # LC1 → FC = 1.35
        # LC2 → FC = 1.20
        # LC3 → FC = 1.00
        # Allow range [1.0, 1.5] with warning if outside typical values
        if calc_input.fc < 1.0 or calc_input.fc > 1.5:
            issues.append(
                ValidationIssue(
                    severity="error",
                    field="fc",
                    code="FC_OUT_OF_RANGE",
                    message_it=f"Fattore di Confidenza FC fuori range ammissibile [1.0, 1.5]: {calc_input.fc}",
                    norm_reference=NormReference(
                        norm_code="NTC2018",
                        chapter="8",
                        paragraph="8.5.4",
                        description_it="Fattori di Confidenza per strutture esistenti",
                    ),
                )
            )
        elif calc_input.lc is not None:
            # Check consistency between LC and FC
            expected_fc_map = {"LC1": 1.35, "LC2": 1.20, "LC3": 1.00}
            expected_fc = expected_fc_map.get(calc_input.lc)
            if expected_fc is not None and abs(calc_input.fc - expected_fc) > 0.05:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="fc",
                        code="FC_LC_MISMATCH",
                        message_it=f"FC = {calc_input.fc} non corrisponde al valore tipico per {calc_input.lc} (atteso: {expected_fc})",
                        norm_reference=NormReference(
                            norm_code="NTC2018",
                            chapter="8",
                            paragraph="8.5.4",
                            description_it="Tabella 8.2 - Corrispondenza LC/FC",
                        ),
                    )
                )

    # 6. Limit state coherence
    if not calc_input.limit_states_enabled or len(calc_input.limit_states_enabled) == 0:
        issues.append(
            ValidationIssue(
                severity="warning",
                field="limit_states_enabled",
                code="NO_LIMIT_STATES",
                message_it="Nessuno stato limite abilitato per la verifica",
            )
        )

    # 7. Norm-specific validation rules
    if active_norm == "NTC2018":
        # Check for SLU-specific requirements
        if calc_input.limit_states_enabled and "SLU" in calc_input.limit_states_enabled:
            # Warn if flexural reinforcement missing
            if calc_input.As is None or calc_input.As == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="As",
                        code="MISSING_FLEXURAL_REINFORCEMENT",
                        message_it=(
                            "Armatura tesa As non specificata o nulla - "
                            "le verifiche a flessione potrebbero non essere eseguibili"
                        ),
                        norm_reference=NormReference(
                            norm_code="NTC2018",
                            chapter="4.1",
                            paragraph="4.1.6.1.1",
                            description_it="Armature longitudinali minime",
                        ),
                    )
                )

            # Warn if effective depth not specified
            if calc_input.d is None or calc_input.d == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="d",
                        code="MISSING_EFFECTIVE_DEPTH",
                        message_it=(
                            "Altezza utile d non specificata - "
                            "verrà stimata come d ≈ 0.9h ma si consiglia di specificarla"
                        ),
                    )
                )

            # Validate stirrup data for shear checks
            # Check if any shear-related templates would be triggered
            has_shear_force = (calc_input.Tx is not None and calc_input.Tx != 0) or (
                calc_input.Ty is not None and calc_input.Ty != 0
            )

            if has_shear_force:
                # Check stirrup data presence
                if (
                    calc_input.staffe_passo is None
                    or calc_input.staffe_passo == 0
                    or calc_input.staffe_diametro is None
                    or calc_input.staffe_diametro == 0
                ):
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            field="staffe_passo",
                            code="INCOMPLETE_STIRRUP_DATA",
                            message_it=(
                                "Forza di taglio presente ma dati staffe incompleti - " "verifiche a taglio non eseguibili"
                            ),
                            norm_reference=NormReference(
                                norm_code="NTC2018",
                                chapter="4.1",
                                paragraph="4.1.2.1.3.2",
                                description_it="Resistenza a taglio con armature trasversali",
                            ),
                        )
                    )

    # 8. Circular rebar layout validation (if present in extra)
    if "circular_rebar_layout" in calc_input.extra:
        layout = calc_input.extra["circular_rebar_layout"]
        if isinstance(layout, dict):
            n_bars = layout.get("n_bars")
            if n_bars is not None and n_bars < 3:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="extra.circular_rebar_layout.n_bars",
                        code="FEW_CIRCULAR_BARS",
                        message_it=f"Numero barre circolari < 3 può essere geometricamente instabile (valore: {n_bars})",
                    )
                )

    # 9. DM96-specific validation (TA + SLU + SLE)
    if active_norm == "DM96":
        # Material compatibility
        if calc_input.material is not None:
            material = calc_input.material
            has_dm92_props = (
                hasattr(material, "sigma_c_adm_kg_cm2")
                or hasattr(material, "sigma_c_adm")
                or hasattr(material, "Rck_kg_cm2")
            )
            has_modern_props = hasattr(material, "f_ck") or hasattr(material, "fck")
            if not has_dm92_props and not has_modern_props:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="material",
                        code="MISSING_DM96_MATERIAL_PROPERTIES",
                        message_it=(
                            "Materiale non compatibile con DM 9/1/1996: "
                            "deve avere sigma_c_adm_kg_cm2 / Rck_kg_cm2 (DM92) o fck (moderne)"
                        ),
                    )
                )

        # LC/FC warning for existing structures
        if calc_input.lc is None or calc_input.fc is None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    field="lc",
                    code="MISSING_LC_FC_DM96",
                    message_it=(
                        "DM 9/1/1996 spesso utilizzato per strutture esistenti: " "considerare di specificare LC e FC"
                    ),
                    norm_reference=NormReference(
                        norm_code="NTC2018",
                        chapter="8",
                        paragraph="8.5.4",
                        description_it="Livelli di conoscenza per strutture esistenti",
                    ),
                )
            )

        # Section check
        if calc_input.section is not None:
            section = calc_input.section
            if hasattr(section, "width") and section.width > 10000:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="section.width",
                        code="POSSIBLE_UNIT_ERROR",
                        message_it=(
                            f"Larghezza sezione molto grande ({section.width} mm): " "verificare le unita. CalcInput usa mm."
                        ),
                    )
                )

        # TA-specific checks
        if calc_input.limit_states_enabled and "TA" in calc_input.limit_states_enabled:
            if calc_input.As is None or calc_input.As == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="As",
                        code="MISSING_REINFORCEMENT_TA_DM96",
                        message_it=("Armatura tesa As non specificata - " "verifiche TA DM 14/02/1992 non eseguibili"),
                    )
                )
            if calc_input.d is None or calc_input.d == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="d",
                        code="MISSING_D_TA_DM96",
                        message_it=("Altezza utile d non specificata - " "verra stimata come d ~ 0.9h per verifiche TA"),
                    )
                )

        # SLU-specific checks
        if calc_input.limit_states_enabled and "SLU" in calc_input.limit_states_enabled:
            if calc_input.As is None or calc_input.As == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="As",
                        code="MISSING_REINFORCEMENT_SLU_DM96",
                        message_it=("Armatura tesa As non specificata - " "verifiche SLU DM 9/1/1996 non eseguibili"),
                    )
                )
            if calc_input.d is None or calc_input.d == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="d",
                        code="MISSING_D_SLU_DM96",
                        message_it="Altezza utile d non specificata per SLU",
                    )
                )
            # Stirrup data for shear
            has_shear = (calc_input.Tx is not None and calc_input.Tx != 0) or (
                calc_input.Ty is not None and calc_input.Ty != 0
            )
            if has_shear and (
                calc_input.staffe_passo is None
                or calc_input.staffe_passo == 0
                or calc_input.staffe_diametro is None
                or calc_input.staffe_diametro == 0
            ):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="staffe_passo",
                        code="INCOMPLETE_STIRRUP_DATA_DM96",
                        message_it=(
                            "Forza di taglio presente ma dati staffe incompleti - " "verifiche a taglio SLU non eseguibili"
                        ),
                    )
                )

        # TODO: validazione PrecompressionData quando integrata in CalcInput

    # 10. FIRE_DM2007-specific validation
    if active_norm == "FIRE_DM2007" or (calc_input.limit_states_enabled and "FIRE" in calc_input.limit_states_enabled):
        if calc_input.extra is not None:
            # Check fire config presence
            fire_cfg = calc_input.extra.get("fire_config", None)
            has_fire_config = fire_cfg is not None
            has_fire_class = False

            if isinstance(fire_cfg, dict):
                has_fire_class = bool(fire_cfg.get("required_fire_resistance_class"))
                exposed = fire_cfg.get("exposed_sides")
                if exposed is not None and (exposed < 1 or exposed > 4):
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            field="extra.fire_config.exposed_sides",
                            code="INVALID_EXPOSED_SIDES",
                            message_it=(
                                f"Numero lati esposti al fuoco non valido: {exposed}. " "Valori ammessi: 1, 2, 3, 4."
                            ),
                        )
                    )
            elif hasattr(fire_cfg, "required_fire_resistance_class"):
                has_fire_class = bool(fire_cfg.required_fire_resistance_class)
                if hasattr(fire_cfg, "exposed_sides"):
                    exposed = fire_cfg.exposed_sides
                    if exposed < 1 or exposed > 4:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                field="extra.fire_config.exposed_sides",
                                code="INVALID_EXPOSED_SIDES",
                                message_it=(
                                    f"Numero lati esposti al fuoco non valido: {exposed}. " "Valori ammessi: 1, 2, 3, 4."
                                ),
                            )
                        )

            if not has_fire_config:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="extra.fire_config",
                        code="MISSING_FIRE_CONFIG",
                        message_it=(
                            "Configurazione incendio (fire_config) non presente in CalcInput.extra. "
                            "Impostare FireVerificationConfig con classe R richiesta."
                        ),
                        norm_reference=NormReference(
                            norm_code="FIRE_DM2007",
                            chapter="DM 9/3/2007",
                            paragraph="Classificazione resistenza al fuoco",
                            description_it="Classe di resistenza al fuoco richiesta",
                        ),
                    )
                )
            elif not has_fire_class:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="extra.fire_config.required_fire_resistance_class",
                        code="MISSING_FIRE_CLASS",
                        message_it=(
                            "Classe di resistenza al fuoco richiesta non specificata. "
                            "Impostare required_fire_resistance_class (es. 'R30', 'R60', 'R90', 'R120')."
                        ),
                        norm_reference=NormReference(
                            norm_code="FIRE_DM2007",
                            chapter="DM 16/2/2007",
                            paragraph="Classi di resistenza al fuoco",
                            description_it="Classificazione R30, R60, R90, R120",
                        ),
                    )
                )

            # Section dimensions needed for fire checks
            if calc_input.section is None:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="section",
                        code="MISSING_SECTION_FIRE",
                        message_it=(
                            "Sezione non specificata - necessaria per verifiche incendio " "(spessori minimi, copriferri)"
                        ),
                    )
                )

    # 11. RD2229-specific validation (Tensioni Ammissibili)
    if active_norm == "RD2229":
        # Warn if LC/FC not specified (TA typically for existing structures)
        if calc_input.lc is None or calc_input.fc is None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    field="lc",
                    code="MISSING_LC_FC_FOR_EXISTING",
                    message_it=(
                        "RD 2229/39 tipicamente utilizzato per strutture esistenti: "
                        "considerare di specificare LC (Livello di Conoscenza) e FC (Fattore di Confidenza)"
                    ),
                    norm_reference=NormReference(
                        norm_code="NTC2018",
                        chapter="8",
                        paragraph="8.5.4",
                        description_it="Livelli di conoscenza per strutture esistenti",
                    ),
                )
            )

        # Check material has TA-compatible properties
        if calc_input.material is not None:
            material = calc_input.material
            # Check if material has either RD2229 properties or modern properties
            has_rd2229_props = hasattr(material, "sigma_c_adm") or hasattr(material, "sigma_c28")
            has_modern_props = hasattr(material, "f_ck")

            if not has_rd2229_props and not has_modern_props:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        field="material",
                        code="MISSING_TA_MATERIAL_PROPERTIES",
                        message_it=(
                            "Materiale non compatibile con RD 2229/39: "
                            "deve avere sigma_c_adm/sigma_c28 (proprietà TA storiche) o f_ck (moderne)"
                        ),
                    )
                )

        # Warn if section dimensions seem wrong (possible unit error)
        if calc_input.section is not None:
            section = calc_input.section
            if hasattr(section, "width") and section.width > 10000:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="section.width",
                        code="POSSIBLE_UNIT_ERROR",
                        message_it=(
                            f"Larghezza sezione molto grande ({section.width} mm): "
                            "verificare che le unità siano corrette. "
                            "RD 2229 usa sistema tecnico (cm), CalcInput usa mm."
                        ),
                    )
                )

        # Check reinforcement data for flessione checks
        if "TA" in calc_input.limit_states_enabled:
            if calc_input.As is None or calc_input.As == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="As",
                        code="MISSING_REINFORCEMENT_TA",
                        message_it=("Armatura tesa As non specificata - " "verifiche a flessione TA non eseguibili"),
                        norm_reference=NormReference(
                            norm_code="RD2229",
                            chapter="Art. 16",
                            paragraph="Tensioni ammissibili",
                            description_it="Verifica tensioni ammissibili richiede armatura definita",
                        ),
                    )
                )

            if calc_input.d is None or calc_input.d == 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        field="d",
                        code="MISSING_EFFECTIVE_DEPTH_TA",
                        message_it=("Altezza utile d non specificata - " "verrà stimata come d ≈ 0.9h per verifiche TA"),
                    )
                )

    return ValidationResult(issues=issues)
