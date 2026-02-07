# Compatibility shim: re-export methods_ta from src.methods.verification.methods_ta
from importlib import import_module as _im
_mod = _im("src.methods.verification.methods_ta")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
