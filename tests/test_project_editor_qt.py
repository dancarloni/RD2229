"""Test Qt per ProjectEditorWindow: CRUD, extra, import repo, roundtrip."""

import pytest

pytest.importorskip("pytestqt")
from pytestqt.qt_compat import qt_api

from src.ui.qt.key_value_dialog import KeyValueDialog
from src.ui.qt.project_editor import ProjectEditorWindow
from src.ui.qt.project_editor_dialogs import GeometryDialog, LoadDialog, MaterialDialog


@pytest.fixture
def editor(qtbot):
    w = ProjectEditorWindow()
    qtbot.addWidget(w)
    return w


def test_add_remove_row_geometry(editor, qtbot, monkeypatch):
    tbl = editor.tbl_geometry
    n0 = tbl.rowCount()

    # Patch dialog to return a consistent entry
    monkeypatch.setattr(
        GeometryDialog,
        "edit",
        staticmethod(
            lambda parent, initial=None: {
                "id": "G1",
                "type": "RECT",
                "width": 10,
                "height": 20,
                "extra": {"foo": 1},
            }
        ),
    )

    editor._add_table_row(tbl)
    assert tbl.rowCount() == n0 + 1
    assert tbl.item(tbl.rowCount() - 1, 0).text() == "G1"

    # Seleziona la riga appena aggiunta e rimuovila
    tbl.setCurrentCell(tbl.rowCount() - 1, 0)
    editor._remove_table_row(tbl)
    assert tbl.rowCount() == n0


def test_edit_extra_json(editor, qtbot, monkeypatch):
    tbl = editor.tbl_geometry
    # Add a row and set extra
    monkeypatch.setattr(
        GeometryDialog,
        "edit",
        staticmethod(
            lambda parent, initial=None: {
                "id": "G1",
                "type": "RECT",
                "width": 10,
                "height": 20,
                "extra": {},
            }
        ),
    )
    editor._add_table_row(tbl)
    row = tbl.rowCount() - 1
    col = tbl.columnCount() - 1
    tbl.setItem(row, col, qt_api.QtWidgets.QTableWidgetItem('{"foo": 1}'))
    tbl.setCurrentCell(row, 0)

    # Stub key/value dialog to change extra
    monkeypatch.setattr(
        KeyValueDialog,
        "edit",
        staticmethod(lambda parent, current: {"foo": 2}),
    )

    editor._edit_extra_for_selected(tbl)
    assert tbl.item(row, col).text() == '{"foo": 2}'


def test_import_material_from_repo_stub(editor, qtbot):
    # For now, just ensure method exists and does not crash
    editor._import_material_from_repo()


def test_roundtrip_extra(editor, qtbot):
    # Simula roundtrip ProjectModel con extra JSON
    from src.project.schema import GeometryEntry, LoadEntry, MaterialEntry, ProjectModel

    model = ProjectModel(
        geometry=[GeometryEntry(id="G1", type="RECT", width=10, height=20, extra={"foo": 1})],
        materials=[
            MaterialEntry(id="M1", type="concrete", material_class="C25", f_ck=25, extra={"bar": 2})
        ],
        loads=[
            LoadEntry(
                element_id="G1", N=1, Mx=2, My=3, Tx=4, Ty=5, description="desc", extra={"baz": 3}
            )
        ],
    )
    editor.load_from_project(model)
    # Check extra loaded as JSON string
    g_extra = editor.tbl_geometry.item(0, 4).text()
    m_extra = editor.tbl_materials.item(0, 5).text()
    l_extra = editor.tbl_loads.item(0, 7).text()
    assert g_extra.startswith("{")
    assert m_extra.startswith("{")
    assert l_extra.startswith("{")
    # Now collect and check dict
    out = editor._collect_project()
    assert out.geometry[0].extra == {"foo": 1}
    assert out.materials[0].extra == {"bar": 2}
    assert out.loads[0].extra == {"baz": 3}


