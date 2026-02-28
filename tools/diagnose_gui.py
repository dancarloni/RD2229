"""Diagnostic helper to check environment and attempt a safe entrypoint call.

This script prints:
- RD2229_UI_TEST env
- PYTEST_CURRENT_TEST env
- which Qt bindings are importable
- the behavior of rd2229.ui_qt.app.main()
"""

import os
import sys

print("CWD=", os.getcwd())
print("PYTHONPATH=", os.environ.get("PYTHONPATH"))
print("RD2229_UI_TEST=", os.environ.get("RD2229_UI_TEST"))
print("PYTEST_CURRENT_TEST=", os.environ.get("PYTEST_CURRENT_TEST"))

# Check Qt bindings
for name in ("PyQt6", "PySide6"):
    try:
        m = __import__(name)
        v = getattr(
            m, "__version__", getattr(m, "QtCore", None) and getattr(m.QtCore, "__version__", None)
        )
        print(f"{name} import OK, version={v}")
    except Exception as e:
        print(f"{name} import FAILED: {e}")

# Import the app entrypoint and call main()
try:
    import rd2229.ui_qt.app as app

    print("Loaded rd2229.ui_qt.app")
    ret = app.main()
    print("rd2229.ui_qt.app.main() returned", ret)
except Exception as e:
    print("Error calling app.main():", e)
    raise
