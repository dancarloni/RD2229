"""PyQt6 GUI entry point for RD2229.

Avvio::

    python -m src.ui.modern.app
    rd2229-gui          # after installation

Richiede PyQt6::

    pip install "rd2229[gui]"

Se PyQt6 non è installato il modulo stampa un messaggio utile ed esce con
codice 2 senza crashare.  Se la variabile d'ambiente ``RD2229_UI_TEST`` è
impostata, l'event loop non viene avviato e la funzione restituisce 0
immediatamente (utile per smoke-test in CI headless).
"""

from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.plugins import PluginSpec  # noqa: F401

logger = logging.getLogger(__name__)


def _build_main_window(plugins: list[PluginSpec]) -> object:  # type: ignore[type-arg]
    """Build and return a plugin-driven QMainWindow.

    The window is wired entirely from *plugins*:
    - Sidebar navigation grouped by ``plugin.category``.
    - Menu bar with one menu per category; actions from ``plugin.actions``.
    - Central stacked area ready to host plugin widgets.
    - Status bar with ready message.
    """
    from collections import defaultdict
    from collections.abc import Callable

    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QMenu,
        QMessageBox,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )

    class PluginMainWindow(QMainWindow):
        def __init__(self, plugin_specs: list[PluginSpec]) -> None:
            super().__init__()
            self.setWindowTitle("RD2229 v0.1.0")
            self.resize(1180, 760)
            self._plugins = plugin_specs
            self._setup_ui()
            self._populate_from_plugins()
            self.statusBar().showMessage("RD2229 v0.1.0 — Pronto")

        def _setup_ui(self) -> None:
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QHBoxLayout(central)

            # Sidebar (left): navigation list
            self._sidebar = QListWidget()
            self._sidebar.setFixedWidth(230)
            self._sidebar.currentRowChanged.connect(self._on_nav_changed)

            # Content area (right): stacked pages
            right_pane = QWidget()
            right_layout = QVBoxLayout(right_pane)
            self._stack = QStackedWidget()
            right_layout.addWidget(self._stack)

            main_layout.addWidget(self._sidebar)
            main_layout.addWidget(right_pane, 1)

            # Mapping: sidebar row index → PluginSpec (populated in _populate_from_plugins)
            self._row_to_plugin: dict[int, PluginSpec] = {}

        def _populate_from_plugins(self) -> None:
            """Build sidebar entries, menus and stacked pages from plugin specs."""
            categories: dict[str, list[PluginSpec]] = defaultdict(list)
            for plugin in self._plugins:
                categories[plugin.category or "general"].append(plugin)

            menu_bar = self.menuBar()
            if menu_bar is None:
                return

            row = 0
            for category, cat_plugins in sorted(categories.items()):
                cat_menu: QMenu = menu_bar.addMenu(category.capitalize())

                for plugin in cat_plugins:
                    label = f"{plugin.icon}  {plugin.title}".strip()
                    self._sidebar.addItem(label)
                    self._row_to_plugin[row] = plugin
                    row += 1

                    # Placeholder page for this plugin
                    page = QWidget()
                    page_layout = QVBoxLayout(page)
                    page_layout.addWidget(QLabel(f"<b>{plugin.title}</b><br/><i>{plugin.description}</i>"))
                    self._stack.addWidget(page)

                    # Populate category menu from plugin actions
                    for action_spec in plugin.actions:
                        action_label = (
                            f"{action_spec.icon}  {action_spec.label}".strip() if action_spec.icon else action_spec.label
                        )
                        qt_action = cat_menu.addAction(action_label)
                        if action_spec.handler is not None:
                            _handler: Callable[..., object] = action_spec.handler
                            qt_action.triggered.connect(
                                lambda _checked=False, h=_handler, s=action_spec: self._run_action_with_spec(h, s)
                            )

            if self._plugins:
                self._sidebar.setCurrentRow(0)

        def _on_nav_changed(self, index: int) -> None:
            if index >= 0:
                self._stack.setCurrentIndex(index)
                plugin = self._row_to_plugin.get(index)
                msg = plugin.title if plugin else f"Item {index}"
                self.statusBar().showMessage(msg)

        def _run_action(self, handler: Callable[..., object]) -> None:
            try:
                result = handler()
                QMessageBox.information(self, "Risultato", str(result))
            except Exception as exc:
                logger.exception("Action handler error: %s", exc)
                QMessageBox.critical(self, "Errore", str(exc))

        def _run_action_with_spec(self, handler: Callable[..., object], spec: object) -> None:
            """Run an action handler prompting for params declared in `spec`.

            Supports basic ParamSpec types: 'file' and 'dir'.
            """
            from PyQt6.QtWidgets import QFileDialog

            try:
                params = []
                for p in getattr(spec, "params", []) or []:
                    ptype = getattr(p, "type", "")
                    label = getattr(p, "label", p.name if hasattr(p, "name") else "Select")
                    if ptype == "file":
                        path, _ = QFileDialog.getOpenFileName(self, label)
                        if not path and getattr(p, "required", False):
                            QMessageBox.information(self, "Annullato", "Operazione annullata dall'utente.")
                            return
                        params.append(path)
                    elif ptype == "dir":
                        path = QFileDialog.getExistingDirectory(self, label)
                        if not path and getattr(p, "required", False):
                            QMessageBox.information(self, "Annullato", "Operazione annullata dall'utente.")
                            return
                        params.append(path)
                    else:
                        # Unknown param type: ask via a simple input dialog
                        from PyQt6.QtWidgets import QInputDialog

                        text, ok = QInputDialog.getText(self, label, label)
                        if not ok and getattr(p, "required", False):
                            QMessageBox.information(self, "Annullato", "Operazione annullata dall'utente.")
                            return
                        params.append(str(text))

                result = handler(*params)
                QMessageBox.information(self, "Risultato", str(result))
            except Exception as exc:
                logger.exception("Action handler error: %s", exc)
                QMessageBox.critical(self, "Errore", str(exc))

    return PluginMainWindow(plugins)


