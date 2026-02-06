"""
Test per la funzione export_backup di SectionRepository.

Verifica:
1. Esportazione in formato JSON
2. Esportazione in formato CSV
3. Estensione di default (.json) quando mancante
4. Gestione errori (percorsi non validi)
5. Non modifica del file principale e backup interno
"""

import json
import csv
import tempfile
import unittest
from pathlib import Path

from sections_app.services.repository import SectionRepository
from sections_app.models.sections import RectangularSection, CircularSection


class TestExportBackup(unittest.TestCase):
    """Test per export_backup()."""

    def setUp(self):
        """Setup con repository temporaneo."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.sections_file = self.temp_path / "sections.json"
        self.repo = SectionRepository(json_file=str(self.sections_file))
        
        # Aggiungi alcune sezioni di test
        rect = RectangularSection(
            name="Rettangolo Test",
            width=300,
            height=500
        )
        circ = CircularSection(
            name="Circolare Test",
            diameter=400
        )
        self.repo.add_section(rect)
        self.repo.add_section(circ)
    
    def tearDown(self):
        """Cleanup."""
        self.temp_dir.cleanup()

    def test_export_to_json(self):
        """Test: Esportazione in formato JSON."""
        export_path = self.temp_path / "export_test.json"
        
        # Esporta
        self.repo.export_backup(export_path)
        
        # Verifica che il file esista
        self.assertTrue(export_path.exists())
        
        # Verifica contenuto JSON
        with export_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("section_type", data[0])
        
        # Verifica che i dati siano corretti
        names = {item["name"] for item in data}
        self.assertIn("Rettangolo Test", names)
        self.assertIn("Circolare Test", names)

    def test_export_to_csv(self):
        """Test: Esportazione in formato CSV."""
        export_path = self.temp_path / "export_test.csv"
        
        # Esporta
        self.repo.export_backup(export_path)
        
        # Verifica che il file esista
        self.assertTrue(export_path.exists())
        
        # Verifica contenuto CSV
        with export_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)
        
        self.assertEqual(len(rows), 2)
        self.assertIn("id", rows[0])
        self.assertIn("name", rows[0])
        self.assertIn("section_type", rows[0])
        
        # Verifica dati
        names = {row["name"] for row in rows}
        self.assertIn("Rettangolo Test", names)
        self.assertIn("Circolare Test", names)

    def test_export_with_path_object(self):
        """Test: Export con oggetto Path invece di stringa."""
        export_path = self.temp_path / "export_with_path.json"
        
        # Passa Path object
        self.repo.export_backup(export_path)
        
        self.assertTrue(export_path.exists())

    def test_export_without_extension_defaults_to_json(self):
        """Test: Senza estensione, usa .json di default."""
        export_path = self.temp_path / "export_no_extension"
        
        # Esporta senza estensione
        self.repo.export_backup(export_path)
        
        # Verifica che sia stato creato con .jsons
        expected_path = self.temp_path / "export_no_extension.jsons"
        self.assertTrue(expected_path.exists())
        
        # Verifica che sia JSON valido
        with expected_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)

    def test_export_with_invalid_extension_defaults_to_json(self):
        """Test: Estensione non valida (.txt), usa .json di default."""
        export_path = self.temp_path / "export_invalid.txt"
        
        # Esporta con estensione non supportata
        self.repo.export_backup(export_path)
        
        # Verifica che sia stato creato con .jsons
        expected_path = self.temp_path / "export_invalid.jsons"
        self.assertTrue(expected_path.exists())

    def test_export_creates_directory_if_needed(self):
        """Test: Crea directory di destinazione se non esiste."""
        nested_path = self.temp_path / "subdir" / "nested" / "export.json"
        
        # Esporta in directory non esistente
        self.repo.export_backup(nested_path)
        
        # Verifica che directory e file siano stati creati
        self.assertTrue(nested_path.parent.exists())
        self.assertTrue(nested_path.exists())

    def test_export_does_not_modify_main_file(self):
        """Test: Export non modifica il file principale."""
        # Ottieni contenuto originale
        with self.sections_file.open("r", encoding="utf-8") as f:
            original_content = f.read()
        
        # Esporta
        export_path = self.temp_path / "export_separate.json"
        self.repo.export_backup(export_path)
        
        # Verifica che il file principale non sia cambiato
        with self.sections_file.open("r", encoding="utf-8") as f:
            current_content = f.read()
        
        self.assertEqual(original_content, current_content)

    def test_export_does_not_modify_backup_file(self):
        """Test: Export non modifica il file di backup interno."""
        # Forza creazione backup interno
        self.repo.save_to_file()
        backup_internal = self.temp_path / "sections_backup.json"
        
        # Verifica che backup interno esista
        self.assertTrue(backup_internal.exists())
        
        # Leggi contenuto backup interno
        with backup_internal.open("r", encoding="utf-8") as f:
            backup_content = f.read()
        
        # Esporta
        export_path = self.temp_path / "export_external.json"
        self.repo.export_backup(export_path)
        
        # Verifica che backup interno non sia cambiato
        with backup_internal.open("r", encoding="utf-8") as f:
            current_backup = f.read()
        
        self.assertEqual(backup_content, current_backup)

    def test_export_empty_repository(self):
        """Test: Export di repository vuoto."""
        # Crea nuovo repository vuoto
        empty_repo = SectionRepository(json_file=str(self.temp_path / "empty.json"))
        empty_repo._sections.clear()
        empty_repo._keys.clear()
        
        export_path = self.temp_path / "empty_export.json"
        empty_repo.export_backup(export_path)
        
        # Verifica che il file esista e contenga lista vuota
        self.assertTrue(export_path.exists())
        with export_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data, [])

    def test_export_preserves_all_section_data(self):
        """Test: Export preserva tutti i dati delle sezioni."""
        export_path = self.temp_path / "full_data.json"
        self.repo.export_backup(export_path)
        
        # Carica export
        with export_path.open("r", encoding="utf-8") as f:
            exported_data = json.load(f)
        
        # Verifica che tutti i campi siano presenti
        for section_data in exported_data:
            if section_data["section_type"] == "RECTANGULAR":
                self.assertIn("width", section_data)
                self.assertIn("height", section_data)
            elif section_data["section_type"] == "CIRCULAR":
                self.assertIn("diameter", section_data)


if __name__ == "__main__":
    unittest.main()
