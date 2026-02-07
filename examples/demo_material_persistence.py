#!/usr/bin/env python3
"""Demo: Persistenza MaterialRepository
Dimostra salvataggio automatico, caricamento, modifica ed eliminazione di materiali.
"""

import os

from core_models.materials import Material, MaterialRepository


def print_header(title: str):
    """Stampa un header formattato."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_materials(repo: MaterialRepository, title: str = "Materiali nel repository"):
    """Stampa tutti i materiali."""
    materials = repo.get_all()
    print(f"\n{title}: ({len(materials)} materiali)")
    for i, mat in enumerate(materials, 1):
        print(f"  {i}. {mat.name} ({mat.type})")
        if mat.properties:
            props = ", ".join(f"{k}={v}" for k, v in mat.properties.items())
            print(f"     Proprietà: {props}")


def main():
    """Demo del MaterialRepository con persistenza."""
    json_file = "demo_materials.json"

    # Cancella file precedente se esiste
    if os.path.isfile(json_file):
        os.remove(json_file)
        print(f"File {json_file} precedente rimosso")

    print_header("DEMO PERSISTENZA MATERIAL REPOSITORY")

    # FASE 1: Creazione materiali
    print_header("[FASE 1] Primo avvio - Creazione materiali")

    repo1 = MaterialRepository(json_file=json_file)
    print("\n✓ Repository inizializzato")
    print(f"  File: {json_file}")
    print(f"  Materiali caricate: {len(repo1.get_all())}")

    print("\nAggiunta materiali...")
    materials = [
        Material(
            name="C25/30",
            type="concrete",
            properties={
                "fck": 25,
                "gamma_c": 1.5,
                "fcd": 16.7,
                "fctm": 2.6,
                "Ec": 31000,
            },
        ),
        Material(
            name="C45/55",
            type="concrete",
            properties={
                "fck": 45,
                "gamma_c": 1.5,
                "fcd": 30.0,
                "fctm": 3.8,
                "Ec": 36000,
            },
        ),
        Material(
            name="B450C",
            type="steel",
            properties={
                "fyk": 450,
                "gamma_s": 1.15,
                "Es": 200000,
            },
        ),
        Material(
            name="B500B",
            type="steel",
            properties={
                "fyk": 500,
                "gamma_s": 1.15,
                "Es": 200000,
            },
        ),
    ]

    for mat in materials:
        repo1.add(mat)
        print(f"  ✓ {mat.name} ({mat.type})")

    print(f"\n✓ {len(materials)} materiali salvati in {json_file}")
    print_materials(repo1)

    # FASE 2: Modifica materiale
    print_header("[FASE 2] Modifica materiale")

    c25_original = repo1.find_by_name("C25/30")
    print("\nMateriale originale:")
    print(f"  Nome: {c25_original.name}")
    print(f"  Proprietà: {c25_original.properties}")

    # Modifica
    c25_id = c25_original.id
    c25_modified = Material(
        id=c25_id,
        name="C25/30",
        type="concrete",
        properties={
            "fck": 25,
            "gamma_c": 1.5,
            "fcd": 17.0,  # Modificato
            "fctm": 2.6,
            "Ec": 32000,  # Modificato
        },
    )

    repo1.update(c25_id, c25_modified)
    print("\nMateriale modificato e salvato")
    print(f"  Nome: {c25_modified.name}")
    print(f"  Proprietà: {c25_modified.properties}")

    # FASE 3: Eliminazione materiale
    print_header("[FASE 3] Eliminazione materiale")

    b450_to_delete = repo1.find_by_name("B450C")
    print(f"\nEliminazione: {b450_to_delete.name}")
    repo1.delete(b450_to_delete.id)
    print("✓ Materiale eliminato e salvato")

    print_materials(repo1, "Materiali rimanenti")

    # FASE 4: Simulazione riavvio applicazione
    print_header("[FASE 4] Simulazione riavvio applicazione")

    print("\nChiusura applicazione...")
    print("✓ Repository distrutto")
    del repo1

    print("\nRiapertura applicazione...")
    repo2 = MaterialRepository(json_file=json_file)
    print("✓ Repository ripristinato")

    print_materials(repo2, "Materiali caricati dal file")

    # FASE 5: Verifica contenuto JSON
    print_header("[FASE 5] Contenuto del file JSON")

    import json

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\nFile: {json_file}")
    print("Formato: JSON")
    print(f"Materiali salvati: {len(data)}")

    if data:
        print("\nPrimo materiale (struttura JSON):")
        first = data[0]
        for key, value in first.items():
            if key != "id":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value[:8]}...")

    # FASE 6: Statistiche finali
    print_header("[FASE 6] Statistiche finali")

    print(f"\nFile creato: {os.path.abspath(json_file)}")
    print(f"Dimensione: {os.path.getsize(json_file)} bytes")
    print(f"Materiali salvati: {len(repo2.get_all())}")

    concrete_mats = [m for m in repo2.get_all() if m.type == "concrete"]
    steel_mats = [m for m in repo2.get_all() if m.type == "steel"]
    print(f"  - Calcestruzzo: {len(concrete_mats)}")
    print(f"  - Acciaio: {len(steel_mats)}")

    print_header("✅ DEMO COMPLETATA")

    print("\nCaratteristiche dimostrate:")
    print("  ✓ Creazione automatica del file JSON")
    print("  ✓ Salvataggio automatico di add()")
    print("  ✓ Salvataggio automatico di update()")
    print("  ✓ Salvataggio automatico di delete()")
    print("  ✓ Caricamento automatico all'avvio")
    print("  ✓ Persistenza dei dati tra sessioni")
    print("  ✓ Conservazione di tutte le proprietà")
    print("  ✓ JSON formattato e leggibile")


if __name__ == "__main__":
    main()
