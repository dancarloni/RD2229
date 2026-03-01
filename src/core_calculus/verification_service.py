"""
Verification service - orchestrates validation and execution of normative checks.

Core functions:
- run_verifications_for_element: Verify one element
- run_verifications_for_all: Verify multiple elements

Pure core module: NO GUI, NO file I/O (except logging).
All verification logic is synchronous and deterministic.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from importlib import import_module
from typing import Any

from src.core_calculus.contracts import (
    CalcInput,
    CalcOutput,
    SingleCheckResult,
    VerificationTemplate,
)
from src.core_calculus.validation_engine import validate_calc_input

logger = logging.getLogger(__name__)


def run_verifications_for_element(
    calc_input: CalcInput,
    active_norm: str,
    templates_registry: list[VerificationTemplate],
    enabled_limit_states: list[str] | None = None,
) -> CalcOutput:
    """Run all applicable verification checks for one element.

    Steps:
    1. Validate input (via validation_engine)
    2. If validation errors: return CalcOutput with errors, NO checks run
    3. Select applicable templates
    4. Execute each template
    5. Aggregate results

    Args:
        calc_input: Complete input data for element
        active_norm: Active norm code (e.g., "NTC2018")
        templates_registry: List of all available templates
        enabled_limit_states: Optional list of enabled limit states (e.g., ["SLU", "SLE"])
                             If None, use calc_input.limit_states_enabled

    Returns:
        CalcOutput with validation result, per-template results, and summary
    """
    # 1. Validate input
    validation_result = validate_calc_input(calc_input, active_norm, templates_registry)

    # 2. If validation errors, return immediately without running checks
    if validation_result.has_errors:
        logger.warning(
            f"Validation errors for element '{calc_input.element_name}': "
            f"{len([i for i in validation_result.issues if i.severity == 'error'])} errors"
        )
        return CalcOutput(
            element_name=calc_input.element_name,
            norm_code=active_norm,
            ok=False,
            per_template_results={},
            validation_result=validation_result,
            summary_metrics={
                "status": "NON_VERIFICATO_PER_ERRORI_INPUT",
                "num_errori_validazione": float(
                    len([i for i in validation_result.issues if i.severity == "error"])
                ),
                "num_warning_validazione": float(
                    len([i for i in validation_result.issues if i.severity == "warning"])
                ),
            },
        )

    # 3. Select applicable templates
    limit_states_to_check = enabled_limit_states or calc_input.limit_states_enabled
    selected_templates = _select_templates(
        templates_registry=templates_registry,
        norm_code=active_norm,
        limit_states=limit_states_to_check,
        section=calc_input.section,
        material=calc_input.material,
        requires_existing=calc_input.lc is not None,  # If LC is set, structure is existing
    )

    logger.debug(
        f"Selected {len(selected_templates)} templates for element '{calc_input.element_name}'"
    )

    # 4. Execute each template
    per_template_results: dict[str, SingleCheckResult] = {}
    for template in selected_templates:
        try:
            check_result = _execute_template(template, calc_input)
            per_template_results[template.template_id] = check_result
            logger.debug(
                f"Template '{template.template_id}': ok={check_result.ok}, "
                f"utilisation={check_result.utilisation}"
            )
        except Exception as e:
            logger.error(
                f"Error executing template '{template.template_id}': {e}",
                exc_info=True,
            )
            # Create error result
            per_template_results[template.template_id] = SingleCheckResult(
                template_id=template.template_id,
                ok=False,
                utilisation=None,
                details={"error": str(e)},
                norm_references=(
                    template.secondary_references
                    if template.primary_reference is None
                    else [template.primary_reference] + template.secondary_references
                ),
                messages_it=[f"Errore nell'esecuzione della verifica: {e}"],
                check_category=template.check_category,
                limit_state=template.limit_state,
            )

    # 5. Aggregate results
    global_ok = all(result.ok for result in per_template_results.values())
    max_utilisation = max(
        (r.utilisation for r in per_template_results.values() if r.utilisation is not None),
        default=None,
    )

    # Find controlling template (highest utilisation)
    controlling_template = None
    if max_utilisation is not None:
        for template_id, result in per_template_results.items():
            if result.utilisation == max_utilisation:
                controlling_template = template_id
                break

    summary_metrics = {
        "status": "OK" if global_ok else "NON_OK",
        "num_verifiche_eseguite": float(len(per_template_results)),
        "num_verifiche_ok": float(sum(1 for r in per_template_results.values() if r.ok)),
        "num_verifiche_non_ok": float(sum(1 for r in per_template_results.values() if not r.ok)),
    }

    if max_utilisation is not None:
        summary_metrics["utilizzazione_massima"] = max_utilisation
    if controlling_template is not None:
        summary_metrics["template_controllante"] = controlling_template
    if validation_result.has_warnings:
        summary_metrics["warning_validazione"] = True

    return CalcOutput(
        element_name=calc_input.element_name,
        norm_code=active_norm,
        ok=global_ok,
        per_template_results=per_template_results,
        validation_result=validation_result,
        summary_metrics=summary_metrics,
    )


def run_verifications_for_all(
    calc_inputs: list[CalcInput],
    active_norm: str,
    templates_registry: list[VerificationTemplate],
    enabled_limit_states: list[str] | None = None,
) -> list[CalcOutput]:
    """Run verification for multiple elements (bulk recalculation).

    Args:
        calc_inputs: List of CalcInput for all elements
        active_norm: Active norm code
        templates_registry: List of all available templates
        enabled_limit_states: Optional list of enabled limit states

    Returns:
        List of CalcOutput, one per input
    """
    logger.info(f"Running bulk verification for {len(calc_inputs)} elements")
    results = []
    for calc_input in calc_inputs:
        result = run_verifications_for_element(
            calc_input=calc_input,
            active_norm=active_norm,
            templates_registry=templates_registry,
            enabled_limit_states=enabled_limit_states,
        )
        results.append(result)

    num_ok = sum(1 for r in results if r.ok)
    logger.info(f"Bulk verification complete: {num_ok}/{len(results)} elements OK")
    return results


def _select_templates(
    templates_registry: list[VerificationTemplate],
    norm_code: str,
    limit_states: list[str],
    section: Any,
    material: Any,
    requires_existing: bool,
) -> list[VerificationTemplate]:
    """Select applicable templates based on criteria.

    Filters templates by:
    - Norm code
    - Limit state
    - Section type compatibility
    - Material tag compatibility
    - Existing structure requirement

    Args:
        templates_registry: All available templates
        norm_code: Active norm code
        limit_states: Enabled limit states
        section: Section object (for type checking)
        material: Material object (for tag checking)
        requires_existing: True if structure is existing (LC/FC set)

    Returns:
        List of applicable templates
    """
    selected = []

    # Get section type from section object
    section_type = None
    if section is not None:
        if hasattr(section, "section_type"):
            section_type = str(section.section_type).lower()
        elif hasattr(section, "type"):
            section_type = str(section.type).lower()

    # Get material tags from material object
    material_tags = []
    if material is not None:
        if hasattr(material, "tags"):
            material_tags = [str(t).lower() for t in material.tags]
        # Default: assume concrete if no tags
        if not material_tags:
            material_tags = ["concrete", "rc"]

    for template in templates_registry:
        # Filter by norm code
        if template.norm_code != norm_code:
            continue

        # Filter by limit state
        if template.limit_state not in limit_states:
            continue

        # Filter by section type (if template specifies applicable types)
        if template.applicable_section_types is not None:
            if section_type is None or section_type not in [
                s.lower() for s in template.applicable_section_types
            ]:
                continue

        # Filter by material tags (if template specifies applicable tags)
        if template.applicable_material_tags is not None:
            template_tags_lower = [t.lower() for t in template.applicable_material_tags]
            if not any(tag in template_tags_lower for tag in material_tags):
                continue

        # Filter by existing structure requirement
        if template.requires_existing_structure and not requires_existing:
            # Skip templates that require existing structure if LC/FC not set
            continue

        selected.append(template)

    return selected


def _execute_template(template: VerificationTemplate, calc_input: CalcInput) -> SingleCheckResult:
    """Execute one verification template.

    Imports function from template.function_path and calls it with calc_input.

    Args:
        template: Template to execute
        calc_input: Input data

    Returns:
        SingleCheckResult from template function

    Raises:
        ImportError: If function_path cannot be imported
        TypeError: If function signature is incorrect
    """
    # Parse function_path: "module.path.function_name"
    function_path = template.function_path
    if not function_path:
        raise ValueError(f"Template '{template.template_id}' has empty function_path")

    module_path, _, function_name = function_path.rpartition(".")
    if not module_path or not function_name:
        raise ValueError(
            f"Invalid function_path '{function_path}' for template '{template.template_id}'"
        )

    # Import module and get function
    module = import_module(module_path)
    check_function: Callable[[CalcInput, VerificationTemplate], SingleCheckResult] = getattr(
        module, function_name
    )

    # Execute function
    result = check_function(calc_input, template)

    # Ensure result has template_id, check_category, limit_state
    if result.template_id != template.template_id:
        result.template_id = template.template_id
    if result.check_category is None:
        result.check_category = template.check_category
    if result.limit_state is None:
        result.limit_state = template.limit_state

    return result
