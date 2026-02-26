"""Settings page widget for Qt launcher."""

from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QComboBox,
        QFormLayout,
        QGroupBox,
        QLabel,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - optional dependency
    QWidget = object

from rd2229.ui_qt.services import SettingsService


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings_service = SettingsService()
        model = self._settings_service.get_model()

        layout = QVBoxLayout(self)

        runtime_box = QGroupBox("Runtime")
        runtime_layout = QFormLayout(runtime_box)
        runtime_layout.addRow("Workspace", QLabel(f"{Path.cwd()}"))

        self.axial_input = QLineEdit(str(model.default_axial_n))
        self.factor_input = QLineEdit(str(model.default_factor))
        self.threshold_input = QLineEdit(str(model.default_threshold))
        self.db_name_input = QLineEdit(model.default_db_name)
        self.check_code_input = QComboBox()
        self.check_code_input.addItems(["MVP_REAL_MIN", "MVP_PLACEHOLDER"])
        idx = self.check_code_input.findText(model.default_check_code)
        self.check_code_input.setCurrentIndex(idx if idx >= 0 else 0)

        runtime_layout.addRow("Axial N", self.axial_input)
        runtime_layout.addRow("Factor", self.factor_input)
        runtime_layout.addRow("Threshold", self.threshold_input)
        runtime_layout.addRow("Check", self.check_code_input)
        runtime_layout.addRow("DB name", self.db_name_input)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save)
        runtime_layout.addRow(save_button)

        self.status_label = QLabel("Storage: SQLite (MVP) | Trace contract: run_id + norm_references + method_id")
        runtime_layout.addRow(self.status_label)

        ui_box = QGroupBox("UI")
        ui_layout = QVBoxLayout(ui_box)
        ui_layout.addWidget(QLabel("Launcher mode: modular pages"))
        ui_layout.addWidget(QLabel("Verification page: module catalog + run output"))

        layout.addWidget(runtime_box)
        layout.addWidget(ui_box)
        layout.addStretch(1)

    def _save(self) -> None:
        self._settings_service.update_runtime_defaults(
            axial_n=self._safe_float(self.axial_input.text(), 120.0),
            factor=self._safe_float(self.factor_input.text(), 1.0),
            threshold=self._safe_float(self.threshold_input.text(), 1000.0),
            check_code=self.check_code_input.currentText(),
            db_name=self.db_name_input.text().strip() or "mvp_alpha.db",
        )
        self.status_label.setText("Impostazioni salvate in logs/ui/launcher_settings.json")

    @staticmethod
    def _safe_float(value: str, fallback: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    def set_project(self, project):
        self._project = project
