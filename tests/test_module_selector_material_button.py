import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
import os
import sys
if os.name != "nt" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"  # Set display for headless environments on non-Windows

from sections_app.ui.module_selector import ModuleSelectorWindow
from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from core_models.materials import MaterialRepository


class TestModuleSelectorMaterialButton(unittest.TestCase):
    """Test suite for Material Editor button in ModuleSelectorWindow."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            # Try to create a root - if Tkinter is not available, skip tests
            test_root = tk.Tk()
            test_root.destroy()
        except tk.TclError:
            self.skipTest("Tkinter not available (headless environment)")
        
        self.repo = SectionRepository()
        self.serializer = CsvSectionSerializer()
        self.material_repo = MaterialRepository()

    def _create_window(self):
        try:
            return ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
        except tk.TclError:
            try:
                tk._default_root = None
            except Exception:
                pass
            return ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)

    def test_material_button_exists_in_module_selector(self):
        """Test that 'Open Materials' button exists in ModuleSelectorWindow."""
        with patch('tkinter.Tk.mainloop'):  # Prevent blocking
            window = self._create_window()
            try:
                # Find all buttons in the window
                def find_button(parent):
                    if isinstance(parent, tk.Button) and parent.cget('text') == "Open Materials":
                        return parent
                    for child in parent.winfo_children():
                        result = find_button(child)
                        if result:
                            return result
                    return None
                
                button = find_button(window)
                self.assertIsNotNone(button, "Button 'Open Materials' not found in ModuleSelectorWindow")
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_open_material_editor_method_exists(self):
        """Test that _open_material_editor method exists and is callable."""
        with patch('tkinter.Tk.mainloop'):  # Prevent blocking
            window = self._create_window()
            try:
                # Check that the method exists
                self.assertTrue(hasattr(window, '_open_material_editor'))
                self.assertTrue(callable(getattr(window, '_open_material_editor')))
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_material_editor_window_closes_on_X(self):
        """Ensure that clicking the X closes the historical material window and clears reference."""
        with patch('tkinter.Tk.mainloop'):
            window = self._create_window()
            try:
                # Open the material editor
                window._open_material_editor()
                self.assertIsNotNone(window._material_editor_window)
                # Simulate user clicking the X by destroying the Toplevel
                window._material_editor_window.destroy()
                # Process events to allow bound handlers to run
                window.update_idletasks()
                window.update()
                # Reference should have been cleared by on_material_editor_close
                self.assertIsNone(window._material_editor_window)
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_material_editor_window_reference_initialized(self):
        """Test that _material_editor_window reference is properly initialized."""
        with patch('tkinter.Tk.mainloop'):  # Prevent blocking
            window = self._create_window()
            try:
                # Check that the window reference exists and is initially None
                self.assertTrue(hasattr(window, '_material_editor_window'))
                self.assertIsNone(window._material_editor_window)
            finally:
                if window.winfo_exists():
                    window.destroy()


if __name__ == "__main__":
    unittest.main()

