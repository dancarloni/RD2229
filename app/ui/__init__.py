"""Compatibility shim for `app.ui` -> `src.ui`."""
from importlib import import_module as _im
from types import ModuleType
import sys as _sys

_mod = _im("src.ui")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val

_sys.modules.setdefault("app.ui", ModuleType("app.ui"))
_mod2 = _sys.modules["app.ui"]
for _name, _val in globals().items():
    setattr(_mod2, _name, _val)
