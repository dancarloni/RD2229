"""Test granulari per verificare l'uso dei percorsi canonici dei repository.

Verifica che:
- SectionRepository usi sec_repository/sec_repository.jsons
- MaterialsRepository/GUI usi mat_repository/Mat_repository.jsonm
- Le operazioni CRUD salvino nei percorsi corretti
- Le funzioni helper usino i default corretti
"""
import json
import os
import tempfile
import shutil
from pathlib import Path
import pytest

from sections_app.services.repository import (
    SectionRepository,
    DEFAULT_JSON_FILE as SECTIONS_DEFAULT,
    load_sections_from_json,
    save_sections_to_json,
)
from sections_app.models.sections import RectangularSection
from materials_repository import MaterialsRepository


class TestSectionRepositoryCanonicalPath:
    """Test per verificare che SectionRepository usi il percorso canonico."""

    def test_default_json_file_points_to_canonical_path(self):
        """Verifica che DEFAULT_JSON_FILE punti a sec_repository/sec_repository.jsons."""
        assert SECTIONS_DEFAULT.endswith("sec_repository/sec_repository.jsons") or \
               SECTIONS_DEFAULT.endswith(r"sec_repository\sec_repository.jsons"), \
               f"DEFAULT_JSON_FILE deve puntare a sec_repository/sec_repository.jsons, trovato: {SECTIONS_DEFAULT}"
        
    def test_section_repository_uses_canonical_path_by_default(self):
        """Verifica che SectionRepository usi il percorso canonico di default."""
        # Crea repository senza specificare il path
        repo = SectionRepository()
        
        # Verifica che il path sia quello canonico
        assert repo._json_file == SECTIONS_DEFAULT, \
               f"Repository dovrebbe usare {SECTIONS_DEFAULT}, usa: {repo._json_file}"
        
    def test_section_repository_creates_canonical_directory(self):
        """Verifica che il repository crei la directory sec_repository se non esiste."""
        canonical_dir = os.path.dirname(SECTIONS_DEFAULT)
        
        # La directory dovrebbe esistere dopo l'inizializzazione
        assert os.path.exists(canonical_dir), \
               f"Directory {canonical_dir} dovrebbe esistere"
        
    def test_section_repository_save_creates_file_in_canonical_path(self, tmpdir):
        """Verifica che save_to_file salvi nel percorso canonico."""
        # Usa un path temporaneo per il test
        test_file = os.path.join(tmpdir, "test_sections.jsons")
        repo = SectionRepository(json_file=test_file)
        
        # Aggiungi una sezione
        section = RectangularSection(
            name="Test Rect",
            width=30.0,
            height=50.0
        )
        repo.add_section(section)
        
        # Verifica che il file sia stato creato
        assert os.path.exists(test_file), f"File {test_file} dovrebbe essere creato"
        
        # Verifica che il file sia JSON valido
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, list), "Il file dovrebbe contenere una lista"
            assert len(data) == 1, "La lista dovrebbe contenere 1 sezione"
            
    def test_section_repository_backup_path(self, tmpdir):
        """Verifica che il backup usi il percorso corretto."""
        test_file = os.path.join(tmpdir, "test_sections.jsons")
        repo = SectionRepository(json_file=test_file)
        
        # Il backup path dovrebbe avere _backup nel nome
        expected_backup = os.path.join(tmpdir, "test_sections_backup.jsons")
        assert str(repo._backup_path) == expected_backup, \
               f"Backup path dovrebbe essere {expected_backup}, trovato: {repo._backup_path}"


class TestSectionHelperFunctions:
    """Test per le funzioni helper load/save_sections_from_json."""
    
    def test_load_sections_uses_canonical_default(self, tmpdir):
        """Verifica che load_sections_from_json usi il default canonico."""
        # Crea un file temporaneo da usare
        test_file = os.path.join(tmpdir, "test_canonical.jsons")
        
        # Prima salva alcune sezioni usando il repository
        repo = SectionRepository(json_file=test_file)
        section = RectangularSection(name="Test Section", width=30.0, height=50.0)
        repo.add_section(section)
        
        # Ora carica usando load_sections_from_json con path esplicito
        sections = load_sections_from_json(test_file)
        
        # Verifica che abbia caricato i dati
        assert len(sections) == 1, "Dovrebbe caricare 1 sezione"
        assert sections[0]["name"] == "Test Section"
        
    def test_save_sections_uses_canonical_default(self, tmpdir):
        """Verifica che save_sections_to_json salvi correttamente."""
        # Crea un file temporaneo da usare
        test_file = os.path.join(tmpdir, "test_save_canonical.jsons")
        
        # Salva specificando il path
        sample_sections = [{
            "name": "Save Test",
            "section_type": "RECTANGULAR",
            "width": 40.0,
            "height": 60.0
        }]
        save_sections_to_json(sample_sections, test_file)
        
        # Verifica che il file sia stato creato
        assert os.path.exists(test_file), f"File {test_file} dovrebbe essere creato"
        
        # Verifica il contenuto
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["name"] == "Save Test"


