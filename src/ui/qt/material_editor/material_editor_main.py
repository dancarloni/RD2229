"""
Material Editor GUI — Entry point

Finestra principale per la gestione dei materiali strutturali.
Lanciabile dalla main window del software RD2229.
"""

from PySide6.QtWidgets import (
    QWidget, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel
)
from PySide6.QtCore import Qt

# Import widget components and controller
from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget
from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame
from src.ui.qt.material_editor.widgets.material_export_widget import MaterialExportWidget
from src.ui.qt.material_editor.controller import MaterialEditorController


class MaterialEditorMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Editor — RD2229")
        self.resize(1200, 700)
        self.controllers = []
        self._init_ui()

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Tab tipologie
        self.tab_widget = QTabWidget()
        for tipologia in ["Calcestruzzi", "Acciai", "Legno", "Muratura", "Compositi", "Terreni"]:
            tab = QWidget()
            tab_layout = QHBoxLayout()
            # Tabella materiali
            table = MaterialTableWidget()
            # Frame dettaglio + export in side panel
            side_panel = QWidget()
            side_layout = QVBoxLayout()
            detail = MaterialDetailFrame()
            export = MaterialExportWidget()
            side_layout.addWidget(detail)
            side_layout.addWidget(export)
            side_panel.setLayout(side_layout)

            tab_layout.addWidget(table, 3)
            tab_layout.addWidget(side_panel, 1)
            tab.setLayout(tab_layout)
            self.tab_widget.addTab(tab, tipologia)

            # Controller per tab
            controller = MaterialEditorController()
            controller.attach_table(table)
            controller.attach_detail(detail)
            controller.attach_export(export)
            self.controllers.append(controller)

        main_layout.addWidget(self.tab_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("Aggiungi")
        self.load_button = QPushButton("Carica")
        self.save_button = QPushButton("Salva")
        self.reset_layout_button = QPushButton("Reset layout")
        self.open_log_button = QPushButton("Apri log")
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.load_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.reset_layout_button)
        toolbar_layout.addWidget(self.open_log_button)
        main_layout.addLayout(toolbar_layout)

        # Connect toolbar actions
        try:
            self.add_button.clicked.connect(self.on_add_clicked)
            self.open_log_button.clicked.connect(self.on_open_log)
            self.reset_layout_button.clicked.connect(self.on_reset_layout)
            self.load_button.clicked.connect(self.on_load_clicked)
            self.save_button.clicked.connect(self.on_save_clicked)
        except Exception:
            pass

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # global shortcuts undo/redo
        try:
            from PySide6.QtGui import QKeySequence
            from PySide6.QtWidgets import QShortcut
            QShortcut(QKeySequence('Ctrl+Z'), self, activated=self._on_undo)
            QShortcut(QKeySequence('Ctrl+Y'), self, activated=self._on_redo)
        except Exception:
            pass

    def get_active_controller(self):
        idx = self.tab_widget.currentIndex()
        if idx < 0 or idx >= len(self.controllers):
            return None
        return self.controllers[idx]

    def on_add_clicked(self):
        ctl = self.get_active_controller()
        if ctl is not None:
            ctl.start_new_material()

    def on_open_log(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        ctl = self.get_active_controller()
        if ctl is None:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle('Audit log')
        layout = QVBoxLayout()
        te = QTextEdit()
        te.setReadOnly(True)
        # show audit log entries
        try:
            lines = []
            for e in getattr(ctl.repo, 'audit_log', []):
                lines.append(str(e))
            te.setPlainText('\n'.join(lines))
        except Exception:
            te.setPlainText('No audit log available')
        layout.addWidget(te)
        btn = QPushButton('Chiudi')
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.exec()

    def on_reset_layout(self):
        # ask active controller to reset its layout prefs
        ctl = self.get_active_controller()
        if ctl is not None and hasattr(ctl.repo, 'reset_layout'):
            try:
                ctl.repo.reset_layout()
            except Exception:
                pass

    def _on_undo(self):
        ctl = self.get_active_controller()
        if ctl is None:
            return
        try:
            ctl.repo.undo()
            if hasattr(ctl, 'model') and ctl.model is not None:
                ctl.model.refresh()
        except Exception:
            pass

    def _on_redo(self):
        ctl = self.get_active_controller()
        if ctl is None:
            return
        try:
            ctl.repo.redo()
            if hasattr(ctl, 'model') and ctl.model is not None:
                ctl.model.refresh()
        except Exception:
            pass

    def on_save_clicked(self):
        from PySide6.QtWidgets import QFileDialog
        ctl = self.get_active_controller()
        if ctl is None:
            return
        fname, _ = QFileDialog.getSaveFileName(self, 'Salva materiali', '', 'JSON Files (*.json);;All Files (*)')
        if fname:
            try:
                ctl.repo.save_to_file(fname)
            except Exception:
                pass

    def on_load_clicked(self):
        from PySide6.QtWidgets import QFileDialog
        ctl = self.get_active_controller()
        if ctl is None:
            return
        fname, _ = QFileDialog.getOpenFileName(self, 'Carica materiali', '', 'JSON Files (*.json);;All Files (*)')
        if fname:
            try:
                ctl.repo.load_from_file(fname)
                if hasattr(ctl, 'model') and ctl.model is not None:
                    ctl.model.refresh()
            except Exception:
                pass

# Per test rapido standalone
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = MaterialEditorMainWindow()
    window.show()
    sys.exit(app.exec())
