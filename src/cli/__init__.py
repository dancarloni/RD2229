"""CLI package for RD2229.

Expose a top-level `main()` to satisfy legacy imports/tests that import
`src.cli.main`.
"""

from __future__ import annotations

from .entrypoint import main  # re-export main entrypoint

__all__ = ["main"]
