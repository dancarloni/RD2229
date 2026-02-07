# Compatibility shim: re-export core.* from src.core_calculus
from importlib import import_module as _im
_mod = _im("src.core_calculus.core")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
