"""
RD2229 Main GUI Entrypoint (PySide6 Implementation)
Launches the Module Selector window and initializes core services.
"""

import argparse
import logging
import sys

from PySide6.QtWidgets import QApplication

from modules.registry import ModuleRegistry
from src.ui.qt.module_selector import ModuleSelectorWindow
from src.ui.qt.services import get_services

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("RD2229.GUI")


def run_gui():
    parser = argparse.ArgumentParser(description="RD2229 - Structural Engineering Tool GUI (Qt)")
    parser.add_argument("--project", help="Path to a ProjectModel (YAML/JSON) to load")
    parser.add_argument("--code", help="Calculation code override (TA, SLU, etc.)")
    args = parser.parse_args()

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
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
