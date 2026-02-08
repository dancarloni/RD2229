"""Compatibility shim for `app.verification` -> `src.methods`."""

import sys as _sys
from importlib import import_module as _im
from types import ModuleType

_mod = _im("src.methods")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val

# Explicit re-exports to help static type checkers
from src.methods.verification.engine_adapter import (  # type: ignore  # noqa: E402
    compute_with_engine,
)
from src.methods.verification.methods_sle import (  # type: ignore  # noqa: E402
    compute_sle_verification,
)
from src.methods.verification.methods_slu import (  # type: ignore  # noqa: E402
    compute_slu_verification,
)
from src.methods.verification.methods_ta import (  # type: ignore  # noqa: E402
    compute_ta_verification,
)

__all__ = [
    "compute_ta_verification",
    "compute_slu_verification",
    "compute_sle_verification",
    "compute_with_engine",
]

_sys.modules.setdefault("app.verification", ModuleType("app.verification"))
_mod2 = _sys.modules["app.verification"]
for _name, _val in globals().items():
    setattr(_mod2, _name, _val)
