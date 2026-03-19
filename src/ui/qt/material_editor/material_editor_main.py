"""Material Editor GUI — Entry point main window."""
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ui.qt.material_editor.controller import MaterialEditorController
from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame
from src.ui.qt.material_editor.widgets.material_export_widget import MaterialExportWidget
from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget


class MaterialEditorMainWindow(QMainWindow):
    """Main window per il Material Editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Editor — RD2229")
        self.resize(1200, 700)
        self.controllers = []
        self._init_ui()

    def _init_ui(self):
        """Inizializza l'UI della finestra principale."""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Crea tab per ogni famiglia di materiali
        self.tab_widget = QTabWidget()
        famiglia_map = {
            "Calcestruzzi": "calcestruzzo",
            "Acciai": "acciaio",
            "Legno": "legno",
            "Muratura": "muratura",
            "Compositi": "composito",
            "Terreni": "terreno"
        }

        for tipologia, famiglia in famiglia_map.items():
            self._create_tab(tipologia, famiglia)

        main_layout.addWidget(self.tab_widget)

        # Toolbar con pulsanti
        toolbar_layout = self._create_toolbar()
        main_layout.addLayout(toolbar_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Shortcut globali
        self._setup_shortcuts()

    def _create_tab(self, tipologia: str, famiglia: str) -> None:
        """Crea una scheda (tab) per una famiglia di materiali."""
        controller = MaterialEditorController(famiglia=famiglia)
        self.controllers.append(controller)

        tab = QWidget()
        tab_layout = QHBoxLayout(tab)
        tab_layout.setContentsMargins(5, 5, 5, 5)
        tab_layout.setSpacing(5)

        # Lato sinistro: tabella (70%)
        table = MaterialTableWidget()
        table.setMinimumHeight(300)
        tab_layout.addWidget(table, 70)

        # Lato destro: detail frame + export (30%)
        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(5)

        detail = MaterialDetailFrame()
        export = MaterialExportWidget()
        side_layout.addWidget(QLabel(f"Parametri {tipologia}:"), 0)
        side_layout.addWidget(detail, 1)
        side_layout.addWidget(QLabel("Esportazione:"), 0)
        side_layout.addWidget(export, 0)

        tab_layout.addWidget(side_panel, 30)
        self.tab_widget.addTab(tab, tipologia)

        # Collega controller ai widget (IMPORTANTE: ordine corretto)
        try:
            controller.attach_detail(detail)
            controller.attach_export(export)
            controller.attach_table(table)
        except Exception as e:
            print(f"Errore setup tab {tipologia}: {e}")

    def _create_toolbar(self) -> QHBoxLayout:
        """Crea la toolbar con i pulsanti di azione."""
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

        self.add_button.clicked.connect(self.on_add_clicked)
        self.open_log_button.clicked.connect(self.on_open_log)
        self.reset_layout_button.clicked.connect(self.on_reset_layout)
        self.load_button.clicked.connect(self.on_load_clicked)
        self.save_button.clicked.connect(self.on_save_clicked)

        return toolbar_layout

    def _setup_shortcuts(self) -> None:
        """Configura i shortcut globali."""
        QShortcut(QKeySequence('Ctrl+Z'), self, activated=self._on_undo)
        QShortcut(QKeySequence('Ctrl+Y'), self, activated=self._on_redo)

    def get_active_controller(self) -> MaterialEditorController | None:
        """Restituisce il controller della tab attiva."""
        idx = self.tab_widget.currentIndex()
        if 0 <= idx < len(self.controllers):
            return self.controllers[idx]
        return None

    def on_add_clicked(self):
        """Handler per pulsante Aggiungi."""
        ctl = self.get_active_controller()
        if ctl:
            ctl.start_new_material()

    def on_open_log(self):
        """Mostra il dialog di audit log."""
        ctl = self.get_active_controller()
        if not ctl:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle('Audit log')
        layout = QVBoxLayout()
        te = QTextEdit()
        te.setReadOnly(True)
        try:
            lines = [str(e) for e in getattr(ctl.repo, 'audit_log', [])]
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
        """Reset layout preferences."""
        ctl = self.get_active_controller()
        if ctl and hasattr(ctl.repo, 'reset_layout'):
            try:
                ctl.repo.reset_layout()
            except Exception:
                pass

    def _on_undo(self):
        """Undo action."""
        ctl = self.get_active_controller()
        if ctl:
            try:
                ctl.repo.undo()
                if hasattr(ctl, 'model') and ctl.model:
                    ctl.model.refresh()
            except Exception:
                pass

    def _on_redo(self):
        """Redo action."""
        ctl = self.get_active_controller()
        if ctl:
            try:
                ctl.repo.redo()
                if hasattr(ctl, 'model') and ctl.model:
                    ctl.model.refresh()
            except Exception:
                pass

    def on_save_clicked(self):
        """Salva i materiali su file JSON."""
        ctl = self.get_active_controller()
        if not ctl:
            return
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Salva materiali', '',
            'JSON Files (*.json);;All Files (*)'
        )
        if fname:
            try:
                ctl.repo.save_to_file(fname)
            except Exception:
                pass

    def on_load_clicked(self):
        """Carica i materiali da file JSON."""
        ctl = self.get_active_controller()
        if not ctl:
            return
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Carica materiali', '',
            'JSON Files (*.json);;All Files (*)'
        )
        if fname:
            try:
                ctl.repo.load_from_file(fname)
                if hasattr(ctl, 'model') and ctl.model:
                    ctl.model.refresh()
            except Exception:
                pass


def main():
    """Funzione main per avviare l'editor."""
    app = QApplication(sys.argv)
    window = MaterialEditorMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
