"""
MaterialTableModel — QAbstractTableModel per i materiali
"""

from typing import Any, Dict, List

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from src.ui.qt.material_editor.logic.material_validation_logic import validate as validate_material

# Ordine colonne per famiglia (usato in _rebuild_columns).
# `codice` è sempre escluso (campo interno).
_COLUMN_ORDER_BY_FAMILY: Dict[str, List[str]] = {
    "calcestruzzo": [
        "material_id",
        "nome",
        "descrizione",
        "norma_riferimento",
        "densita_kg_m3",
        "f_ck",
        "sigma_c28",
        "nu",
        "f_Rck",
        "f_cm",
        "f_ctm",
        "f_ctk005",
        "f_ctk095",
        "f_cd",
        "f_ctd",
        "E",
        "G",
        "eps_c1",
        "eps_c2",
        "eps_cu",
        "eps_cu2",
        "eps_c3",
        "eps_cu3",
        "n_plr",
        "lambda_factor",
        "eta_factor",
        "sigma_c_adm",
        "sigma_c_fless_adm",
        "tau_c0_adm",
        "tau_c1_adm",
        "tau_max_adm",
        "tau_ct_adm",
        "gamma_c",
        "alpha_cc",
        "n_omogenizzazione",
        "E_c_storico",
    ],
    "acciaio": [
        "material_id",
        "nome",
        "descrizione",
        "norma_riferimento",
        "densita_kg_m3",
        "f_yk",
        "f_uk",
        "nu",
        "f_yd",
        "f_ud",
        "E",
        "G",
        "eps_uk",
        "eps_ud",
        "gamma_s",
    ],
    "muratura": [
        "material_id",
        "nome",
        "descrizione",
        "norma_riferimento",
        "densita_kg_m3",
        "f_k",
        "f_vk0",
        "f_d",
        "f_vd",
        "E",
        "G",
        "gamma_m",
    ],
    "legno": [
        "material_id",
        "nome",
        "descrizione",
        "norma_riferimento",
        "densita_kg_m3",
        "f_mk",
        "f_t0k",
        "f_c0k",
        "f_vk",
        "f_md",
        "f_t0d",
        "f_c0d",
        "f_vd",
        "E",
        "E_05",
        "G_mean",
        "gamma_m",
        "k_mod",
    ],
    "composito": [
        "material_id",
        "nome",
        "descrizione",
        "norma_riferimento",
        "f_fk",
        "E_f",
        "f_fd",
        "E",
        "gamma_f",
    ],
}
_COLUMN_ORDER_DEFAULT: List[str] = [
    "material_id",
    "nome",
    "descrizione",
    "famiglia",
    "norma_riferimento",
]
# Colonne interne mai mostrate
_HIDDEN_COLUMNS = {"codice", "id"}


class MaterialTableModel(QAbstractTableModel):
    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.repo = repository
        self._columns: List[str] = []
        self._rebuild_columns()

    def _rebuild_columns(self):
        cols: set = set()
        for mat in self.repo.materials:
            cols.update(k for k in mat.keys() if not k.endswith("_override"))
        # Rimuovi colonne interne
        cols -= _HIDDEN_COLUMNS

        # Determina famiglia dal primo materiale
        famiglia = ""
        if self.repo.materials:
            famiglia = self.repo.materials[0].get("famiglia", "").lower()

        priority = _COLUMN_ORDER_BY_FAMILY.get(famiglia, _COLUMN_ORDER_DEFAULT)

        ordered: List[str] = []
        for k in priority:
            if k in cols:
                ordered.append(k)
                cols.discard(k)
        # Colonne rimanenti non in priority: ordine alfabetico in fondo
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
