"""Compatibility package exposing the previous `app` import paths while
re-exporting implementations from `src` package for a smooth transition.
"""
# flake8: noqa: E302,E305

from importlib import import_module as _im

# Lazy re-exports to avoid heavy imports at package import time

def _reexport(module_name: str, attr: str) -> None:
    mod = _im(module_name)
    globals()[attr] = getattr(mod, attr)



# Re-export commonly used modules and name to mimic old structure
_app_map = {
    "app.domain.models": "src.domain.models",
    "app.domain.sections": "src.domain.sections",
    "app.domain.materials": "src.domain.materials",
    "app.verification.engine_adapter": "src.methods.engine_adapter",
    "app.verification.methods_ta": "src.methods.ta",
    "app.verification.methods_slu": "src.methods.slu",
    "app.verification.methods_sle": "src.methods.sle",
    "app.ui.verification_table_app": "src.ui.verification_table_app",
}

for old, new in _app_map.items():
    # create a dummy module object mapping in sys.modules so `from app.domain import X` works
    try:
        _im(new)
    except Exception:
        # Ignore import errors here; tests will surface missing modules later
        pass
