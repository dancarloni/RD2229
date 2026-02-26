"""Navigation – sidebar con stacked widget per la GUI moderna RD2229.

Richiede PySide6.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QSizePolicy,
        QStackedWidget,
        QWidget,
    )
    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False


if not _PYSIDE6_AVAILABLE:
    # Stub per import sicuro quando PySide6 non è installato
    class NavigationPanel:  # type: ignore[no-redef]
        def __init__(self, *a: Any, **kw: Any) -> None:
            pass


else:
    class NavigationPanel(QWidget):  # type: ignore[no-redef]
        """Sidebar + QStackedWidget per la navigazione tra le schede.

        Uso::

            nav = NavigationPanel(parent)
            nav.add_feature("project_info", "📂 Progetto", widget_project)
            nav.add_feature("run",          "▶️ Esegui",   widget_run)
            nav.add_feature("results",      "📊 Risultati", widget_results)
        """

        SIDEBAR_WIDTH = 200

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            self._feature_ids: list[str] = []

            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # Sidebar list
            self._sidebar = QListWidget()
            self._sidebar.setFixedWidth(self.SIDEBAR_WIDTH)
            self._sidebar.setObjectName("sidebar")
            self._sidebar.currentRowChanged.connect(self._on_row_changed)
            layout.addWidget(self._sidebar)

            # Stacked content
            self._stack = QStackedWidget()
            layout.addWidget(self._stack)

        def add_feature(self, feature_id: str, label: str, widget: Any) -> None:
            """Aggiunge una scheda alla sidebar e al pannello principale."""
            self._feature_ids.append(feature_id)
            item = QListWidgetItem(label)
            self._sidebar.addItem(item)
            self._stack.addWidget(widget)

        def select_feature(self, feature_id: str) -> None:
            """Seleziona una scheda per ID."""
            if feature_id in self._feature_ids:
                idx = self._feature_ids.index(feature_id)
                self._sidebar.setCurrentRow(idx)

        def _on_row_changed(self, row: int) -> None:
            if 0 <= row < self._stack.count():
                self._stack.setCurrentIndex(row)
