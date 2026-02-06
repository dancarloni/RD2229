"""
Test per le funzioni helper di gestione JSON del repository.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from sections_app.services.repository import load_sections_from_json, save_sections_to_json


class TestJsonWrappers(unittest.TestCase):
    """Test per load_sections_from_json e save_sections_to_json."""

    def setUp(self):
        """Setup per ogni test."""
        # Crea directory temporanea
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_sections.json")

    def tearDown(self):
        """Cleanup dopo ogni test."""
        # Rimuovi file temporanei
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_load_sections_from_json_file_esistente(self):
        """Verifica caricamento da file JSON esistente."""
        # Crea file JSON con sezioni di test
        test_data = [
            {
                "id": "rect-001",
                "name": "Rettangolo Test",
                "section_type": "rectangular",
                "width": 30.0,
                "height": 50.0,
                "area": 1500.0,
                "x_G": 15.0,
                "y_G": 25.0,
            },
            {
                "id": "rect-002",
                "name": "Quadrato Test",
                "section_type": "rectangular",
                "width": 40.0,
                "height": 40.0,
                "area": 1600.0,
                "x_G": 20.0,
                "y_G": 20.0,
            },
        ]

        with open(self.test_file, "w") as f:
            json.dump(test_data, f)

        # Carica sezioni
        sections = load_sections_from_json(self.test_file)

        # Verifica risultati
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]["name"], "Rettangolo Test")
        self.assertEqual(sections[1]["name"], "Quadrato Test")
        self.assertEqual(sections[0]["width"], 30.0)

    def test_load_sections_from_json_file_non_esistente(self):
        """Verifica che file non esistente ritorni lista vuota."""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.json")

        # Carica da file inesistente
        sections = load_sections_from_json(non_existent_file)

        # Verifica che ritorni lista vuota
        self.assertEqual(sections, [])
        self.assertIsInstance(sections, list)

    def test_save_sections_to_json_crea_file(self):
        """Verifica che save_sections_to_json crei correttamente il file."""
        # Prepara dati di test
        test_sections = [
            {"name": "Test 1", "section_type": "rectangular", "width": 30.0, "height": 50.0},
            {"name": "Test 2", "section_type": "rectangular", "width": 40.0, "height": 40.0},
        ]

        # Salva sezioni
        save_sections_to_json(test_sections, self.test_file)

        # Verifica che il file esista
        self.assertTrue(os.path.exists(self.test_file))

        # Verifica contenuto
        with open(self.test_file, "r") as f:
            saved_data = json.load(f)

        self.assertEqual(len(saved_data), 2)
        # Verifica che i nomi siano presenti
        names = [s.get("name") for s in saved_data]
        self.assertIn("Test 1", names)
        self.assertIn("Test 2", names)

    def test_save_sections_to_json_preserva_id(self):
        """Verifica che save_sections_to_json preservi gli ID delle sezioni."""
        # Prepara dati con ID specifici
        test_sections = [
            {
                "id": "custom-id-123",
                "name": "Sezione con ID",
                "section_type": "rectangular",
                "width": 30.0,
                "height": 50.0,
            }
        ]

        # Salva sezioni
        save_sections_to_json(test_sections, self.test_file)

        # Ricarica e verifica ID
        loaded = load_sections_from_json(self.test_file)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].get("id"), "custom-id-123")

    def test_roundtrip_save_poi_load(self):
        """Verifica che save seguito da load preservi i dati."""
        # Dati originali
        original_sections = [
            {
                "id": "rect-round-1",
                "name": "Roundtrip Test",
                "section_type": "rectangular",
                "width": 35.5,
                "height": 55.5,
            },
            {
                "id": "rect-round-2",
                "name": "Roundtrip Test 2",
                "section_type": "rectangular",
                "width": 45.5,
                "height": 65.5,
            },
        ]

        # Salva
        save_sections_to_json(original_sections, self.test_file)

        # Ricarica
        loaded_sections = load_sections_from_json(self.test_file)

        # Verifica che i dati siano preservati
        self.assertEqual(len(loaded_sections), 2)

        # Verifica ID preservati
        loaded_ids = [s.get("id") for s in loaded_sections]
        self.assertIn("rect-round-1", loaded_ids)
        self.assertIn("rect-round-2", loaded_ids)

        # Verifica nomi preservati
        loaded_names = [s.get("name") for s in loaded_sections]
        self.assertIn("Roundtrip Test", loaded_names)
        self.assertIn("Roundtrip Test 2", loaded_names)

    def test_save_sections_to_json_con_sezione_invalida(self):
        """Verifica gestione sezioni invalide durante salvataggio."""
        # Mix di sezioni valide e invalide
        test_sections = [
            {"name": "Valida", "section_type": "rectangular", "width": 30.0, "height": 50.0},
            {
                "name": "Invalida",
                "section_type": "tipo_inesistente",  # Tipo non valido
                "width": 30.0,
                "height": 50.0,
            },
        ]

        # Salva (dovrebbe saltare la sezione invalida senza sollevare eccezioni)
        save_sections_to_json(test_sections, self.test_file)

        # Verifica che il file esista
        self.assertTrue(os.path.exists(self.test_file))

        # Ricarica
        loaded = load_sections_from_json(self.test_file)

        # Potrebbe avere solo la sezione valida (dipende dall'implementazione)
        # Verifichiamo almeno che non sia crashato
        self.assertIsInstance(loaded, list)


if __name__ == "__main__":
    unittest.main()
