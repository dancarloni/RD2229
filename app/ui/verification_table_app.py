# Compatibility shim: re-export verification_table_app from src.ui.ui.verification_table_app
# Explicit re-exports to satisfy static analyzers
from src.ui.ui.verification_table_app import (  # type: ignore
    COLUMNS,
    VerificationTableApp,
    VerificationTableWindow,
)

__all__ = ["COLUMNS", "VerificationTableApp", "VerificationTableWindow"]
from importlib import import_module as _im

_mod = _im("src.ui.ui.verification_table_app")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
