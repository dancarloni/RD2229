import os
import tkinter as tk
import unittest
from unittest.mock import patch

os.environ["DISPLAY"] = ":0"

from core_models.materials import MaterialRepository
from sections_app.ui.frc_verification_window import FrcVerificationWindow


class TestFrcVerificationWindow(unittest.TestCase):
    def setUp(self):
        try:
            t = tk.Tk()
            t.destroy()
        except tk.TclError:
            self.skipTest("Tkinter not available")
        self.material_repo = MaterialRepository()

    def test_run_without_material_shows_output(self):
        with patch("tkinter.Tk.mainloop"):
            win = FrcVerificationWindow(master=None, material_repository=self.material_repo)
            try:
                win.ent_b.delete(0, tk.END)
                win.ent_b.insert(0, "20")
                win.ent_h.delete(0, tk.END)
                win.ent_h.insert(0, "40")
                win.ent_As.delete(0, tk.END)
                win.ent_As.insert(0, "2")
                win.ent_d.delete(0, tk.END)
                win.ent_d.insert(0, "35")
                win.ent_M.delete(0, tk.END)
                win.ent_M.insert(0, "1000")
                win.ent_area.delete(0, tk.END)
                win.ent_area.insert(0, "0.0")
                win._run()
                content = win.output.get("1.0", tk.END)
                self.assertIn("Sigma concrete max", content)
            finally:
                if win.winfo_exists():
                    win.destroy()


if __name__ == "__main__":
    unittest.main()
