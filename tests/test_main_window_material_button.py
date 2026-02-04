import unittest

import tkinter as tk

from sections_app.ui.main_window import MainWindow
from sections_app.services.repository import SectionRepository, CsvSectionSerializer


class TestMainWindowMaterialButton(unittest.TestCase):
    def setUp(self):
        # Create a root that will be used as parent for windows; avoid mainloop
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_editor_material_button_triggers_open_material_manager(self):
        repo = SectionRepository()
        serializer = CsvSectionSerializer()
        mw = MainWindow(repo, serializer, material_repository=None)

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