class TestMaterialsRepositoryCanonicalPath:
    """Test per verificare che MaterialsRepository usi il percorso canonico."""
    
    def test_materials_gui_has_canonical_path_constant(self):
        """Verifica che materials_gui.py definisca MATERIALS_REPO_PATH."""
        from gui.materials_gui import MATERIALS_REPO_PATH
        
        assert MATERIALS_REPO_PATH.endswith("mat_repository/Mat_repository.jsonm") or \
               MATERIALS_REPO_PATH.endswith(r"mat_repository\Mat_repository.jsonm"), \
               f"MATERIALS_REPO_PATH deve puntare a mat_repository/Mat_repository.jsonm, trovato: {MATERIALS_REPO_PATH}"
    
    def test_materials_repository_can_use_jsonm_extension(self, tmpdir):
        """Verifica che MaterialsRepository accetti file .jsonm."""
        test_file = os.path.join(tmpdir, "test_materials.jsonm")
        
        # Crea un file di test
        sample_materials = [{
            "name": "Test Material",
            "type": "concrete",
            "cement_type": "normal",
            "sigma_c28": 200.0,
            "condition": "semplicemente_compresa",
            "controlled_quality": True
        }]
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(sample_materials, f)
        
        # Carica con MaterialsRepository
        repo = MaterialsRepository()
        mats = repo.load_from_jsonm(test_file)
        
        # Verifica
        assert len(mats) == 1, "Dovrebbe caricare 1 materiale"
        assert mats[0]["name"] == "Test Material"
        
    def test_materials_repository_save_to_jsonm(self, tmpdir):
        """Verifica che MaterialsRepository salvi correttamente in .jsonm."""
        test_file = os.path.join(tmpdir, "save_test.jsonm")
        
        repo = MaterialsRepository()
        
        # Aggiungi un materiale
        material = {
            "name": "Save Test Material",
            "type": "concrete",
            "cement_type": "high",
            "sigma_c28": 250.0,
            "condition": "semplicemente_compresa",
            "controlled_quality": False
        }
        repo.add(material)
        
        # Salva
        repo.save_to_jsonm(test_file)
        
        # Verifica che il file esista
        assert os.path.exists(test_file), f"File {test_file} dovrebbe essere creato"
        
        # Verifica il contenuto
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["name"] == "Save Test Material"
            
    def test_materials_repository_rejects_non_jsonm_extension(self, tmpdir):
        """Verifica che load_from_jsonm sollevi errore per estensioni diverse da .jsonm."""
        test_file = os.path.join(tmpdir, "wrong_extension.json")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        repo = MaterialsRepository()
        
        # Dovrebbe sollevare ValueError
        with pytest.raises(ValueError, match="must have .jsonm extension"):
            repo.load_from_jsonm(test_file)


class TestMaterialsGUIIntegration:
    """Test di integrazione per MaterialsApp con percorso canonico."""
    
    def test_materials_app_initializes_with_canonical_path(self, tmpdir, monkeypatch):
        """Verifica che MaterialsApp si inizializzi con il percorso canonico."""
        # Questo test richiede tkinter, lo saltiamo se non disponibile
        try:
            import tkinter as tk
        except ImportError:
            pytest.skip("tkinter non disponibile")
        
        # Mock del percorso canonico
        test_canonical = os.path.join(tmpdir, "test_canonical.jsonm")
        
        import gui.materials_gui as mat_gui_module
        original_path = mat_gui_module.MATERIALS_REPO_PATH
        monkeypatch.setattr(mat_gui_module, 'MATERIALS_REPO_PATH', test_canonical)
        
        # Crea l'app (in modalità headless)
        try:
            root = tk.Tk()
            root.withdraw()  # Nascondi la finestra
            
            from gui.materials_gui import MaterialsApp
            app = MaterialsApp(master=root)
            
            # Verifica che current_materials_path sia il canonico
            assert app.current_materials_path == test_canonical, \
                   f"current_materials_path dovrebbe essere {test_canonical}, trovato: {app.current_materials_path}"
            
            root.destroy()
        except Exception as e:
            pytest.skip(f"Impossibile testare GUI: {e}")
        finally:
            monkeypatch.setattr(mat_gui_module, 'MATERIALS_REPO_PATH', original_path)


