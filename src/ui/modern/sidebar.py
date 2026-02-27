"""Helpers to build dynamic sidebar/toolbar entries from feature registry."""

from __future__ import annotations

from src.ui.modern.features.registry import FeatureSpec, get_all


def list_enabled_features() -> list[FeatureSpec]:
    """Return enabled features ordered by registry order."""
    return [feature for feature in get_all() if feature.enabled]


def build_sidebar_labels() -> list[str]:
    """Return labels ready for sidebar rendering."""
    return [f"{feature.icon} {feature.label}".strip() for feature in list_enabled_features()]
