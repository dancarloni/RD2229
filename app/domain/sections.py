# Compatibility shim: re-export sections from src.domain.domain.sections
from importlib import import_module as _im
_mod = _im("src.domain.domain.sections")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
