# Compatibility shim: re-export from src.ui.ui.rebar_calculator
# Explicit re-exports to satisfy static analyzers
from src.ui.ui.rebar_calculator import RebarCalculatorWindow  # type: ignore

__all__ = ["RebarCalculatorWindow"]
from importlib import import_module as _im

_mod = _im("src.ui.ui.rebar_calculator")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
