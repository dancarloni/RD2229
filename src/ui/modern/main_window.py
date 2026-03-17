"""Finestra principale operativa tab-based per la GUI moderna RD2229."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

from src.core.persistence import ProjectIndex
from src.core.user_config import UserConfig
from src.reporting.report_builder import build_report
from src.ui.qt.code_settings import CodeSettingsWindow
from src.ui.qt.cordoli_widget import CordoliWidget
from src.ui.qt.material_editor import EditorMaterialeWidget
from src.ui.qt.notification_center import NotificationCenterWindow
from src.ui.qt.pipeline_runner import PipelineRunnerWindow
from src.ui.qt.project_editor import ProjectEditorWindow
from src.ui.qt.report_viewer import ReportViewerWindow
from src.ui.qt.section_manager import SectionManagerWindow
from src.ui.qt.telaio.telaio_window import TelaioWindow

from .features.registry import FeatureSpec, clear as clear_registry, get_enabled, register
from .services import ActionReport, CalculationService, PresetExecutionService, ProjectIOService


class _ProjectServiceProxy:
    def __init__(self, project: Any) -> None:
        self.current_project = project

    def set_project(self, project: Any) -> None:
        self.current_project = project


def _format_report(report: ActionReport) -> list[str]:
    lines = [f"[{report.name}] {'OK' if report.ok else 'NON OK'} - {report.summary}"]
    for key, value in report.details.items():
        lines.append(f"  - {key}: {value}")
    return lines


def _load_qaction(backend_mod: str) -> Any:
    module_name = "PyQt6.QtGui" if backend_mod.startswith("PyQt6") else "PySide6.QtGui"
    module = importlib.import_module(module_name)
    return getattr(module, "QAction")


def _load_qtimer(backend_mod: str) -> Any:
    module_name = "PyQt6.QtCore" if backend_mod.startswith("PyQt6") else "PySide6.QtCore"
    module = importlib.import_module(module_name)
    return getattr(module, "QTimer")


def _load_qsplitter(backend_mod: str) -> Any:
    module_name = "PyQt6.QtWidgets" if backend_mod.startswith("PyQt6") else "PySide6.QtWidgets"
    module = importlib.import_module(module_name)
    return getattr(module, "QSplitter")


def _load_qlistwidget(backend_mod: str) -> Any:
    """Carica QListWidget dal backend Qt corretto (GUI-3.3)."""
    module_name = "PyQt6.QtWidgets" if backend_mod.startswith("PyQt6") else "PySide6.QtWidgets"
    module = importlib.import_module(module_name)
    return getattr(module, "QListWidget")


def build_main_window(
    qt: dict[str, Any],
    default_project: str | None,
    default_output: str | None,
    runner: Callable[[str, str | None], dict[str, str | bool]],
) -> Any:
    """Costruisce shell operativa con tab, preset, menu e persistenza utente."""

    QMainWindow = qt["QMainWindow"]
    QWidget = qt["QWidget"]
    QLabel = qt["QLabel"]
    QLineEdit = qt["QLineEdit"]
    QPushButton = qt["QPushButton"]
    QTextEdit = qt["QTextEdit"]
    QGridLayout = qt["QGridLayout"]
    QVBoxLayout = qt["QVBoxLayout"]
    QHBoxLayout = qt["QHBoxLayout"]
    QTabWidget = qt["QTabWidget"]
    QFileDialog = qt["QFileDialog"]

    backend_mod = qt["QWidget"].__module__.split(".")[0]
    QAction = _load_qaction(backend_mod)
    QTimer = _load_qtimer(backend_mod)
    QSplitter = _load_qsplitter(backend_mod)
    QListWidget = _load_qlistwidget(backend_mod)  # GUI-3.3

    io_service = ProjectIOService()
    calc_service = CalculationService()
    preset_service = PresetExecutionService(io_service=io_service, calculation_service=calc_service)
    user_cfg = UserConfig.load()
    project_index = ProjectIndex()

    state: dict[str, Any] = {
        "project": io_service.new_project(),
        "project_path": None,
        "results": None,
    }

    # Servizi condivisi (material_repo, ecc.)
    from src.ui.qt.services import get_services

    services = get_services()
    project_service = _ProjectServiceProxy(state["project"])

    window = QMainWindow()
    window.setWindowTitle("RD2229 - Centro Operativo GUI-V2")
    window.resize(1280, 800)

    central = QWidget(window)
    root = QVBoxLayout(central)
    window.setCentralWidget(central)
    status = window.statusBar()
    status.showMessage("Pronto")

    status_norm = QLabel("Norma: -")
    status_project = QLabel("Progetto: non caricato")
    status_elements = QLabel("Elementi: 0")
    status_warnings = QLabel("Warnings: 0")
    status.addPermanentWidget(status_norm)
    status.addPermanentWidget(status_project)
    status.addPermanentWidget(status_elements)
    status.addPermanentWidget(status_warnings)

    tabs = QTabWidget(central)
    root.addWidget(tabs)

    # Dashboard tab
    dashboard = QWidget(tabs)
    dash_root = QVBoxLayout(dashboard)
    dash_root.addWidget(QLabel("<b>RD2229 Centro Operativo</b>"))
    dash_root.addWidget(
        QLabel("Workflow completo, preset rapidi e controllo I/O in una singola finestra.")
    )

    form = QGridLayout()
    txt_project = QLineEdit(default_project or "")
    txt_output = QLineEdit(default_output or user_cfg.last_output_dir or "")
    btn_project = QPushButton("Sfoglia progetto")
    btn_output = QPushButton("Sfoglia output")
    form.addWidget(QLabel("Progetto JSON"), 0, 0)
    form.addWidget(txt_project, 0, 1)
    form.addWidget(btn_project, 0, 2)
    form.addWidget(QLabel("Cartella output"), 1, 0)
    form.addWidget(txt_output, 1, 1)
    form.addWidget(btn_output, 1, 2)
    dash_root.addLayout(form)

    io_row = QHBoxLayout()
    btn_new = QPushButton("Nuovo")
    btn_open = QPushButton("Apri")
    btn_save = QPushButton("Salva")
    btn_run_pipeline = QPushButton("Esegui pipeline")
    btn_export_json = QPushButton("Export JSON")
    btn_export_md = QPushButton("Export MD")
    btn_export_html = QPushButton("Export HTML")
    for button in [
        btn_new,
        btn_open,
        btn_save,
        btn_run_pipeline,
        btn_export_json,
        btn_export_md,
        btn_export_html,
    ]:
        io_row.addWidget(button)
    io_row.addStretch(1)
    dash_root.addLayout(io_row)

    nav_row = QHBoxLayout()
    btn_go_project = QPushButton("Progetto e Dati")
    btn_go_verify = QPushButton("Verifiche e Pipeline")
    btn_go_report = QPushButton("Report e Tracciabilita")
    btn_go_special = QPushButton("Moduli Specialistici")
    for button in [btn_go_project, btn_go_verify, btn_go_report, btn_go_special]:
        button.setMinimumHeight(38)
        nav_row.addWidget(button)
    dash_root.addLayout(nav_row)

    body = QHBoxLayout()
    left_col = QVBoxLayout()
    right_col = QVBoxLayout()
    body.addLayout(left_col, 1)
    body.addLayout(right_col, 2)
    dash_root.addLayout(body)

    left_col.addWidget(QLabel("Card preset operativi"))

    # GUI-3.3: pannello progetti recenti nel dashboard (colonna destra)
    right_col.addWidget(QLabel("<b>Progetti recenti</b>"))
    recent_list = QListWidget(dashboard)
    recent_list.setMaximumHeight(130)
    recent_list.setToolTip(
        "Doppio click per aprire un progetto recente — stessa funzione del menu File > Recenti"
    )
    for rp in user_cfg.recent_projects:
        recent_list.addItem(rp)
    right_col.addWidget(recent_list)

    dash_log = QTextEdit(dashboard)
    dash_log.setReadOnly(True)
    right_col.addWidget(QLabel("Log esecuzione"))
    right_col.addWidget(dash_log)

    tabs.addTab(dashboard, "Dashboard")

    # Core tabs
    project_editor = ProjectEditorWindow(
        project_service=project_service,
        material_repo=getattr(services, "material_repo", None),
        parent=tabs,
    )
    pipeline_runner = PipelineRunnerWindow(project_service=project_service, parent=tabs)
    report_viewer = ReportViewerWindow(parent=tabs)
    materials_editor = EditorMaterialeWidget(parent=tabs)
    section_manager = SectionManagerWindow(project_service=project_service, parent=tabs)

    fem_tab = QWidget(tabs)
    fem_layout = QVBoxLayout(fem_tab)
    fem_layout.addWidget(QLabel("<b>FEM / Telai</b>"))

    fem_splitter = QSplitter(fem_tab)
    cordoli_widget = CordoliWidget(parent=fem_splitter)
    fem_splitter.addWidget(cordoli_widget)

    telaio_container = QWidget(fem_splitter)
    telaio_layout = QVBoxLayout(telaio_container)
    telaio_layout.addWidget(QLabel("<b>Telaio Cross-Pozzati</b>"))
    telaio_open_btn = QPushButton("Apri Telaio in finestra dedicata")
    telaio_layout.addWidget(telaio_open_btn)

    _telaio_windows: list[Any] = []

    def _open_telaio_window() -> None:
        telaio_window = TelaioWindow(parent=window)
        telaio_window.show()
        _telaio_windows.append(telaio_window)
        _append("Modulo Telaio aperto in finestra dedicata.")

    telaio_open_btn.clicked.connect(lambda _checked=False: _open_telaio_window())
    fem_splitter.addWidget(telaio_container)
    fem_splitter.setSizes([640, 540])
    fem_layout.addWidget(fem_splitter)

    wind_tab = QWidget(tabs)
    wind_layout = QVBoxLayout(wind_tab)
    wind_btn = QPushButton("Esegui preset vento NTC2018", wind_tab)
    wind_log = QTextEdit(wind_tab)
    wind_log.setReadOnly(True)
    wind_layout.addWidget(wind_btn)
    wind_layout.addWidget(wind_log)

    # Additional utility tabs for previously stubbed modules
    code_settings_tab = CodeSettingsWindow(parent=tabs)
    notifications_tab = NotificationCenterWindow(parent=tabs)

    # Macro-settore: Progetto e Dati
    project_data_tab = QWidget(tabs)
    project_data_layout = QVBoxLayout(project_data_tab)
    project_data_tabs = QTabWidget(project_data_tab)
    project_data_tabs.addTab(project_editor, "Progetto")
    project_data_tabs.addTab(materials_editor, "Materiali")
    project_data_tabs.addTab(section_manager, "Sezioni")
    project_data_tabs.addTab(code_settings_tab, "Normativa")
    project_data_layout.addWidget(project_data_tabs)

    # Macro-settore: Verifiche e Pipeline
    verify_tab = QWidget(tabs)
    verify_layout = QVBoxLayout(verify_tab)
    verify_layout.addWidget(pipeline_runner)

    # Macro-settore: Report e Tracciabilita
    report_tab = QWidget(tabs)
    report_layout = QVBoxLayout(report_tab)
    report_tabs = QTabWidget(report_tab)
    report_tabs.addTab(report_viewer, "Report")
    report_tabs.addTab(notifications_tab, "Notifiche")
    report_layout.addWidget(report_tabs)

    # Macro-settore: Moduli Specialistici
    specialist_tab = QWidget(tabs)
    specialist_layout = QVBoxLayout(specialist_tab)
    specialist_tabs = QTabWidget(specialist_tab)
    specialist_tabs.addTab(fem_tab, "FEM/Telai")
    specialist_tabs.addTab(wind_tab, "Vento")
    specialist_layout.addWidget(specialist_tabs)

    tabs.addTab(project_data_tab, "Progetto e Dati")
    tabs.addTab(verify_tab, "Verifiche e Pipeline")
    tabs.addTab(report_tab, "Report e Tracciabilita")
    tabs.addTab(specialist_tab, "Moduli Specialistici")

    def _refresh_status() -> None:
        project = project_service.current_project
        code_settings = getattr(project, "code_settings", None)
        geometry = getattr(project, "geometry", [])
        norm_code = getattr(code_settings, "norm_code", "-") if code_settings else "-"
        status_norm.setText(f"Norma: {norm_code}")
        project_label = state.get("project_path") or "non caricato"
        status_project.setText(f"Progetto: {project_label}")
        status_elements.setText(f"Elementi: {len(geometry)}")
        warnings_count = 0
        if state.get("results") is not None:
            warnings_count = len(getattr(state["results"], "warnings", []))
        status_warnings.setText(f"Warnings: {warnings_count}")

    def _append(message: str) -> None:
        dash_log.append(message)
        status.showMessage(message, 4000)

    def _append_report(report: ActionReport) -> None:
        for line in _format_report(report):
            _append(line)

    def _record_recent(path: str) -> None:
        user_cfg.add_recent(path)
        user_cfg.last_output_dir = txt_output.text().strip()
        user_cfg.save()
        project = project_service.current_project
        project_index.upsert(
            path=path,
            name=project.project_info.name or Path(path).stem,
            norm_code=project.code_settings.norm_code,
        )
        _rebuild_recent_menu()

    def _sync_project_state(project: Any, project_path: str | None = None) -> None:
        state["project"] = project
        project_service.set_project(project)
        project_editor.load_from_project(project)
        state["project_path"] = project_path
        txt_project.setText(project_path or "")
        section_manager.refresh_from_project()
        _refresh_status()

    def _ensure_loaded_project() -> bool:
        project_path = txt_project.text().strip()
        if not project_path:
            return True
        path_obj = Path(project_path)
        if not path_obj.exists():
            _append(f"File progetto non trovato: {project_path}")
            return False
        if state["project_path"] != str(path_obj):
            project = io_service.open_project(str(path_obj))
            _sync_project_state(project, str(path_obj))
            _record_recent(str(path_obj))
            _append(f"Progetto caricato: {path_obj}")
        return True

    def _pick_project() -> None:
        path, _ = QFileDialog.getOpenFileName(
            window,
            "Seleziona progetto",
            txt_project.text() or str(Path.cwd()),
            "Progetti JSON (*.json *.jsonp);;Tutti i file (*.*)",
        )
        if path:
            txt_project.setText(path)
            _ensure_loaded_project()

    def _pick_output() -> None:
        path = QFileDialog.getExistingDirectory(
            window,
            "Seleziona cartella output",
            txt_output.text() or str(Path.cwd()),
        )
        if path:
            txt_output.setText(path)
            user_cfg.last_output_dir = path
            user_cfg.save()

    def _new_project() -> None:
        state["results"] = None
        _sync_project_state(io_service.new_project(), None)
        _append("Nuovo progetto creato.")

    def _open_project() -> None:
        _pick_project()

    def _save_project() -> None:
        target_path = txt_project.text().strip()
        if not target_path:
            path, _ = QFileDialog.getSaveFileName(
                window,
                "Salva progetto",
                str(Path.cwd() / "progetto_rd2229.jsonp"),
                "Progetti JSON (*.json *.jsonp)",
            )
            if not path:
                return
            target_path = path
            txt_project.setText(target_path)
        io_service.save_project(project_service.current_project, target_path)
        state["project_path"] = target_path
        _record_recent(target_path)
        _append(f"Progetto salvato: {target_path}")

    def _run_pipeline() -> None:
        if not _ensure_loaded_project():
            return
        try:
            results = calc_service.run(project_service.current_project)
            state["results"] = results
            artifact = build_report(project_service.current_project, results)
            report_viewer.set_report(artifact)
            _refresh_status()
            _append(
                f"Pipeline eseguita: ok={results.ok} elementi={len(results.elements)} "
                f"warnings={len(results.warnings)}"
            )
        except Exception as exc:
            _append(f"Errore pipeline: {exc}")

    def _output_base_dir() -> Path:
        configured = txt_output.text().strip()
        if configured:
            return Path(configured)
        if state["project_path"]:
            return Path(state["project_path"]).parent
        return Path.cwd()

    def _export_results_json() -> None:
        if state["results"] is None:
            _append("Nessun risultato presente: eseguire prima la pipeline.")
            return
        base_dir = _output_base_dir()
        base_dir.mkdir(parents=True, exist_ok=True)
        target = base_dir / "results_ui_modern.json"
        calc_service.export_results(state["results"], str(target))
        _append(f"Risultati esportati: {target}")

    def _export_report(fmt: str) -> None:
        if state["results"] is None:
            _append("Nessun risultato presente: eseguire prima la pipeline.")
            return
        base_dir = _output_base_dir()
        base_dir.mkdir(parents=True, exist_ok=True)
        ext = "md" if fmt == "md" else "html"
        target = base_dir / f"report_ui_modern.{ext}"
        calc_service.export_report(
            project_service.current_project, state["results"], str(target), fmt=fmt
        )
        _append(f"Report esportato ({fmt}): {target}")

    def _run_full_workflow() -> None:
        project_path = txt_project.text().strip()
        if not project_path:
            _append("Preset workflow completo: selezionare prima un progetto JSON.")
            return
        output_dir = txt_output.text().strip() or None
        outcome = runner(project_path, output_dir)
        _append(
            "Preset workflow completo eseguito | "
            f"ok={outcome.get('ok')} | md={outcome.get('report_md')} | "
            f"html={outcome.get('report_html')}"
        )

    def _run_report_action(action: Callable[[], ActionReport]) -> None:
        try:
            report = action()
            _append_report(report)
        except Exception as exc:
            _append(f"Errore preset: {exc}")

    # Registry preset buttons
    clear_registry()
    register(
        FeatureSpec(
            feature_id="preset_full_project",
            label="Workflow progetto completo",
            category="pipeline",
            description="Carica progetto da file, esegue pipeline e genera report MD/HTML.",
            order=10,
            tooltip="Preset end-to-end su file reale.",
            action=_run_full_workflow,
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_normative_rd2229",
            label="Preset normativa RD2229",
            category="norme",
            description="Scenario rapido per verifiche TA RD2229.",
            order=20,
            action=lambda: _run_report_action(preset_service.run_normative_rd2229),
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_secondari_ntc2018",
            label="Preset secondari NTC2018",
            category="norme",
            description="Scenario SLU/SLE con output orientato elementi secondari.",
            order=30,
            action=lambda: _run_report_action(preset_service.run_secondari_ntc2018),
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_wind",
            label="Calcolo vento",
            category="moduli",
            description="WindActionService NTC2018 con profilo e zone di pressione.",
            order=40,
            action=lambda: _run_report_action(preset_service.run_wind_ntc2018),
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_fem",
            label="Calcolo FEM 2D",
            category="moduli",
            description="Assemblaggio, vincoli e soluzione di trave appoggiata.",
            order=50,
            action=lambda: _run_report_action(preset_service.run_fem_demo),
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_cross",
            label="Cross-Pozzati",
            category="moduli",
            description="Metodo iterativo storico per telaio no-sway.",
            order=60,
            action=lambda: _run_report_action(preset_service.run_cross_pozzati_demo),
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_solai",
            label="Input Solai X1",
            category="moduli",
            description="Parsing e normalizzazione input solaio.",
            order=70,
            action=lambda: _run_report_action(preset_service.run_solaio_input_demo),
        )
    )
    register(
        FeatureSpec(
            feature_id="preset_x8",
            label="Casi speciali X8",
            category="moduli",
            description="Valutazione preliminare predalles/collaborante/CLT.",
            order=80,
            action=lambda: _run_report_action(preset_service.run_x8_demo),
        )
    )

    cards_grid = QGridLayout()
    left_col.addLayout(cards_grid)

    def _card_widget(title: str, description: str, on_click: Callable[[], None]) -> Any:
        card = QWidget(dashboard)
        card_layout = QVBoxLayout(card)
        btn = QPushButton(title)
        btn.setMinimumHeight(44)
        btn.setToolTip(description)
        text = QLabel(description)
        text.setWordWrap(True)
        card_layout.addWidget(btn)
        card_layout.addWidget(text)
        btn.clicked.connect(lambda _checked=False: on_click())
        return card

    for idx, spec in enumerate(get_enabled()):
        if spec.action is None:
            continue
        card = _card_widget(spec.label, spec.description, spec.action)
        cards_grid.addWidget(card, idx // 2, idx % 2)

    launchers = QGridLayout()
    left_col.addWidget(QLabel("Accesso rapido moduli"))
    left_col.addLayout(launchers)

    def _open_project_sector() -> None:
        tabs.setCurrentWidget(project_data_tab)

    def _open_verify_sector() -> None:
        tabs.setCurrentWidget(verify_tab)

    def _open_report_sector() -> None:
        tabs.setCurrentWidget(report_tab)

    def _open_special_sector() -> None:
        tabs.setCurrentWidget(specialist_tab)

    def _open_materials() -> None:
        tabs.setCurrentWidget(project_data_tab)
        project_data_tabs.setCurrentWidget(materials_editor)

    def _open_sections() -> None:
        tabs.setCurrentWidget(project_data_tab)
        project_data_tabs.setCurrentWidget(section_manager)

    def _open_fem() -> None:
        tabs.setCurrentWidget(specialist_tab)
        specialist_tabs.setCurrentWidget(fem_tab)

    def _open_telaio() -> None:
        tabs.setCurrentWidget(specialist_tab)
        specialist_tabs.setCurrentWidget(fem_tab)
        _open_telaio_window()

    def _open_wind() -> None:
        tabs.setCurrentWidget(specialist_tab)
        specialist_tabs.setCurrentWidget(wind_tab)

    quick_actions: list[tuple[str, Callable[[], None]]] = [
        ("Materiali", _open_materials),
        ("Sezioni", _open_sections),
        ("FEM/Telai", _open_fem),
        ("Telaio", _open_telaio),
        ("Vento", _open_wind),
    ]
    for idx, (label, handler) in enumerate(quick_actions):
        button = QPushButton(label)
        button.clicked.connect(lambda _checked=False, action=handler: action())
        launchers.addWidget(button, idx // 2, idx % 2)

    def _on_pipeline_results(results: Any) -> None:
        state["results"] = results
        artifact = build_report(project_service.current_project, results)
        report_viewer.set_report(artifact)
        _append("Risultati pipeline aggiornati nel tab Report.")

    pipeline_runner.results_ready.connect(_on_pipeline_results)

    def _run_wind_tab() -> None:
        report = preset_service.run_wind_ntc2018()
        for line in _format_report(report):
            wind_log.append(line)

    wind_btn.clicked.connect(_run_wind_tab)

    # Menu bar + recent projects
    menu_file = window.menuBar().addMenu("File")
    menu_calc = window.menuBar().addMenu("Calcolo")
    menu_help = window.menuBar().addMenu("Aiuto")
    act_new = QAction("Nuovo", window)
    act_open = QAction("Apri", window)
    act_save = QAction("Salva", window)
    act_run = QAction("Esegui pipeline", window)
    act_norm = QAction("Impostazioni norma", window)
    act_help = QAction("Guida rapida GUI", window)
    recent_menu = menu_file.addMenu("Recenti")

    def _rebuild_recent_menu() -> None:
        recent_menu.clear()
        for path in user_cfg.recent_projects:
            action = QAction(path, window)
            action.triggered.connect(
                lambda checked=False, p=path: txt_project.setText(p) or _ensure_loaded_project()
            )
            recent_menu.addAction(action)
        # GUI-3.3: sincronizza anche la lista recenti nel dashboard
        recent_list.clear()
        for path in user_cfg.recent_projects:
            recent_list.addItem(path)

    def _autosave_tick() -> None:
        if not user_cfg.autosave_enabled:
            return
        if not state.get("project_path"):
            return
        try:
            io_service.save_project(project_service.current_project, str(state["project_path"]))
            _append(f"Auto-save completato: {state['project_path']}")
        except Exception as exc:  # pragma: no cover - defensive guard in GUI runtime
            _append(f"Auto-save fallito: {exc}")

    act_new.triggered.connect(_new_project)
    act_open.triggered.connect(_open_project)
    act_save.triggered.connect(_save_project)
    act_run.triggered.connect(_run_pipeline)
    act_norm.triggered.connect(
        lambda checked=False: tabs.setCurrentWidget(project_data_tab)
        or project_data_tabs.setCurrentWidget(code_settings_tab)
    )
    act_help.triggered.connect(
        lambda checked=False: _append(
            "Aiuto: usare Progetto -> Verifica -> Report; impostazioni norma nel tab Code Settings."
        )
    )
    menu_file.addAction(act_new)
    menu_file.addAction(act_open)
    menu_file.addAction(act_save)
    menu_calc.addAction(act_run)
    menu_calc.addAction(act_norm)
    menu_help.addAction(act_help)
    _rebuild_recent_menu()

    btn_go_project.clicked.connect(lambda _checked=False: _open_project_sector())
    btn_go_verify.clicked.connect(lambda _checked=False: _open_verify_sector())
    btn_go_report.clicked.connect(lambda _checked=False: _open_report_sector())
    btn_go_special.clicked.connect(lambda _checked=False: _open_special_sector())

    # GUI-3.3: doppio click su recent_list apre il progetto
    def _open_recent_item(item: Any) -> None:
        """Apre il progetto selezionato dalla lista recenti del dashboard."""
        path = item.text()
        txt_project.setText(path)
        _ensure_loaded_project()

    recent_list.itemDoubleClicked.connect(_open_recent_item)

    # Button bindings
    btn_project.clicked.connect(lambda _checked=False: _pick_project())
    btn_output.clicked.connect(lambda _checked=False: _pick_output())
    btn_new.clicked.connect(lambda _checked=False: _new_project())
    btn_open.clicked.connect(lambda _checked=False: _open_project())
    btn_save.clicked.connect(lambda _checked=False: _save_project())
    btn_run_pipeline.clicked.connect(lambda _checked=False: _run_pipeline())
    btn_export_json.clicked.connect(lambda _checked=False: _export_results_json())
    btn_export_md.clicked.connect(lambda _checked=False: _export_report("md"))
    btn_export_html.clicked.connect(lambda _checked=False: _export_report("html"))

    autosave_timer = QTimer(window)
    autosave_timer.timeout.connect(_autosave_tick)
    if user_cfg.autosave_enabled:
        autosave_timer.start(max(1, int(user_cfg.autosave_minutes)) * 60_000)
        _append(f"Auto-save attivo ogni {max(1, int(user_cfg.autosave_minutes))} min.")

    if default_project:
        txt_project.setText(default_project)
        _ensure_loaded_project()

    _append("GUI moderna inizializzata con macro-settori GUI-V2.")
    _append(
        "Tab attivi: Dashboard, Progetto e Dati, Verifiche e Pipeline, Report e Tracciabilita, "
        "Moduli Specialistici."
    )
    _refresh_status()

    return window
