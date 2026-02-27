# Compatibility shim: re-export methods_sle from src.methods.verification.methods_sle
# Explicit re-export to satisfy static analyzers
from src.methods.verification.methods_sle import compute_sle_verification  # type: ignore

__all__ = ["compute_sle_verification"]
from importlib import import_module as _im

_mod = _im("src.methods.verification.methods_sle")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
