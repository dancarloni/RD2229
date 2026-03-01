# filepath: tests/test_module_selector_controller.py
from unittest.mock import MagicMock, Mock, patch

import pytest

from sections_app.ui.module_selector import ModuleSelectorController


@pytest.fixture
def controller():
    with (
        patch("sections_app.ui.module_selector.MaterialRepository") as mock_mat,
        patch("sections_app.ui.module_selector.GeometryRepository") as mock_sec,
        patch("sections_app.ui.module_selector.HistoricalMaterialLibrary") as mock_hist,
        patch("sections_app.ui.module_selector.NotificationCenter") as mock_notif,
    ):
        mock_mat.return_value = Mock()
        mock_sec.return_value = Mock()
        mock_hist.return_value = Mock()
        mock_notif.return_value = Mock()
        return ModuleSelectorController()


def test_get_available_modules(controller):
    modules = controller.get_available_modules()
    # modules is a list of ModuleSpec objects
    keys = {m.key for m in modules}
    assert "geometry" in keys
    geom = next(m for m in modules if m.key == "geometry")
    assert geom.name == "Geometry Module"


def test_select_module_valid(controller):
    with patch("sections_app.ui.module_selector.MainWindow") as mock_window:
        # ensure registry returns a factory that calls MainWindow
        controller.registry._factories["geometry"] = lambda master=None, **kw: mock_window()
        with patch("threading.Thread") as mock_thread:
            controller.select_module("geometry")
            mock_thread.assert_called_once()


def test_select_module_invalid(controller):
    # Patch both the public shim and the legacy module notify function to be
    # robust against the shim/legacy split introduced during migration.
    with patch("sections_app.ui.module_selector.notify_error") as mock_notify:
        with patch("src.legacy.sections_app.ui.module_selector.notify_error") as mock_notify_legacy:
            controller.select_module("invalid")
            # At least one of the targets should have been invoked with expected args
            expected_kwargs = dict(
                title="Errore",
                message="Modulo 'invalid' non trovato o non disponibile.",
                source="module_selector",
            )
            assert mock_notify.called or mock_notify_legacy.called
            if mock_notify.called:
                mock_notify.assert_called_once_with(**expected_kwargs)
            if mock_notify_legacy.called:
                mock_notify_legacy.assert_called_once_with(**expected_kwargs)


def test_load_sections(controller, monkeypatch):
    # patch CSV import to return two dummy sections
    dummy_sec = MagicMock()
    # patch both shim and legacy paths to make sure we intercept import
    monkeypatch.setattr(
        "sections_app.ui.module_selector.CsvSectionSerializer.import_from_csv",
        lambda self, fp, **kw: [dummy_sec, dummy_sec],
    )
    monkeypatch.setattr(
        "src.legacy.sections_app.ui.module_selector.CsvSectionSerializer.import_from_csv",
        lambda self, fp, **kw: [dummy_sec, dummy_sec],
    )
    # ensure GeometryRepository used inside load_sections is a mock so add_section calls are observable
    mock_repo = MagicMock()
    mock_repo.add_section = MagicMock(return_value=True)
    monkeypatch.setattr(
        "sections_app.ui.module_selector.GeometryRepository", lambda *a, **kw: mock_repo
    )
    monkeypatch.setattr(
        "src.legacy.sections_app.ui.module_selector.GeometryRepository", lambda *a, **kw: mock_repo
    )

    controller.load_sections("test.csv")
    # repository should be created and add_section called twice
    assert hasattr(controller, "section_repo")
    assert controller.section_repo is mock_repo
    assert controller.section_repo.add_section.call_count == 2
