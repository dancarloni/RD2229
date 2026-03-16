"""Dispatcher standalone X8 (post-V1, non integrato nel core pipeline)."""

from __future__ import annotations

from .x8_clt import evaluate_clt
from .x8_collaboranti import evaluate_collaborante
from .x8_models import SpecialCaseInput, SpecialCaseResult, SpecialCaseType
from .x8_predalles import evaluate_predalles


def evaluate_special_case(
    data: SpecialCaseInput,
    *,
    strict_blocking: bool = True,
) -> SpecialCaseResult:
    """Instrada il caso speciale verso il valutatore dedicato."""
    if data.case_type == SpecialCaseType.PREDALLES:
        return evaluate_predalles(data, strict_blocking=strict_blocking)
    if data.case_type == SpecialCaseType.COLLABORANTE:
        return evaluate_collaborante(data, strict_blocking=strict_blocking)
    if data.case_type == SpecialCaseType.CLT:
        return evaluate_clt(data, strict_blocking=strict_blocking)
    raise ValueError(f"Tipo caso speciale non gestito: {data.case_type}")