def test_add_remove_row_materials(editor, qtbot, monkeypatch):
    tbl = editor.tbl_materials
    n0 = tbl.rowCount()

    monkeypatch.setattr(
        MaterialDialog,
        "edit",
        staticmethod(
            lambda parent, initial=None: {
                "id": "M1",
                "type": "concrete",
                "material_class": "C25",
                "f_ck": 25,
                "f_yk": 30,
                "extra": {"bar": 2},
            }
        ),
    )

    editor._add_table_row(tbl)
    assert tbl.rowCount() == n0 + 1
    tbl.setCurrentCell(tbl.rowCount() - 1, 0)
    editor._remove_table_row(tbl)
    assert tbl.rowCount() == n0


def test_add_remove_row_loads(editor, qtbot, monkeypatch):
    tbl = editor.tbl_loads
    n0 = tbl.rowCount()

    monkeypatch.setattr(
        LoadDialog,
        "edit",
        staticmethod(
            lambda parent, initial=None: {
                "element_id": "G1",
                "N": 1,
                "Mx": 2,
                "My": 3,
                "Tx": 4,
                "Ty": 5,
                "description": "desc",
                "extra": {"baz": 3},
            }
        ),
    )

    editor._add_table_row(tbl)
    assert tbl.rowCount() == n0 + 1
    tbl.setCurrentCell(tbl.rowCount() - 1, 0)
    editor._remove_table_row(tbl)
    assert tbl.rowCount() == n0


def test_edit_extra_materials_with_mock(editor, qtbot, monkeypatch):
    tbl = editor.tbl_materials
    editor._add_table_row(tbl)
    row = tbl.rowCount() - 1
    col = tbl.columnCount() - 1
    tbl.setItem(row, col, qt_api.QtWidgets.QTableWidgetItem('{"foo": 1}'))
    tbl.setCurrentCell(row, 0)

    # Stub key/value dialog to change extra
    monkeypatch.setattr(
        KeyValueDialog,
        "edit",
        staticmethod(lambda parent, current: {"foo": 2}),
    )

    editor._edit_extra_for_selected(tbl)
    assert tbl.item(row, col).text() == '{"foo": 2}'


def test_edit_extra_loads_with_mock(editor, qtbot, monkeypatch):
    tbl = editor.tbl_loads
    editor._add_table_row(tbl)
    row = tbl.rowCount() - 1
    col = tbl.columnCount() - 1
    tbl.setItem(row, col, qt_api.QtWidgets.QTableWidgetItem('{"a": 1}'))
    tbl.setCurrentCell(row, 0)

    monkeypatch.setattr(
        KeyValueDialog,
        "edit",
        staticmethod(lambda parent, current: {"a": 9}),
    )

    editor._edit_extra_for_selected(tbl)
    assert tbl.item(row, col).text() == '{"a": 9}'


def test_import_material_from_repo_with_repo(qtbot, monkeypatch):
    from importlib import import_module

    from src.materials.material_repo import MaterialRepository

    repo = MaterialRepository()
    repo.carica_defaults()
    editor = ProjectEditorWindow(material_repo=repo)
    qtbot.addWidget(editor)
    # Monkeypatch dialog to auto-select first material
    mod = import_module("src.ui.qt.material_import_dialog")
    original = mod.MaterialImportDialog.select_material
    try:
        mod.MaterialImportDialog.select_material = staticmethod(lambda parent, r: r.list_all()[0])
        n0 = editor.tbl_materials.rowCount()
        editor._import_material_from_repo()
        assert editor.tbl_materials.rowCount() == n0 + 1
    finally:
        mod.MaterialImportDialog.select_material = original


def test_edit_selected_row_with_dialog(editor, monkeypatch):
    tbl = editor.tbl_geometry
    # Patch dialog to return modified values
    monkeypatch.setattr(
        GeometryDialog,
        "edit",
        staticmethod(
            lambda parent, initial=None: {
                "id": "G100",
                "type": "CIRCLE",
                "width": 30,
                "height": 30,
                "extra": {"x": 1},
            }
        ),
    )

    editor._add_table_row(tbl)
    row = tbl.rowCount() - 1
    tbl.setCurrentCell(row, 0)

    editor._edit_table_row(tbl)
    assert tbl.item(row, 0).text() == "G100"
    assert tbl.item(row, 1).text() == "CIRCLE"
