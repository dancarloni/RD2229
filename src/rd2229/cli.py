"""Small CLI entrypoint for running demo / quick tasks.

Installed as `rd2229-demo` via pyproject scripts entry.
"""

from __future__ import annotations

import logging


def main() -> None:
    """Run the verification demo GUI.

    This delegates to the app entrypoint which constructs the Tk window.
    """
    logging.basicConfig(level=logging.INFO)
    try:
        # direct app entrypoint
        from app.entrypoints.run_demo import run_demo

        run_demo()
    except Exception as exc:  # pragma: no cover - UI runtime
        logging.exception("Failed to launch demo: %s", exc)
        raise
