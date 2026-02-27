"""Compatibility package: expose legacy UI modules under `src.ui.ui.*`.

Some tests and legacy shims import `src.ui.ui.<module>` while the
implementation lives in `src/legacy/ui/`. To preserve those imports we
extend this package's search path to include the legacy folder.
"""

from __future__ import annotations

import os

# Compute path to src/legacy/ui relative to this file and add it to __path__
_here = os.path.dirname(__file__)
_legacy_ui = os.path.normpath(os.path.join(_here, "..", "..", "legacy", "ui"))
if os.path.isdir(_legacy_ui) and _legacy_ui not in __path__:  # type: ignore[name-defined]
    __path__.append(_legacy_ui)  # type: ignore[name-defined]

__all__ = []
