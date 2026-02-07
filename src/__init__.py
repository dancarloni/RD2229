"""Top-level package for the RD2229 project.

This module avoids importing subpackages at import time to prevent circular
imports during test collection. Import subpackages explicitly where needed
(e.g., ``from src import core_calculus``).
"""

__all__ = ["core_calculus", "domain", "methods", "repositories", "ui", "utils"]

__version__ = "0.1.0"
