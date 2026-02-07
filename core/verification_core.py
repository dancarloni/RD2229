# Compatibility shim mapping to src.core_calculus.verification_core
from importlib import import_module as _im

_mod = _im("src.core_calculus.verification_core")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