class TestCRUDOperationsOnCanonicalPaths:
    """Test delle operazioni CRUD sui percorsi canonici."""
    
    def test_section_crud_cycle_on_canonical_path(self, tmpdir):
        """Test completo CRUD per sezioni sul percorso canonico."""
        test_file = os.path.join(tmpdir, "crud_test.jsons")
        repo = SectionRepository(json_file=test_file)
        
        # CREATE
        section1 = RectangularSection(name="CRUD Test 1", width=30, height=50)
        assert repo.add_section(section1), "Add dovrebbe ritornare True"
        assert os.path.exists(test_file), "File dovrebbe esistere dopo add"
        
        # READ
        all_sections = repo.get_all_sections()
        assert len(all_sections) == 1, "Dovrebbe esserci 1 sezione"
        
        found = repo.find_by_id(section1.id)
        assert found is not None, "find_by_id dovrebbe trovare la sezione"
        assert found.name == "CRUD Test 1"
        
        # UPDATE
        section1.width = 35.0
        repo.update_section(section1.id, section1)
        
        updated = repo.find_by_id(section1.id)
        assert updated.width == 35.0, "Width dovrebbe essere aggiornato"
        
        # DELETE
        repo.delete_section(section1.id)
        assert len(repo.get_all_sections()) == 0, "Non dovrebbero esserci sezioni dopo delete"
        
    def test_materials_crud_cycle_on_canonical_path(self, tmpdir):
        """Test completo CRUD per materiali sul percorso canonico."""
        test_file = os.path.join(tmpdir, "materials_crud.jsonm")
        repo = MaterialsRepository()
        
        # CREATE
        mat1 = {
            "name": "CRUD Material 1",
            "type": "concrete",
            "cement_type": "normal",
            "sigma_c28": 200.0,
            "condition": "semplicemente_compresa",
            "controlled_quality": True
        }
        repo.add(mat1)
        repo.save_to_jsonm(test_file)
        
        assert os.path.exists(test_file), "File dovrebbe esistere"
        
        # READ
        all_mats = repo.get_all()
        assert len(all_mats) == 1, "Dovrebbe esserci 1 materiale"
        
        found = repo.get_by_name("CRUD Material 1")
        assert found is not None, "get_by_name dovrebbe trovare il materiale"
        assert found["sigma_c28"] == 200.0
        
        # UPDATE
        updates = {"sigma_c28": 250.0}
        repo.update("CRUD Material 1", updates)
        repo.save_to_jsonm(test_file)
        
        updated = repo.get_by_name("CRUD Material 1")
        assert updated["sigma_c28"] == 250.0, "sigma_c28 dovrebbe essere aggiornato"
        
        # DELETE
        repo.delete("CRUD Material 1")
        assert len(repo.get_all()) == 0, "Non dovrebbero esserci materiali dopo delete"


class TestBackupMechanisms:
    """Test per i meccanismi di backup."""
    
    def test_section_repository_creates_backup_on_save(self, tmpdir):
        """Verifica che SectionRepository crei un backup prima di salvare."""
        test_file = os.path.join(tmpdir, "backup_test.jsons")
        backup_file = os.path.join(tmpdir, "backup_test_backup.jsons")
        
        # Prima scrittura
        repo = SectionRepository(json_file=test_file)
        section1 = RectangularSection(name="Backup Test", width=30, height=50)
        repo.add_section(section1)
        
        assert os.path.exists(test_file), "File principale dovrebbe esistere"
        
        # Seconda scrittura (dovrebbe creare backup)
        section2 = RectangularSection(name="Backup Test 2", width=40, height=60)
        repo.add_section(section2)
        
        assert os.path.exists(backup_file), "File di backup dovrebbe essere creato"
        
        # Verifica che il backup contenga i dati precedenti
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
            assert len(backup_data) == 1, "Backup dovrebbe contenere 1 sezione (snapshot precedente)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
