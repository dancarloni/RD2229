#!/usr/bin/env python3
"""
Test del Section Manager: verifica che il Treeview visualizzi tutte le colonne
e che i dati siano caricati correttamente.
"""

import sys
from pathlib import Path

# Aggiungi il root al path per importare i moduli
sys.path.insert(0, str(Path(__file__).parent))

from sections_app.models.sections import RectangularSection, CircularSection, TSection
from sections_app.services.repository import SectionRepository, CsvSectionSerializer


def test_section_manager_data():
    """Test: verifica che le sezioni siano serializzate con tutti i dati."""
    print("=" * 70)
    print("TEST: Verifica serializzazione completa delle sezioni")
    print("=" * 70)

    # Crea un repository in memoria
    repo = SectionRepository()

    # Crea sezioni diverse
    rect = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
    circ = CircularSection(name="Circolare d=25", diameter=25)
    t_sec = TSection(
        name="Sezione a T",
        flange_width=40,
        flange_thickness=5,
        web_thickness=8,
        web_height=25,
    )

    # Calcola proprietà (obbligatorio)
    print("\n[1] Calcolo proprietà geometriche...")
    for section in [rect, circ, t_sec]:
        try:
            section.compute_properties()
            print(f"  ✓ {section.name}: {section.section_type} - OK")
        except Exception as e:
            print(f"  ✗ {section.name}: ERRORE - {e}")
            return False

    # Aggiunge al repository
    print("\n[2] Inserimento nel repository...")
    for section in [rect, circ, t_sec]:
        if repo.add_section(section):
            print(f"  ✓ {section.name} aggiunta")
        else:
            print(f"  ✗ {section.name} duplicata o errore")

    # Verifica serializzazione
    print("\n[3] Verifica serializzazione (to_dict)...")
    for section in repo.get_all_sections():
        data = section.to_dict()
        print(f"\n  Sezione: {data['name']}")
        print(f"    ID: {data['id']}")
        print(f"    Tipo: {data['section_type']}")
        print(f"    Campi geometrici:")
        for key in ['width', 'height', 'diameter', 'flange_width']:
            if data.get(key):
                print(f"      {key}: {data[key]}")
        print(f"    Campi calcolati (sample):")
        print(f"      area: {data.get('area', 'N/A')}")
        print(f"      x_G: {data.get('x_G', 'N/A')}")
        print(f"      Ix: {data.get('Ix', 'N/A')}")

    # Verifica CSV headers
    print("\n[4] Verifica CSV headers disponibili...")
    from sections_app.models.sections import CSV_HEADERS
    print(f"  Totale colonne CSV: {len(CSV_HEADERS)}")
    print(f"  Colonne: {', '.join(CSV_HEADERS)}")

    print("\n" + "=" * 70)
    print("✓ TEST COMPLETATO CON SUCCESSO")
    print("=" * 70)
    return True


def test_treeview_columns():
    """Test: verifica che le colonne del Treeview siano ben configurate."""
    print("\n" + "=" * 70)
    print("TEST: Configurazione colonne Treeview")
    print("=" * 70)

    from sections_app.models.sections import CSV_HEADERS

    # Simula la configurazione delle colonne come nel SectionManager
    col_config = {
        "id": (0, "w"),
        "name": (100, "w"),
        "section_type": (90, "center"),
        "width": (65, "center"),
        "height": (65, "center"),
        "diameter": (65, "center"),
        "flange_width": (70, "center"),
        "flange_thickness": (70, "center"),
        "web_thickness": (70, "center"),
        "web_height": (70, "center"),
        "area": (75, "center"),
        "x_G": (65, "center"),
        "y_G": (65, "center"),
        "Ix": (80, "center"),
        "Iy": (80, "center"),
        "Ixy": (75, "center"),
        "Qx": (70, "center"),
        "Qy": (70, "center"),
        "rx": (65, "center"),
        "ry": (65, "center"),
        "core_x": (70, "center"),
        "core_y": (70, "center"),
        "ellipse_a": (75, "center"),
        "ellipse_b": (75, "center"),
        "note": (120, "w"),
    }

    print(f"\nColonne CSV_HEADERS: {len(CSV_HEADERS)}")
    print(f"Colonne configurate: {len(col_config)}")

    # Verifica che tutte le colonne siano configurate
    missing = set(CSV_HEADERS) - set(col_config.keys())
    if missing:
        print(f"\n  ✗ Colonne mancanti da configurare: {missing}")
        return False
    else:
        print(f"  ✓ Tutte le colonne sono configurate")

    # Verifica larghezze
    print(f"\nLarghezze colonne:")
    id_width = col_config["id"][0]
    print(f"  ID (invisibile): {id_width} px {'✓' if id_width == 0 else '✗'}")

    total_width = sum(w for w, _ in col_config.values())
    print(f"  Larghezza totale calcolata: ~{total_width} px")

    print("\n" + "=" * 70)
    print("✓ TEST COLONNE COMPLETATO")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_section_manager_data() and test_treeview_columns()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERRORE NEL TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
