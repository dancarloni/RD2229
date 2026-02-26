import os
import sys

# Ensure top-level packages (like sections_app) are importable when running as module
base = os.path.dirname(os.path.dirname(__file__))
if base not in sys.path:
    sys.path.insert(0, base)

from sections_app.app import run_app

if __name__ == "__main__":
    run_app()
