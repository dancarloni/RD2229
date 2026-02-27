"""Compatibility shim package for rd2229.ui_qt used by tests.

Provides a minimal `services` subpackage with SettingsService and
VerificationService so tests importing `rd2229.ui_qt.services.*` succeed.
"""

from __future__ import annotations

__all__ = ["services", "app"]
