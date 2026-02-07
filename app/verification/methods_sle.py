# Compatibility shim: re-export methods_sle from src.methods.verification.methods_sle
from importlib import import_module as _im
_mod = _im("src.methods.verification.methods_sle")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
