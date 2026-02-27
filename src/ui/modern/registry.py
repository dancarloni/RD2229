"""Compatibility shim: re-export feature registry API.

Some parts of the code import `src.ui.modern.registry` while the
actual implementation lives in `src.ui.modern.features.registry`.
This file provides a minimal re-export to preserve backwards
compatibility until imports are standardized.
"""

from __future__ import annotations

from src.ui.modern.features.registry import (
    FeatureSpec,
    register,
    get_all,
    clear,
)

__all__ = ["FeatureSpec", "register", "get_all", "clear"]
