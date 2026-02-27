"""
ReportViewerWindow (PySide6 MVVM stub)
"""

from PySide6.QtWidgets import QSizePolicy, QTextBrowser, QVBoxLayout, QWidget


class ReportViewerWindow(QWidget):
    def __init__(self, report=None, parent=None):
        super().__init__(parent)
        self.report = report
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setHtml("<h3>Report Viewer (work in progress)</h3>")
        layout.addWidget(browser)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update()


MODULE_SPEC = {
    "key": "report_viewer",
    "name": "Report Viewer",
    "description": "Visualizza l’HTML/MD generato, pulsanti export (PySide6)",
}


def create_module(master=None, **context):
    return ReportViewerWindow(report=context.get("report"), parent=master)
