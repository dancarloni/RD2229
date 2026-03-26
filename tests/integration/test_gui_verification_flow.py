"""Test di integrazione: verifica che i dialog e widget principali non crashino su PyQt6."""

import os
import pytest


def test_geometry_dialog_instantiation(qapp):
    """Verifica che GeometryDialog si istanzi senza AttributeError."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from src.ui.qt.project_editor_dialogs import GeometryDialog

    dlg = GeometryDialog()
    assert dlg is not None
    assert dlg.txt_id is not None


def test_material_dialog_instantiation(qapp):
    """Verifica che MaterialDialog si istanzi senza AttributeError."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from src.ui.qt.project_editor_dialogs import MaterialDialog

    dlg = MaterialDialog()
    assert dlg is not None
    assert dlg.txt_id is not None


def test_key_value_dialog_instantiation(qapp):
    """Verifica che KeyValueDialog si istanzi senza AttributeError."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from src.ui.qt.key_value_dialog import KeyValueDialog

    dlg = KeyValueDialog()
    assert dlg is not None
    assert dlg._table is not None


def test_material_table_widget_instantiation(qapp):
    """Verifica che MaterialTableWidget si istanzi senza AttributeError."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget

    w = MaterialTableWidget()
    assert w is not None


def test_material_editor_main_window(qapp):
    """Verifica che MaterialEditorMainWindow si istanzi senza AttributeError."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from src.ui.qt.material_editor.material_editor_main import MaterialEditorMainWindow

    w = MaterialEditorMainWindow()
    assert w is not None
    assert w.tab_widget is not None
