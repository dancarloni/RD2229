# Compatibility shim: re-export materials from src.domain.domain.materials
from importlib import import_module as _im

_mod = _im("src.domain.domain.materials")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
