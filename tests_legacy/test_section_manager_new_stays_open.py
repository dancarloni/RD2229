"""Test per verificare che Section Manager resti aperto dopo "Nuova sezione"."""

import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.section_manager import SectionManager


class TestSectionManagerNewStaysOpen(unittest.TestCase):
    """Test per verificare che _new_section NON chiuda il manager."""

    def setUp(self):
        """Setup per ogni test."""
        # Crea finestra root Tk
        self.root = tk.Tk()
        self.root.withdraw()

        # Mock repository e serializer
        self.repository = MagicMock(spec=SectionRepository)
        self.repository.get_all_sections.return_value = []

        self.serializer = MagicMock(spec=CsvSectionSerializer)

        # Mock callback
        self.on_edit = MagicMock()

    def tearDown(self):
        """Cleanup dopo ogni test."""
        try:
            if hasattr(self, "manager") and self.manager.winfo_exists():
                self.manager.destroy()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

    def test_new_section_non_chiude_manager(self):
        """Verifica che _new_section NON chiuda il Section Manager."""
        # Crea manager
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Verifica che il manager esista prima
        self.assertTrue(manager.winfo_exists())

        # Mock master con reset_form
        manager.master.reset_form = MagicMock()
        manager.master.lift = MagicMock()
        manager.master.focus_force = MagicMock()

        # Chiama _new_section
        manager._new_section()

        # Verifica che il manager ESISTA ANCORA (non è stato chiuso)
        self.assertTrue(manager.winfo_exists(), "Section Manager dovrebbe restare aperto dopo _new_section")

        # Verifica che reset_form sia stato chiamato
        manager.master.reset_form.assert_called_once()

    def test_new_section_apre_geometry_con_module_selector(self):
        """Verifica che _new_section apra Geometry quando master è ModuleSelector."""
        # Crea manager
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Mock master come ModuleSelector con _open_geometry
        mock_geometry_window = MagicMock()
        mock_geometry_window.reset_form = MagicMock()
        mock_geometry_window.lift = MagicMock()
        mock_geometry_window.focus_force = MagicMock()

        manager.master._open_geometry = MagicMock()
        manager.master._geometry_window = mock_geometry_window

        # Rimuovi reset_form dal master per forzare il path di _open_geometry
        if hasattr(manager.master, "reset_form"):
            delattr(manager.master, "reset_form")

        # Chiama _new_section
        manager._new_section()

        # Verifica che _open_geometry sia stato chiamato
        manager.master._open_geometry.assert_called_once()

        # Verifica che reset_form di Geometry sia stato chiamato
        mock_geometry_window.reset_form.assert_called_once()

        # Verifica che il manager ESISTA ANCORA
        self.assertTrue(manager.winfo_exists(), "Section Manager dovrebbe restare aperto")

    def test_new_section_con_master_senza_metodi(self):
        """Verifica comportamento quando master non ha né reset_form né _open_geometry."""
        # Crea manager con master base
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Assicurati che master non abbia né reset_form né _open_geometry
        if hasattr(manager.master, "reset_form"):
            delattr(manager.master, "reset_form")
        if hasattr(manager.master, "_open_geometry"):
            delattr(manager.master, "_open_geometry")

        # Mock ask_confirm per simulare risposta "No"
        def _fake_ask_confirm(title, message, callback=None, **kwargs):
            if callback:
                callback(False)
            return lambda ans: None

        with patch("sections_app.services.notification.ask_confirm", side_effect=_fake_ask_confirm):
            # Chiama _new_section
            manager._new_section()

            # Verifica che il manager ESISTA ANCORA
            self.assertTrue(manager.winfo_exists(), "Manager dovrebbe restare aperto anche senza azioni")

    def test_new_section_multiple_chiamate_non_chiudono_manager(self):
        """Verifica che chiamate multiple a _new_section mantengano il manager aperto."""
        # Crea manager
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Mock master
        manager.master.reset_form = MagicMock()
        manager.master.lift = MagicMock()
        manager.master.focus_force = MagicMock()

        # Chiama _new_section più volte
        manager._new_section()
        self.assertTrue(manager.winfo_exists())

        manager._new_section()
        self.assertTrue(manager.winfo_exists())

        manager._new_section()
        self.assertTrue(manager.winfo_exists())

        # Verifica che reset_form sia stato chiamato 3 volte
        self.assertEqual(manager.master.reset_form.call_count, 3)


if __name__ == "__main__":
    unittest.main()
