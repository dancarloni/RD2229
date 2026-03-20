"""Material Editor GUI — Entry point main window."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ui.qt.material_editor.controller import MaterialEditorController
from src.ui.qt.material_editor.logic.material_layout_logic import MaterialLayoutLogic
from src.ui.qt.material_editor.widgets.material_add_wizard import MaterialAddWizard
from src.ui.qt.material_editor.widgets.material_batch_edit_dialog import MaterialBatchEditDialog
from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame
from src.ui.qt.material_editor.widgets.material_export_widget import MaterialExportWidget
from src.ui.qt.material_editor.widgets.material_settings_dialog import MaterialSettingsDialog
from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget


class MaterialEditorMainWindow(QMainWindow):
    """Main window per il Material Editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Editor — RD2229")
        self.resize(1200, 700)
        self.controllers = []
        self._splitters: list[QSplitter] = []
        self._init_ui()
        self._restore_splitter_sizes()

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
            "Terreni": "terreno",
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

        # Lato sinistro: filtro norma + tabella (70%)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(3)

        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(6)
        filter_bar.addWidget(QLabel("Filtro norma:"))
        filter_combo = QComboBox()
        filter_combo.setMinimumWidth(160)
        filter_combo.addItem("Tutte le norme", None)
        filter_bar.addWidget(filter_combo)
        filter_bar.addStretch()
        left_layout.addLayout(filter_bar)

        table = MaterialTableWidget()
        table.setMinimumHeight(300)
        left_layout.addWidget(table)

        # Lato destro: detail frame + export
        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(5)

        detail = MaterialDetailFrame()
        export = MaterialExportWidget()  # collegato al controller ma non nel layout
        side_layout.addWidget(QLabel(f"Parametri {tipologia}:"), 0)
        side_layout.addWidget(detail, 1)

        # Splitter orizzontale ridimensionabile
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(side_panel)
        splitter.setSizes([800, 500])
        splitter.setChildrenCollapsible(False)
        splitter.splitterMoved.connect(self._on_splitter_moved)
        self._splitters.append(splitter)

        tab_layout.addWidget(splitter)
        self.tab_widget.addTab(tab, tipologia)

        # Collega controller ai widget (IMPORTANTE: ordine corretto)
        try:
            controller.attach_detail(detail)
            controller.attach_export(export)
            controller.attach_table(table)
        except Exception as e:
            print(f"Errore setup tab {tipologia}: {e}")

        # Popola e collega il filtro norma (dopo attach_table per avere i dati)
        self._populate_norma_filter(filter_combo, controller)
        filter_combo.currentIndexChanged.connect(
            lambda _idx, tbl=table, ctl=controller, cb=filter_combo: self._apply_norma_filter(
                tbl, ctl, cb.currentData()
            )
        )

    def _create_toolbar(self) -> QHBoxLayout:
        """Crea la toolbar con i pulsanti di azione."""
        toolbar_layout = QHBoxLayout()
        self.add_button = QPushButton("Aggiungi")
        self.load_button = QPushButton("Carica")
        self.save_button = QPushButton("Salva")
        self.reset_layout_button = QPushButton("Reset layout")
        self.open_log_button = QPushButton("Apri log")

        self.batch_edit_button = QPushButton("Modifica batch…")
        self.save_catalog_button = QPushButton("Salva su catalogo…")
        self.settings_button = QPushButton("Impostazioni")

        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.load_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.batch_edit_button)
        toolbar_layout.addWidget(self.save_catalog_button)
        toolbar_layout.addWidget(self.reset_layout_button)
        toolbar_layout.addWidget(self.open_log_button)
        toolbar_layout.addWidget(self.settings_button)

        self.add_button.clicked.connect(self.on_add_clicked)
        self.open_log_button.clicked.connect(self.on_open_log)
        self.reset_layout_button.clicked.connect(self.on_reset_layout)
        self.load_button.clicked.connect(self.on_load_clicked)
        self.save_button.clicked.connect(self.on_save_clicked)
        self.batch_edit_button.clicked.connect(self.on_batch_edit_clicked)
        self.save_catalog_button.clicked.connect(self.on_save_catalog_clicked)
        self.settings_button.clicked.connect(self.on_settings_clicked)

        return toolbar_layout

    # ── norma filter helpers ──────────────────────────────────────────────────

    def _populate_norma_filter(self, filter_combo: QComboBox, controller) -> None:
        """Aggiunge al combo le norme presenti nei materiali del controller."""
        norme = sorted(
            {
                mat.get("norma_riferimento") or mat.get("norma", "")
                for mat in controller.repo.materials
                if mat.get("norma_riferimento") or mat.get("norma")
            }
        )
        filter_combo.blockSignals(True)
        filter_combo.clear()
        filter_combo.addItem("Tutte le norme", None)
        for n in norme:
            filter_combo.addItem(n, n)
        filter_combo.blockSignals(False)

    def _apply_norma_filter(self, table, controller, norma_key) -> None:
        """Nasconde le righe non corrispondenti alla norma e le colonne vuote."""
        model = table.model()
        if model is None:
            return
        # Righe
        for row in range(model.rowCount()):
            if norma_key is None:
                table.setRowHidden(row, False)
            else:
                mat = controller.repo.materials[row]
                mat_norma = mat.get("norma_riferimento") or mat.get("norma", "")
                table.setRowHidden(row, mat_norma != norma_key)
        # Colonne vuote (per le righe visibili)
        for col in range(model.columnCount()):
            has_value = False
            for row in range(model.rowCount()):
                if not table.isRowHidden(row):
                    val = model.data(model.index(row, col))
                    if val and str(val).strip():
                        has_value = True
                        break
            table.setColumnHidden(col, not has_value)

    def _setup_shortcuts(self) -> None:
        """Configura i shortcut globali."""
        sc_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        sc_undo.activated.connect(self._on_undo)
        sc_redo = QShortcut(QKeySequence("Ctrl+Y"), self)
        sc_redo.activated.connect(self._on_redo)

    def get_active_controller(self) -> MaterialEditorController | None:
        """Restituisce il controller della tab attiva."""
        idx = self.tab_widget.currentIndex()
        if 0 <= idx < len(self.controllers):
            return self.controllers[idx]
        return None

    def on_add_clicked(self):
        """Apre il wizard per aggiungere un nuovo materiale."""
        ctl = self.get_active_controller()
        if not ctl:
            return
        wizard = MaterialAddWizard(self)
        # Pre-seleziona famiglia dal tab attivo
        if ctl.famiglia:
            from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

            families = MaterialConfigLoader().load_families()
            for i, f in enumerate(families):
                if f["key"] == ctl.famiglia:
                    try:
                        wizard._combo_famiglia.setCurrentIndex(i)
                        wizard._on_famiglia_changed()
                    except Exception:
                        pass
                    break
        if wizard.exec() == QDialog.DialogCode.Accepted:
            mat = wizard.get_result_material()
            if mat:
                ctl.repo.add_material(mat)
                if hasattr(ctl, "model") and ctl.model:
                    ctl.model.refresh()
                # Seleziona il nuovo materiale
                last_idx = len(ctl.repo.materials) - 1
                if last_idx >= 0:
                    ctl.current_index = last_idx
                    ctl.populate_detail_from_index(last_idx)
                    if ctl.table:
                        try:
                            ctl.table.selectRow(last_idx)
                        except Exception:
                            pass

    def on_batch_edit_clicked(self):
        """Apre il dialog batch edit per modificare lo stesso campo su N materiali."""
        ctl = self.get_active_controller()
        if ctl is None:
            return

        # Recupera indici selezionati dalla tabella (se disponibile)
        selected_indices: list[int] = []
        try:
            if hasattr(ctl, "table") and ctl.table is not None:
                selected_indices = [idx.row() for idx in ctl.table.selectionModel().selectedRows()]
        except Exception:
            pass

        if not selected_indices:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "Nessuna selezione",
                "Selezionare almeno un materiale nella tabella prima di usare il batch edit.",
            )
            return

        dlg = MaterialBatchEditDialog(
            materials=ctl.repo.materials,
            selected_indices=selected_indices,
            parent=self,
        )
        if dlg.exec() == MaterialBatchEditDialog.DialogCode.Accepted:
            field, value = dlg.get_result()
            if field:
                ctl.on_batch_edit_accepted(field, value, selected_indices)

    def on_save_catalog_clicked(self):
        """Salva i materiali del tab attivo nel catalogo di sistema corrispondente."""
        from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QMessageBox

        ctl = self.get_active_controller()
        if ctl is None:
            return

        # Raccogli famiglie e norme disponibili dai materiali del repo
        norme_disponibili: list[str] = sorted(
            {
                m.get("norma_riferimento") or m.get("norma", "")
                for m in ctl.repo.materials
                if m.get("norma_riferimento") or m.get("norma")
            }
        )
        famiglie_disponibili: list[str] = sorted(
            {m.get("famiglia", "") for m in ctl.repo.materials if m.get("famiglia")}
        )

        if not norme_disponibili or not famiglie_disponibili:
            QMessageBox.information(
                self,
                "Nessun materiale",
                "Nessun materiale con famiglia e norma definite nel repository attivo.",
            )
            return

        # Dialog selezione famiglia + norma
        dlg = QDialog(self)
        dlg.setWindowTitle("Salva su catalogo di sistema")
        form = QFormLayout(dlg)

        combo_fam = QComboBox()
        for f in famiglie_disponibili:
            combo_fam.addItem(f)
        if ctl.famiglia:
            idx = combo_fam.findText(ctl.famiglia)
            if idx >= 0:
                combo_fam.setCurrentIndex(idx)
        form.addRow("Famiglia:", combo_fam)

        combo_norma = QComboBox()
        for n in norme_disponibili:
            combo_norma.addItem(n)
        form.addRow("Norma:", combo_norma)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        famiglia = combo_fam.currentText()
        norma = combo_norma.currentText()

        # Conta materiali che verranno salvati
        subset = [
            m
            for m in ctl.repo.materials
            if m.get("famiglia") == famiglia
            and (m.get("norma_riferimento") == norma or m.get("norma") == norma)
        ]
        if not subset:
            QMessageBox.information(
                self,
                "Nessun materiale",
                f"Nessun materiale trovato per famiglia='{famiglia}' e norma='{norma}'.",
            )
            return

        # Conferma
        reply = QMessageBox.question(
            self,
            "Conferma salvataggio catalogo",
            f"Salvare {len(subset)} materiale/i ({famiglia} / {norma}) nel catalogo di sistema?\n"
            "Un backup (.bak) sarà creato automaticamente.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            saved_path = ctl.repo.save_catalog(famiglia, norma)
            QMessageBox.information(
                self,
                "Catalogo salvato",
                f"Salvati {len(subset)} materiali in:\n{saved_path}",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Errore salvataggio catalogo",
                f"Impossibile salvare il catalogo:\n{exc}",
            )

    def on_settings_clicked(self):
        """Apre il dialog Impostazioni con tab config materiali + coefficienti globali."""
        from src.ui.qt.settings.material_coefficients_settings_widget import (
            MaterialCoefficientsSettingsWidget,
        )

        dlg = QDialog(self)
        dlg.setWindowTitle("Impostazioni — Materiali")
        dlg.resize(860, 580)

        tabs = QTabWidget(dlg)
        # Tab 1: coefficienti normativi globali
        coeffs_tab = MaterialCoefficientsSettingsWidget(dlg)
        tabs.addTab(coeffs_tab, "Coefficienti normativi globali")

        # Tab 2: configurazione schemi/formule (vista formule)
        config_tab = MaterialSettingsDialog(dlg)
        tabs.addTab(config_tab, "Schema e formule")

        layout = QVBoxLayout(dlg)
        layout.addWidget(tabs)
        dlg.exec()

    def on_open_log(self):
        """Mostra il dialog di audit log."""
        ctl = self.get_active_controller()
        if not ctl:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Audit log")
        layout = QVBoxLayout()
        te = QTextEdit()
        te.setReadOnly(True)
        try:
            lines = [str(e) for e in getattr(ctl.repo, "audit_log", [])]
            te.setPlainText("\n".join(lines))
        except Exception:
            te.setPlainText("No audit log available")
        layout.addWidget(te)
        btn = QPushButton("Chiudi")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.exec()

    def closeEvent(self, event) -> None:
        """Salva le dimensioni degli splitter alla chiusura."""
        self._save_splitter_sizes()
        super().closeEvent(event)

    def _on_splitter_moved(self, pos: int, index: int) -> None:
        """Salva le dimensioni ogni volta che uno splitter viene mosso."""
        self._save_splitter_sizes()

    def _save_splitter_sizes(self) -> None:
        if self._splitters:
            sizes = self._splitters[0].sizes()
            MaterialLayoutLogic.save_layout({"splitter_sizes": sizes})

    def _restore_splitter_sizes(self) -> None:
        prefs = MaterialLayoutLogic.load_layout()
        sizes = prefs.get("splitter_sizes")
        if sizes and len(sizes) == 2 and self._splitters:
            for splitter in self._splitters:
                splitter.setSizes(sizes)

    def on_reset_layout(self):
        """Reset layout preferences e ripristina dimensioni default."""
        MaterialLayoutLogic.reset_layout()
        for splitter in self._splitters:
            splitter.setSizes([800, 500])

    def _on_undo(self):
        """Undo action."""
        ctl = self.get_active_controller()
        if ctl:
            try:
                ctl.repo.undo()
                if hasattr(ctl, "model") and ctl.model:
                    ctl.model.refresh()
            except Exception:
                pass

    def _on_redo(self):
        """Redo action."""
        ctl = self.get_active_controller()
        if ctl:
            try:
                ctl.repo.redo()
                if hasattr(ctl, "model") and ctl.model:
                    ctl.model.refresh()
            except Exception:
                pass

    def on_save_clicked(self):
        """Salva i materiali su file JSON."""
        ctl = self.get_active_controller()
        if not ctl:
            return
        fname, _ = QFileDialog.getSaveFileName(
            self, "Salva materiali", "", "JSON Files (*.json);;All Files (*)"
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
            self, "Carica materiali", "", "JSON Files (*.json);;All Files (*)"
        )
        if fname:
            try:
                ctl.repo.load_from_file(fname)
                if hasattr(ctl, "model") and ctl.model:
                    ctl.model.refresh()
            except Exception:
                pass


def main():
    """Funzione main per avviare l'editor."""
    app = QApplication(sys.argv)
    window = MaterialEditorMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
