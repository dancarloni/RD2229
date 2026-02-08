# filepath: tests/test_module_selector_controller.py
import pytest
from unittest.mock import MagicMock, patch, Mock
from sections_app.ui.module_selector import ModuleSelectorController

@pytest.fixture
def controller():
    with patch('sections_app.ui.module_selector.MaterialRepository') as mock_mat, \
         patch('sections_app.ui.module_selector.SectionRepository') as mock_sec, \
         patch('sections_app.ui.module_selector.HistoricalMaterialLibrary') as mock_hist, \
         patch('sections_app.ui.module_selector.NotificationCenter') as mock_notif:
        mock_mat.return_value = Mock()
        mock_sec.return_value = Mock()
        mock_hist.return_value = Mock()
        mock_notif.return_value = Mock()
        return ModuleSelectorController()

def test_get_available_modules(controller):
    modules = controller.get_available_modules()
    assert "geometry" in modules
    assert modules["geometry"]["name"] == "Geometry Module"

def test_select_module_valid(controller):
    with patch('sections_app.ui.module_selector.MainWindow') as mock_window:
        controller.select_module("geometry")
        mock_window.assert_called_once()

def test_select_module_invalid(controller):
    with patch('sections_app.ui.module_selector.notify_error') as mock_notify:
        controller.select_module("invalid")
        mock_notify.assert_called_once_with(title="Errore", message="Modulo 'invalid' non trovato nella configurazione.", source="module_selector")

def test_load_sections(controller):
    controller.load_sections("test.csv")
    controller.section_repo.load_from_csv.assert_called_once_with("test.csv")