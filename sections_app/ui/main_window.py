from __future__ import annotations

import importlib
import warnings

warnings.warn(
    "sections_app.ui.main_window is deprecated and moved to src.legacy.sections_app.ui.main_window",
    DeprecationWarning,
)

def _load_legacy():
    return importlib.import_module("src.legacy.sections_app.ui.main_window")

def __getattr__(name: str):
    return getattr(_load_legacy(), name)

def __dir__():
    return dir(_load_legacy())
