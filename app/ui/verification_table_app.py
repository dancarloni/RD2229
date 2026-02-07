# Compatibility shim: re-export verification_table_app from src.ui.ui.verification_table_app
from importlib import import_module as _im

_mod = _im("src.ui.ui.verification_table_app")
for _name, _val in vars(_mod).items():
    if not _name.startswith("_"):
        globals()[_name] = _val
