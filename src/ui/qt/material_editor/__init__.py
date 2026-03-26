"""Material Editor package — exports EditorMaterialeWidget from parent module.

This package exists alongside src/ui/qt/material_editor.py (the module file).
We re-export EditorMaterialeWidget from the module for compatibility.
"""

from __future__ import annotations

# Work around package/module naming conflict by importing from the actual module
# The real implementation is in src.ui.qt.material_editor (the .py file)
# But Python treats src.ui.qt.material_editor as this package (the __init__.py)
# Solution: Import using absolute path and re-export

try:
    from src.ui.qt.material_editor import EditorMaterialeWidget

    __all__ = ["EditorMaterialeWidget"]
except (ImportError, ModuleNotFoundError):
    # If the above fails, try importing from controller or other modules in this package
    try:
        from .controller import EditorMaterialeWidget  # type: ignore

        __all__ = ["EditorMaterialeWidget"]
    except (ImportError, ModuleNotFoundError):
        __all__ = []
