import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch

from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from sections_app.ui.section_manager import SectionManager
from sections_app.ui.module_selector import ModuleSelectorWindow, MAX_EDIT_LOAD_RETRIES


class TestSectionManagerSelectionFallback(unittest.TestCase):
    def setUp(self):
        try:
            test_root = tk.Tk()
            test_root.destroy()
        except tk.TclError:
            self.skipTest("Tkinter not available (headless environment)")

        self.root = tk.Tk()
        self.root.withdraw()

        self.repository = MagicMock(spec=SectionRepository)
        # repository.get_all_sections deve restituire almeno [] per costruire colonne
        self.repository.get_all_sections.return_value = []
        self.serializer = MagicMock(spec=CsvSectionSerializer)
        self.on_edit = MagicMock()

    def tearDown(self):
        try:
            if hasattr(self, 'manager') and self.manager.winfo_exists():
                self.manager.destroy()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_edit_uses_selection_when_focus_empty(self):
        """Se la riga è selezionata ma focus() è vuoto, _edit_section() deve comunque caricare la sezione."""
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Inserisci una riga manualmente (iid = 'sec1')
        manager.tree.insert('', 'end', iid='sec1', values=['test'])
        # Assicura che selection sia impostata ma focus sia vuoto
        manager.tree.selection_set('sec1')
        manager.tree.focus('')  # rimuove il focus

        # Prepara repository.find_by_id
        mock_section = MagicMock()
        self.repository.find_by_id.return_value = mock_section

        # Chiama edit
        manager._edit_section()

        # Verifica che il callback on_edit sia stato chiamato con la sezione
        self.on_edit.assert_called_once_with(mock_section)


class TestModuleSelectorEditRetries(unittest.TestCase):
    def setUp(self):
        try:
            test_root = tk.Tk()
            test_root.destroy()
        except tk.TclError:
            self.skipTest("Tkinter not available (headless environment)")

        self.repo = MagicMock(spec=SectionRepository)
        self.serializer = MagicMock(spec=CsvSectionSerializer)
        self.material_repo = MagicMock()

    def tearDown(self):
        try:
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.destroy()
        except Exception:
            pass

    def test_on_section_edit_limits_retries(self):
        # Patch MainWindow to return an object WITHOUT load_section_into_form
        with patch('tkinter.Tk.mainloop'), patch('sections_app.ui.module_selector.MainWindow') as MockMain:
            MockMain.return_value = object()
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            self.window = window

            section = MagicMock()
            section.id = 'sec_x'

            # Override after to call immediately (synchronous) so recursion happens in test
            calls = []

            def immediate_after(delay, func):
                calls.append(1)
                func()

            window.after = immediate_after

            # Call _on_section_edit which should schedule retries up to the max
            window._on_section_edit(section)

            # The number of scheduled retries (immediate calls) should equal MAX_EDIT_LOAD_RETRIES
            self.assertEqual(len(calls), MAX_EDIT_LOAD_RETRIES)

            # The retry counter for the section should have been removed after reaching the cap
            counts = getattr(window, '_section_edit_retry_counts', {})
            self.assertNotIn(section.id, counts)


if __name__ == '__main__':
    unittest.main()
