"""
MaterialEditorController — controller specifico per il Material Editor

Estende ControllerBase e coordina repository, table widget, detail frame
ed export widget. Non esegue operazioni Qt all'importazione: i collegamenti
ai widget vengono effettuati tramite i metodi `attach_*` a runtime.
"""

import logging
from typing import Any, Dict, Optional

from src.core.controller_base import ControllerBase
from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader
from src.ui.qt.material_editor.logic.material_export_logic import MaterialExportLogic
from src.ui.qt.material_editor.logic.material_repository import MaterialRepository
from src.ui.qt.material_editor.logic.material_validation_logic import (
    validate as validate_material,
    validate_full,
)

logger = logging.getLogger(__name__)
_config = MaterialConfigLoader()


class MaterialEditorController(ControllerBase):
    def __init__(
        self, repository: Optional[MaterialRepository] = None, famiglia: Optional[str] = None
    ):
        super().__init__()
        self.repo = repository or MaterialRepository()
        self.famiglia = famiglia
        self.table = None
        self.detail = None
        self.export_widget = None
        self.current_index: Optional[int] = None

    def attach_table(self, table_widget) -> None:
        """Collega la table widget al controller. Deve essere chiamato a runtime."""
        self.table = table_widget
        try:
            # Filtra i materiali per famiglia se richiesto
            if self.famiglia:
                filtered = [
                    m
                    for m in self.repo.materials
                    if m.get("famiglia", "").lower() == self.famiglia.lower()
                ]
                self.repo.materials = filtered

            # batch edit signal PRIMA di setModel (non dipende dal selectionModel)
            if hasattr(self.table, "batchEditRequested"):
                try:
                    self.table.batchEditRequested.connect(self.on_batch_edit_requested)
                except Exception:
                    pass

            # Crea e imposta il modello
            from src.ui.qt.material_editor.widgets.material_table_model import MaterialTableModel

            self.model = MaterialTableModel(self.repo)
            self.table.setModel(self.model)  # crea un nuovo QItemSelectionModel interno
            self.model.refresh()

            # FONDAMENTALE: connetti selectionModel DOPO setModel per usare quello definitivo
            self.table.selectionModel().selectionChanged.connect(self._on_table_selection_changed)

            try:
                self.table.resizeColumnsToContents()
            except Exception:
                pass

            # Popola il primo materiale (solo se detail è già collegato)
            self._try_populate_first()
        except Exception:
            import traceback

            traceback.print_exc()

    def _try_populate_first(self) -> None:
        """Seleziona e popola il primo materiale se modello e detail sono entrambi pronti."""
        try:
            if (
                self.detail is not None
                and hasattr(self, "model")
                and self.model is not None
                and self.table is not None
                and self.model.rowCount() > 0
            ):
                self.table.selectRow(0)
        except Exception:
            pass

    def attach_detail(self, detail_frame) -> None:
        """Collega il frame dettaglio e i suoi pulsanti."""
        self.detail = detail_frame
        try:
            if hasattr(self.detail, "save_button"):
                self.detail.save_button.clicked.connect(self.on_save_clicked)
            if hasattr(self.detail, "cancel_button"):
                self.detail.cancel_button.clicked.connect(self.on_cancel_clicked)
            if hasattr(self.detail, "reset_derived_button"):
                self.detail.reset_derived_button.clicked.connect(self.on_reset_derived_clicked)
            if hasattr(self.detail, "inputChanged"):
                self.detail.inputChanged.connect(self._on_input_changed)
            # setup Ctrl+S shortcut on the detail frame (runtime)
            try:
                from PySide6.QtGui import QKeySequence
                from PySide6.QtWidgets import QShortcut

                QShortcut(QKeySequence("Ctrl+S"), self.detail, activated=self.on_save_clicked)
            except Exception:
                pass
        except Exception:
            pass
        # Se il modello è già pronto, popola subito il primo materiale
        self._try_populate_first()

    def attach_export(self, export_widget) -> None:
        self.export_widget = export_widget
        try:
            if hasattr(self.export_widget, "format_combo"):
                try:
                    self.export_widget.format_combo.currentIndexChanged.connect(
                        lambda _: self._update_export_text()
                    )
                except Exception:
                    pass
            # also listen to the high-level signal if the widget exposes it
            if hasattr(self.export_widget, "formatChanged"):
                try:
                    self.export_widget.formatChanged.connect(lambda _: self._update_export_text())
                except Exception:
                    pass
            if hasattr(self.export_widget, "copy_button"):
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
            fmt = "HTML"
            if hasattr(self.export_widget, "format_combo"):
                try:
                    fmt = self.export_widget.format_combo.currentText()
                except Exception:
                    fmt = "HTML"

            # if no selection, show a template/empty-preview using model headers or defaults
            if self.current_index is None:
                mat = {}
                try:
                    if hasattr(self, "model") and self.model is not None:
                        # derive header names from model
                        try:
                            from PySide6.QtCore import Qt

                            cols = self.model.columnCount()
                            headers = []
                            for c in range(cols):
                                try:
                                    hdr = self.model.headerData(c, Qt.Horizontal)
                                    headers.append(str(hdr) if hdr is not None else f"col_{c}")
                                except Exception:
                                    headers.append(f"col_{c}")
                            for h in headers:
                                mat[h] = ""
                        except Exception:
                            # fallback to sensible defaults
                            for h in ["codice", "descrizione", "norma", "f_ck", "gamma_c"]:
                                mat[h] = ""
                    else:
                        for h in ["codice", "descrizione", "norma", "f_ck", "gamma_c"]:
                            mat[h] = ""
                except Exception:
                    mat = {"codice": "", "descrizione": "", "norma": "", "f_ck": "", "gamma_c": ""}
            else:
                try:
                    mat = self.repo.materials[self.current_index]
                except Exception:
                    mat = {}

            txt = MaterialExportLogic.export(mat, fmt)
            if hasattr(self.export_widget, "export_text"):
                self.export_widget.export_text.setPlainText(txt)
        except Exception:
            pass

    def _on_export_copy(self) -> None:
        try:
            from PySide6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            if hasattr(self.export_widget, "export_text"):
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

    def _get_norm_schema(self, material: Dict[str, Any]) -> Optional[Dict]:
        """Restituisce lo schema norma per famiglia + norma_riferimento del materiale."""
        famiglia = material.get("famiglia") or self.famiglia
        norma = material.get("norma_riferimento") or material.get("norma")
        if not famiglia or not norma:
            return None
        try:
            return _config.get_norm_schema(famiglia, norma)
        except Exception as exc:
            logger.debug("Schema non trovato per %s/%s: %s", famiglia, norma, exc)
            return None

    def _recompute_derived(self, material: Dict[str, Any]) -> None:
        """Calcola i derivati e li aggiorna nel detail frame."""
        if self.detail is None:
            return
        norm_schema = self._get_norm_schema(material)
        if norm_schema is None:
            return
        # Leggi gli override correnti dal detail
        current_vals = {}
        if hasattr(self.detail, "get_field_values"):
            current_vals = self.detail.get_field_values()
        current_overrides = {}
        if hasattr(self.detail, "get_overrides"):
            current_overrides = self.detail.get_overrides()
        # Unisci: materiale base + valori editati dall'utente + override correnti
        merged = dict(material)
        for k, v in current_vals.items():
            if v is not None:
                merged[k] = v
        for k, checked in current_overrides.items():
            merged[f"{k}_override"] = checked
        try:
            famiglia_mat = material.get("famiglia") or self.famiglia
            derived = _config.compute_derived(merged, norm_schema, famiglia=famiglia_mat)
            if hasattr(self.detail, "update_derived_values"):
                self.detail.update_derived_values(derived)
        except Exception as exc:
            logger.debug("Errore compute_derived: %s", exc)

    def _on_input_changed(self) -> None:
        """Ricalcola i derivati quando un campo input cambia."""
        if self.current_index is None:
            # materiale nuovo: prendi valori dal form
            if self.detail and hasattr(self.detail, "get_field_values"):
                mat = self.detail.get_field_values()
            else:
                return
        else:
            if self.current_index < 0 or self.current_index >= len(self.repo.materials):
                return
            mat = dict(self.repo.materials[self.current_index])
            if self.detail and hasattr(self.detail, "get_field_values"):
                for k, v in self.detail.get_field_values().items():
                    if v is not None:
                        mat[k] = v
        self._recompute_derived(mat)

    def on_reset_derived_clicked(self) -> None:
        """Rimuove tutti gli override dal materiale corrente e ricalcola."""
        if self.current_index is None or self.detail is None:
            return
        # Rimuovi flag override dal materiale nel repository
        if 0 <= self.current_index < len(self.repo.materials):
            mat = self.repo.materials[self.current_index]
            keys_to_remove = [k for k in list(mat.keys()) if k.endswith("_override")]
            for k in keys_to_remove:
                mat.pop(k, None)
        # Reset visivo nel detail
        if hasattr(self.detail, "reset_all_overrides"):
            self.detail.reset_all_overrides()
        # Ricalcola
        if 0 <= self.current_index < len(self.repo.materials):
            self._recompute_derived(self.repo.materials[self.current_index])

    def populate_detail_from_index(self, idx: int) -> None:
        if idx is None or idx < 0 or idx >= len(self.repo.materials):
            return
        mat = self.repo.materials[idx]
        if self.detail is None:
            return
        # Recupera schema norma e popola il detail
        norm_schema = self._get_norm_schema(mat)
        if hasattr(self.detail, "set_fields"):
            self.detail.set_fields(mat, norm_schema)
        # Calcola subito i derivati
        self._recompute_derived(mat)
        # soft validation
        try:
            res = validate_material(mat)
            msgs = []
            if res.get("missing"):
                msgs.append("Campi mancanti: " + ", ".join(res.get("missing")))
            if res.get("warnings"):
                msgs.append("Avvisi: " + "; ".join(res.get("warnings")))
            msg = ". ".join(msgs) if msgs else ""
            if hasattr(self.detail, "set_warning"):
                self.detail.set_warning(msg)
        except Exception:
            if hasattr(self.detail, "set_warning"):
                self.detail.set_warning("")

    def on_save_clicked(self) -> None:
        if self.detail is None:
            return
        # Raccogli tutti i valori correnti dal detail frame
        data: Dict[str, Any] = {}
        if hasattr(self.detail, "get_field_values"):
            data.update(self.detail.get_field_values())
        if hasattr(self.detail, "get_overrides"):
            for key, checked in self.detail.get_overrides().items():
                data[f"{key}_override"] = checked
        # Eredita famiglia e norma_riferimento dal materiale corrente (se presenti)
        if self.current_index is not None and 0 <= self.current_index < len(self.repo.materials):
            base = self.repo.materials[self.current_index]
            for inherit_key in ("famiglia", "norma_riferimento", "id"):
                if inherit_key in base and inherit_key not in data:
                    data[inherit_key] = base[inherit_key]

        # Validazione normativa completa prima del salvataggio
        try:
            norm_schema = self._get_norm_schema(data)
            norm_code = data.get("norma_riferimento") or data.get("norma")
            validation = validate_full(data, norm_schema=norm_schema, norm_code=norm_code)
            if not validation.is_valid:
                # Errori bloccanti → non salvare
                err_lines = [f"• [{i.field}] {i.message}" for i in validation.errors]
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    None,
                    "Errori di validazione — salvataggio bloccato",
                    "Il materiale non può essere salvato:\n\n" + "\n".join(err_lines),
                )
                return
            if validation.warnings:
                # Warning non bloccanti → chiede conferma
                warn_lines = [f"• [{i.field}] {i.message}" for i in validation.warnings]
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.warning(
                    None,
                    "Avvisi di validazione",
                    "Sono presenti avvisi:\n\n"
                    + "\n".join(warn_lines)
                    + "\n\nSalvare comunque?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        except Exception as exc:
            logger.debug("Errore validazione pre-save: %s", exc)

        if self.current_index is None:
            # aggiungi nuovo materiale
            self.repo.add_material(data)
            self.current_index = len(self.repo.materials) - 1
            self.emit("material_added", self.current_index, data)
        else:
            self.repo.update_material(self.current_index, data)
            self.emit("material_updated", self.current_index, data)

        # aggiorna export text se presente
        if self.export_widget is not None and hasattr(self.export_widget, "format_combo"):
            fmt = self.export_widget.format_combo.currentText()
            txt = MaterialExportLogic.export(self.repo.materials[self.current_index], fmt)
            if hasattr(self.export_widget, "export_text"):
                self.export_widget.export_text.setPlainText(txt)
        # refresh model if present
        try:
            if hasattr(self, "model") and self.model is not None:
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
                    if res.get("missing"):
                        msgs.append("Campi mancanti: " + ", ".join(res.get("missing")))
                    if res.get("warnings"):
                        msgs.append("Avvisi: " + "; ".join(res.get("warnings")))
                    msg = ". ".join(msgs) if msgs else ""
                    if self.detail is not None and hasattr(self.detail, "set_warning"):
                        self.detail.set_warning(msg)
                except Exception:
                    if self.detail is not None and hasattr(self.detail, "set_warning"):
                        self.detail.set_warning("")
        except Exception:
            pass

    def on_batch_edit_accepted(
        self,
        field: str,
        value: Any,
        material_indices: List[int],
    ) -> None:
        """Applica lo stesso valore a N materiali selezionati con rollback su errore.

        Args:
            field: Nome del campo da modificare.
            value: Nuovo valore (numerico o stringa).
            material_indices: Indici dei materiali nel repo.
        """
        if not field or not material_indices:
            return

        # Snapshot per rollback
        snapshots = {
            idx: dict(self.repo.materials[idx])
            for idx in material_indices
            if 0 <= idx < len(self.repo.materials)
        }

        errors: List[str] = []
        updated: List[int] = []

        for idx in material_indices:
            if idx < 0 or idx >= len(self.repo.materials):
                continue
            try:
                patch = {field: value}
                self.repo.update_material(idx, patch)
                updated.append(idx)
            except Exception as exc:
                errors.append(f"Materiale {idx}: {exc}")

        if errors:
            # Rollback
            for idx, snapshot in snapshots.items():
                try:
                    self.repo._materials[idx] = snapshot
                except Exception:
                    pass
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Batch edit fallito",
                "Errori durante il batch edit (rollback eseguito):\n\n"
                + "\n".join(errors),
            )
            return

        # Refresh UI
        try:
            if hasattr(self, "model") and self.model is not None:
                self.model.refresh()
        except Exception:
            pass

        # Riseleziona il materiale corrente se incluso
        if self.current_index in updated:
            self.populate_detail_from_index(self.current_index)

        logger.info("Batch edit: %s=%s su %d materiali", field, value, len(updated))
        self.emit("batch_updated", updated, field, value)

    def on_cancel_clicked(self) -> None:
        # ripristina valori originali
        if self.current_index is not None:
            self.populate_detail_from_index(self.current_index)
        # refresh export preview to reflect restored detail/new material
        try:
            self._update_export_text()
        except Exception:
            pass

    def start_new_material(self, prefill: Optional[Dict[str, Any]] = None) -> None:
        """Prepara il dettaglio per l'inserimento di un nuovo materiale."""
        self.current_index = None
        if self.detail is None:
            return
        template = prefill or {"famiglia": self.famiglia or ""}
        norm_schema = self._get_norm_schema(template)
        if hasattr(self.detail, "set_fields"):
            self.detail.set_fields(template, norm_schema)
        if hasattr(self.detail, "set_warning"):
            self.detail.set_warning("")
        try:
            self._update_export_text()
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
            if (
                isinstance(col_or_key, int)
                and self.table is not None
                and self.table.model() is not None
            ):
                try:
                    # headerData may return display name; map to a dict key
                    header = self.table.model().headerData(col_or_key, 1)  # Qt.Horizontal == 1
                    key = str(header) if header is not None else f"col_{col_or_key}"
                except Exception:
                    key = f"col_{col_or_key}"
            else:
                key = str(col_or_key)
        except Exception:
            key = str(col_or_key)

        # import dialog dynamically (runtime UI)
        try:
            from src.ui.qt.material_editor.widgets.material_batch_edit_dialog import (
                MaterialBatchEditDialog,
            )
        except Exception:
            # fallback local import
            from .widgets.material_batch_edit_dialog import MaterialBatchEditDialog

        dlg = MaterialBatchEditDialog(key)
        if dlg.exec() == True:
            val = dlg.get_value()
            # try to coerce numeric values
            try:
                if val is None or val == "":
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
                    if hasattr(self, "model") and self.model is not None:
                        self.model.refresh()
                except Exception:
                    pass
                self.emit("batch_updated", indices, key, coerced)
            except Exception:
                pass

    def _initialize_default_materials(self):
        """Aggiunge materiali predefiniti al repository."""
        default_materials = [
            {
                "codice": "C25/30",
                "descrizione": "Calcestruzzo classe C25/30",
                "norma": "NTC2018",
                "f_ck": 25.0,
                "gamma_c": 1.5,
            },
            {
                "codice": "S355",
                "descrizione": "Acciaio S355",
                "norma": "EN 10025",
                "f_ck": 355.0,
                "gamma_c": 1.1,
            },
            {
                "codice": "GL24h",
                "descrizione": "Legno lamellare GL24h",
                "norma": "EN 14080",
                "f_ck": 24.0,
                "gamma_c": 1.3,
            },
            {
                "codice": "Muratura M10",
                "descrizione": "Muratura portante classe M10",
                "norma": "NTC2018",
                "f_ck": 10.0,
                "gamma_c": 2.0,
            },
        ]
        for material in default_materials:
            self.repo.add_material(material)
        # Aggiorna la tabella dopo aver aggiunto i materiali predefiniti
        if self.table and hasattr(self, "model") and self.model:
            self.model.refresh()
