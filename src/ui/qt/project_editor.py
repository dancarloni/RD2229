"""Project editor window for ProjectModel full-form editing (Qt6)."""

from __future__ import annotations

import json
from pathlib import Path

try:
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtWidgets import (
        QFileDialog,
        QFormLayout,
        QGridLayout,
        QHBoxLayout,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QFileDialog,
        QFormLayout,
        QGridLayout,
        QHBoxLayout,
        QLineEdit,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

from src.project.repository import load_project, save_project
from src.project.schema import (
    CodeSettings,
    FireSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
    SeismicInputs,
)

from .key_value_dialog import KeyValueDialog
from .project_editor_dialogs import GeometryDialog, LoadDialog, MaterialDialog


class ProjectEditorWindow(QWidget):
    project_changed = Signal(object)

    def __init__(self, project_service=None, material_repo=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
        self.material_repo = material_repo
        self._current_path: str | None = None
        self._project = getattr(project_service, "current_project", ProjectModel())

        self.setWindowTitle("RD2229 - Project Editor")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self.load_from_project(self._project)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.btn_new = QPushButton("Nuovo")
        self.btn_open = QPushButton("Apri")
        self.btn_save = QPushButton("Salva")
        self.btn_save_as = QPushButton("Salva con nome")
        self.btn_validate = QPushButton("Validazione")

        self.btn_new.clicked.connect(self._new_project)
        self.btn_open.clicked.connect(self._open_project)
        self.btn_save.clicked.connect(self._save_project)
        self.btn_save_as.clicked.connect(self._save_project_as)
        self.btn_validate.clicked.connect(self._validate_project)

        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_open)
        toolbar.addWidget(self.btn_save)
        toolbar.addWidget(self.btn_save_as)
        toolbar.addWidget(self.btn_validate)
        toolbar.addStretch(1)
        root.addLayout(toolbar)

        tabs = QTabWidget(self)
        root.addWidget(tabs)

        # --- Tab principale: Progetto ---
        tab_main = QWidget(self)
        main_layout = QVBoxLayout(tab_main)

        info_form = QFormLayout()
        self.txt_name = QLineEdit()
        self.txt_desc = QLineEdit()
        self.txt_author = QLineEdit()
        self.txt_created = QLineEdit()
        self.txt_updated = QLineEdit()
        info_form.addRow("Nome progetto:", self.txt_name)
        info_form.addRow("Descrizione:", self.txt_desc)
        info_form.addRow("Autore:", self.txt_author)
        info_form.addRow("Creato il:", self.txt_created)
        info_form.addRow("Aggiornato il:", self.txt_updated)
        main_layout.addLayout(info_form)

        grid = QGridLayout()

        # --- Tabella Geometria ---
        self.tbl_geometry = QTableWidget(0, 5, self)
        self.tbl_geometry.setHorizontalHeaderLabels(["id", "type", "width", "height", "extra"])
        self._add_table_crud_buttons(main_layout, self.tbl_geometry, "Geometria")

        # --- Tabella Materiali ---
        self.tbl_materials = QTableWidget(0, 6, self)
        self.tbl_materials.setHorizontalHeaderLabels(
            ["id", "type", "class", "f_ck", "f_yk", "extra"]
        )
        self._add_table_crud_buttons(main_layout, self.tbl_materials, "Materiali", import_repo=True)

        # --- Tabella Carichi ---
        self.tbl_loads = QTableWidget(0, 8, self)
        self.tbl_loads.setHorizontalHeaderLabels(
            ["element_id", "N", "Mx", "My", "Tx", "Ty", "desc", "extra"]
        )
        self._add_table_crud_buttons(main_layout, self.tbl_loads, "Carichi")

        main_layout.addLayout(grid)
        tabs.addTab(tab_main, "Progetto")

        # --- Tab CodeSettings ---
        tab_code = QWidget(self)
        code_form = QFormLayout(tab_code)
        self.txt_norm_code = QLineEdit()
        self.txt_limit_states = QLineEdit()
        self.txt_units_force = QLineEdit()
        self.txt_units_length = QLineEdit()
        code_form.addRow("Norma:", self.txt_norm_code)
        code_form.addRow("Stati limite (csv):", self.txt_limit_states)
        code_form.addRow("Unità forza:", self.txt_units_force)
        code_form.addRow("Unità lunghezza:", self.txt_units_length)
        tabs.addTab(tab_code, "CodeSettings")

        # --- Tab SeismicInputs ---
        tab_seismic = QWidget(self)
        seismic_form = QFormLayout(tab_seismic)
        self.txt_class_of_use = QLineEdit()
        self.txt_vita_nominale = QLineEdit()
        self.txt_vr_years = QLineEdit()
        self.txt_site_label = QLineEdit()
        seismic_form.addRow("Classe d'uso:", self.txt_class_of_use)
        seismic_form.addRow("Vita nominale [anni]:", self.txt_vita_nominale)
        seismic_form.addRow("VR [anni]:", self.txt_vr_years)
        seismic_form.addRow("Sito:", self.txt_site_label)
        tabs.addTab(tab_seismic, "SeismicInputs")

        # --- Tab FireInputs ---
        tab_fire = QWidget(self)
        fire_form = QFormLayout(tab_fire)
        self.txt_fire_enabled = QLineEdit()
        self.txt_fire_scenario = QLineEdit()
        self.txt_fire_rating = QLineEdit()
        fire_form.addRow("Enabled (true/false):", self.txt_fire_enabled)
        fire_form.addRow("Scenario:", self.txt_fire_scenario)
        fire_form.addRow("Rating min:", self.txt_fire_rating)
        tabs.addTab(tab_fire, "FireInputs")

    def _add_table_crud_buttons(self, layout, table, label, import_repo=False):
        row = QHBoxLayout()
        btn_add = QPushButton(f"Aggiungi {label}")
        btn_edit = QPushButton(f"Modifica {label}")
        btn_remove = QPushButton(f"Rimuovi {label}")
        btn_edit_extra = QPushButton("Modifica extra")
        row.addWidget(btn_add)
        row.addWidget(btn_edit)
        row.addWidget(btn_remove)
        row.addWidget(btn_edit_extra)
        if import_repo:
            btn_import = QPushButton("Importa da archivio")
            row.addWidget(btn_import)
            btn_import.clicked.connect(lambda: self._import_material_from_repo())
        row.addStretch(1)
        layout.addWidget(table)
        layout.addLayout(row)
        # Connect signals
        btn_add.clicked.connect(lambda: self._add_table_row(table))
        btn_edit.clicked.connect(lambda: self._edit_table_row(table))
        btn_remove.clicked.connect(lambda: self._remove_table_row(table))
        btn_edit_extra.clicked.connect(lambda: self._edit_extra_for_selected(table))
        table.itemDoubleClicked.connect(lambda _item: self._edit_table_row(table))

    def _add_table_row(self, table: QTableWidget) -> None:
        """Apre un dialog specifico per creare una nuova riga nella tabella."""
        if table is self.tbl_geometry:
            data = GeometryDialog.edit(self, {})
        elif table is self.tbl_materials:
            data = MaterialDialog.edit(self, {})
        elif table is self.tbl_loads:
            data = LoadDialog.edit(self, {})
        else:
            return

        if data is None:
            return

        values = self._row_dict_to_values(table, data)
        self._table_set_row(table, table.rowCount(), values)

    def _remove_table_row(self, table):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    def _edit_extra_for_selected(self, table):
        row = table.currentRow()
        if row < 0:
            return
        col = table.columnCount() - 1  # extra is always last
        item = table.item(row, col)
        current = item.text() if item else "{}"
        try:
            current_dict = json.loads(current) if current.strip() else {}
        except Exception:
            current_dict = {}
        new_dict = KeyValueDialog.edit(self, current_dict)
        if new_dict is not None:
            table.setItem(row, col, QTableWidgetItem(json.dumps(new_dict, ensure_ascii=False)))

    def _edit_table_row(self, table: QTableWidget) -> None:
        row = table.currentRow()
        if row < 0:
            return

        # Costruisci il dict iniziale per il dialog
        initial = self._row_to_dict(table, row)

        if table is self.tbl_geometry:
            edited = GeometryDialog.edit(self, initial)
        elif table is self.tbl_materials:
            edited = MaterialDialog.edit(self, initial)
        elif table is self.tbl_loads:
            edited = LoadDialog.edit(self, initial)
        else:
            return

        if edited is None:
            return

        values = self._row_dict_to_values(table, edited)
        for col, value in enumerate(values):
            table.setItem(row, col, QTableWidgetItem(str(value)))

    def _row_to_dict(self, table: QTableWidget, row: int) -> dict:
        if table is self.tbl_geometry:
            return {
                "id": self._table_text(table, row, 0),
                "type": self._table_text(table, row, 1),
                "width": self._table_text(table, row, 2),
                "height": self._table_text(table, row, 3),
                "extra": self._table_text(table, row, 4),
            }
        if table is self.tbl_materials:
            return {
                "id": self._table_text(table, row, 0),
                "type": self._table_text(table, row, 1),
                "material_class": self._table_text(table, row, 2),
                "f_ck": self._table_text(table, row, 3),
                "f_yk": self._table_text(table, row, 4),
                "extra": self._table_text(table, row, 5),
            }
        if table is self.tbl_loads:
            return {
                "element_id": self._table_text(table, row, 0),
                "N": self._table_text(table, row, 1),
                "Mx": self._table_text(table, row, 2),
                "My": self._table_text(table, row, 3),
                "Tx": self._table_text(table, row, 4),
                "Ty": self._table_text(table, row, 5),
                "description": self._table_text(table, row, 6),
                "extra": self._table_text(table, row, 7),
            }
        return {}

    def _row_dict_to_values(self, table: QTableWidget, data: dict) -> list[str]:
        if table is self.tbl_geometry:
            return [
                data.get("id", ""),
                data.get("type", ""),
                str(data.get("width", "")),
                str(data.get("height", "")),
                json.dumps(data.get("extra", {}), ensure_ascii=False),
            ]
        if table is self.tbl_materials:
            return [
                data.get("id", ""),
                data.get("type", ""),
                data.get("material_class", ""),
                str(data.get("f_ck", "")),
                str(data.get("f_yk", "")),
                json.dumps(data.get("extra", {}), ensure_ascii=False),
            ]
        if table is self.tbl_loads:
            return [
                data.get("element_id", ""),
                str(data.get("N", "")),
                str(data.get("Mx", "")),
                str(data.get("My", "")),
                str(data.get("Tx", "")),
                str(data.get("Ty", "")),
                data.get("description", ""),
                json.dumps(data.get("extra", {}), ensure_ascii=False),
            ]
        return []

    def _remove_table_row(self, table):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    def _edit_extra_for_selected(self, table):
        row = table.currentRow()
        if row < 0:
            return
        col = table.columnCount() - 1  # extra is always last
        item = table.item(row, col)
        current = item.text() if item else "{}"
        try:
            current_dict = json.loads(current) if current.strip() else {}
        except Exception:
            current_dict = {}
        new_dict = KeyValueDialog.edit(self, current_dict)
        if new_dict is not None:
            table.setItem(row, col, QTableWidgetItem(json.dumps(new_dict, ensure_ascii=False)))

    def _edit_table_row(self, table: QTableWidget) -> None:
        row = table.currentRow()
        if row < 0:
            return

        payload = {
            str(table.horizontalHeaderItem(col).text()): self._table_text(table, row, col)
            for col in range(table.columnCount())
        }
        edited = self._show_json_edit_dialog(json.dumps(payload, ensure_ascii=False, indent=2))
        if edited is None:
            return
        try:
            parsed = json.loads(edited)
        except Exception:
            QMessageBox.warning(self, "Modifica riga", "JSON non valido: modifiche annullate.")
            return

        for col in range(table.columnCount()):
            key = str(table.horizontalHeaderItem(col).text())
            table.setItem(row, col, QTableWidgetItem(str(parsed.get(key, ""))))

    def _show_json_edit_dialog(self, current_json):
        # Use the modular JsonEditDialog (lazy import to keep startup light)
        try:
            from src.ui.qt.json_edit_dialog import JsonEditDialog
        except Exception:
            return current_json
        return JsonEditDialog.edit_json(self, current_json)

    def _import_material_from_repo(self):
        # Importa un materiale dal MaterialRepository e lo aggiunge alla tabella
        try:
            from src.ui.qt.material_import_dialog import MaterialImportDialog
        except Exception:
            return
        if self.material_repo is None:
            QMessageBox.information(
                self, "Archivio materiale", "Nessun archivio materiali disponibile."
            )
            return

        mat = MaterialImportDialog.select_material(self, self.material_repo)
        if mat is None:
            return

        import json

        values = [
            mat.material_id,
            getattr(mat, "famiglia", ""),
            getattr(mat, "descrizione", ""),
            "" if getattr(mat, "f_ck", 0.0) == 0.0 else str(getattr(mat, "f_ck", "")),
            "" if getattr(mat, "f_yk", 0.0) == 0.0 else str(getattr(mat, "f_yk", "")),
            json.dumps(
                {"note": getattr(mat, "note", ""), "source_refs": getattr(mat, "source_refs", [])},
                ensure_ascii=False,
            ),
        ]
        self._table_set_row(self.tbl_materials, self.tbl_materials.rowCount(), values)

    def _table_set_row(self, table: QTableWidget, row: int, values: list[str]) -> None:
        table.insertRow(row)
        for col, value in enumerate(values):
            table.setItem(row, col, QTableWidgetItem(str(value)))

    def _table_text(self, table: QTableWidget, row: int, col: int) -> str:
        item = table.item(row, col)
        return item.text().strip() if item is not None else ""

    def _to_float_or_none(self, value: str) -> float | None:
        txt = value.strip()
        if not txt:
            return None
        try:
            return float(txt)
        except ValueError:
            return None

    def load_from_project(self, project: ProjectModel) -> None:
        import json

        self._project = project
        info = project.project_info
        self.txt_name.setText(info.name)
        self.txt_desc.setText(info.description)
        self.txt_author.setText(info.author)
        self.txt_created.setText(info.created_at)
        self.txt_updated.setText(info.updated_at)

        self.tbl_geometry.setRowCount(0)
        for idx, entry in enumerate(project.geometry):
            self._table_set_row(
                self.tbl_geometry,
                idx,
                [
                    entry.id,
                    entry.type,
                    str(entry.width),
                    str(entry.height),
                    json.dumps(entry.extra or {}, ensure_ascii=False),
                ],
            )

        self.tbl_materials.setRowCount(0)
        for idx, entry in enumerate(project.materials):
            self._table_set_row(
                self.tbl_materials,
                idx,
                [
                    entry.id,
                    entry.type,
                    entry.material_class,
                    "" if entry.f_ck is None else str(entry.f_ck),
                    "" if entry.f_yk is None else str(entry.f_yk),
                    json.dumps(entry.extra or {}, ensure_ascii=False),
                ],
            )

        self.tbl_loads.setRowCount(0)
        for idx, entry in enumerate(project.loads):
            self._table_set_row(
                self.tbl_loads,
                idx,
                [
                    entry.element_id,
                    "" if entry.N is None else str(entry.N),
                    "" if entry.Mx is None else str(entry.Mx),
                    "" if entry.My is None else str(entry.My),
                    "" if entry.Tx is None else str(entry.Tx),
                    "" if entry.Ty is None else str(entry.Ty),
                    entry.description,
                    json.dumps(entry.extra or {}, ensure_ascii=False),
                ],
            )

        cs = project.code_settings
        self.txt_norm_code.setText(cs.norm_code)
        self.txt_limit_states.setText(",".join(cs.limit_states))
        self.txt_units_force.setText(cs.units_force)
        self.txt_units_length.setText(cs.units_length)

        si = project.seismic_inputs
        self.txt_class_of_use.setText(si.class_of_use)
        self.txt_vita_nominale.setText(str(si.vita_nominale_years))
        self.txt_vr_years.setText(str(si.vr_years))
        self.txt_site_label.setText(si.site_label)

        fire = project.fire
        self.txt_fire_enabled.setText("true" if fire.enabled else "false")
        self.txt_fire_scenario.setText(fire.scenario)
        self.txt_fire_rating.setText(str(fire.required_rating_minutes))

    def _parse_extra_json(self, value: str) -> dict:
        import json

        if not value.strip():
            return {}
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                raise ValueError("Il campo extra deve essere un oggetto JSON")
            return parsed
        except Exception as exc:
            raise ValueError(f"JSON extra non valido: {exc}")

    def _collect_project(self) -> ProjectModel:
        geometry: list[GeometryEntry] = []
        for row in range(self.tbl_geometry.rowCount()):
            geometry.append(
                GeometryEntry(
                    id=self._table_text(self.tbl_geometry, row, 0),
                    type=self._table_text(self.tbl_geometry, row, 1),
                    width=float(self._table_text(self.tbl_geometry, row, 2) or 0.0),
                    height=float(self._table_text(self.tbl_geometry, row, 3) or 0.0),
                    extra=self._parse_extra_json(self._table_text(self.tbl_geometry, row, 4)),
                )
            )

        materials: list[MaterialEntry] = []
        for row in range(self.tbl_materials.rowCount()):
            materials.append(
                MaterialEntry(
                    id=self._table_text(self.tbl_materials, row, 0),
                    type=self._table_text(self.tbl_materials, row, 1),
                    material_class=self._table_text(self.tbl_materials, row, 2),
                    f_ck=self._to_float_or_none(self._table_text(self.tbl_materials, row, 3)),
                    f_yk=self._to_float_or_none(self._table_text(self.tbl_materials, row, 4)),
                    extra=self._parse_extra_json(self._table_text(self.tbl_materials, row, 5)),
                )
            )

        loads: list[LoadEntry] = []
        for row in range(self.tbl_loads.rowCount()):
            loads.append(
                LoadEntry(
                    element_id=self._table_text(self.tbl_loads, row, 0),
                    N=self._to_float_or_none(self._table_text(self.tbl_loads, row, 1)),
                    Mx=self._to_float_or_none(self._table_text(self.tbl_loads, row, 2)),
                    My=self._to_float_or_none(self._table_text(self.tbl_loads, row, 3)),
                    Tx=self._to_float_or_none(self._table_text(self.tbl_loads, row, 4)),
                    Ty=self._to_float_or_none(self._table_text(self.tbl_loads, row, 5)),
                    description=self._table_text(self.tbl_loads, row, 6),
                    extra=self._parse_extra_json(self._table_text(self.tbl_loads, row, 7)),
                )
            )

        project = ProjectModel(
            project_info=ProjectInfo(
                name=self.txt_name.text().strip(),
                description=self.txt_desc.text().strip(),
                author=self.txt_author.text().strip(),
                created_at=self.txt_created.text().strip(),
                updated_at=self.txt_updated.text().strip(),
            ),
            geometry=geometry,
            materials=materials,
            loads=loads,
            code_settings=CodeSettings(
                norm_code=self.txt_norm_code.text().strip() or "RD2229",
                limit_states=[
                    s.strip() for s in self.txt_limit_states.text().split(",") if s.strip()
                ]
                or ["TA"],
                units_force=self.txt_units_force.text().strip() or "kN",
                units_length=self.txt_units_length.text().strip() or "cm",
            ),
            seismic_inputs=SeismicInputs(
                class_of_use=self.txt_class_of_use.text().strip(),
                vita_nominale_years=int(self.txt_vita_nominale.text().strip() or 0),
                vr_years=int(self.txt_vr_years.text().strip() or 0),
                site_label=self.txt_site_label.text().strip(),
            ),
            fire=FireSettings(
                enabled=self.txt_fire_enabled.text().strip().lower() in {"1", "true", "yes", "si"},
                scenario=self.txt_fire_scenario.text().strip() or "ISO_834",
                required_rating_minutes=int(self.txt_fire_rating.text().strip() or 60),
            ),
        )
        return project

    def _new_project(self) -> None:
        self._current_path = None
        self.load_from_project(ProjectModel())
        self._push_project_to_service()

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Apri progetto",
            str(Path.cwd()),
            "Project JSON (*.json *.jsonp)",
        )
        if not path:
            return
        self._current_path = path
        self.load_from_project(load_project(path))
        self._push_project_to_service()

    def _save_project(self) -> None:
        if self._current_path is None:
            self._save_project_as()
            return
        project = self._collect_project()
        save_project(project, self._current_path)
        self._project = project
        self._push_project_to_service()

    def _save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva progetto",
            str(Path.cwd() / "progetto_rd2229.jsonp"),
            "Project JSON (*.json *.jsonp)",
        )
        if not path:
            return
        self._current_path = path
        self._save_project()

    def _validate_project(self) -> None:
        try:
            project = self._collect_project()
            ProjectModel.model_validate(project.model_dump(mode="json"))
            QMessageBox.information(self, "Validazione", "Progetto valido.")
        except Exception as exc:
            QMessageBox.warning(self, "Validazione", f"Progetto non valido: {exc}")

    def _push_project_to_service(self) -> None:
        if self.project_service is not None and hasattr(self.project_service, "set_project"):
            self.project_service.set_project(self._collect_project())
        self.project_changed.emit(self._collect_project())


MODULE_SPEC = {
    "key": "project_editor",
    "name": "Project Editor",
    "description": "GUI per creare/caricare/salvare ProjectModel (Qt6)",
}


def create_module(master=None, **context):
    return ProjectEditorWindow(
        project_service=context.get("project_service"),
        material_repo=context.get("material_repo"),
        parent=master,
    )
