"""RD2229 main Qt GUI entrypoint.

This entrypoint is Qt6-first on PyQt6 and falls back to PySide6 when
PyQt6 is not available in the runtime environment.
"""

import argparse
import os
import sys

from modules.registry import ModuleRegistry
from src.ui.qt.module_selector import ModuleSelectorWindow
from src.ui.qt.services import get_services

# Setup logging via bridge
from src.rd2229.logging_bridge import get_logger, setup_logging

setup_logging("DEBUG")
logger = get_logger("gui")


def run_gui() -> int:
    if os.environ.get("RD2229_UI_TEST") == "1":
        return 0

    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:  # pragma: no cover - fallback for environments with PySide6 only
        from PySide6.QtWidgets import QApplication

    parser = argparse.ArgumentParser(description="RD2229 - Structural Engineering Tool GUI (Qt)")
    parser.add_argument("--project", help="Path to a ProjectModel (YAML/JSON) to load")
    parser.add_argument("--code", help="Calculation code override (TA, SLU, etc.)")
    args, _unknown = parser.parse_known_args()

    app = QApplication(sys.argv)
    app.setApplicationName("RD2229 Structural Tool")
    app.setApplicationVersion("0.1.0")

    # Initialize Registry for Qt modules
    registry = ModuleRegistry(package="src.ui.qt")

    # Initialize Core Services
    services = get_services()

    # Handle optional project load
    if args.project:
        logger.info("Auto-loading project: %s", args.project)
        # TODO: call ProjectModel.load(args.project)

    # Main Window (Module Selector)
    selector = ModuleSelectorWindow(project_service=services.project_service, registry=registry)

    # Connect signals (Simplified router logic)
    def _on_module_request(module_key):
        logger.debug("Switching to module: %s", module_key)
        factory = registry.get_factory(module_key)
        if factory:
            # Open a new window (or switch tab/view)
            window = factory(
                master=selector,
                project_service=services.project_service,
                registry=registry,
                # Pass other dependencies...
            )
            # Toplevel-like behavior: non-modal separate window
            window.show()
        else:
            logger.error("Factory not found for key: %s", module_key)

    selector.module_requested.connect(_on_module_request)

    selector.show()
    logger.info("GUI starting...")
    return app.exec()


def main() -> int:
    """Console-script compatible entrypoint."""
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
