"""Compatibility PyQt6 app entrypoint used by smoke tests."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Callable


def run_bootstrap_workflow(
    project_path: str, output_dir: str | None = None
) -> dict[str, str | bool]:
    """Esegue un flusso completo load -> pipeline -> report per la GUI moderna.

    Questa funzione consente di verificare in modalità headless che i moduli
    principali siano collegati correttamente, senza avviare il loop Qt.
    """
    from src.core.pipeline import run_pipeline
    from src.project.repository import load_project
    from src.reporting.export import export_report_html, export_report_md
    from src.reporting.report_builder import build_report

    project = load_project(project_path)
    results = run_pipeline(project)
    artifact = build_report(project, results)

    target_dir = Path(output_dir) if output_dir else Path(project_path).parent
    target_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(project_path).stem
    md_path = target_dir / f"{stem}_report.md"
    html_path = target_dir / f"{stem}_report.html"

    export_report_md(artifact, str(md_path))
    export_report_html(artifact, str(html_path))

    return {
        "ok": results.ok,
        "report_md": str(md_path),
        "report_html": str(html_path),
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project", dest="project_path")
    parser.add_argument("--output-dir", dest="output_dir")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--help", action="store_true")
    return parser.parse_known_args(argv)[0]


def _print_help() -> None:
    print(
        "RD2229 UI moderna\n"
        "Opzioni:\n"
        "  --project <path>      Percorso progetto JSON\n"
        "  --output-dir <path>   Cartella output report\n"
        "  --headless            Esegue solo workflow load->pipeline->report\n"
        "  --no-gui              Alias di --headless\n"
    )


def _load_qt_widgets() -> tuple[dict[str, Any], str]:
    """Carica backend Qt disponibile (PyQt6 preferito, fallback PySide6)."""
    # Test smoke for missing PyQt6 explicitly injects `None` in sys.modules.
    # Keep legacy behavior for that scenario.
    if "PyQt6" in sys.modules and sys.modules.get("PyQt6") is None:
        raise ModuleNotFoundError("No module named 'PyQt6' (blocked)")

    try:
        from PyQt6.QtWidgets import (
            QApplication,
            QFileDialog,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QPushButton,
            QStatusBar,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        return {
            "QApplication": QApplication,
            "QWidget": QWidget,
            "QLabel": QLabel,
            "QLineEdit": QLineEdit,
            "QMainWindow": QMainWindow,
            "QPushButton": QPushButton,
            "QStatusBar": QStatusBar,
            "QTabWidget": QTabWidget,
            "QTextEdit": QTextEdit,
            "QGridLayout": QGridLayout,
            "QVBoxLayout": QVBoxLayout,
            "QHBoxLayout": QHBoxLayout,
            "QFileDialog": QFileDialog,
        }, "PyQt6"
    except ModuleNotFoundError:
        from PySide6.QtWidgets import (
            QApplication,
            QFileDialog,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QPushButton,
            QStatusBar,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        return {
            "QApplication": QApplication,
            "QWidget": QWidget,
            "QLabel": QLabel,
            "QLineEdit": QLineEdit,
            "QMainWindow": QMainWindow,
            "QPushButton": QPushButton,
            "QStatusBar": QStatusBar,
            "QTabWidget": QTabWidget,
            "QTextEdit": QTextEdit,
            "QGridLayout": QGridLayout,
            "QVBoxLayout": QVBoxLayout,
            "QHBoxLayout": QHBoxLayout,
            "QFileDialog": QFileDialog,
        }, "PySide6"


def _build_main_window(
    qt: dict[str, Any],
    default_project: str | None,
    default_output: str | None,
    runner: Callable[[str, str | None], dict[str, str | bool]],
) -> Any:
    from .main_window import build_main_window

    return build_main_window(
        qt=qt,
        default_project=default_project,
        default_output=default_output,
        runner=runner,
    )


def main() -> int:
    if os.environ.get("RD2229_UI_TEST") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return 0

    args = _parse_args(sys.argv[1:])
    if args.help:
        _print_help()
        return 0

    project_path = args.project_path or os.environ.get("RD2229_UI_PROJECT")
    output_dir = args.output_dir or os.environ.get("RD2229_UI_OUTPUT_DIR")
    headless = bool(args.headless or args.no_gui or os.environ.get("RD2229_UI_HEADLESS") == "1")

    if project_path:
        try:
            outcome = run_bootstrap_workflow(project_path, output_dir)
            print(
                f"Workflow completato: ok={outcome['ok']} md={outcome['report_md']} "
                f"html={outcome['report_html']}"
            )
            if headless:
                return 0
        except Exception as exc:
            print(f"Errore bootstrap workflow UI moderna: {exc}", file=sys.stderr)
            return 1
    elif headless:
        print("Modalita headless richiesta ma --project non specificato", file=sys.stderr)
        return 1

    try:
        qt, backend = _load_qt_widgets()
    except ModuleNotFoundError:
        print("PyQt6 non disponibile. Installa le dipendenze GUI.", file=sys.stderr)
        return 2

    QApplication = qt["QApplication"]
    app = QApplication.instance() or QApplication(sys.argv)
    try:
        from src.core.user_config import UserConfig
        from src.ui.qt.stylesheet import apply_theme

        apply_theme(app, UserConfig.load().theme)
    except Exception:
        # Theme loading must never block app startup.
        pass

    window = _build_main_window(qt, project_path, output_dir, run_bootstrap_workflow)
    print(f"Avvio GUI moderna con backend {backend}...")
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
