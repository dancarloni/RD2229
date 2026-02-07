"""Compatibility shim for legacy imports from `verification_table`.

This module re-exports a small set of stable names from the new `app`
package to preserve backwards compatibility. Implementation lives in
`app.domain`, `app.verification` and `app.ui`.
"""

from __future__ import annotations

import logging
from typing import List

from app.domain.materials import get_concrete_properties, get_steel_properties

# Re-export a small set of stable names for backward compatibility
from app.domain.models import VerificationInput, VerificationOutput
from app.domain.sections import get_section_geometry
from app.ui.verification_table_app import COLUMNS, VerificationTableApp, VerificationTableWindow
from app.verification.engine_adapter import compute_with_engine
from app.verification.methods_sle import compute_sle_verification
from app.verification.methods_slu import compute_slu_verification
from app.verification.methods_ta import compute_ta_verification

# Logger and deprecation warning emitted at import time
logger = logging.getLogger(__name__)
logger.warning(
    "verification_table is deprecated; import from 'app' package "
    "(e.g., 'app.domain'/'app.verification'/'app.ui') instead."
)

__all__: List[str] = [
    "VerificationInput",
    "VerificationOutput",
    "get_section_geometry",
    "get_concrete_properties",
    "get_steel_properties",
    "compute_with_engine",
    "compute_verification_result",
    "compute_ta_verification",
    "compute_slu_verification",
    "compute_sle_verification",
    "VerificationTableApp",
    "VerificationTableWindow",
    "COLUMNS",
]

# Backwards-compatibility alias (used by legacy tests and external monkeypatches)
_compute_with_engine = compute_with_engine


def compute_verification_result(
    _input: VerificationInput,
    section_repository: object | None = None,
    material_repository: object | None = None,
) -> VerificationOutput:
    """Compatibility wrapper mirroring original behavior.

    This wrapper calls the module-level ``_compute_with_engine`` alias so tests
    can monkeypatch it by replacing ``verification_table._compute_with_engine``.
    """
    method = (_input.verification_method or "").upper().strip()

    if method in ("TA", "SLU", "SLE"):
        engine_result = _compute_with_engine(_input, section_repository, material_repository)
        if engine_result is not None:
            return engine_result

    if method == "TA":
        return compute_ta_verification(_input, section_repository, material_repository)
    if method == "SLU":
        return compute_slu_verification(_input, section_repository, material_repository)
    if method == "SLE":
        return compute_sle_verification(_input, section_repository, material_repository)

    return VerificationOutput(
        sigma_c_max=0.0,
        sigma_c_min=0.0,
        sigma_s_max=0.0,
        asse_neutro=0.0,
        deformazioni="",
        coeff_sicurezza=0.0,
        esito="ERRORE",
        messaggi=[
            "Metodo di verifica non specificato o sconosciuto: '{}'".format(method),
            "Selezionare un metodo dalla colonna 'Metodo verifica': TA, SLU, SLE, SANT",
        ],
    )


def run_demo() -> None:
    """Launch the legacy demo window (delegates to new entrypoint)."""
    from app.entrypoints.run_demo import run_demo as _run

    _run()


if __name__ == "__main__":
    run_demo()

# End of compatibility shim. Implementation moved to `app` package.
