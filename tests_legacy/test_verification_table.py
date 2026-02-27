import tkinter as tk
import unittest

from sections_app.models.sections import RectangularSection
from sections_app.services.repository import SectionRepository

try:
    from core_models.materials import Material, MaterialRepository
except Exception:  # pylint: disable=broad-exception-caught
    MaterialRepository = None
    Material = None

from verification_table import VerificationTableWindow


class TestVerificationTableWindow(unittest.TestCase):
    def setUp(self) -> None:
        # Create a root Tk and hide it (skip test if Tk not available)
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in this environment")

    def tearDown(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_window_receives_repositories_and_debug_info(self):
        section_repo = SectionRepository()
        # Ensure repository is empty to avoid conflicts with preloaded demo data
        section_repo.clear()
        # create a simple section and add to repository
        rect = RectangularSection(name="TestRect", width=20, height=30)
        rect.compute_properties()
        added = section_repo.add_section(rect)
        self.assertTrue(added)

        if MaterialRepository is not None and Material is not None:
            mat_repo = MaterialRepository()
            mat_repo.add(Material(name="C100", type="concrete"))
        else:
            mat_repo = None

        win = VerificationTableWindow(self.root, section_repository=section_repo, material_repository=mat_repo)

        # repositories stored on window
        self.assertIs(win.section_repository, section_repo)
        self.assertIs(win.material_repository, mat_repo)

        # debug info
        info = win.app.debug_check_sources()
        self.assertIn("sections_count", info)
        self.assertGreaterEqual(info["sections_count"], 1)
        self.assertIn("sections_sample", info)
        if mat_repo is not None:
            self.assertIn("materials_count", info)
            self.assertGreaterEqual(info["materials_count"], 1)

        # cleanup
        win.destroy()


if __name__ == "__main__":
    unittest.main()
