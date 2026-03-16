"""PySide6/PyQt6 stylesheet adapter for RD2229 GUI.

Provides a minimal base stylesheet and utilities for consistent
UI theming across all Qt windows. Import this instead of
hardcoding styles in individual widgets.

Usage::

    from src.ui.qt.stylesheet import apply_base_stylesheet, BASE_QSS

    app = QApplication(sys.argv)
    apply_base_stylesheet(app)

DiagnosticsService hook::

    from src.ui.qt.stylesheet import DiagnosticsPanel

    panel = DiagnosticsPanel(parent=my_widget)
    panel.refresh()  # queries DiagnosticsService for recent events
"""

from __future__ import annotations

BASE_QSS = """
/* RD2229 base stylesheet – PySide6/PyQt6 compatible */

QMainWindow, QDialog {
    background-color: #f5f5f5;
}

QMenuBar {
    background-color: #2c3e50;
    color: #ecf0f1;
}

QMenuBar::item:selected {
    background-color: #3498db;
}

QMenu {
    background-color: #2c3e50;
    color: #ecf0f1;
}

QMenu::item:selected {
    background-color: #3498db;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 3px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1a5276;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

QTableWidget, QTableView {
    gridline-color: #d5d8dc;
    alternate-background-color: #f0f3f4;
    selection-background-color: #3498db;
    selection-color: white;
}

QHeaderView::section {
    background-color: #2c3e50;
    color: #ecf0f1;
    padding: 4px;
    border: 1px solid #566573;
    font-weight: bold;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    padding: 4px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #3498db;
}

QLabel {
    color: #2c3e50;
}

QStatusBar {
    background-color: #2c3e50;
    color: #ecf0f1;
}

QGroupBox {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    margin-top: 8px;
    font-weight: bold;
    color: #2c3e50;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px;
}

QComboBox {
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    padding: 4px;
    background-color: white;
}

QTabWidget::pane {
    border: 1px solid #bdc3c7;
}

QTabBar::tab {
    background-color: #ecf0f1;
    padding: 6px 14px;
    border: 1px solid #bdc3c7;
}

QTabBar::tab:selected {
    background-color: #3498db;
    color: white;
}

QScrollBar:vertical {
    width: 12px;
    background: #ecf0f1;
}

QScrollBar::handle:vertical {
    background: #bdc3c7;
    min-height: 20px;
    border-radius: 6px;
}
"""


DARK_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #1f252a;
    color: #dfe6eb;
}

QMenuBar, QMenu, QStatusBar {
    background-color: #151a1f;
    color: #dfe6eb;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #2f7ea8;
}

QPushButton {
    background-color: #2f7ea8;
    color: #ffffff;
    border: 1px solid #38617a;
    border-radius: 4px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #3a94c5;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QTableWidget, QTableView {
    background-color: #2b3339;
    color: #dfe6eb;
    border: 1px solid #3b464e;
}

QHeaderView::section {
    background-color: #151a1f;
    color: #dfe6eb;
    border: 1px solid #3b464e;
    padding: 4px;
}

QTabWidget::pane {
    border: 1px solid #3b464e;
}

QTabBar::tab {
    background-color: #2b3339;
    color: #dfe6eb;
    padding: 6px 14px;
    border: 1px solid #3b464e;
}

QTabBar::tab:selected {
    background-color: #2f7ea8;
    color: #ffffff;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #2f7ea8;
    color: #ffffff;
}
"""


RESULT_STATUS_QSS = """
QTableWidget::item[status='ok'] { color: #1f8f4c; }
QTableWidget::item[status='warn'] { color: #d27d00; }
QTableWidget::item[status='ko'] { color: #b42b2b; }
"""


def apply_base_stylesheet(app: object) -> None:
    """Apply the RD2229 base stylesheet to a QApplication instance.

    Parameters
    ----------
    app:
        A ``QApplication`` instance (PyQt6 or PySide6).
    """
    if hasattr(app, "setStyleSheet"):
        app.setStyleSheet(BASE_QSS)


def apply_theme(app: object, theme: str = "light") -> None:
    """Apply named theme to QApplication (light or dark)."""
    if not hasattr(app, "setStyleSheet"):
        return
    selected = DARK_QSS if str(theme).lower() == "dark" else BASE_QSS
    app.setStyleSheet(selected + "\n" + RESULT_STATUS_QSS)


class DiagnosticsPanel:
    """Minimal Qt widget adapter for displaying DiagnosticsService events.

    This is a framework-agnostic helper.  Instantiate it inside a Qt widget
    and call ``refresh()`` to load recent events.

    Example (PyQt6/PySide6)::

        try:
            from PyQt6.QtWidgets import QTextEdit
        except ImportError:
            from PySide6.QtWidgets import QTextEdit

        class MyWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self._diag_panel = DiagnosticsPanel(widget=QTextEdit(self))

            def show_diagnostics(self):
                text = self._diag_panel.refresh(limit=50)
                self._diag_panel.widget.setPlainText(text)
    """

    def __init__(self, widget: object | None = None) -> None:
        self.widget = widget

    def refresh(
        self,
        session_id: str | None = None,
        source: str | None = None,
        limit: int = 100,
    ) -> str:
        """Query DiagnosticsService and return a formatted text summary.

        Parameters
        ----------
        session_id:
            Filter to a specific session.
        source:
            Filter by source component.
        limit:
            Maximum events to retrieve.

        Returns
        -------
        str
            Human-readable formatted events (suitable for QTextEdit).
        """
        try:
            from src.rd2229.diagnostics import get_diagnostics
        except ImportError:
            return "DiagnosticsService not available."

        diag = get_diagnostics()
        events = diag.query_events(session_id=session_id, source=source, limit=limit)

        if not events:
            return "No diagnostic events recorded."

        lines = [f"Diagnostic Events ({len(events)} total)\n" + "=" * 50]
        for ev in events:
            ts = ev.timestamp[:19].replace("T", " ")
            lines.append(f"[{ts}] {ev.source}/{ev.event_type}  sid={ev.session_id[:12]}")
            if ev.payload:
                import json

                lines.append(f"  → {json.dumps(ev.payload, ensure_ascii=False)[:120]}")
        return "\n".join(lines)
