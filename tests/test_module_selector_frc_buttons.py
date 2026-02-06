import unittest
import tkinter as tk
from unittest.mock import patch
import os
import sys
if os.name != "nt" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"

from sections_app.ui.module_selector import ModuleSelectorWindow
from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from core_models.materials import MaterialRepository


class TestModuleSelectorFrcButtons(unittest.TestCase):
    def setUp(self):
        try:
            test_root = tk.Tk()
            test_root.destroy()
        except tk.TclError:
            self.skipTest("Tkinter not available (headless environment)")
        self.repo = SectionRepository()
        self.serializer = CsvSectionSerializer()
        self.material_repo = MaterialRepository()

    def test_frc_manager_button_exists(self):
        with patch('tkinter.Tk.mainloop'):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                def find_button(parent):
                    if isinstance(parent, tk.Button) and parent.cget('text') == "Open FRC Manager":
                        return parent
                    for child in parent.winfo_children():
                        result = find_button(child)
                        if result:
                            return result
                    return None
                btn = find_button(window)
                self.assertIsNotNone(btn, "Button 'Open FRC Manager' not found")
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_frc_verification_button_exists(self):
        with patch('tkinter.Tk.mainloop'):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                def find_button(parent):
                    if isinstance(parent, tk.Button) and parent.cget('text') == "Open FRC Verification":
                        return parent
                    for child in parent.winfo_children():
                        result = find_button(child)
                        if result:
                            return result
                    return None
                btn = find_button(window)
                self.assertIsNotNone(btn, "Button 'Open FRC Verification' not found")
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_open_frc_manager_method(self):
        with patch('tkinter.Tk.mainloop'):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                self.assertTrue(callable(getattr(window, '_open_frc_manager', None)))
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_open_frc_verification_method(self):
        with patch('tkinter.Tk.mainloop'):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                self.assertTrue(callable(getattr(window, '_open_frc_verification', None)))
            finally:
                if window.winfo_exists():
                    window.destroy()


if __name__ == '__main__':
    unittest.main()
