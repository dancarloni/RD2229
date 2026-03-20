"""
MaterialTableModel — QAbstractTableModel per i materiali
"""

from typing import Any, List

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from src.ui.qt.material_editor.logic.material_validation_logic import validate as validate_material


class MaterialTableModel(QAbstractTableModel):
    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.repo = repository
        self._columns: List[str] = []
        self._rebuild_columns()

    def _rebuild_columns(self):
        cols = set()
        for mat in self.repo.materials:
            cols.update(k for k in mat.keys() if not k.endswith("_override"))
        # deterministic order: put priority columns first
        priority = ["codice", "descrizione", "famiglia", "norma_riferimento", "material_id", "id"]
        ordered = []
        for k in priority:
            if k in cols:
                ordered.append(k)
                cols.discard(k)
        ordered.extend(sorted(cols))
        self._columns = ordered

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.repo.materials)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            key = self._columns[col]
            mat = self.repo.materials[row]
            val = mat.get(key, "")
            return "" if val is None else str(val)
        # background highlight for incomplete materials
        if role == Qt.BackgroundRole:
            row = index.row()
            mat = self.repo.materials[row]
            try:
                res = validate_material(mat)
                if not res.get("is_complete", True):
                    return QColor(255, 250, 200)  # light yellow
            except Exception:
                pass
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._columns[section]
        return str(section + 1)

    def refresh(self):
        self.beginResetModel()
        self._rebuild_columns()
        self.endResetModel()

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        key = self._columns[column]
        reverse = order == Qt.DescendingOrder
        try:
            self.repo.sort_materials(key, reverse=reverse)
            self.layoutChanged.emit()
        except Exception:
            pass
