"""Codici warning strutturati per la Fase X6.

Fornisce un formato stabile per warning codificati con severita e
riferimento normativo, mantenendo compatibilita con warning legacy testuali.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WarningCode:
    """Descrive un warning codificato X6."""

    code: str
    severity: str
    norm_ref: str
    message: str

    def render(self) -> str:
        return f"{self.code}:{self.severity}::{self.norm_ref}::{self.message}"


def make_warning_code(
    section: str,
    index: int,
    *,
    severity: str = "WARN",
    norm_ref: str = "GENERIC",
    message: str,
) -> str:
    """Crea un warning codificato nel formato X6-<SECTION>-NNN."""
    normalized_section = section.upper().replace("_", "-")
    return WarningCode(
        code=f"X6-{normalized_section}-{index:03d}",
        severity=severity.upper(),
        norm_ref=norm_ref,
        message=message,
    ).render()


def normalize_warnings(raw_warnings: list[str]) -> list[str]:
    """Normalizza warning legacy in codici X6, preservando quelli gia codificati."""
    normalized: list[str] = []
    for index, warning in enumerate(raw_warnings, start=1):
        if warning.startswith("X6-"):
            normalized.append(warning)
            continue
        normalized.append(
            make_warning_code(
                "REP",
                index,
                severity="WARN",
                norm_ref="TRACE",
                message=warning,
            )
        )
    return normalized


def infer_contract_warnings(
    *,
    element_count: int,
    has_trace: bool,
    existing_structure: bool,
    lc: str | None,
) -> list[str]:
    """Genera warning X6 da condizioni contrattuali note del report."""
    warnings: list[str] = []
    if element_count == 0:
        warnings.append(
            make_warning_code(
                "REP",
                901,
                severity="WARN",
                norm_ref="X6-CONTRACT",
                message="Nessun risultato elemento disponibile nel report",
            )
        )
    if not has_trace:
        warnings.append(
            make_warning_code(
                "AUD",
                1,
                severity="WARN",
                norm_ref="X6-AUDIT",
                message="Trace pipeline assente o vuota",
            )
        )
    if existing_structure and not lc:
        warnings.append(
            make_warning_code(
                "NORM",
                1,
                severity="WARN",
                norm_ref="NTC2018-§C8.5.4",
                message="Struttura esistente senza LC esplicito nel report",
            )
        )
    return warnings
