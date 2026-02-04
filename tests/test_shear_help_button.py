import unittest
import tkinter as tk
from unittest.mock import patch

from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from sections_app.ui.main_window import MainWindow


class TestShearHelpButton(unittest.TestCase):
    def setUp(self):
        # Setup Tk and skip if headless
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

    def test_help_button_opens_info_dialog(self):
        repo = SectionRepository()
        serializer = CsvSectionSerializer()
        mw = MainWindow(self.root, repo, serializer, material_repository=None)

        # Find the help button (text='?') in the left panel
        help_btn = None
        for child in mw.left_frame.winfo_children():
            # shear_frame is a child; search its children
            try:
                for sub in child.winfo_children():
                    if getattr(sub, 'cget', None) and sub.cget('text') == '?':
                        help_btn = sub
                        break
                if help_btn:
                    break
            except Exception:
                continue

        self.assertIsNotNone(help_btn, "Help button '?' not found in MainWindow")

        # Patch messagebox.showinfo and invoke the button
        with patch('sections_app.ui.main_window.messagebox.showinfo') as mock_info:
            help_btn.invoke()
            mock_info.assert_called_once()
            # the first arg is the title used in showinfo
            title_arg = mock_info.call_args[0][0]
            self.assertIn('Fattori di forma', title_arg)

        mw.destroy()


if __name__ == '__main__':
    unittest.main()
