#!/usr/bin/env python3
"""Test per verificare la persistenza JSON del MaterialRepository."""

import json
import os
import tempfile

from core_models.materials import Material, MaterialRepository


def test_material_persistence_basic():
    """Test: crea materiali, salva, carica e verifica."""
    print("=" * 70)
    print("TEST 1: Creazione, salvataggio e caricamento materiali")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_materials.json")
        
        # FASE 1: Crea repository, aggiungi materiali
        print("\n[1] Creazione repository con materiali...")
        repo1 = MaterialRepository(json_file=json_file)
        
        c120 = Material(name="C120", type="concrete", properties={"fck": 120, "gamma_c": 1.5})
        c200 = Material(name="C200", type="concrete", properties={"fck": 200, "gamma_c": 1.5})
        a500 = Material(name="A500", type="steel", properties={"fyk": 500, "gamma_s": 1.15})
        
        for material in [c120, c200, a500]:
            repo1.add(material)
            print(f"  ✓ Aggiunto: {material.name} (ID: {material.id[:8]}...)")
        
        # Verifica che il file esista
        assert os.path.isfile(json_file), f"File {json_file} non creato!"
        print(f"  ✓ File JSON creato: {json_file}")
        
        # Verifica contenuto JSON
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3, f"JSON contiene {len(data)} materiali, attesi 3"
        print(f"  ✓ JSON contiene 3 materiali")
        
        # Stampa struttura JSON di un materiale
        print(f"\n[2] Struttura JSON (primo materiale):")
        first_material = data[0]
        print(f"  - id: {first_material.get('id')[:8]}...")
        print(f"  - name: {first_material.get('name')}")
        print(f"  - type: {first_material.get('type')}")
        print(f"  - properties: {first_material.get('properties')}")
        
        # FASE 2: Crea nuovo repository dallo stesso file
        print("\n[3] Caricamento da file JSON...")
        repo2 = MaterialRepository(json_file=json_file)
        loaded_materials = repo2.get_all()
        
        assert len(loaded_materials) == 3, f"Caricati {len(loaded_materials)} materiali, attesi 3"
        print(f"  ✓ Caricati {len(loaded_materials)} materiali")
        
        for material in loaded_materials:
            print(f"  ✓ Caricato: {material.name} (tipo: {material.type})")
        
        # Verifica che i dati siano corretti
        c120_loaded = repo2.find_by_name("C120")
        assert c120_loaded is not None, "Materiale C120 non caricato"
        assert c120_loaded.type == "concrete", f"Type errato: {c120_loaded.type}"
        assert c120_loaded.properties.get("fck") == 120, f"fck errata: {c120_loaded.properties.get('fck')}"
        print(f"  ✓ Verificate proprietà materiale C120")
        
        a500_loaded = repo2.find_by_name("A500")
        assert a500_loaded is not None, "Materiale A500 non caricato"
        assert a500_loaded.type == "steel", f"Type errato: {a500_loaded.type}"
        assert a500_loaded.properties.get("fyk") == 500, f"fyk errata: {a500_loaded.properties.get('fyk')}"
        print(f"  ✓ Verificate proprietà materiale A500")
    
    print("\n✅ TEST 1 PASSATO\n")
    return True


def test_material_persistence_update_delete():
    """Test: modifica e elimina materiali, verifica persistenza."""
    print("=" * 70)
    print("TEST 2: Modifica e eliminazione con persistenza")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_materials.json")
        
        # Crea e salva materiali
        print("\n[1] Creazione iniziale...")
        repo1 = MaterialRepository(json_file=json_file)
        
        c120 = Material(name="C120", type="concrete", properties={"fck": 120})
        c200 = Material(name="C200", type="concrete", properties={"fck": 200})
        
        repo1.add(c120)
        repo1.add(c200)
        print(f"  ✓ Aggiunti 2 materiali")
        
        c120_id = c120.id
        c200_id = c200.id
        
        # Modifica un materiale
        print("\n[2] Modifica materiale...")
        c120_modified = Material(
            id=c120_id,
            name="C120_Modified",
            type="concrete",
            properties={"fck": 125}
        )
        repo1.update(c120_id, c120_modified)
        print(f"  ✓ Modificato materiale {c120_id[:8]}...")
        
        # Elimina un materiale
        print("\n[3] Eliminazione materiale...")
        repo1.delete(c200_id)
        print(f"  ✓ Eliminato materiale {c200_id[:8]}...")
        
        # Carica da file
        print("\n[4] Caricamento da file...")
        repo2 = MaterialRepository(json_file=json_file)
        loaded_materials = repo2.get_all()
        
        assert len(loaded_materials) == 1, f"Caricati {len(loaded_materials)} materiali, atteso 1"
        print(f"  ✓ Caricato 1 materiale (l'eliminato non c'è)")
        
        loaded_material = loaded_materials[0]
        assert loaded_material.name == "C120_Modified", f"Name errato: {loaded_material.name}"
        assert loaded_material.properties.get("fck") == 125, f"fck errata: {loaded_material.properties.get('fck')}"
        print(f"  ✓ Verificate proprietà modificate")
    
    print("\n✅ TEST 2 PASSATO\n")
    return True


def test_empty_repository():
    """Test: repository vuoto."""
    print("=" * 70)
    print("TEST 3: Repository vuoto")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "empty.json")
        
        # File non esiste
        print("\n[1] Repository senza file...")
        repo1 = MaterialRepository(json_file=json_file)
        assert len(repo1.get_all()) == 0, "Repository non vuoto"
        print(f"  ✓ Repository vuoto (file non esiste)")
        
        # Aggiungi un materiale e poi cancella tutto
        print("\n[2] Svuotamento repository...")
        material = Material(name="Test", type="concrete")
        repo1.add(material)
        repo1.clear()
        
        repo2 = MaterialRepository(json_file=json_file)
        assert len(repo2.get_all()) == 0, "Repository non svuotato"
        print(f"  ✓ Repository svuotato e salvato")
    
    print("\n✅ TEST 3 PASSATO\n")
    return True


def test_find_by_id():
    """Test: ricerca materiale per ID."""
    print("=" * 70)
    print("TEST 4: Ricerca per ID")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_materials.json")
        
        print("\n[1] Creazione e ricerca...")
        repo1 = MaterialRepository(json_file=json_file)
        
        material = Material(name="C120", type="concrete", properties={"fck": 120})
        repo1.add(material)
        material_id = material.id
        print(f"  ✓ Aggiunto materiale con ID: {material_id[:8]}...")
        
        # Carica da file
        print("\n[2] Ricerca da nuovo repository...")
        repo2 = MaterialRepository(json_file=json_file)
        found = repo2.find_by_id(material_id)
        
        assert found is not None, "Materiale non trovato per ID"
        assert found.name == "C120", f"Name errato: {found.name}"
        print(f"  ✓ Trovato materiale per ID: {found.name}")
    
    print("\n✅ TEST 4 PASSATO\n")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST PERSISTENZA MaterialRepository")
    print("=" * 70)
    
    tests = [
        test_material_persistence_basic,
        test_material_persistence_update_delete,
        test_empty_repository,
        test_find_by_id,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n❌ ERRORE in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))
    
    print("\n" + "=" * 70)
    print("RIEPILOGO TEST")
    print("=" * 70)
    for test_name, result in results:
        status = "✅ PASSATO" if result else "❌ FALLITO"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✅ TUTTI I TEST PASSATI!")
    else:
        print("\n❌ ALCUNI TEST FALLITI")
        exit(1)
