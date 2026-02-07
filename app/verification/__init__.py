"""Compatibility shim for `app.verification` -> `src.methods`."""
from importlib import import_module as _im
from types import ModuleType
import sys as _sys

_mod = _im("src.methods")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val

_sys.modules.setdefault("app.verification", ModuleType("app.verification"))
_mod2 = _sys.modules["app.verification"]
for _name, _val in globals().items():
    setattr(_mod2, _name, _val)
