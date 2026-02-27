"""Features package shim for src.ui.modern.features."""

from __future__ import annotations

from .registry import FeatureSpec, clear, get_all, register

__all__ = ["FeatureSpec", "register", "get_all", "clear"]
