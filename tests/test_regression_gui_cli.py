"""
Test di regressione per la nuova GUI Qt/PySide6 e CLI RD2229

- Garantisce la parità funzionale rispetto alla versione Tkinter
- Usa pytest-qt per la GUI, pytest standard per la CLI
"""

import pytest


# --- GUI (pytest-qt) ---
def test_module_selector_window(qtbot):
    """Apre ModuleSelectorWindow e verifica che i moduli reali siano presenti."""
    from src.ui.qt.module_selector import ModuleSelectorWindow

    win = ModuleSelectorWindow()
    qtbot.addWidget(win)
    win.show()
    assert win.sidebar.count() > 0
    win.close()


def test_project_editor_create_save_load(qtbot, tmp_path):
    """Crea un nuovo progetto, aggiunge un elemento, salva e ricarica."""
    from src.ui.qt.project_editor import ProjectEditorWindow

    win = ProjectEditorWindow()
    qtbot.addWidget(win)
    win.show()
    # Simula inserimento dati...
    win.project.name = "TestProject"
    win.save_project(str(tmp_path / "test_project.json"))
    win.load_project(str(tmp_path / "test_project.json"))
    assert win.project.name == "TestProject"
    win.close()


def test_pipeline_run_and_results(qtbot):
    """Esegue pipeline su progetto di esempio e verifica che la tabella risultati compaia."""
    from src.ui.qt.pipeline_runner import PipelineRunnerWindow

    win = PipelineRunnerWindow()
    qtbot.addWidget(win)
    win.show()
    win.load_example_project()
    win.run_pipeline()
    assert win.results_model is not None
    win.close()


def test_report_generation_and_view(qtbot):
    """Genera un report e controlla che il contenuto sia visualizzato."""
    from src.ui.qt.report_viewer import ReportViewerWindow

    win = ReportViewerWindow()
    qtbot.addWidget(win)
    win.show()
    win.load_example_report()
    assert win.text_edit.toPlainText() != ""
    win.close()


# --- CLI ---
def test_cli_pipeline(tmp_path):
    """Testa la CLI: rd2229 run <file> genera un report senza errori."""
    import shutil
    import subprocess

    example = shutil.copy("examples/project_example.json", tmp_path)
    result = subprocess.run(
        ["python", "-m", "src.cli.entrypoint", "run", str(example)], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "OK" in result.stdout or "Report" in result.stdout
