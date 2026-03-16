"""Warning codes strutturati per Fase X8."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class X8WarningCode(StrEnum):
    """Codici warning ufficiali del modulo X8."""

    OUT_OF_V1_SCOPE = "X8-SPC-001"
    FALLBACK_SIMPLIFIED = "X8-SPC-002"
    ADVANCED_MODEL_REQUIRED = "X8-SPC-003"


@dataclass(frozen=True)
class X8Warning:
    """Warning strutturato serializzabile per report/tracciabilita."""

    code: X8WarningCode
    severity: str
    norm_ref: str
    message: str

    def render(self) -> str:
        return f"{self.code}:{self.severity}::{self.norm_ref}::{self.message}"


def make_warning(
    code: X8WarningCode,
    *,
    message: str,
    severity: str = "WARN",
    norm_ref: str = "X8-CONTRACT",
) -> str:
    """Crea warning codificato X8 in formato testuale stabile."""
    return X8Warning(
        code=code,
        severity=severity.upper(),
        norm_ref=norm_ref,
        message=message,
    ).render()
