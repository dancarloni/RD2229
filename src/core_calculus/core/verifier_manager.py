"""
Multi-norm verifier manager.

Selects appropriate adapter(s) based on CalcInput configuration,
runs verification, and produces normalized CalcOutput.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import logging
from typing import Any

from src.core_calculus.contracts import CalcInput, CalcOutput, ElementRole

from .adapters.base import EligibilityResult, NormAdapter
from .adapters.ntc2018_adapter import Ntc2018Adapter
from .adapters.rd2229_adapter import Rd2229Adapter
from .classification import classify_element

logger = logging.getLogger(__name__)


class VerifierManager:
    """Manages norm adapters and orchestrates verification."""

    def __init__(self) -> None:
        self._adapters: list[NormAdapter] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in adapters."""
        self._adapters = [
            Ntc2018Adapter(),
            Rd2229Adapter(),
        ]

    def register_adapter(self, adapter: NormAdapter) -> None:
        """Register a custom adapter."""
        self._adapters.append(adapter)

    @property
    def available_norms(self) -> list[str]:
        """List available norm codes."""
        return [a.norm_code for a in self._adapters]

    def get_adapter(self, norm_code: str) -> NormAdapter | None:
        """Get adapter by norm code."""
        for a in self._adapters:
            if a.norm_code == norm_code:
                return a
        return None

    def check_applicability(self, calc_input: CalcInput) -> dict[str, EligibilityResult]:
        """Check which adapters are applicable for the given input."""
        results: dict[str, EligibilityResult] = {}
        for adapter in self._adapters:
            results[adapter.norm_code] = adapter.applicability(calc_input)
        return results

    def verify(self, calc_input: CalcInput) -> CalcOutput:
        """Run verification using the appropriate adapter.

        If calc_input.norm_code is specified, uses that adapter.
        Otherwise, tries all adapters and uses the first eligible one.
        """
        # Auto-classify element role if UNDETERMINED
        if calc_input.element_role == ElementRole.UNDETERMINED:
            element_type = calc_input.extra.get("element_type", "")
            if element_type:
                classification = classify_element(element_type)
                calc_input = dataclasses.replace(calc_input, element_role=classification.role)

        # Find adapter
        adapter = None
        if calc_input.norm_code:
            adapter = self.get_adapter(calc_input.norm_code)
            if adapter is None:
                return CalcOutput(
                    element_name=calc_input.element_name,
                    norm_code=calc_input.norm_code,
                    ok=False,
                    element_role=calc_input.element_role,
                    summary_metrics={
                        "status": "ERRORE",
                        "motivo": f"Adapter '{calc_input.norm_code}' non trovato",
                    },
                )
        else:
            for a in self._adapters:
                elig = a.applicability(calc_input)
                if elig.eligible:
                    adapter = a
                    break

        if adapter is None:
            return CalcOutput(
                element_name=calc_input.element_name,
                ok=False,
                element_role=calc_input.element_role,
                summary_metrics={"status": "ERRORE", "motivo": "Nessun adapter applicabile"},
            )

        logger.info(
            "Verifica elemento '%s' con adapter '%s'", calc_input.element_name, adapter.norm_code
        )
        return adapter.verify(calc_input)

    def verify_bulk(self, inputs: list[CalcInput]) -> list[CalcOutput]:
        """Run verification for multiple elements."""
        return [self.verify(ci) for ci in inputs]


def calc_output_to_dict(
    output: CalcOutput,
    *,
    include_metadata: bool = False,
    metadata: dict[str, Any] | None = None,
    generated: str | None = None,
) -> dict[str, Any]:
    """Serialize CalcOutput to a JSON-compatible dict.

    Parameters
    ----------
    output:
        The :class:`CalcOutput` to serialise.
    include_metadata:
        When ``True`` a ``metadata`` key is included with standard audit
        fields (schema_version, tool, generated timestamp).  Defaults to
        ``False`` to preserve the original output shape for existing callers.
    metadata:
        Optional additional metadata fields to merge into the ``metadata``
        block.  Ignored when *include_metadata* is ``False``.
    generated:
        Optional ISO-8601 timestamp to use as the ``generated`` field.
        When omitted, the current UTC time is used.  Supply a fixed value
        (e.g. the run timestamp) to produce deterministic, audit-safe output.
    """

    def _norm_ref_to_dict(nr):
        return {
            "norm_code": nr.norm_code,
            "chapter": nr.chapter,
            "paragraph": nr.paragraph,
            "formula_label": nr.formula_label,
            "description_it": nr.description_it,
        }

    result: dict[str, Any] = {
        "element_name": output.element_name,
        "norm_code": output.norm_code,
        "ok": output.ok,
        "element_role": (
            output.element_role.value
            if isinstance(output.element_role, ElementRole)
            else str(output.element_role)
        ),
        "profile_used": output.profile_used,
        "summary_metrics": output.summary_metrics,
        "checks": {},
    }
    for tid, scr in output.per_template_results.items():
        result["checks"][tid] = {
            "ok": scr.ok,
            "utilisation": scr.utilisation,
            "details": scr.details,
            "norm_references": [_norm_ref_to_dict(nr) for nr in scr.norm_references],
            "messages_it": scr.messages_it,
            "check_category": scr.check_category,
            "limit_state": scr.limit_state,
        }

    if include_metadata:
        _meta: dict[str, Any] = {
            "schema_version": "1.0",
            "tool": "calc_output_to_dict",
            "generated": generated if generated is not None else _dt.datetime.now(_dt.timezone.utc).isoformat(),
        }
        if metadata:
            _meta.update(metadata)
        result["metadata"] = _meta

    return result
