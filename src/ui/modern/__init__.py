"""Compatibility shim package for `src.ui.modern` after GUI removals.

Exports a minimal `services`, `viewmodels` and `features` submodules
so tests importing `src.ui.modern.*` continue to work.
"""

from __future__ import annotations

from .services import CalculationService, PresetExecutionService, ProjectIOService

__all__ = ["ProjectIOService", "CalculationService", "PresetExecutionService"]
