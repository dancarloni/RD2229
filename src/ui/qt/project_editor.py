"""Project editor window for ProjectModel full-form editing (Qt6)."""

from __future__ import annotations

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
        QTabWidget,
        QTableWidget,
        QTableWidgetItem,
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


class ProjectEditorWindow(QWidget):
    project_changed = Signal(object)

    def __init__(self, project_service=None, parent=None):
        super().__init__(parent)
        self.project_service = project_service
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
        self.tbl_geometry = QTableWidget(0, 4, self)
        self.tbl_geometry.setHorizontalHeaderLabels(["id", "type", "width", "height"])
        self.tbl_materials = QTableWidget(0, 5, self)
        self.tbl_materials.setHorizontalHeaderLabels(["id", "type", "class", "f_ck", "f_yk"])
        self.tbl_loads = QTableWidget(0, 7, self)
        self.tbl_loads.setHorizontalHeaderLabels(
            ["element_id", "N", "Mx", "My", "Tx", "Ty", "desc"]
        )

        grid.addWidget(self.tbl_geometry, 0, 0)
        grid.addWidget(self.tbl_materials, 0, 1)
        grid.addWidget(self.tbl_loads, 1, 0, 1, 2)
        main_layout.addLayout(grid)

        tabs.addTab(tab_main, "Progetto")

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

        tab_fire = QWidget(self)
        fire_form = QFormLayout(tab_fire)
        self.txt_fire_enabled = QLineEdit()
        self.txt_fire_scenario = QLineEdit()
        self.txt_fire_rating = QLineEdit()
        fire_form.addRow("Enabled (true/false):", self.txt_fire_enabled)
        fire_form.addRow("Scenario:", self.txt_fire_scenario)
        fire_form.addRow("Rating min:", self.txt_fire_rating)
        tabs.addTab(tab_fire, "FireInputs")

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
                [entry.id, entry.type, str(entry.width), str(entry.height)],
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

    def _collect_project(self) -> ProjectModel:
        geometry: list[GeometryEntry] = []
        for row in range(self.tbl_geometry.rowCount()):
            geometry.append(
                GeometryEntry(
                    id=self._table_text(self.tbl_geometry, row, 0),
                    type=self._table_text(self.tbl_geometry, row, 1),
                    width=float(self._table_text(self.tbl_geometry, row, 2) or 0.0),
                    height=float(self._table_text(self.tbl_geometry, row, 3) or 0.0),
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
    return ProjectEditorWindow(project_service=context.get("project_service"), parent=master)
