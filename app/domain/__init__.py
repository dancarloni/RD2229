"""Compatibility shim for `app.domain` package re-exporting `src.domain`."""

from importlib import import_module as _im
from types import ModuleType
import sys as _sys

_mod = _im("src.domain")
# Re-export all public names
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val

# Ensure `app.domain` appears as module
_sys.modules.setdefault("app.domain", ModuleType("app.domain"))
_mod2 = _sys.modules["app.domain"]
for _name, _val in globals().items():
    setattr(_mod2, _name, _val)
