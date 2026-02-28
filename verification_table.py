"""Shim module for `verification_table`.

The full legacy implementation has been moved to `src.legacy.verification_table`.
This shim lazily imports the legacy module on first attribute access so that
headless imports (e.g. in CI or non-GUI contexts) don't fail at import time.
"""

from __future__ import annotations

import importlib
import warnings
from types import ModuleType

_LEGACY_MODULE = "src.legacy.ui.verification_table_app"


# Prefer modern, non-GUI implementations for core domain helpers so tests
# can import them without forcing the legacy GUI module to be parsed.
try:
    from app.domain.models import VerificationInput, VerificationOutput  # type: ignore
except Exception:
    try:
        from src.domain.domain.models import VerificationInput, VerificationOutput  # type: ignore
    except Exception:
        VerificationInput = None  # type: ignore
        VerificationOutput = None  # type: ignore

try:
    from app.domain.sections import get_section_geometry  # type: ignore
except Exception:
    try:
        from src.domain.domain.sections import get_section_geometry  # type: ignore
    except Exception:
        get_section_geometry = None  # type: ignore

try:
    from app.domain.materials import get_concrete_properties, get_steel_properties  # type: ignore
except Exception:
    try:
        from src.domain.domain.materials import (  # type: ignore
            get_concrete_properties,
            get_steel_properties,
        )
    except Exception:
        get_concrete_properties = None  # type: ignore
        get_steel_properties = None  # type: ignore

try:
    from app.verification.dispatcher import (  # type: ignore
        compute_verification_result as _real_compute,
    )
except Exception:
    try:
        from src.methods.verification.dispatcher import (  # type: ignore
            compute_verification_result as _real_compute,
        )
    except Exception:
        _real_compute = None  # type: ignore


def compute_verification_result(*args: object, **kwargs: object) -> object:
    """Legacy shim wrapper used by dispatcher tests.

    First invokes ``_compute_with_engine`` (which tests can monkeypatch). If it
    returns a non-``None`` value, that result is returned directly. Otherwise we
    delegate to the real dispatcher implementation if available.
    """
    # prefer stubbed engine path
    try:
        res = _compute_with_engine(*args, **kwargs)
    except Exception:
        res = None
    if res is not None:
        return res
    if _real_compute is not None:
        return _real_compute(*args, **kwargs)
    raise RuntimeError("no verification engine available")


# legacy stub used by dispatcher tests; real computation happens elsewhere
# tests may monkeypatch this attribute, so it must exist at import time.
def _compute_with_engine(*args: object, **kwargs: object) -> object | None:
    """Placeholder that mimics legacy function signature.

    Returns ``None`` by default; patched by tests when needed.
    """
    return None


def _load_legacy() -> ModuleType:
    mod = importlib.import_module(_LEGACY_MODULE)
    # Export public names into this module's globals for backward compatibility
    for name in dir(mod):
        if name.startswith("_"):
            continue
        try:
            globals()[name] = getattr(mod, name)
        except Exception:
            # Defensive: skip problematic attributes
            pass
    return mod


def __getattr__(name: str):
    warnings.warn(
        "verification_table has moved to src.legacy.verification_table; "
        "importing through this shim is deprecated.",
        DeprecationWarning,
        stacklevel=2,
    )
    mod = _load_legacy()
    try:
        return getattr(mod, name)
    except AttributeError:
        raise AttributeError(f"module 'verification_table' has no attribute '{name}'") from None


def __dir__():
    # Avoid importing the legacy module during simple introspection.
    # Only expose the shim's public names until an attribute is requested.
    return [n for n in globals().keys() if not n.startswith("_")]
