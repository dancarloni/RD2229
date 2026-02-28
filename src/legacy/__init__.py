"""Legacy Tkinter modules package.

Contains deprecated Tkinter-based modules kept for archival/compatibility.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "The `src.legacy` package contains deprecated Tkinter GUI code "
    "and should not be imported by active application logic.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = []
"""
Legacy code — original project modules preserved unchanged.

DO NOT EDIT FILES IN THIS FOLDER.

This folder contains all the original Python scripts and data files
from the root directory, preserved for backward compatibility during
the restructuring process.
"""
