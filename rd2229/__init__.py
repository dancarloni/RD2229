"""Top-level shim package to expose `src/rd2229` as `rd2229` during tests.

This file ensures imports like `rd2229.ui_qt` resolve to the code
located under `src/rd2229` without requiring installation.
"""

from __future__ import annotations

import importlib
import os

# Prepend the src/rd2229 path to this package's __path__ so submodules
# can be resolved from the source tree.
_here = os.path.dirname(__file__)
_src_rd2229 = os.path.normpath(os.path.join(_here, "..", "src", "rd2229"))
if os.path.isdir(_src_rd2229) and _src_rd2229 not in __path__:  # type: ignore[name-defined]
    __path__.insert(0, _src_rd2229)  # type: ignore[name-defined]

# Try to import top-level implementation (if present) to surface attributes
try:
    importlib.import_module("src.rd2229")
except Exception:
    # Ignore: tests only need submodule resolution
    pass

__all__ = []
