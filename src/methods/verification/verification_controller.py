"""
Verification controller - bridges GUI and core verification service.

Provides interface for GUI to:
- Build CalcInput from GUI row data + repositories
- Run verification (real-time or bulk)
- Format results for GUI display

NO Tkinter in this module - pure controller logic.
"""

from __future__ import annotations

import logging
from typing import Any

from src.core_calculus.contracts import CalcInput, CalcOutput
from src.core_calculus.normative_registry import get_all_templates
from src.core_calculus.verification_service import (
    run_verifications_for_all,
    run_verifications_for_element,
)

logger = logging.getLogger(__name__)


class VerificationController:
    """Controller for verification operations.

    Bridges GUI and core verification service.
    """

    def __init__(
        self,
        section_repository: Any,
        material_repository: Any,
    ):
        """Initialize controller.

        Args:
            section_repository: Repository for resolving sections by ID
            material_repository: Repository for resolving materials by ID
        """
        self.section_repository = section_repository
        self.material_repository = material_repository
        self.templates_registry = get_all_templates()
        logger.info(
            f"VerificationController initialized with {len(self.templates_registry)} templates"
        )

    def verify_element_from_row_data(
        self,
        row_data: dict[str, Any],
        active_norm: str = "NTC2018",
        enabled_limit_states: list[str] | None = None,
    ) -> CalcOutput:
        """Verify one element from GUI row data.

        Args:
            row_data: Dictionary with GUI row data (element name, section_id, material_id, N, Mx, As, etc.)
            active_norm: Active norm code (default: "NTC2018")
            enabled_limit_states: Enabled limit states (default: ["SLU"])

        Returns:
            CalcOutput with verification results
        """
        # Build CalcInput from row data
        try:
            calc_input = self._build_calc_input_from_row_data(row_data)
        except Exception as e:
            logger.error(f"Error building CalcInput from row data: {e}", exc_info=True)
            # Return error output
            return CalcOutput(
                element_name=row_data.get("element", "Elemento sconosciuto"),
                norm_code=active_norm,
                ok=False,
                per_template_results={},
                validation_result=None,
                summary_metrics={
                    "status": "ERRORE_INPUT",
                    "error_message": str(e),
                },
            )

        # Run verification
        return run_verifications_for_element(
            calc_input=calc_input,
            active_norm=active_norm,
            templates_registry=self.templates_registry,
            enabled_limit_states=enabled_limit_states or ["SLU"],
        )

    def verify_all_elements_from_rows(
        self,
        rows_data: list[dict[str, Any]],
        active_norm: str = "NTC2018",
        enabled_limit_states: list[str] | None = None,
    ) -> list[CalcOutput]:
        """Verify multiple elements from GUI rows (bulk recalculation).

        Args:
            rows_data: List of row data dictionaries
            active_norm: Active norm code
            enabled_limit_states: Enabled limit states

        Returns:
            List of CalcOutput, one per row
        """
        # Build CalcInputs
        calc_inputs = []
        for row_data in rows_data:
            try:
                calc_input = self._build_calc_input_from_row_data(row_data)
                calc_inputs.append(calc_input)
            except Exception as e:
                logger.error(
                    f"Error building CalcInput for row {row_data.get('element', 'unknown')}: {e}"
                )
                # Add error output
                calc_inputs.append(
                    CalcInput(
                        element_name=row_data.get("element", "Elemento sconosciuto"),
                        norm_code=active_norm,
                    )
                )

        # Run bulk verification
        return run_verifications_for_all(
            calc_inputs=calc_inputs,
            active_norm=active_norm,
            templates_registry=self.templates_registry,
            enabled_limit_states=enabled_limit_states or ["SLU"],
        )

    def _build_calc_input_from_row_data(self, row_data: dict[str, Any]) -> CalcInput:
        """Build CalcInput from GUI row data.

        Args:
            row_data: GUI row data dictionary

        Returns:
            CalcInput object

        Raises:
            ValueError: If required data missing or invalid
        """
        # Extract element name
        element_name = str(row_data.get("element", "Elemento senza nome"))

        # Resolve section from repository
        section_id = row_data.get("section_id") or row_data.get("section")
        if section_id and self.section_repository is not None:
            if hasattr(self.section_repository, "get_section_by_id"):
                section = self.section_repository.get_section_by_id(section_id)
            elif hasattr(self.section_repository, "get"):
                section = self.section_repository.get(section_id)
            else:
                logger.warning(f"Section repository has no get method, section_id: {section_id}")
                section = None
        else:
            section = None

        # Resolve material from repository
        material_id = row_data.get("material_id") or row_data.get("mat_concrete")
        if material_id and self.material_repository is not None:
            if hasattr(self.material_repository, "get_material_by_id"):
                material = self.material_repository.get_material_by_id(material_id)
            elif hasattr(self.material_repository, "get"):
                material = self.material_repository.get(material_id)
            else:
                logger.warning(f"Material repository has no get method, material_id: {material_id}")
                material = None
        else:
            material = None

        # Extract normative context
        norm_code = row_data.get("norm_code", "NTC2018")
        limit_states_enabled = row_data.get("limit_states_enabled", ["SLU"])

        # Extract LC/FC for existing structures
        lc = row_data.get("lc")
        fc = row_data.get("fc")
        if fc is not None:
            fc = float(fc)

        # Extract internal forces (convert to float, handle None)
        N = _safe_float(row_data.get("N"))
        Mx = _safe_float(row_data.get("Mx"))
        My = _safe_float(row_data.get("My"))
        Mz = _safe_float(row_data.get("Mz"))
        Tx = _safe_float(row_data.get("Tx"))
        Ty = _safe_float(row_data.get("Ty"))

        # Extract reinforcement geometry
        # Note: VerificationTableApp uses "As" for superior (tesa) and "As_p" for inferior (compressa)
        # Map to CalcInput.As (tesa) and CalcInput.As_prime (compressa)
        As = _safe_float(row_data.get("As"))
        As_prime = _safe_float(row_data.get("As_p"))
        d = _safe_float(row_data.get("d"))
        d_prime = _safe_float(row_data.get("d_p"))

        # Extract stirrups
        staffe_diametro = _safe_float(row_data.get("stirrups_diam"))
        staffe_passo = _safe_float(row_data.get("stirrups_step"))
        # Note: VerificationTableApp doesn't have num_bracci, default to 2
        staffe_num_bracci = 2

        # Build CalcInput
        return CalcInput(
            element_name=element_name,
            section=section,
            material=material,
            norm_code=norm_code,
            limit_states_enabled=limit_states_enabled,
            lc=lc,
            fc=fc,
            N=N,
            Mx=Mx,
            My=My,
            Mz=Mz,
            Tx=Tx,
            Ty=Ty,
            As=As,
            As_prime=As_prime,
            d=d,
            d_prime=d_prime,
            staffe_diametro=staffe_diametro,
            staffe_num_bracci=staffe_num_bracci,
            staffe_passo=staffe_passo,
        )

    def format_output_for_display(self, calc_output: CalcOutput) -> str:
        """Format CalcOutput for GUI display (Italian).

        Args:
            calc_output: Verification output

        Returns:
            Formatted string for display
        """
        lines = []
        lines.append(f"=== VERIFICA: {calc_output.element_name} ===")
        lines.append(f"Normativa: {calc_output.norm_code}")
        lines.append("")

        # Status
        status = calc_output.summary_metrics.get("status", "SCONOSCIUTO")
        lines.append(f"STATO: {status}")

        if status == "NON_VERIFICATO_PER_ERRORI_INPUT":
            lines.append("")
            lines.append("ERRORI DI VALIDAZIONE:")
            if calc_output.validation_result:
                for issue in calc_output.validation_result.issues:
                    if issue.severity == "error":
                        lines.append(f"  ✗ {issue.message_it}")
            return "\n".join(lines)

        # Global result
        esito = "✓ OK" if calc_output.ok else "✗ NON OK"
        lines.append(f"ESITO GLOBALE: {esito}")
        lines.append("")

        # Summary metrics
        num_verifiche = calc_output.summary_metrics.get("num_verifiche_eseguite", 0)
        num_ok = calc_output.summary_metrics.get("num_verifiche_ok", 0)
        num_non_ok = calc_output.summary_metrics.get("num_verifiche_non_ok", 0)
        lines.append(f"Verifiche eseguite: {num_verifiche} ({num_ok} OK, {num_non_ok} NON OK)")

        max_util = calc_output.summary_metrics.get("utilizzazione_massima")
        if max_util is not None:
            lines.append(f"Utilizzazione massima: {max_util:.3f}")

        controlling_template = calc_output.summary_metrics.get("template_controllante")
        if controlling_template:
            lines.append(f"Verifica controllante: {controlling_template}")

        # Per-template results
        if calc_output.per_template_results:
            lines.append("")
            lines.append("DETTAGLIO VERIFICHE:")
            for template_id, result in calc_output.per_template_results.items():
                esito_check = "✓" if result.ok else "✗"
                util_str = f"{result.utilisation:.3f}" if result.utilisation is not None else "N/A"
                lines.append(f"  {esito_check} {template_id}: utilisazione = {util_str}")

        return "\n".join(lines)


def _safe_float(value: Any) -> float | None:
    """Convert value to float, return None if not possible.

    Args:
        value: Value to convert

    Returns:
        Float value or None
    """
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
