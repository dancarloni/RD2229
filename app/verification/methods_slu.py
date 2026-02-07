# Compatibility shim: re-export methods_slu from src.methods.verification.methods_slu
# Explicit re-export to satisfy static analyzers
from src.methods.verification.methods_slu import compute_slu_verification  # type: ignore

__all__ = ["compute_slu_verification"]
from importlib import import_module as _im

_mod = _im("src.methods.verification.methods_slu")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
