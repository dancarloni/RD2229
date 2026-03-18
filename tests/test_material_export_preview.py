import pytest

from src.ui.qt.material_editor.controller import MaterialEditorController
from src.ui.qt.material_editor.logic.material_repository import MaterialRepository


class DummyFormatCombo:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text


class DummyExportText:
    def __init__(self):
        self.last_text = None

    def setPlainText(self, txt):
        self.last_text = txt

    def toPlainText(self):
        return self.last_text


class DummyExportWidget:
    def __init__(self, fmt='Markdown'):
        self.format_combo = DummyFormatCombo(fmt)
        self.export_text = DummyExportText()
        self.copy_button = None


def test_preview_new_material_no_selection():
    ctrl = MaterialEditorController(repository=MaterialRepository())
    ctrl.export_widget = DummyExportWidget(fmt='Markdown')
    ctrl.current_index = None
    # no model attached -> should use default headers
    ctrl._update_export_text()
    txt = ctrl.export_widget.export_text.last_text
    assert txt is not None
    assert '**codice**' in txt
    assert '**descrizione**' in txt
    assert '**f_ck**' in txt


def test_preview_with_selection_shows_values():
    repo = MaterialRepository()
    repo.materials = [{'codice': 'C20/25', 'descrizione': 'Calcestruzzo', 'f_ck': 25.0, 'gamma_c': 1.5}]
    ctrl = MaterialEditorController(repository=repo)
    ctrl.export_widget = DummyExportWidget(fmt='Markdown')
    ctrl.current_index = 0
    ctrl._update_export_text()
    txt = ctrl.export_widget.export_text.last_text
    assert '**codice**: C20/25' in txt
    assert '**f_ck**: 25.0' in txt
