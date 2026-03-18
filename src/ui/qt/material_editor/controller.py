"""
MaterialEditorController — controller specifico per il Material Editor

Estende ControllerBase e coordina repository, table widget, detail frame
ed export widget. Non esegue operazioni Qt all'importazione: i collegamenti
ai widget vengono effettuati tramite i metodi `attach_*` a runtime.
"""
from typing import Optional, Any, Dict

from src.core.controller_base import ControllerBase
from src.ui.qt.material_editor.logic.material_repository import MaterialRepository
from src.ui.qt.material_editor.logic.material_export_logic import MaterialExportLogic
from src.ui.qt.material_editor.logic.material_validation_logic import validate as validate_material

class MaterialEditorController(ControllerBase):
    def __init__(self, repository: Optional[MaterialRepository] = None):
        super().__init__()
        self.repo = repository or MaterialRepository()
        self.table = None
        self.detail = None
        self.export_widget = None
        self.current_index: Optional[int] = None

    def attach_table(self, table_widget) -> None:
        """Collega la table widget al controller. Deve essere chiamato a runtime."""
        self.table = table_widget
        try:
            sel_model = self.table.selectionModel()
            sel_model.selectionChanged.connect(self._on_table_selection_changed)
            # batch edit signal if provided by the table widget
            if hasattr(self.table, 'batchEditRequested'):
                try:
                    self.table.batchEditRequested.connect(self.on_batch_edit_requested)
                except Exception:
                    pass
            # set a table model bound to the repository
            try:
                from src.ui.qt.material_editor.widgets.material_table_model import MaterialTableModel
                self.model = MaterialTableModel(self.repo)
                self.table.setModel(self.model)
                try:
                    self.table.resizeColumnsToContents()
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            # table might not support selectionModel at import-time
            pass

    def attach_detail(self, detail_frame) -> None:
        """Collega il frame dettaglio e i suoi pulsanti."""
        self.detail = detail_frame
        try:
            if hasattr(self.detail, 'save_button'):
                self.detail.save_button.clicked.connect(self.on_save_clicked)
            if hasattr(self.detail, 'cancel_button'):
                self.detail.cancel_button.clicked.connect(self.on_cancel_clicked)
            # setup Ctrl+S shortcut on the detail frame (runtime)
            try:
                from PySide6.QtGui import QKeySequence
                from PySide6.QtWidgets import QShortcut
                QShortcut(QKeySequence('Ctrl+S'), self.detail, activated=self.on_save_clicked)
            except Exception:
                pass
        except Exception:
            pass

    def attach_export(self, export_widget) -> None:
        self.export_widget = export_widget
        try:
            if hasattr(self.export_widget, 'format_combo'):
                try:
                    self.export_widget.format_combo.currentIndexChanged.connect(lambda _: self._update_export_text())
                except Exception:
                    pass
            # also listen to the high-level signal if the widget exposes it
            if hasattr(self.export_widget, 'formatChanged'):
                try:
                    self.export_widget.formatChanged.connect(lambda _: self._update_export_text())
                except Exception:
                    pass
            if hasattr(self.export_widget, 'copy_button'):
                try:
                    self.export_widget.copy_button.clicked.connect(self._on_export_copy)
                except Exception:
                    pass
            # initially populate export text if possible
            try:
                self._update_export_text()
            except Exception:
                pass
        except Exception:
            pass

    def _update_export_text(self) -> None:
        if self.export_widget is None:
            return
        try:
            # determine format (safe)
            fmt = 'HTML'
            if hasattr(self.export_widget, 'format_combo'):
                try:
                    fmt = self.export_widget.format_combo.currentText()
                except Exception:
                    fmt = 'HTML'

            # if no selection, show a template/empty-preview using model headers or defaults
            if self.current_index is None:
                mat = {}
                try:
                    if hasattr(self, 'model') and self.model is not None:
                        # derive header names from model
                        try:
                            from PySide6.QtCore import Qt
                            cols = self.model.columnCount()
                            headers = []
                            for c in range(cols):
                                try:
                                    hdr = self.model.headerData(c, Qt.Horizontal)
                                    headers.append(str(hdr) if hdr is not None else f'col_{c}')
                                except Exception:
                                    headers.append(f'col_{c}')
                            for h in headers:
                                mat[h] = ''
                        except Exception:
                            # fallback to sensible defaults
                            for h in ['codice', 'descrizione', 'norma', 'f_ck', 'gamma_c']:
                                mat[h] = ''
                    else:
                        for h in ['codice', 'descrizione', 'norma', 'f_ck', 'gamma_c']:
                            mat[h] = ''
                except Exception:
                    mat = {'codice': '', 'descrizione': '', 'norma': '', 'f_ck': '', 'gamma_c': ''}
            else:
                try:
                    mat = self.repo.materials[self.current_index]
                except Exception:
                    mat = {}

            txt = MaterialExportLogic.export(mat, fmt)
            if hasattr(self.export_widget, 'export_text'):
                self.export_widget.export_text.setPlainText(txt)
        except Exception:
            pass

    def _on_export_copy(self) -> None:
        try:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            if hasattr(self.export_widget, 'export_text'):
                clipboard.setText(self.export_widget.export_text.toPlainText())
        except Exception:
            pass

    def _on_table_selection_changed(self, selected, deselected) -> None:
        # selected is a QItemSelection; choose first index
        try:
            indexes = selected.indexes()
            if not indexes:
                self.current_index = None
                return
            # assume first column index contains row
            row = indexes[0].row()
            self.current_index = row
            self.populate_detail_from_index(row)
        except Exception:
            pass

    def populate_detail_from_index(self, idx: int) -> None:
        if idx is None or idx < 0 or idx >= len(self.repo.materials):
            return
        mat = self.repo.materials[idx]
        if self.detail is None:
            return
        # popola i campi del detail frame se esistono
        try:
            if hasattr(self.detail, 'code_edit'):
                self.detail.code_edit.setText(str(mat.get('codice', '')))
            if hasattr(self.detail, 'desc_edit'):
                self.detail.desc_edit.setText(str(mat.get('descrizione', '')))
            if hasattr(self.detail, 'norma_edit'):
                self.detail.norma_edit.setText(str(mat.get('norma', '')))
            if hasattr(self.detail, 'fck_edit'):
                self.detail.fck_edit.setText(str(mat.get('f_ck', '')))
            if hasattr(self.detail, 'gamma_c_edit'):
                self.detail.gamma_c_edit.setText(str(mat.get('gamma_c', '')))
            # impostare flag override se presente
            if hasattr(self.detail, 'fck_override'):
                self.detail.fck_override.setChecked(bool(mat.get('f_ck_override', False)))
            if hasattr(self.detail, 'gamma_c_override'):
                self.detail.gamma_c_override.setChecked(bool(mat.get('gamma_c_override', False)))
        except Exception:
            pass

        # soft validation: show warnings in the detail frame (non-blocking)
        try:
            try:
                res = validate_material(mat)
                msgs = []
                if res.get('missing'):
                    msgs.append("Campi mancanti: " + ", ".join(res.get('missing')))
                if res.get('warnings'):
                    msgs.append("Avvisi: " + "; ".join(res.get('warnings')))
                msg = ". ".join(msgs) if msgs else ""
                if hasattr(self.detail, 'set_warning'):
                    self.detail.set_warning(msg)
            except Exception:
                if hasattr(self.detail, 'set_warning'):
                    self.detail.set_warning("")
        except Exception:
            pass

    def on_save_clicked(self) -> None:
        if self.detail is None:
            return
        # raccogli dati dal dettaglio
        data: Dict[str, Any] = {}
        try:
            if hasattr(self.detail, 'code_edit'):
                data['codice'] = self.detail.code_edit.text()
            if hasattr(self.detail, 'desc_edit'):
                data['descrizione'] = self.detail.desc_edit.text()
            if hasattr(self.detail, 'norma_edit'):
                data['norma'] = self.detail.norma_edit.text()
            if hasattr(self.detail, 'fck_edit'):
                val = self.detail.fck_edit.text()
                data['f_ck'] = float(val) if val else None
            if hasattr(self.detail, 'gamma_c_edit'):
                val = self.detail.gamma_c_edit.text()
                data['gamma_c'] = float(val) if val else None
            # override flags
            if hasattr(self.detail, 'fck_override'):
                data['f_ck_override'] = bool(self.detail.fck_override.isChecked())
            if hasattr(self.detail, 'gamma_c_override'):
                data['gamma_c_override'] = bool(self.detail.gamma_c_override.isChecked())
        except Exception:
            # non blocchiamo l'interfaccia per errori di conversione
            pass

        if self.current_index is None:
            # aggiungi nuovo materiale
            self.repo.add_material(data)
            self.current_index = len(self.repo.materials) - 1
            self.emit('material_added', self.current_index, data)
        else:
            self.repo.update_material(self.current_index, data)
            self.emit('material_updated', self.current_index, data)

        # aggiorna export text se presente
        if self.export_widget is not None and hasattr(self.export_widget, 'format_combo'):
            fmt = self.export_widget.format_combo.currentText()
            txt = MaterialExportLogic.export(self.repo.materials[self.current_index], fmt)
            if hasattr(self.export_widget, 'export_text'):
                self.export_widget.export_text.setPlainText(txt)
        # refresh model if present
        try:
            if hasattr(self, 'model') and self.model is not None:
                self.model.refresh()
        except Exception:
            pass

        # after save, run soft validation and update detail warnings for the saved material
        try:
            if self.current_index is not None:
                try:
                    mat = self.repo.materials[self.current_index]
                    res = validate_material(mat)
                    msgs = []
                    if res.get('missing'):
                        msgs.append("Campi mancanti: " + ", ".join(res.get('missing')))
                    if res.get('warnings'):
                        msgs.append("Avvisi: " + "; ".join(res.get('warnings')))
                    msg = ". ".join(msgs) if msgs else ""
                    if self.detail is not None and hasattr(self.detail, 'set_warning'):
                        self.detail.set_warning(msg)
                except Exception:
                    if self.detail is not None and hasattr(self.detail, 'set_warning'):
                        self.detail.set_warning("")
        except Exception:
            pass

    def on_cancel_clicked(self) -> None:
        # ripristina valori originali
        if self.current_index is not None:
            self.populate_detail_from_index(self.current_index)
        # refresh export preview to reflect restored detail/new material
        try:
            self._update_export_text()
        except Exception:
            pass

    def start_new_material(self) -> None:
        """Prepara il dettaglio per l'inserimento di un nuovo materiale."""
        self.current_index = None
        if self.detail is None:
            return
        try:
            if hasattr(self.detail, 'code_edit'):
                self.detail.code_edit.clear()
            if hasattr(self.detail, 'desc_edit'):
                self.detail.desc_edit.clear()
            if hasattr(self.detail, 'norma_edit'):
                self.detail.norma_edit.clear()
            if hasattr(self.detail, 'fck_edit'):
                self.detail.fck_edit.clear()
            if hasattr(self.detail, 'gamma_c_edit'):
                self.detail.gamma_c_edit.clear()
            if hasattr(self.detail, 'fck_override'):
                self.detail.fck_override.setChecked(False)
            if hasattr(self.detail, 'gamma_c_override'):
                self.detail.gamma_c_override.setChecked(False)
        except Exception:
            pass
        # update export preview for new (empty) material
        try:
            self._update_export_text()
        except Exception:
            pass
        # clear any warnings in the detail frame for new material
        try:
            if self.detail is not None and hasattr(self.detail, 'set_warning'):
                self.detail.set_warning("")
        except Exception:
            pass

    def on_batch_edit_requested(self, col_or_key, indices) -> None:
        """Handle batch edit request emitted by the table widget.
        col_or_key: either integer column index or a string key
        indices: list of selected row indices
        """
        # resolve column index to key if possible
        key = None
        try:
            if isinstance(col_or_key, int) and self.table is not None and self.table.model() is not None:
                try:
                    # headerData may return display name; map to a dict key
                    header = self.table.model().headerData(col_or_key, 1)  # Qt.Horizontal == 1
                    key = str(header) if header is not None else f'col_{col_or_key}'
                except Exception:
                    key = f'col_{col_or_key}'
            else:
                key = str(col_or_key)
        except Exception:
            key = str(col_or_key)

        # import dialog dynamically (runtime UI)
        try:
            from src.ui.qt.material_editor.widgets.material_batch_edit_dialog import MaterialBatchEditDialog
        except Exception:
            # fallback local import
            from .widgets.material_batch_edit_dialog import MaterialBatchEditDialog

        dlg = MaterialBatchEditDialog(key)
        if dlg.exec() == True:
            val = dlg.get_value()
            # try to coerce numeric values
            try:
                if val is None or val == '':
                    coerced = None
                else:
                    coerced = float(val)
            except Exception:
                coerced = val
            # apply batch update on repository
            try:
                self.repo.batch_update(indices, key, coerced)
                # refresh model view
                try:
                    if hasattr(self, 'model') and self.model is not None:
                        self.model.refresh()
                except Exception:
                    pass
                self.emit('batch_updated', indices, key, coerced)
            except Exception:
                pass
