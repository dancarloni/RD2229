"""Fase X8 - Casi speciali (Predalles, Collaboranti, CLT).

Package standalone post-V1: non e collegato al dispatcher principale.
Espone API per valutazione preliminare e tracciabilita warning.
"""

from .x8_dispatcher import evaluate_special_case
from .x8_models import SpecialCaseInput, SpecialCaseResult
from .x8_warnings import X8Warning, X8WarningCode, make_warning

__all__ = [
    "SpecialCaseInput",
    "SpecialCaseResult",
    "X8Warning",
    "X8WarningCode",
    "make_warning",
    "evaluate_special_case",
]
