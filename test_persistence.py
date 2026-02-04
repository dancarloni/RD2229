#!/usr/bin/env python3
"""Test per verificare la persistenza JSON del SectionRepository."""

import json
import os
import tempfile
from pathlib import Path

from sections_app.models.sections import (
    CircularSection,
    RectangularSection,
    TSection,
)
from sections_app.services.repository import SectionRepository


def test_persistence_create_and_load():
    """Test: crea sezioni, salva, carica e verifica."""
    print("=" * 70)
    print("TEST 1: Creazione, salvataggio e caricamento sezioni")
    print("=" * 70)
    
    # Crea una directory temporanea per il test
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_sections.json")
        
        # FASE 1: Crea repository, aggiungi sezioni e salva
        print("\n[1] Creazione repository con sezioni...")
        repo1 = SectionRepository(json_file=json_file)
        
        rect = RectangularSection(name="Rettangolare 20x30", width=20, height=30, note="Test")
        circ = CircularSection(name="Circolare d=25", diameter=25, note="Tubo")
        t_sec = TSection(
            name="Sezione a T",
            flange_width=40,
            flange_thickness=5,
            web_thickness=8,
            web_height=25,
            note="Profilo",
        )
        
        for section in [rect, circ, t_sec]:
            if repo1.add_section(section):
                print(f"  ✓ Aggiunta: {section.name} (ID: {section.id})")
            else:
                assert False, f"Errore aggiunta: {section.name}"
        
        # Verifica contenuto JSON
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3, f"JSON contiene {len(data)} sezioni, attese 3"
        print(f"  ✓ JSON contiene 3 sezioni")
        
        # Stampa struttura JSON di una sezione
        print(f"\n[2] Struttura JSON (prima sezione):")
        first_section = data[0]
        print(f"  - id: {first_section.get('id')}")
        print(f"  - name: {first_section.get('name')}")
        print(f"  - section_type: {first_section.get('section_type')}")
        print(f"  - width: {first_section.get('width')}")
        print(f"  - height: {first_section.get('height')}")
        print(f"  - area: {first_section.get('area')}")
        print(f"  - rotation_angle_deg: {first_section.get('rotation_angle_deg')}")
        
        # FASE 2: Crea nuovo repository dallo stesso file
        print("\n[3] Caricamento da file JSON...")
        repo2 = SectionRepository(json_file=json_file)
        loaded_sections = repo2.get_all_sections()
        
        assert len(loaded_sections) == 3, f"Caricate {len(loaded_sections)} sezioni, attese 3"
        print(f"  ✓ Caricate {len(loaded_sections)} sezioni")
        
        for section in loaded_sections:
            print(f"  ✓ Caricata: {section.name} (ID: {section.id})")
        
        # Verifica che i dati siano corretti
        rect_loaded = next((s for s in loaded_sections if s.name == "Rettangolare 20x30"), None)
        assert rect_loaded is not None, "Sezione rettangolare non caricata"
        assert rect_loaded.width == 20, f"Width errata: {rect_loaded.width}"
        assert rect_loaded.height == 30, f"Height errata: {rect_loaded.height}"
        assert rect_loaded.note == "Test", f"Note errata: {rect_loaded.note}"
        print(f"  ✓ Verificate proprietà sezione rettangolare")
        
        circ_loaded = next((s for s in loaded_sections if s.name == "Circolare d=25"), None)
        assert circ_loaded is not None, "Sezione circolare non caricata"
        assert circ_loaded.diameter == 25, f"Diameter errata: {circ_loaded.diameter}"
        print(f"  ✓ Verificate proprietà sezione circolare")
    
    print("\n✅ TEST 1 PASSATO\n")


