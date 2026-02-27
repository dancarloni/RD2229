"""Features package shim for src.ui.modern.features."""
from __future__ import annotations

from .registry import FeatureSpec, register, get_all, clear

__all__ = ["FeatureSpec", "register", "get_all", "clear"]
