"""Verification page with executable module catalog."""

from __future__ import annotations

try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QLabel,
        QListWidget,
        QPushButton,
        QTextEdit,
        QHBoxLayout,
        QGroupBox,
        QFormLayout,
        QLineEdit,
        QComboBox,
    )
except Exception:  # pragma: no cover - optional dependency
    QWidget = object

from rd2229.ui_qt.services import SettingsService, VerificationService, build_module_catalog


class VerificationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings_service = SettingsService()
        self._service = VerificationService(settings_service=self._settings_service)
        self._catalog = build_module_catalog()
        defaults = self._settings_service.get_model()

        layout = QVBoxLayout(self)

        intro = QLabel("Moduli disponibili")
        layout.addWidget(intro)

        main_row = QHBoxLayout()

        left_box = QGroupBox("Catalogo")
        left_layout = QVBoxLayout(left_box)
        self.module_list = QListWidget()
        for module in self._catalog:
            self.module_list.addItem(f"{module.title} [{module.status}]")
        if self._catalog:
            self.module_list.setCurrentRow(0)
        left_layout.addWidget(self.module_list)

        self.run_button = QPushButton("Run Module")
        self.run_button.clicked.connect(self._run_selected_module)
        left_layout.addWidget(self.run_button)

        self.module_desc = QLabel("")
        self._refresh_description()
        self.module_list.currentRowChanged.connect(lambda _: self._refresh_description())
        left_layout.addWidget(self.module_desc)

        input_box = QGroupBox("Input")
        input_layout = QFormLayout(input_box)

        self.axial_input = QLineEdit(str(defaults.default_axial_n))
        self.factor_input = QLineEdit(str(defaults.default_factor))
        self.threshold_input = QLineEdit(str(defaults.default_threshold))
        self.db_name_input = QLineEdit(defaults.default_db_name)

        self.check_code_input = QComboBox()
        self.check_code_input.addItems(["MVP_REAL_MIN", "MVP_PLACEHOLDER"])
        current_index = self.check_code_input.findText(defaults.default_check_code)
        self.check_code_input.setCurrentIndex(current_index if current_index >= 0 else 0)

        input_layout.addRow("Axial N", self.axial_input)
        input_layout.addRow("Factor", self.factor_input)
        input_layout.addRow("Threshold", self.threshold_input)
        input_layout.addRow("Check", self.check_code_input)
        input_layout.addRow("DB name", self.db_name_input)
        left_layout.addWidget(input_box)

        self.save_defaults_button = QPushButton("Save Defaults")
        self.save_defaults_button.clicked.connect(self._save_defaults)
        left_layout.addWidget(self.save_defaults_button)

        right_box = QGroupBox("Output")
        right_layout = QVBoxLayout(right_box)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Risultati esecuzione modulo")
        right_layout.addWidget(self.output_text)

        main_row.addWidget(left_box, 1)
        main_row.addWidget(right_box, 2)
        layout.addLayout(main_row)

    def _selected_module_id(self) -> str | None:
        index = self.module_list.currentRow()
        if index < 0 or index >= len(self._catalog):
            return None
        return self._catalog[index].module_id

    def _refresh_description(self) -> None:
        index = self.module_list.currentRow()
        if index < 0 or index >= len(self._catalog):
            self.module_desc.setText("Nessun modulo selezionato")
            return
        module = self._catalog[index]
        self.module_desc.setText(module.description)

    def _run_selected_module(self) -> None:
        module_id = self._selected_module_id()
        if module_id is None:
            self.output_text.setPlainText("Nessun modulo selezionato")
            return
        result = self._service.run_module(module_id, self._collect_runtime_inputs())
        self.output_text.setPlainText(self._format_result(result))

    def _collect_runtime_inputs(self) -> dict:
        return {
            "axial_n": self._safe_float(self.axial_input.text(), 120.0),
            "factor": self._safe_float(self.factor_input.text(), 1.0),
            "threshold": self._safe_float(self.threshold_input.text(), 1000.0),
            "check_code": self.check_code_input.currentText(),
            "db_name": self.db_name_input.text().strip() or "mvp_alpha.db",
        }

    def _save_defaults(self) -> None:
        runtime = self._collect_runtime_inputs()
        self._settings_service.update_runtime_defaults(
            axial_n=runtime["axial_n"],
            factor=runtime["factor"],
            threshold=runtime["threshold"],
            check_code=runtime["check_code"],
            db_name=runtime["db_name"],
        )
        self.output_text.setPlainText("Impostazioni salvate.")

    @staticmethod
    def _safe_float(value: str, fallback: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _format_result(result: dict) -> str:
        lines = [f"Status: {result.get('status', 'UNKNOWN')}"]
        message = result.get("message")
        if message:
            lines.append(f"Message: {message}")
        summary = result.get("summary")
        if isinstance(summary, dict):
            lines.append("Summary:")
            for key in sorted(summary.keys()):
                lines.append(f"  - {key}: {summary[key]}")
        for field in ("db_path", "config_path", "run_timestamp"):
            if field in result:
                lines.append(f"{field}: {result[field]}")
        return "\n".join(lines)

    def set_project(self, project):
        self._project = project
