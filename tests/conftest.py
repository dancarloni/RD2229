"""pytest configuration for the tests/ directory.

The standard (CI) test suite excludes any legacy GUI tests under
``tests/legacy_tkinter`` and ``tests/legacy_qt``.  These directories contain
deprecated Tkinter- or Qt-based tests that are no longer run by default.
"""

from __future__ import annotations

# Directories to ignore during normal collection.  Placing legacy UI tests
# here keeps them available for manual execution while preventing failures
# in headless CI environments.
collect_ignore = ["legacy_tkinter", "legacy_qt"]
