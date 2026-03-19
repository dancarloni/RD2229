"""
MaterialDetailFrame — Frame dettaglio materiale, editing rapido, override
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class MaterialDetailFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._fields = {}
        self._overrides = {}

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(2)

        # area warning (fuori dalla scroll area)
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #b35f00;")
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        outer_layout.addWidget(self.warning_label)

        # ScrollArea per i campi dinamici
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._fields_widget = QWidget()
        self._fields_container = QVBoxLayout(self._fields_widget)
        self._fields_container.setContentsMargins(4, 4, 4, 4)
        self._fields_container.setSpacing(3)
        self._fields_container.addStretch(1)  # placeholder iniziale
        self._scroll.setWidget(self._fields_widget)
        outer_layout.addWidget(self._scroll, stretch=1)

        # Pulsanti (fuori dalla scroll area)
        btn_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva")
        btn_layout.addWidget(self.save_button)
        self.cancel_button = QPushButton("Annulla")
        btn_layout.addWidget(self.cancel_button)
        outer_layout.addLayout(btn_layout)

    def set_fields(self, material: dict):
        # Rimuovi vecchi widget e stretch
        while self._fields_container.count():
            item = self._fields_container.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._fields.clear()
        self._overrides.clear()
        # Crea nuovi campi dinamici
        for key, value in material.items():
            if key in ("id",):
                continue
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            label = QLabel(f"{key}:")
            label.setFixedWidth(90)
            edit = QLineEdit()
            edit.setText(str(value) if value is not None else "")
            self._fields[key] = edit
            row.addWidget(label)
            row.addWidget(edit, stretch=1)
            # Flag override per ogni campo
            override = QCheckBox("↑")
            override.setToolTip(f"Override manuale {key}")
            override.setFixedWidth(24)
            self._overrides[key] = override
            row.addWidget(override)
            self._fields_container.addWidget(row_widget)
        self._fields_container.addStretch(1)

    def get_field_values(self):
        # Restituisce i valori correnti dei campi
        return {k: self._fields[k].text() for k in self._fields}

    def get_overrides(self):
        # Restituisce lo stato dei flag override
        return {k: self._overrides[k].isChecked() for k in self._overrides}

    def set_warning(self, text: str) -> None:
        if text:
            self.warning_label.setText(text)
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setText("")
            self.warning_label.setVisible(False)

# Per test rapido
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    frame = MaterialDetailFrame()
    frame.show()
    sys.exit(app.exec())
