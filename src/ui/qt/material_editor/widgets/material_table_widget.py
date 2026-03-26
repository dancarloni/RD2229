"""
MaterialTableWidget — Tabella materiali ordinabile, filtrabile, drag&drop
"""

try:
    from PyQt6.QtCore import Qt, pyqtSignal as Signal
    from PyQt6.QtGui import QAction
    from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QMenu, QTableView
except ImportError:
    from PySide6.QtCore import Qt, Signal  # type: ignore
    from PySide6.QtGui import QAction  # type: ignore
    from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMenu, QTableView  # type: ignore


class MaterialTableWidget(QTableView):
    # signal: column (int) or key (str), selected rows list
    batchEditRequested = Signal(object, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # enable custom context menu for batch editing
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_custom_context_menu)

    def _on_custom_context_menu(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        selected_rows = sorted({r.row() for r in self.selectionModel().selectedRows()})
        if not selected_rows:
            return
        col = index.column()
        menu = QMenu(self)
        action_batch = QAction("Modifica batch", self)

        def _on_batch():
            # emit column index and selected rows; controller will map to key
            self.batchEditRequested.emit(col, selected_rows)

        action_batch.triggered.connect(_on_batch)
        menu.addAction(action_batch)
        menu.exec(self.viewport().mapToGlobal(pos))


# Per test rapido
if __name__ == "__main__":
    import sys

    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        from PySide6.QtWidgets import QApplication  # type: ignore

    app = QApplication(sys.argv)
    table = MaterialTableWidget()
    table.show()
    sys.exit(app.exec())
