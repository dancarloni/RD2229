# Compatibility shim: re-export compute_with_engine from src.methods.verification.engine_adapter
from importlib import import_module as _im

_mod = _im("src.methods.verification.engine_adapter")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
