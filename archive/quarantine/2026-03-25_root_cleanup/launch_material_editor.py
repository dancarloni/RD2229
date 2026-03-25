#!/usr/bin/env python
"""Launcher clean per Material Editor."""
import sys

from PySide6.QtWidgets import QApplication

from src.ui.qt.material_editor.material_editor_main import MaterialEditorMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MaterialEditorMainWindow()
    window.show()
    sys.exit(app.exec())
