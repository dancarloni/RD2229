#!/usr/bin/env python3
"""
Test: Verifica che i repository vengono caricati automaticamente all'avvio.
"""

import json
import os
import tempfile

from sections_app.services.repository import SectionRepository
from sections_app.models.sections import RectangularSection, CircularSection
from core_models.materials import Material, MaterialRepository


def test_repositories_auto_load_at_startup():
    """Test: crea archivi persistenti e verifica che vengono caricati all'avvio."""
    print("=" * 70)
    print("TEST: Caricamento automatico repository all'avvio")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        sections_file = os.path.join(tmpdir, "sections.json")
        materials_file = os.path.join(tmpdir, "materials.json")
        
        # FASE 1: Crea archivi persistenti
        print("\n[FASE 1] Creazione archivi persistenti...")
        
        # Crea archivio sezioni
        print("  Creazione sezioni...")
        repo_sections_1 = SectionRepository(json_file=sections_file)
        rect = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
        circ = CircularSection(name="Circolare d=25", diameter=25)
        repo_sections_1.add_section(rect)
        repo_sections_1.add_section(circ)
        print(f"    ✓ Aggiunte 2 sezioni, salvate in {sections_file}")
        
        # Crea archivio materiali
        print("  Creazione materiali...")
        repo_materials_1 = MaterialRepository(json_file=materials_file)
        c25 = Material(name="C25/30", type="concrete", properties={"fck": 25})
        a500 = Material(name="A500", type="steel", properties={"fyk": 500})
        repo_materials_1.add(c25)
        repo_materials_1.add(a500)
        print(f"    ✓ Aggiunti 2 materiali, salvati in {materials_file}")
        
        # FASE 2: Simulazione avvio app - Caricamento esplicito
        print("\n[FASE 2] Simulazione avvio app con caricamento esplicito...")
        
        # Simula il codice in app.py
        print("  Creazione e caricamento sezioni...")
        repo_sections_2 = SectionRepository(json_file=sections_file)
        repo_sections_2.load_from_file()  # Caricamento esplicito
        
        print("  Creazione e caricamento materiali...")
        repo_materials_2 = MaterialRepository(json_file=materials_file)
        repo_materials_2.load_from_file()  # Caricamento esplicito
        
        # FASE 3: Verifica che i repository siano caricati
        print("\n[FASE 3] Verifica caricamento...")
        
        # Verifica sezioni
        sections = repo_sections_2.get_all_sections()
        assert len(sections) == 2, f"Caricate {len(sections)} sezioni, attese 2"
        print(f"  ✓ Caricate {len(sections)} sezioni")
        for section in sections:
            print(f"    - {section.name}")
        
        # Verifica materiali
        materials = repo_materials_2.get_all()
        assert len(materials) == 2, f"Caricati {len(materials)} materiali, attesi 2"
        print(f"  ✓ Caricati {len(materials)} materiali")
        for material in materials:
            print(f"    - {material.name}")
        
        # FASE 4: Verifica caricamento automatico (senza explicit call)
        print("\n[FASE 4] Verifica caricamento automatico (nel __init__)...")
        
        print("  Creazione sezioni (caricamento automatico nel __init__)...")
        repo_sections_3 = SectionRepository(json_file=sections_file)
        # Non chiamiamo load_from_file(), dovrebbe essere già fatto
        sections_3 = repo_sections_3.get_all_sections()
        assert len(sections_3) == 2, f"Caricate {len(sections_3)} sezioni (attese 2)"
        print(f"  ✓ Caricate {len(sections_3)} sezioni automaticamente")
        
        print("  Creazione materiali (caricamento automatico nel __init__)...")
        repo_materials_3 = MaterialRepository(json_file=materials_file)
        # Non chiamiamo load_from_file(), dovrebbe essere già fatto
        materials_3 = repo_materials_3.get_all()
        assert len(materials_3) == 2, f"Caricati {len(materials_3)} materiali (attesi 2)"
        print(f"  ✓ Caricati {len(materials_3)} materiali automaticamente")
    
    print("\n✅ TEST PASSATO\n")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST CARICAMENTO AUTOMATICO REPOSITORY ALL'AVVIO")
    print("=" * 70)
    
    try:
        result = test_repositories_auto_load_at_startup()
        if result:
            print("\n✅ CARICAMENTO AUTOMATICO VERIFICATO!")
            print("\nConcluzione:")
            print("- I repository caricano automaticamente nel __init__()")
            print("- È anche possibile chiamare load_from_file() esplicitamente")
            print("- App.py ora chiama entrambi per massima chiarezza")
        else:
            print("\n❌ TEST FALLITO")
            exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
