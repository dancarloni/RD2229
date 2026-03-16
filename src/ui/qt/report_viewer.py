"""Report viewer window with QWebEngine fallback (Qt6)."""

from __future__ import annotations

import tempfile
import webbrowser
from pathlib import Path
from typing import Any

try:
    from PyQt6.QtWidgets import (
        QFileDialog,
        QHBoxLayout,
        QPushButton,
        QSizePolicy,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import (
        QFileDialog,
        QHBoxLayout,
        QPushButton,
        QSizePolicy,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )


def _load_web_engine_view() -> type[Any] | None:
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView

        return QWebEngineView
    except Exception:
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView

            return QWebEngineView
        except Exception:
            return None


class ReportViewerWindow(QWidget):
    def __init__(self, report=None, parent=None):
        super().__init__(parent)
        self._artifact = report
        self._temp_html: Path | None = None

        self.setWindowTitle("RD2229 - Report Viewer")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.btn_open_browser = QPushButton("Apri nel browser")
        self.btn_save_html = QPushButton("Salva HTML")
        self.btn_save_md = QPushButton("Salva MD")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_open_browser.clicked.connect(self._open_in_browser)
        self.btn_save_html.clicked.connect(self._save_html)
        self.btn_save_md.clicked.connect(self._save_md)
        self.btn_refresh.clicked.connect(self._refresh_view)

        toolbar.addWidget(self.btn_open_browser)
        toolbar.addWidget(self.btn_save_html)
        toolbar.addWidget(self.btn_save_md)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch(1)
        root.addLayout(toolbar)

        web_cls = _load_web_engine_view()
        self._uses_web_engine = web_cls is not None
        if web_cls is not None:
            self.viewer = web_cls(self)
        else:
            self.viewer = QTextBrowser(self)
        root.addWidget(self.viewer)

        self._refresh_view()

    def set_report(self, artifact: Any) -> None:
        self._artifact = artifact
        self._refresh_view()

    def _html_text(self) -> str:
        if self._artifact is None:
            return "<h3>Nessun report caricato</h3><p>Eseguire prima la pipeline.</p>"
        html = getattr(self._artifact, "html", "")
        if html:
            return html
        markdown = getattr(self._artifact, "markdown", "")
        if markdown:
            escaped = markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return f"<html><body><pre>{escaped}</pre></body></html>"
        return "<h3>Report vuoto</h3>"

    def _refresh_view(self) -> None:
        html = self._html_text()
        if self._uses_web_engine:
            self.viewer.setHtml(html)
        else:
            self.viewer.setHtml(html)

    def _ensure_temp_html(self) -> Path:
        html = self._html_text()
        if self._temp_html is None:
            handle = tempfile.NamedTemporaryFile(
                prefix="rd2229_report_", suffix=".html", delete=False
            )
            handle.close()
            self._temp_html = Path(handle.name)
        self._temp_html.write_text(html, encoding="utf-8")
        return self._temp_html

    def _open_in_browser(self) -> None:
        target = self._ensure_temp_html()
        webbrowser.open(target.as_uri())

    def _save_html(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva report HTML",
            str(Path.cwd() / "report_rd2229.html"),
            "HTML (*.html)",
        )
        if not path:
            return
        Path(path).write_text(self._html_text(), encoding="utf-8")

    def _save_md(self) -> None:
        if self._artifact is None:
            return
        markdown = getattr(self._artifact, "markdown", "")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva report Markdown",
            str(Path.cwd() / "report_rd2229.md"),
            "Markdown (*.md)",
        )
        if not path:
            return
        Path(path).write_text(markdown, encoding="utf-8")


MODULE_SPEC = {
    "key": "report_viewer",
    "name": "Report Viewer",
    "description": "Visualizza l’HTML/MD generato, pulsanti export (Qt6)",
}


def create_module(master=None, **context):
    return ReportViewerWindow(report=context.get("report"), parent=master)
