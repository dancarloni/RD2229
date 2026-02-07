#!/usr/bin/env python3
"""Test: Verifica che il sistema di recovery automatico funzioni correttamente
quando i file JSON sono danneggiati o mancanti.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from core_models.materials import MaterialRepository
from sections_app.models.sections import RectangularSection
from sections_app.services.repository import SectionRepository


class TestRecoverySystem(unittest.TestCase):
    """Test del sistema di recovery automatico."""

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

    def test_section_loads_from_main_file_normally(self):
        """Test: Caricamento normale dal file principale."""
        # Crea file principale valido
        data = [
            {"name": "Rect1", "section_type": "rectangular", "width": 20, "height": 30},
            {"name": "Rect2", "section_type": "rectangular", "width": 25, "height": 40},
        ]
        with open(self.sections_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # Carica repository
        repo = SectionRepository(json_file=self.sections_file)

        # Verifica che le sezioni siano state caricate
        sections = repo.get_all_sections()
        self.assertEqual(len(sections), 2)
        names = {s.name for s in sections}
        self.assertIn("Rect1", names)
        self.assertIn("Rect2", names)

    def test_section_recovers_from_backup_when_main_corrupted(self):
        """Test: Recovery dal backup quando il file principale è corrotto."""
        # Crea backup valido
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        backup_data = [
            {"name": "BackupRect", "section_type": "rectangular", "width": 30, "height": 50},
        ]
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(backup_data, f)

        # Crea file principale CORROTTO (JSON invalido)
        with open(self.sections_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json here }")

        # Carica repository
        repo = SectionRepository(json_file=self.sections_file)

        # Verifica che sia stato caricato dal backup
        sections = repo.get_all_sections()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].name, "BackupRect")

    def test_section_starts_empty_when_both_files_corrupted(self):
        """Test: Archivio vuoto quando sia principale che backup sono corrotti."""
        # Crea file principale corrotto
        with open(self.sections_file, "w", encoding="utf-8") as f:
            f.write("{ corrupted }")

        # Crea backup corrotto
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        with backup_path.open("w", encoding="utf-8") as f:
            f.write("[ invalid ]")

        # Carica repository
        repo = SectionRepository(json_file=self.sections_file)

        # Verifica che l'archivio sia vuoto
        sections = repo.get_all_sections()
        self.assertEqual(len(sections), 0)

    def test_section_starts_empty_when_no_files_exist(self):
        """Test: Archivio vuoto quando nessun file esiste."""
        # Non creare nessun file

        # Carica repository
        repo = SectionRepository(json_file=self.sections_file)

        # Verifica che l'archivio sia vuoto
        sections = repo.get_all_sections()
        self.assertEqual(len(sections), 0)

    def test_material_loads_from_main_file_normally(self):
        """Test: Caricamento normale materiali dal file principale."""
        # Crea file principale valido
        data = [
            {"name": "C25/30", "type": "concrete", "properties": {"fck": 25}},
            {"name": "A500", "type": "steel", "properties": {"fyk": 500}},
        ]
        with open(self.materials_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # Carica repository
        repo = MaterialRepository(json_file=self.materials_file)

        # Verifica che i materiali siano stati caricati
        materials = repo.get_all()
        self.assertEqual(len(materials), 2)
        names = {m.name for m in materials}
        self.assertIn("C25/30", names)
        self.assertIn("A500", names)

    def test_material_recovers_from_backup_when_main_corrupted(self):
        """Test: Recovery materiali dal backup quando il file principale è corrotto."""
        # Crea backup valido
        backup_path = Path(self.materials_file).with_name("materials_backup.json")
        backup_data = [
            {"name": "BackupMat", "type": "concrete", "properties": {"fck": 35}},
        ]
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(backup_data, f)

        # Crea file principale CORROTTO
        with open(self.materials_file, "w", encoding="utf-8") as f:
            f.write("not valid json")

        # Carica repository
        repo = MaterialRepository(json_file=self.materials_file)

        # Verifica che sia stato caricato dal backup
        materials = repo.get_all()
        self.assertEqual(len(materials), 1)
        self.assertEqual(materials[0].name, "BackupMat")

    def test_material_starts_empty_when_both_files_corrupted(self):
        """Test: Archivio materiali vuoto quando entrambi i file sono corrotti."""
        # Crea file principale corrotto
        with open(self.materials_file, "w", encoding="utf-8") as f:
            f.write("{ bad json }")

        # Crea backup corrotto
        backup_path = Path(self.materials_file).with_name("materials_backup.json")
        with backup_path.open("w", encoding="utf-8") as f:
            f.write("not json at all")

        # Carica repository
        repo = MaterialRepository(json_file=self.materials_file)

        # Verifica che l'archivio sia vuoto
        materials = repo.get_all()
        self.assertEqual(len(materials), 0)

    def test_section_recovers_when_main_is_not_a_list(self):
        """Test: Recovery quando il file principale contiene JSON valido ma non è una lista."""
        # Crea backup valido
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        backup_data = [
            {"name": "BackupRect", "section_type": "rectangular", "width": 20, "height": 30},
        ]
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(backup_data, f)

        # Crea file principale con oggetto invece di lista
        with open(self.sections_file, "w", encoding="utf-8") as f:
            json.dump({"key": "value"}, f)  # JSON valido ma non lista

        # Carica repository
        repo = SectionRepository(json_file=self.sections_file)

        # Verifica che sia stato caricato dal backup
        sections = repo.get_all_sections()
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].name, "BackupRect")

    def test_section_recovery_preserves_data_integrity(self):
        """Test: Il recovery dal backup preserva l'integrità dei dati."""
        # Crea backup con dati completi
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        section_id = "test-id-12345"
        backup_data = [
            {
                "id": section_id,
                "name": "DetailedRect",
                "section_type": "rectangular",
                "width": 35,
                "height": 55,
            }
        ]
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(backup_data, f)

        # Corrompi file principale
        with open(self.sections_file, "w", encoding="utf-8") as f:
            f.write("corrupted")

        # Carica repository
        repo = SectionRepository(json_file=self.sections_file)

        # Verifica che i dati siano integri
        sections = repo.get_all_sections()
        self.assertEqual(len(sections), 1)
        section = sections[0]
        self.assertEqual(section.id, section_id)
        self.assertEqual(section.name, "DetailedRect")
        # Verifica che le proprietà geometriche siano state preservate
        self.assertIsNotNone(section.width)
        self.assertGreater(section.width, 0)

    def test_section_can_save_after_recovery(self):
        """Test: È possibile salvare nuove sezioni dopo un recovery."""
        # Crea backup valido
        backup_path = Path(self.sections_file).with_name("sections_backup.json")
        backup_data = [
            {"name": "Original", "section_type": "rectangular", "width": 20, "height": 30},
        ]
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(backup_data, f)

        # Corrompi file principale
        with open(self.sections_file, "w", encoding="utf-8") as f:
            f.write("bad json")

        # Carica repository (recovery dal backup)
        repo = SectionRepository(json_file=self.sections_file)

        # Aggiungi nuova sezione
        new_section = RectangularSection(name="New", width=25, height=40)
        result = repo.add_section(new_section)

        # Verifica che il salvataggio sia riuscito
        self.assertTrue(result)

        # Verifica che il file principale sia stato ripristinato
        self.assertTrue(Path(self.sections_file).exists())

        # Ricarica e verifica
        repo2 = SectionRepository(json_file=self.sections_file)
        sections = repo2.get_all_sections()
        self.assertEqual(len(sections), 2)
        names = {s.name for s in sections}
        self.assertIn("Original", names)
        self.assertIn("New", names)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST: Sistema Recovery Automatico da Backup")
    print("=" * 70)

    # Run tests
    unittest.main(verbosity=2)
