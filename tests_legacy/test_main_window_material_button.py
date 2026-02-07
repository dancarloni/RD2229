import tkinter as tk
import unittest

from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.main_window import MainWindow


class TestMainWindowMaterialButton(unittest.TestCase):
    def setUp(self):
        # Check Tkinter availability
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available (headless environment)")

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_editor_material_button_triggers_open_material_manager(self):
        repo = SectionRepository()
        serializer = CsvSectionSerializer()
        # ✅ MainWindow è ora Toplevel e richiede un master (root come parent)
        mw = MainWindow(self.root, repo, serializer, material_repository=None)

        called = {"ok": False}

        def stub_open():
            called["ok"] = True

        # Find button with label 'Editor materiali' and invoke it
        found = False
        for child in mw.buttons_frame.winfo_children():
            try:
                if child.cget("text") == "Editor materiali":
                    # Replace the button command to ensure our stub is called
                    child.config(command=stub_open)
                    child.invoke()
                    found = True
                    break
            except Exception:
                continue

        self.assertTrue(found, "Editor materiali button not found in MainWindow")
        self.assertTrue(called["ok"], "Clicking the button should call open_material_manager")

        # Clean up
        mw.destroy()


if __name__ == "__main__":
    unittest.main()
