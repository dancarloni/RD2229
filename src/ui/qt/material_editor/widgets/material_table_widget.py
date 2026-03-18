"""
MaterialTableWidget — Tabella materiali ordinabile, filtrabile, drag&drop
"""

from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QMenu, QAction
from PySide6.QtCore import Qt, Signal

class MaterialTableWidget(QTableView):
    # signal: column (int) or key (str), selected rows list
    batchEditRequested = Signal(object, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # enable custom context menu for batch editing
        self.setContextMenuPolicy(Qt.CustomContextMenu)
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
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    table = MaterialTableWidget()
    table.show()
    sys.exit(app.exec())
