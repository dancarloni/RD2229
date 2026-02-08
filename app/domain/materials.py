# Compatibility shim: re-export materials from src.domain.domain.materials
# Explicit re-exports to satisfy static analyzers
from src.domain.domain.materials import (  # type: ignore
    get_concrete_properties,
    get_steel_properties,
)

__all__ = ["get_concrete_properties", "get_steel_properties"]
from importlib import import_module as _im

_mod = _im("src.domain.domain.materials")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
