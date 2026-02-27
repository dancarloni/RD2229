"""RD2229 Module Selector (Qt6 implementation)."""

import logging

try:
    from PyQt6.QtCore import Qt, pyqtSignal as Signal
    from PyQt6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover - fallback for environments with PySide6 only
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )

from typing import Any

_ALIGN_RIGHT: Any = getattr(Qt.AlignmentFlag, "AlignRight", getattr(Qt, "AlignRight", 0))

logger = logging.getLogger(__name__)


class ModuleSelectorWindow(QMainWindow):
    """Main shell for module navigation and discovery."""

    module_requested = Signal(str)

    def __init__(self, project_service=None, registry=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RD2229 - Module Selector")
        self.setMinimumSize(900, 600)
        self.project_service = project_service
        self.registry = registry
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left Sidebar
        self.sidebar_layout = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar_frame.setFixedWidth(210)
        sidebar_frame.setLayout(self.sidebar_layout)

        self.sidebar_list = QListWidget()
        self.sidebar_list.itemClicked.connect(self._on_sidebar_click)
        self.sidebar_layout.addWidget(QLabel("<b>DASHBOARD</b>"))
        self.sidebar_layout.addWidget(self.sidebar_list)

        refresh_btn = QPushButton("Aggiorna Moduli")
        refresh_btn.clicked.connect(self._refresh_modules)
        self.sidebar_layout.addWidget(refresh_btn)

        main_layout.addWidget(sidebar_frame)

        # Right content area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.flow_layout = QVBoxLayout(container)
        self.flow_layout.setSpacing(8)
        self.flow_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll.setWidget(container)
        main_layout.addWidget(self.scroll)

        self._create_menubar()
        self._refresh_modules()

    def _create_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Progetto")
        file_menu.addAction("Nuovo", lambda: self.module_requested.emit("project_editor"))
        file_menu.addAction("Apri", lambda: self.module_requested.emit("project_editor"))
        file_menu.addAction("Salva", lambda: self.module_requested.emit("project_editor"))
        file_menu.addSeparator()
        file_menu.addAction("Esci", self.close)

        tools_menu = menubar.addMenu("&Strumenti")
        tools_menu.addAction(
            "Materials Editor", lambda: self.module_requested.emit("material_editor")
        )
        tools_menu.addAction(
            "Section Manager", lambda: self.module_requested.emit("section_manager")
        )
        tools_menu.addAction(
            "Pipeline Runner", lambda: self.module_requested.emit("pipeline_runner")
        )

        help_menu = menubar.addMenu("&?")
        help_menu.addAction(
            "Informazioni",
            lambda: QMessageBox.about(self, "About", "RD2229 Structural Tool v0.1.0"),
        )

    def _refresh_modules(self):
        self.sidebar_list.clear()
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.registry:
            logger.warning("No registry provided to ModuleSelectorWindow")
            placeholder = QLabel("<i>Registry non caricato</i>")
            self.flow_layout.addWidget(placeholder)
            return

        for spec in self.registry.get_specs():
            key = spec.key
            if key == "module_selector":
                continue
            self.sidebar_list.addItem(spec.name)
            self._add_module_card(key, spec)
        try:
            w = self.scroll.widget()
            if w:
                w.updateGeometry()
                w.adjustSize()
            self.scroll.update()
            self.scroll.repaint()
        except Exception:
            logger.debug("Post-refresh layout update failed", exc_info=True)

    def _add_module_card(self, key, spec):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            "QFrame { background-color: #f9f9f9; border: 1px solid #ccc; "
            "border-radius: 8px; margin: 4px; padding: 10px; }"
        )
        layout = QVBoxLayout(card)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(80)

        title = QLabel(f"<b>{spec.name}</b>")
        title.setStyleSheet("font-size: 14px;")

        desc = QLabel(spec.description or "Nessuna descrizione.")
        desc.setWordWrap(True)

        btn = QPushButton("Apri modulo")
        btn.setFixedWidth(120)
        btn.clicked.connect(lambda _, k=key: self.module_requested.emit(k))

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(btn, 0, _ALIGN_RIGHT)

        self.flow_layout.addWidget(card)

    def _on_sidebar_click(self, item):
        pass


MODULE_SPEC = {
    "key": "module_selector",
    "name": "Module Selector",
    "description": "Sidebar e selettore moduli dinamico (Qt6)",
    "category": "core",
}


def create_module(master=None, **context):
    return ModuleSelectorWindow(
        project_service=context.get("project_service"),
        registry=context.get("registry"),
        parent=master,
    )


if __name__ == "__main__":
    import sys

    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:  # pragma: no cover
        from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ModuleSelectorWindow()
    window.show()
    sys.exit(app.exec())