def test_persistence_update_delete():
    """Test: modifica e elimina sezioni, verifica persistenza."""
    print("=" * 70)
    print("TEST 2: Modifica e eliminazione con persistenza")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_sections.json")
        
        # Crea e salva sezioni
        print("\n[1] Creazione iniziale...")
        repo1 = SectionRepository(json_file=json_file)
        
        rect1 = RectangularSection(name="Rect1", width=10, height=20)
        rect2 = RectangularSection(name="Rect2", width=15, height=25)
        
        repo1.add_section(rect1)
        repo1.add_section(rect2)
        print(f"  ✓ Aggiunte 2 sezioni")
        
        rect1_id = rect1.id
        rect2_id = rect2.id
        
        # Modifica una sezione
        print("\n[2] Modifica sezione...")
        rect1_modified = RectangularSection(name="Rect1_Modified", width=12, height=22)
        repo1.update_section(rect1_id, rect1_modified)
        print(f"  ✓ Modificata sezione {rect1_id}")
        
        # Elimina una sezione
        print("\n[3] Eliminazione sezione...")
        repo1.delete_section(rect2_id)
        print(f"  ✓ Eliminata sezione {rect2_id}")
        
        # Carica da file
        print("\n[4] Caricamento da file...")
        repo2 = SectionRepository(json_file=json_file)
        loaded_sections = repo2.get_all_sections()
        
        assert len(loaded_sections) == 1, f"Caricate {len(loaded_sections)} sezioni, attesa 1"
        print(f"  ✓ Caricata 1 sezione (l'eliminata non c'è)")
        
        loaded_section = loaded_sections[0]
        assert loaded_section.name == "Rect1_Modified", f"Name errato: {loaded_section.name}"
        assert loaded_section.width == 12, f"Width errata: {loaded_section.width}"
        assert loaded_section.height == 22, f"Height errata: {loaded_section.height}"
        print(f"  ✓ Verificate proprietà modificate")
    
    print("\n✅ TEST 2 PASSATO\n")


def test_persistence_rotation():
    """Test: persistenza con rotazione."""
    print("=" * 70)
    print("TEST 3: Persistenza con rotazione")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_sections.json")
        
        print("\n[1] Creazione sezione con rotazione...")
        repo1 = SectionRepository(json_file=json_file)
        
        rect = RectangularSection(
            name="Rotated Rect",
            width=20,
            height=30,
            rotation_angle_deg=45.0,
            note="Ruotata 45°"
        )
        repo1.add_section(rect)
        rect_id = rect.id
        print(f"  ✓ Aggiunta sezione con rotazione 45°")
        
        # Carica da file
        print("\n[2] Caricamento da file...")
        repo2 = SectionRepository(json_file=json_file)
        loaded_section = repo2.find_by_id(rect_id)
        
        assert loaded_section is not None, "Sezione non caricata"
        assert loaded_section.rotation_angle_deg == 45.0, f"Rotazione errata: {loaded_section.rotation_angle_deg}"
        print(f"  ✓ Verificata rotazione: {loaded_section.rotation_angle_deg}°")
    
    print("\n✅ TEST 3 PASSATO\n")


def test_empty_repository():
    """Test: repository vuoto."""
    print("=" * 70)
    print("TEST 4: Repository vuoto")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "empty.json")
        
        # File non esiste
        print("\n[1] Repository senza file...")
        repo1 = SectionRepository(json_file=json_file)
        assert len(repo1.get_all_sections()) == 0, "Repository non vuoto"
        print(f"  ✓ Repository vuoto (file non esiste)")
        
        # Aggiungi una sezione e poi cancella tutto
        print("\n[2] Svuotamento repository...")
        rect = RectangularSection(name="Test", width=10, height=20)
        repo1.add_section(rect)
        repo1.clear()
        
        repo2 = SectionRepository(json_file=json_file)
        assert len(repo2.get_all_sections()) == 0, "Repository non svuotato"
        print(f"  ✓ Repository svuotato e salvato")
    
    print("\n✅ TEST 4 PASSATO\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST PERSISTENZA SectionRepository")
    print("=" * 70)

    try:
        test_persistence_create_and_load()
        test_persistence_update_delete()
        test_persistence_rotation()
        test_empty_repository()
        print("\n✅ TUTTI I TEST PASSATI!")
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE in test suite: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
