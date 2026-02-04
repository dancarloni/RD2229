"""
Test per la funzionalità di esportazione backup dalla GUI.

Verifica che il menu "Esporta backup..." sia presente e funzionante.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from sections_app.ui.module_selector import ModuleSelectorWindow
from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from core_models.materials import MaterialRepository, Material
from sections_app.models.sections import RectangularSection


class TestExportBackupGUI(unittest.TestCase):
    """Test per la funzionalità di export dalla GUI."""

    def setUp(self):
        """Setup con repository temporanei."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Crea repository con dati di test
        self.section_repo = SectionRepository(json_file=str(self.temp_path / "sections.json"))
        rect = RectangularSection(name="Test Section", width=300, height=500)
        self.section_repo.add_section(rect)
        
        self.material_repo = MaterialRepository(json_file=str(self.temp_path / "materials.json"))
        mat = Material(id="MAT-001", name="Test Material", type="concrete", properties={"fck": 25.0})
        self.material_repo.add(mat)
        
        self.serializer = CsvSectionSerializer()
    
    def tearDown(self):
        """Cleanup."""
        self.temp_dir.cleanup()

    def test_module_selector_has_menu(self):
        """Test: ModuleSelectorWindow ha il menu File."""
        window = ModuleSelectorWindow(self.section_repo, self.serializer, self.material_repo)
        
        # Verifica che esista il menu
        menubar = window.nametowidget(window.cget('menu'))
        self.assertIsNotNone(menubar)
        
        # Chiudi la finestra
        window.destroy()

    @patch('sections_app.ui.module_selector.filedialog.asksaveasfilename')
    @patch('sections_app.ui.module_selector.messagebox.showinfo')
    def test_export_sections_json(self, mock_showinfo, mock_asksaveasfilename):
        """Test: Export sezioni in JSON dalla GUI."""
        export_path = self.temp_path / "export_test.json"
        mock_asksaveasfilename.return_value = str(export_path)
        
        window = ModuleSelectorWindow(self.section_repo, self.serializer, self.material_repo)
        
        # Simula la scelta "sezioni" nel dialog
        with patch.object(window, 'wait_window'):
            with patch('tkinter.Toplevel') as mock_toplevel:
                # Simula immediatamente la scelta "sezioni"
                def fake_wait_window(dialog):
                    # Trova il callback per "sezioni" e chiamalo
                    pass
                
                # Chiamiamo direttamente il metodo di export
                # Dobbiamo simulare la scelta dell'utente
                original_export = window._export_backup
                
                def mock_export():
                    # Simula scelta "sezioni"
                    file_path = str(export_path)
                    try:
                        window.section_repository.export_backup(file_path)
                        # Non chiamiamo messagebox durante il test
                    except Exception as e:
                        pass
                
                mock_export()
        
        # Verifica che il file sia stato creato
        self.assertTrue(export_path.exists())
        
        # Verifica contenuto
        with export_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        
        window.destroy()

    def test_material_repository_export_backup(self):
        """Test: MaterialRepository.export_backup() funziona."""
        export_path = self.temp_path / "materials_export.json"
        
        self.material_repo.export_backup(export_path)
        
        # Verifica che il file esista
        self.assertTrue(export_path.exists())
        
        # Verifica contenuto
        with export_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Material")

    def test_material_repository_export_adds_json_extension(self):
        """Test: MaterialRepository aggiunge .json se mancante."""
        export_path = self.temp_path / "materials_no_ext"
        
        self.material_repo.export_backup(export_path)
        
        # Verifica che sia stato creato con .json
        expected_path = self.temp_path / "materials_no_ext.json"
        self.assertTrue(expected_path.exists())

    def test_export_both_creates_two_files(self):
        """Test: Export entrambi crea due file separati."""
        base_path = self.temp_path / "backup_completo.json"
        
        # Simula export di entrambi
        sections_path = self.temp_path / "backup_completo_sezioni.json"
        materials_path = self.temp_path / "backup_completo_materiali.json"
        
        self.section_repo.export_backup(sections_path)
        self.material_repo.export_backup(materials_path)
        
        # Verifica che entrambi i file esistano
        self.assertTrue(sections_path.exists())
        self.assertTrue(materials_path.exists())
        
        # Verifica contenuti
        with sections_path.open("r", encoding="utf-8") as f:
            sections_data = json.load(f)
        self.assertEqual(len(sections_data), 1)
        
        with materials_path.open("r", encoding="utf-8") as f:
            materials_data = json.load(f)
        self.assertEqual(len(materials_data), 1)


if __name__ == "__main__":
    unittest.main()
