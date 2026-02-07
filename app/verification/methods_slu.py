# Compatibility shim: re-export methods_slu from src.methods.verification.methods_slu
from importlib import import_module as _im
_mod = _im("src.methods.verification.methods_slu")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
