#!/usr/bin/env python3
"""Test: Verificare che VerificationTable si aggiorna automaticamente
quando cambiano sezioni e materiali.
"""

import os
import tempfile
import tkinter as tk
import unittest

from core_models.materials import Material, MaterialRepository
from sections_app.models.sections import RectangularSection
from sections_app.services.event_bus import EventBus
from sections_app.services.repository import SectionRepository
from verification_table import VerificationTableWindow


class TestVerificationTableAutoUpdate(unittest.TestCase):
    def setUp(self):
        """Setup test fixtures."""
        # Clear EventBus
        EventBus().clear()

        # Create temp directories for repositories
        self.temp_dir = tempfile.mkdtemp()
        self.sections_file = os.path.join(self.temp_dir, "sections.json")
        self.materials_file = os.path.join(self.temp_dir, "materials.json")

        # Create repositories
        self.section_repo = SectionRepository(json_file=self.sections_file)
        self.material_repo = MaterialRepository(json_file=self.materials_file)

        # Add initial data
        rect1 = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
        self.section_repo.add_section(rect1)

        mat1 = Material(name="C25/30", type="concrete", properties={"fck": 25})
        self.material_repo.add(mat1)

        # Create root window for testing
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window during tests
        except tk.TclError:
            # Headless environment without Tcl/Tk: skip these GUI tests
            self.skipTest("Tcl/Tk not available in this environment; skipping GUI tests")

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

        # Clean up temp files
        import shutil

        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

        # Clear EventBus
        EventBus().clear()

    def test_verification_table_loads_initial_data(self):
        """Test: VerificationTable carica dati iniziali."""
        window = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        # Verify initial data
        self.assertEqual(len(window.app.section_names), 1)
        self.assertEqual(len(window.app.material_names), 1)
        self.assertIn("Rettangolare 20x30", window.app.section_names)
        self.assertIn("C25/30", window.app.material_names)

        window.destroy()

    def test_verification_table_updates_on_section_add(self):
        """Test: VerificationTable si aggiorna quando si aggiunge una sezione."""
        window = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        # Initial count
        initial_count = len(window.app.section_names)
        self.assertEqual(initial_count, 1)

        # Add new section
        rect2 = RectangularSection(name="Rettangolare 25x40", width=25, height=40)
        self.section_repo.add_section(rect2)

        # Force update (in real scenario, event triggers automatically)
        self.root.update()

        # Verify update
        self.assertEqual(len(window.app.section_names), 2)
        self.assertIn("Rettangolare 25x40", window.app.section_names)

        window.destroy()

    def test_verification_table_updates_on_material_add(self):
        """Test: VerificationTable si aggiorna quando si aggiunge un materiale."""
        window = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        # Initial count
        initial_count = len(window.app.material_names)
        self.assertEqual(initial_count, 1)

        # Add new material
        mat2 = Material(name="C30/37", type="concrete", properties={"fck": 30})
        self.material_repo.add(mat2)

        # Force update
        self.root.update()

        # Verify update
        self.assertEqual(len(window.app.material_names), 2)
        self.assertIn("C30/37", window.app.material_names)

        window.destroy()

    def test_verification_table_updates_on_section_update(self):
        """Test: VerificationTable si aggiorna quando si modifica una sezione."""
        window = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        # Get existing section
        sections = self.section_repo.get_all_sections()
        section_id = sections[0].id

        # Update section
        rect_updated = RectangularSection(name="Rettangolare MODIFICATA 20x30", width=20, height=30)
        self.section_repo.update_section(section_id, rect_updated)

        # Force update
        self.root.update()

        # Verify update
        self.assertIn("Rettangolare MODIFICATA 20x30", window.app.section_names)
        self.assertNotIn("Rettangolare 20x30", window.app.section_names)

        window.destroy()

    def test_verification_table_updates_on_section_delete(self):
        """Test: VerificationTable si aggiorna quando si elimina una sezione."""
        # Add second section first
        rect2 = RectangularSection(name="Rettangolare 25x40", width=25, height=40)
        self.section_repo.add_section(rect2)

        window = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        # Initial count
        self.assertEqual(len(window.app.section_names), 2)

        # Delete section
        sections = self.section_repo.get_all_sections()
        section_to_delete = [s for s in sections if s.name == "Rettangolare 20x30"][0]
        self.section_repo.delete_section(section_to_delete.id)

        # Force update
        self.root.update()

        # Verify update
        self.assertEqual(len(window.app.section_names), 1)
        self.assertNotIn("Rettangolare 20x30", window.app.section_names)
        self.assertIn("Rettangolare 25x40", window.app.section_names)

        window.destroy()

    def test_multiple_windows_all_update(self):
        """Test: Multiple VerificationTableWindows si aggiornano tutte."""
        window1 = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        window2 = VerificationTableWindow(
            self.root,
            section_repository=self.section_repo,
            material_repository=self.material_repo,
        )

        # Initial counts
        self.assertEqual(len(window1.app.section_names), 1)
        self.assertEqual(len(window2.app.section_names), 1)

        # Add new section
        rect2 = RectangularSection(name="Rettangolare 30x50", width=30, height=50)
        self.section_repo.add_section(rect2)

        # Force update
        self.root.update()

        # Verify both windows updated
        self.assertEqual(len(window1.app.section_names), 2)
        self.assertEqual(len(window2.app.section_names), 2)
        self.assertIn("Rettangolare 30x50", window1.app.section_names)
        self.assertIn("Rettangolare 30x50", window2.app.section_names)

        window1.destroy()
        window2.destroy()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST: Auto-Aggiornamento VerificationTable")
    print("=" * 70)

    # Run tests
    unittest.main(verbosity=2)
