#!/usr/bin/env python3
"""Test: Verifica che il sistema di backup automatico funzioni correttamente
per SectionRepository e MaterialRepository.
"""

import os
import tempfile
import unittest
from pathlib import Path

from core_models.materials import Material, MaterialRepository
from sections_app.models.sections import RectangularSection
from sections_app.services.repository import SectionRepository


class TestBackupSystem(unittest.TestCase):
    """Test del sistema di backup automatico."""

    def setUp(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sections_file = os.path.join(self.temp_dir, "sections.json")
        self.materials_file = os.path.join(self.temp_dir, "materials.json")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def test_section_backup_created_on_save(self):
        """Test: Backup sezioni viene creato quando si salva."""
        repo = SectionRepository(json_file=self.sections_file)

        # Aggiungi prima sezione
        rect1 = RectangularSection(name="Rect 20x30", width=20, height=30)
        repo.add_section(rect1)

        # Verifica che il file principale esista
        self.assertTrue(Path(self.sections_file).exists())

        # Il backup non esiste ancora (primo salvataggio)
        backup_path = Path(self.sections_file).with_name("sections_backup.json")

        # Aggiungi seconda sezione (questo dovrebbe creare il backup)
        rect2 = RectangularSection(name="Rect 25x40", width=25, height=40)
        repo.add_section(rect2)

        # Ora il backup dovrebbe esistere
        self.assertTrue(backup_path.exists(), "Backup file dovrebbe esistere dopo il secondo salvataggio")

        # Verifica che il backup contenga i dati della prima versione
        import json

        with backup_path.open("r", encoding="utf-8") as f:
            backup_data = json.load(f)

        # Il backup dovrebbe avere 1 sezione (stato precedente)
        self.assertEqual(len(backup_data), 1)
        self.assertEqual(backup_data[0]["name"], "Rect 20x30")

    def test_material_backup_created_on_save(self):
        """Test: Backup materiali viene creato quando si salva."""
        repo = MaterialRepository(json_file=self.materials_file)

        # Aggiungi primo materiale
        mat1 = Material(name="C25/30", type="concrete", properties={"fck": 25})
        repo.add(mat1)

        # Verifica che il file principale esista
        self.assertTrue(Path(self.materials_file).exists())

        backup_path = Path(self.materials_file).with_name("materials_backup.json")

        # Aggiungi secondo materiale (questo dovrebbe creare il backup)
        mat2 = Material(name="C30/37", type="concrete", properties={"fck": 30})
        repo.add(mat2)

        # Ora il backup dovrebbe esistere
        self.assertTrue(backup_path.exists(), "Backup file dovrebbe esistere dopo il secondo salvataggio")

        # Verifica che il backup contenga i dati della prima versione
        import json

        with backup_path.open("r", encoding="utf-8") as f:
            backup_data = json.load(f)

        # Il backup dovrebbe avere 1 materiale (stato precedente)
        self.assertEqual(len(backup_data), 1)
        self.assertEqual(backup_data[0]["name"], "C25/30")

    def test_section_safe_write_with_temp_file(self):
        """Test: Scrittura sicura tramite file temporaneo per sezioni."""
        repo = SectionRepository(json_file=self.sections_file)

        # Aggiungi sezione
        rect = RectangularSection(name="Rect 30x50", width=30, height=50)
        repo.add_section(rect)

        # Verifica che il file temporaneo non esista dopo il salvataggio
        tmp_path = Path(self.sections_file).with_suffix(".json.tmp")
        self.assertFalse(tmp_path.exists(), "File temporaneo non dovrebbe esistere dopo salvataggio riuscito")

        # Verifica che il file principale esista
        self.assertTrue(Path(self.sections_file).exists())

    def test_material_safe_write_with_temp_file(self):
        """Test: Scrittura sicura tramite file temporaneo per materiali."""
        repo = MaterialRepository(json_file=self.materials_file)

        # Aggiungi materiale
        mat = Material(name="A500", type="steel", properties={"fyk": 500})
        repo.add(mat)

        # Verifica che il file temporaneo non esista dopo il salvataggio
        tmp_path = Path(self.materials_file).with_suffix(".json.tmp")
        self.assertFalse(tmp_path.exists(), "File temporaneo non dovrebbe esistere dopo salvataggio riuscito")

        # Verifica che il file principale esista
        self.assertTrue(Path(self.materials_file).exists())

    def test_section_backup_preserves_old_data(self):
        """Test: Il backup preserva i dati precedenti anche dopo multiple modifiche."""
        repo = SectionRepository(json_file=self.sections_file)

        # Aggiungi sezioni
        rect1 = RectangularSection(name="V1", width=20, height=30)
        repo.add_section(rect1)

        rect2 = RectangularSection(name="V2", width=25, height=40)
        repo.add_section(rect2)

        rect3 = RectangularSection(name="V3", width=30, height=50)
        repo.add_section(rect3)

        # Verifica che il file principale abbia 3 sezioni
        import json

        with Path(self.sections_file).open("r", encoding="utf-8") as f:
            main_data = json.load(f)
        self.assertEqual(len(main_data), 3)

        # Verifica che il backup abbia 2 sezioni (stato prima dell'ultima aggiunta)
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        with backup_path.open("r", encoding="utf-8") as f:
            backup_data = json.load(f)
        self.assertEqual(len(backup_data), 2)

    def test_section_backup_on_update(self):
        """Test: Backup viene creato anche quando si aggiorna una sezione."""
        repo = SectionRepository(json_file=self.sections_file)

        # Aggiungi sezione
        rect = RectangularSection(name="Original", width=20, height=30)
        repo.add_section(rect)

        sections = repo.get_all_sections()
        section_id = sections[0].id

        # Modifica la sezione
        updated = RectangularSection(name="Updated", width=25, height=40)
        repo.update_section(section_id, updated)

        # Verifica che il backup esista
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        self.assertTrue(backup_path.exists())

        # Verifica che il backup contenga il nome originale
        import json

        with backup_path.open("r", encoding="utf-8") as f:
            backup_data = json.load(f)
        self.assertEqual(backup_data[0]["name"], "Original")

        # Verifica che il file principale abbia il nome aggiornato
        with Path(self.sections_file).open("r", encoding="utf-8") as f:
            main_data = json.load(f)
        self.assertEqual(main_data[0]["name"], "Updated")

    def test_section_backup_on_delete(self):
        """Test: Backup viene creato anche quando si elimina una sezione."""
        repo = SectionRepository(json_file=self.sections_file)

        # Aggiungi sezioni
        rect1 = RectangularSection(name="Rect1", width=20, height=30)
        rect2 = RectangularSection(name="Rect2", width=25, height=40)
        repo.add_section(rect1)
        repo.add_section(rect2)

        # Elimina una sezione
        sections = repo.get_all_sections()
        repo.delete_section(sections[0].id)

        # Verifica che il backup contenga 2 sezioni
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        import json

        with backup_path.open("r", encoding="utf-8") as f:
            backup_data = json.load(f)
        self.assertEqual(len(backup_data), 2)

        # Verifica che il file principale abbia 1 sezione
        with Path(self.sections_file).open("r", encoding="utf-8") as f:
            main_data = json.load(f)
        self.assertEqual(len(main_data), 1)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST: Sistema Backup Automatico")
    print("=" * 70)

    # Run tests
    unittest.main(verbosity=2)
