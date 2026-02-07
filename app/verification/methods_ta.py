# Compatibility shim: re-export methods_ta from src.methods.verification.methods_ta
# Explicit re-export to satisfy static analyzers
from src.methods.verification.methods_ta import compute_ta_verification  # type: ignore
__all__ = ["compute_ta_verification"]
from importlib import import_module as _im

_mod = _im("src.methods.verification.methods_ta")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
