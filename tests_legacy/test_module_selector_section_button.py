import os
import tkinter as tk
import unittest
from unittest.mock import patch

os.environ["DISPLAY"] = ":0"  # Set display for headless environments

from core_models.materials import MaterialRepository
from sections_app.models.sections import RectangularSection
from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.module_selector import ModuleSelectorWindow


class TestModuleSelectorSectionButton(unittest.TestCase):
    """Test suite for Sections Archive button in ModuleSelectorWindow."""

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

    def test_section_button_exists_in_module_selector(self):
        """Test that 'Open Sections' button exists in ModuleSelectorWindow."""
        with patch("tkinter.Tk.mainloop"):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                # Find all buttons in the window
                def find_button(parent):
                    if isinstance(parent, tk.Button) and parent.cget("text") == "Open Sections":
                        return parent
                    for child in parent.winfo_children():
                        result = find_button(child)
                        if result:
                            return result
                    return None

                button = find_button(window)
                self.assertIsNotNone(button, "Button 'Open Sections' not found in ModuleSelectorWindow")
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_open_section_manager_method_exists(self):
        """Test that _open_section_manager method exists and is callable."""
        with patch("tkinter.Tk.mainloop"):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                # Check that the method exists
                self.assertTrue(hasattr(window, "_open_section_manager"))
                self.assertTrue(callable(getattr(window, "_open_section_manager")))
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_section_manager_window_closes_on_X(self):
        """Ensure that clicking the X closes the SectionManager window and clears reference."""
        with patch("tkinter.Tk.mainloop"):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                # Open the section manager
                window._open_section_manager()
                self.assertIsNotNone(window._section_manager_window)
                # Simulate user clicking the X by destroying the Toplevel
                window._section_manager_window.destroy()
                # Process events to allow bound handlers to run
                window.update_idletasks()
                window.update()
                # Reference should have been cleared
                self.assertIsNone(window._section_manager_window)
            finally:
                if window.winfo_exists():
                    window.destroy()

    def test_on_section_edit_opens_geometry_and_loads_section(self):
        """Check that invoking the edit callback opens Geometry and loads the section."""
        # Mock MainWindow to avoid flaky GUI creation in headless tests
        from unittest.mock import MagicMock

        with (
            patch("tkinter.Tk.mainloop"),
            patch("sections_app.ui.module_selector.MainWindow") as MockMain,
        ):
            window = ModuleSelectorWindow(self.repo, self.serializer, self.material_repo)
            try:
                # Create a sample section and invoke the callback
                section = RectangularSection(name="25x50", width=25.0, height=50.0)

                # Configure the fake MainWindow instance
                fake = MagicMock()

                def _load(section_arg):
                    fake.name_entry = MagicMock(get=MagicMock(return_value=section_arg.name))

                fake.load_section_into_form.side_effect = _load
                fake.winfo_exists.return_value = True
                fake.lift.return_value = None
                fake.focus_force.return_value = None
                MockMain.return_value = fake

                window._on_section_edit(section)
                # Process events to allow any scheduled calls to run
                window.update_idletasks()
                window.update()

                # Geometry window should now exist (mocked) and the form should contain the section name
                self.assertIsNotNone(window._geometry_window)
                self.assertEqual(window._geometry_window.name_entry.get(), "25x50")
            finally:
                # Close geometry if opened
                try:
                    if getattr(window, "_geometry_window", None) is not None and window._geometry_window.winfo_exists():
                        window._geometry_window.destroy()
                except Exception:
                    pass
                if window.winfo_exists():
                    window.destroy()


if __name__ == "__main__":
    unittest.main()
