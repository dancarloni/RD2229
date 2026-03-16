"""Tests for modern UI app headless and backend behavior."""

from __future__ import annotations

import importlib.util
import sys

from src.ui.modern import app as modern_app


def test_parse_args_headless_flags() -> None:
    args = modern_app._parse_args(["--project", "p.json", "--output-dir", "out", "--headless"])
    assert args.project_path == "p.json"
    assert args.output_dir == "out"
    assert args.headless is True


def test_main_headless_executes_workflow(monkeypatch) -> None:
    calls: list[tuple[str, str | None]] = []

    def _fake_runner(project_path: str, output_dir: str | None = None) -> dict[str, str | bool]:
        calls.append((project_path, output_dir))
        return {"ok": True, "report_md": "r.md", "report_html": "r.html"}

    monkeypatch.delenv("RD2229_UI_TEST", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(modern_app, "run_bootstrap_workflow", _fake_runner)
    monkeypatch.setattr(sys, "argv", ["rd2229-ui", "--project", "p.json", "--headless"])

    result = modern_app.main()

    assert result == 0
    assert calls == [("p.json", None)]


def test_main_headless_requires_project(monkeypatch) -> None:
    monkeypatch.delenv("RD2229_UI_TEST", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(sys, "argv", ["rd2229-ui", "--headless"])

    result = modern_app.main()

    assert result == 1


def test_qt_backend_fallback_behavior() -> None:
    pyqt6_available = importlib.util.find_spec("PyQt6") is not None
    pyside6_available = importlib.util.find_spec("PySide6") is not None

    if not pyqt6_available and not pyside6_available:
        return

    qt, backend = modern_app._load_qt_widgets()

    assert "QApplication" in qt
    if not pyqt6_available and pyside6_available:
        assert backend == "PySide6"
