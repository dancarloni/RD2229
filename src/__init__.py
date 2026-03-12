"""
Root package of the restructured engineering verification framework.

This package contains:
- The legacy code (in src/legacy/)
- The new modular architecture (calc, materials, elements, codes, actions, report, config, tools, tests)
- The existing core_calculus, domain, methods, repositories, ui, and utils modules

This module avoids importing subpackages at import time to prevent circular
imports during test collection. Import subpackages explicitly where needed
(e.g., ``from src import core_calculus``).
"""

__all__ = [
    "core_calculus",
    "domain",
    "methods",
    "repositories",
    "ui",
    "utils",
    "calc",
    "materials",
    "elements",
    "codes",
    "actions",
    "report",
    "geotecnica",
    "esistenti",
    "config",
    "tools",
    "tests",
    "legacy",
    "seismic",
]

__version__ = "0.1.0"
