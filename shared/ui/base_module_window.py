"""
Classe base per tutte le finestre modulo di calcolo.

Fornisce:
- Menu bar standard (File | Calcolo | Aiuto)
- Toolbar con pulsanti comuni (Calcola, Batch, Salva, Export, Tabulato)
- Barra norma con selezione norma / stato limite / LC
- Area centrale splitter: Input (sinistro) | Risultati (destro)
- Status bar con info stato

Ogni modulo eredita da questa classe e personalizza:
- _create_input_panel() — pannello input specifico modulo
- _create_results_panel() — pannello risultati specifico modulo
- _create_batch_panel() — tab batch multi-elemento
- _create_tabulato_panel() — generazione tabulato con formule
"""

from typing import Any, Optional

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QLabel,
        QMainWindow,
        QMenu,
        QMenuBar,
        QSplitter,
        QTabWidget,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    QT_BACKEND = "PySide6"
except ImportError:
    from PyQt6.QtCore import Qt, pyqtSignal as Signal
    from PyQt6.QtGui import QAction
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QLabel,
        QMainWindow,
        QMenu,
        QMenuBar,
        QSplitter,
        QTabWidget,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

    QT_BACKEND = "PyQt6"

from pipeline.module_registry import ModuleInfo, ModuleResult


class BaseModuleWindow(QMainWindow):
    """
    Classe base per la finestra di ogni modulo di calcolo.

    Fornisce interfaccia unificata con:
    - Menu bar (File | Calcolo | Aiuto)
    - Toolbar con pulsanti standard
    - Selezione norma / stato limite / LC/FC
    - Splitter Input | Risultati
    - Status bar

    Subclass deve implementare:
    - _create_input_panel()
    - _create_results_panel()
    - _create_batch_panel()
    - _create_tabulato_panel()
    """

    # Segnali comuni
    calculation_completed = Signal(ModuleResult)
    data_changed = Signal()

    def __init__(self, module_info: ModuleInfo, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.module_info = module_info
        self.current_norm = None
        self.current_limit_state = None
        self.current_kc = None

        # Setup UI
        self.setWindowTitle(f"{module_info.name} — RD2229 v0.1.0")
        self._setup_menu()
        self._setup_toolbar()
        self._setup_norm_bar()
        self._setup_central()
        self._setup_status_bar()

        # Default size
        self.resize(1200, 700)

    def _setup_menu(self) -> None:
        """Crea menu bar con File | Calcolo | Aiuto."""
        menubar: QMenuBar = self.menuBar()

        # Menu File
        file_menu: QMenu = menubar.addMenu("File")
        save_action = QAction("💾 Salva", self)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Calcolo
        calc_menu: QMenu = menubar.addMenu("Calcolo")
        run_action = QAction("▶ Calcola", self)
        run_action.triggered.connect(self._on_calculate)
        calc_menu.addAction(run_action)
        run_batch_action = QAction("▶ Calcola Batch", self)
        run_batch_action.triggered.connect(self._on_calculate_batch)
        calc_menu.addAction(run_batch_action)

        # Menu Aiuto
        help_menu: QMenu = menubar.addMenu("Aiuto")
        about_action = QAction("Info modulo", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Crea toolbar con pulsanti standard."""
        toolbar: QToolBar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        calc_action = QAction("▶ Calcola", self)
        calc_action.triggered.connect(self._on_calculate)
        toolbar.addAction(calc_action)

        batch_action = QAction("📊 Batch", self)
        batch_action.triggered.connect(self._on_calculate_batch)
        toolbar.addAction(batch_action)

        toolbar.addSeparator()

        save_action = QAction("💾 Salva", self)
        save_action.triggered.connect(self._on_save)
        toolbar.addAction(save_action)

        export_action = QAction("📤 Export", self)
        export_action.triggered.connect(self._on_export)
        toolbar.addAction(export_action)

    def _setup_norm_bar(self) -> None:
        """Crea barra con selezione norma / SL / LC."""
        norm_bar: QToolBar = self.addToolBar("Norm Bar")
        norm_bar.setMovable(False)

        # Etichetta e combo norma
        norm_label = QLabel("Norma: ")
        norm_bar.addWidget(norm_label)

        self.norm_combo = QComboBox()
        self.norm_combo.addItems(self.module_info.norms_supported)
        self.norm_combo.currentTextChanged.connect(self._on_norm_changed)
        norm_bar.addWidget(self.norm_combo)

        # Etichetta e combo stato limite
        sl_label = QLabel("  Stato Limite: ")
        norm_bar.addWidget(sl_label)

        self.sl_combo = QComboBox()
        self.sl_combo.addItems(["SLU", "SLE_rara", "SLE_freq", "SLE_qp", "SLV"])
        self.sl_combo.currentTextChanged.connect(self._on_sl_changed)
        norm_bar.addWidget(self.sl_combo)

        # Checkbox struttura esistente
        norm_bar.addSeparator()
        self.existing_structure_check = QCheckBox("☐ Struttura esistente")
        self.existing_structure_check.stateChanged.connect(self._on_existing_changed)
        norm_bar.addWidget(self.existing_structure_check)

        # Combo LC (disabilitato finché non selezionata "struttura esistente")
        lc_label = QLabel("  LC: ")
        norm_bar.addWidget(lc_label)

        self.lc_combo = QComboBox()
        self.lc_combo.addItems(["LC1", "LC2", "LC3"])
        self.lc_combo.setEnabled(False)
        self.lc_combo.currentTextChanged.connect(self._on_lc_changed)
        norm_bar.addWidget(self.lc_combo)

    def _setup_central(self) -> None:
        """Crea area centrale con splitter Input | Risultati."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Splitter orizzontale
        splitter = QSplitter(Qt.Horizontal)

        # Tab sinistra: INPUT
        self.input_tabs = QTabWidget()
        self.input_panel = self._create_input_panel()
        self.batch_panel = self._create_batch_panel()
        self.input_tabs.addTab(self.input_panel, "Input")
        self.input_tabs.addTab(self.batch_panel, "📊 Batch")
        splitter.addWidget(self.input_tabs)

        # Tab destra: RISULTATI
        self.result_tabs = QTabWidget()
        self.results_panel = self._create_results_panel()
        self.tabulato_panel = self._create_tabulato_panel()
        self.result_tabs.addTab(self.results_panel, "Risultati")
        self.result_tabs.addTab(self.tabulato_panel, "📜 Tabulato")
        splitter.addWidget(self.result_tabs)

        # Proporzionamento
        splitter.setSizes([500, 700])
        layout.addWidget(splitter)

    def _setup_status_bar(self) -> None:
        """Crea status bar con info stato."""
        self.status_label = QLabel("Pronto")
        self.statusBar().addWidget(self.status_label)

    def _create_input_panel(self) -> QWidget:
        """Crea pannello input specifico modulo. Override in subclass."""
        raise NotImplementedError("Subclass must implement _create_input_panel()")

    def _create_batch_panel(self) -> QWidget:
        """Crea tab batch multi-elemento. Override in subclass."""
        raise NotImplementedError("Subclass must implement _create_batch_panel()")

    def _create_results_panel(self) -> QWidget:
        """Crea pannello risultati specifico modulo. Override in subclass."""
        raise NotImplementedError("Subclass must implement _create_results_panel()")

    def _create_tabulato_panel(self) -> QWidget:
        """Crea pannello tabulato con formule. Override in subclass."""
        raise NotImplementedError("Subclass must implement _create_tabulato_panel()")

    # Slot comuni
    def _on_calculate(self) -> None:
        """Esegue calcolo su elemento singolo."""
        self.status_label.setText("Calcolo in corso...")
        # Implementare nel modulo specifico
        self.status_label.setText("Calcolo completato")

    def _on_calculate_batch(self) -> None:
        """Esegue calcolo batch su più elementi."""
        self.status_label.setText("Calcolo batch in corso...")
        # Implementare nel modulo specifico
        self.status_label.setText("Calcolo batch completato")

    def _on_save(self) -> None:
        """Salva risultati."""
        self.status_label.setText("Salvataggio...")
        # Implementare nel modulo specifico

    def _on_export(self) -> None:
        """Esporta risultati (CSV, PDF, ecc.)."""
        self.status_label.setText("Esportazione...")
        # Implementare nel modulo specifico

    def _on_norm_changed(self, norm_code: str) -> None:
        """Cambia norma di calcolo. Filtra materiali disponibili."""
        self.current_norm = norm_code
        self.status_label.setText(f"Norma: {norm_code}")
        self.data_changed.emit()

    def _on_sl_changed(self, sl_code: str) -> None:
        """Cambia stato limite."""
        self.current_limit_state = sl_code
        self.status_label.setText(f"Stato limite: {sl_code}")
        self.data_changed.emit()

    def _on_existing_changed(self) -> None:
        """Abilita/disabilita selezione LC."""
        is_checked = self.existing_structure_check.isChecked()
        self.lc_combo.setEnabled(is_checked)
        if is_checked:
            self.current_kc = self.lc_combo.currentText()
        else:
            self.current_kc = None
        self.data_changed.emit()

    def _on_lc_changed(self, lc_code: str) -> None:
        """Cambia livello conoscenza (LC1/LC2/LC3)."""
        if self.existing_structure_check.isChecked():
            self.current_kc = lc_code
            self.status_label.setText(f"LC: {lc_code} (FC={self._get_fc(lc_code)})")
            self.data_changed.emit()

    def _on_about(self) -> None:
        """Mostra info modulo."""
        msg = f"{self.module_info.name}\n"
        msg += f"Norme: {', '.join(self.module_info.norms_supported)}\n"
        msg += f"Descrizione: {self.module_info.description}"
        # Mostrare in dialog (implementare)

    @staticmethod
    def _get_fc(lc_code: str) -> float:
        """Restituisce fattore di confidenza per LC."""
        fc_map = {"LC1": 1.35, "LC2": 1.20, "LC3": 1.00}
        return fc_map.get(lc_code, 1.0)


__all__ = ["BaseModuleWindow", "QT_BACKEND"]
