"""DEPRECATED shim — use `apps.sections.shear_factors` (canonical).

This module is kept only for backward compatibility with legacy import
paths (e.g. `shear_factors_module.shear_factors`). It re-exports the
canonical implementation and emits a DeprecationWarning on import.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Deprecated module 'shear_factors_module.shear_factors' — use 'apps.sections.shear_factors' instead",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical implementation
from apps.sections.shear_factors import DEFAULT_SHEAR_FACTORS, get_default_shear_factor

__all__ = ["DEFAULT_SHEAR_FACTORS", "get_default_shear_factor"]
