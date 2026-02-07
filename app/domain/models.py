# Compatibility shim: re-export models from src.domain.domain.models
# Explicit re-exports to satisfy static analyzers
from src.domain.domain.models import VerificationInput, VerificationOutput  # type: ignore
__all__ = ["VerificationInput", "VerificationOutput"]
from importlib import import_module as _im

_mod = _im("src.domain.domain.models")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
