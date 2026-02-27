"""Legacy re-export for verification table APIs.

The active implementation is maintained in `verification_table`.
This module remains only as compatibility import path under `src.legacy`.
"""

from __future__ import annotations

from verification_table import (
    VerificationInput,
    VerificationOutput,
    compute_ta_verification,
    compute_verification_result,
    get_concrete_properties,
    get_section_geometry,
    get_steel_properties,
)

__all__ = [
    "VerificationInput",
    "VerificationOutput",
    "compute_ta_verification",
    "compute_verification_result",
    "get_concrete_properties",
    "get_section_geometry",
    "get_steel_properties",
]