def main() -> int:
    """Avvia la GUI PyQt6.

    Returns:
        0  – successo (o test mode)
        1  – errore di runtime
        2  – PyQt6 non installato
    """
    try:
        from PyQt6.QtWidgets import QApplication  # noqa: F401
    except ImportError:
        print(
            "Errore: PyQt6 non è installato.\n"
            "Installa la dipendenza opzionale GUI:\n"
            "    pip install 'rd2229[gui]'\n"
            "oppure direttamente:\n"
            "    pip install 'PyQt6>=6.4'",
            file=sys.stderr,
        )
        return 2

    # Allow CI smoke-tests without starting the event loop
    if os.environ.get("RD2229_UI_TEST"):
        return 0

    try:
        from pathlib import Path

        import yaml  # type: ignore[import]
        from PyQt6.QtWidgets import QApplication

        from src.plugins.loader import load_all_plugins

        # Load app config for plugin discovery settings
        plugin_cfg: dict[str, object] = {}
        config_path = Path(__file__).resolve().parents[2] / "config" / "app.yml"
        if config_path.exists():
            with config_path.open(encoding="utf-8") as fh:
                app_cfg = yaml.safe_load(fh) or {}
                plugin_cfg = app_cfg.get("plugins", {})  # type: ignore[assignment]

        plugins = load_all_plugins(plugin_cfg)  # type: ignore[arg-type]
        if not plugins:
            logger.warning("No plugins loaded; check config or plugins/ directory.")

        app = QApplication.instance() or QApplication(sys.argv)
        window = _build_main_window(plugins)
        window.show()  # type: ignore[attr-defined]
        return app.exec()  # type: ignore[return-value]
    except Exception as exc:
        logger.exception("GUI error: %s", exc)
        print(f"GUI error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
