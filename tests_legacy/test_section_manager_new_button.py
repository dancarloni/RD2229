import os
import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

os.environ["DISPLAY"] = ":0"

from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.main_window import MainWindow
from sections_app.ui.module_selector import ModuleSelectorWindow


class TestSectionManagerNewButton(unittest.TestCase):
    def setUp(self):
        try:
            tk.Tk().destroy()
        except tk.TclError:
            self.skipTest("Tkinter not available")
        self.repo = SectionRepository()
        self.serializer = CsvSectionSerializer()

    def test_new_section_calls_reset_on_mainwindow_master(self):
        with patch("tkinter.Tk.mainloop"):
            main = MainWindow(None, self.repo, self.serializer)
            # Patch reset_form to observe calls
            main.reset_form = MagicMock()
            # Open manager from MainWindow
            main.open_manager()
            manager = main.section_manager
            try:
                manager._new_section()
                # Allow events
                main.update_idletasks()
                main.update()
                main.reset_form.assert_called()
                # ✅ Manager should stay open (nuovo comportamento)
                self.assertTrue(getattr(manager, "winfo_exists", lambda: False)())
            finally:
                try:
                    if (
                        getattr(main, "section_manager", None) is not None
                        and main.section_manager.winfo_exists()
                    ):
                        main.section_manager.destroy()
                except Exception:
                    pass
                if main.winfo_exists():
                    main.destroy()

    def test_new_section_opens_geometry_when_master_is_module_selector(self):
        with patch("tkinter.Tk.mainloop"):
            selector = ModuleSelectorWindow(self.repo, self.serializer)
            # Open the section manager from selector
            selector._open_section_manager()
            manager = selector._section_manager_window
            try:
                # Patch selector._open_geometry to set a fake _geometry_window
                fake_gw = MagicMock()
                fake_gw.reset_form = MagicMock()

                def fake_open_geometry():
                    selector._geometry_window = fake_gw

                selector._open_geometry = fake_open_geometry

                manager._new_section()
                # Allow events
                selector.update_idletasks()
                selector.update()
                fake_gw.reset_form.assert_called()
                # ✅ Manager should stay open (nuovo comportamento)
                self.assertTrue(getattr(manager, "winfo_exists", lambda: False)())
            finally:
                try:
                    if (
                        getattr(selector, "_section_manager_window", None) is not None
                        and selector._section_manager_window.winfo_exists()
                    ):
                        selector._section_manager_window.destroy()
                except Exception:
                    pass
                if selector.winfo_exists():
                    selector.destroy()


if __name__ == "__main__":
    unittest.main()
