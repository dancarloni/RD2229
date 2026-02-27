"""
GUI MCP Simulator
Starts the Qt GUI in offscreen mode, simulates basic user interactions via QTest,
captures screenshots for each module and logs exceptions.
"""

import logging
import os
import sys
import time
import traceback

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from modules.registry import ModuleRegistry
from src.ui.qt.services import get_services

LOG_DIR = "logs/gui_mcp"
SCREEN_DIR = os.path.join(LOG_DIR, "screenshots")
os.makedirs(SCREEN_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("gui_mcp")


def grab_and_save(widget, name: str) -> str:
    path = os.path.join(SCREEN_DIR, f"{name}.png")
    try:
        pix = widget.grab()
        pix.save(path)
        logger.info("Saved screenshot %s", path)
    except Exception:
        logger.exception("Failed to capture %s", name)
    return path


def main() -> int:
    app = QApplication.instance() or QApplication([])

    registry = ModuleRegistry(package="src.ui.qt")
    services = get_services()

    results = {
        "started": True,
        "errors": {},
        "screenshots": [],
    }

    # Try to open the module selector first
    try:
        factory = registry.get_factory("module_selector")
        assert factory is not None
        selector = factory(master=None, project_service=services.project_service, registry=registry)
        selector.resize(1000, 700)
        selector.show()
        app.processEvents()
        QTest.qWait(200)
        results["screenshots"].append(grab_and_save(selector, "module_selector"))
    except Exception as e:
        logger.exception("module_selector failed to instantiate: %s", e)
        results["errors"]["module_selector"] = traceback.format_exc()

    # Iterate all discovered modules and open them
    for spec in registry.get_specs():
        key = spec.key
        if key == "module_selector":
            continue
        try:
            factory = registry.get_factory(key)
            if not factory:
                logger.warning("No factory for %s", key)
                results["errors"][key] = "missing factory"
                continue
            win = factory(master=None, project_service=services.project_service, registry=registry)
            # Some factories return QWidget subclasses, ensure visible
            try:
                win.resize(900, 600)
            except Exception:
                pass
            try:
                win.show()
            except Exception:
                pass
            app.processEvents()
            QTest.qWait(200)
            fname = f"module_{key}"
            results["screenshots"].append(grab_and_save(win, fname))
            # Simulate a couple of interactions: focus, click center
            try:
                widget = win
                rect = widget.rect()
                center = rect.center()
                QTest.mouseClick(widget, Qt.LeftButton, Qt.NoModifier, center)
                app.processEvents()
                QTest.qWait(100)
                grab_and_save(win, f"module_{key}_after_click")
            except Exception:
                # not all widgets accept mouseClick at top-level
                logger.debug("No clickable area for %s", key)
            try:
                win.close()
            except Exception:
                pass
            app.processEvents()
            QTest.qWait(80)
        except Exception as e:
            logger.exception("Module %s interaction failed: %s", key, e)
            results["errors"][key] = traceback.format_exc()

    # Give a small delay for any final events
    QTest.qWait(200)

    out = os.path.join(LOG_DIR, "mcp_run_summary.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("Errors:\n")
        for k, v in results["errors"].items():
            f.write(f"--- {k} ---\n{v}\n")
        f.write("\nScreenshots:\n")
        for s in results["screenshots"]:
            f.write(s + "\n")

    logger.info("MCP run finished, summary written to %s", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
