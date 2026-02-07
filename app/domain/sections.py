# Compatibility shim: re-export sections from src.domain.domain.sections
# Explicit re-exports to satisfy static analyzers
from src.domain.domain.sections import get_section_geometry  # type: ignore
__all__ = ["get_section_geometry"]
from importlib import import_module as _im

_mod = _im("src.domain.domain.sections")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
