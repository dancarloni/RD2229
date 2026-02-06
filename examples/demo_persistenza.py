#!/usr/bin/env python3
"""
Esempio pratico di persistenza del SectionRepository.

Questo script mostra come le sezioni vengono salvate e ripristinate automaticamente.
"""

import os
import sys

from sections_app.models.sections import (
    CircularSection,
    LSection,
    RectangularSection,
    TSection,
)
from sections_app.services.repository import SectionRepository


def main():
    print("\n" + "=" * 70)
    print("DEMO PERSISTENZA SECTION REPOSITORY")
    print("=" * 70)

    # Usa un file JSON personalizzato per la demo
    json_file = "demo_sections.jsons"

    # FASE 1: Primo avvio - crea sezioni
    print("\n[FASE 1] Primo avvio - Creazione sezioni")
    print("-" * 70)

    repo = SectionRepository(json_file=json_file)
    print(f"\n✓ Repository inizializzato")
    print(f"  File: {json_file}")
    print(f"  Sezioni caricate: {len(repo.get_all_sections())}")

    # Crea alcune sezioni
    print("\nAggiunta sezioni...")
    sections = [
        RectangularSection(name="Pilastro 30x50", width=30, height=50, note="Colonna principale"),
        CircularSection(name="Palo d=60", diameter=60, note="Tubo acciaio"),
        TSection(
            name="Profilo a T",
            flange_width=80,
            flange_thickness=10,
            web_thickness=8,
            web_height=60,
            note="Acciaio S355",
        ),
        LSection(
            name="Angolare L 50x50",
            width=50,
            height=50,
            t_horizontal=5,
            t_vertical=5,
            note="Angolare acciaio",
        ),
        RectangularSection(
            name="Trave 40x60", width=40, height=60, rotation_angle_deg=45, note="Rotata 45°"
        ),
    ]

    for i, section in enumerate(sections, 1):
        repo.add_section(section)
        print(f"  {i}. {section.name} ({section.section_type})")

    print(f"\n✓ {len(repo.get_all_sections())} sezioni salvate in {json_file}")

    # FASE 2: Mostra le proprietà di una sezione
    print("\n[FASE 2] Proprietà della sezione 'Pilastro 30x50'")
    print("-" * 70)

    pilastro = next((s for s in repo.get_all_sections() if s.name == "Pilastro 30x50"), None)
    if pilastro:
        print(f"\nSezione: {pilastro.name}")
        print(f"  Tipo: {pilastro.section_type}")
        print(f"  Dimensioni: {pilastro.width} x {pilastro.height}")
        print(f"  Area: {pilastro.properties.area:.2f}")
        print(
            f"  Baricentro: ({pilastro.properties.centroid_x:.2f}, {pilastro.properties.centroid_y:.2f})"
        )
        print(f"  Momenti d'inerzia:")
        print(f"    Ix: {pilastro.properties.ix:.2f}")
        print(f"    Iy: {pilastro.properties.iy:.2f}")
        print(f"    Ixy: {pilastro.properties.ixy:.2f}")
        print(f"  Raggi di inerzia:")
        print(f"    rx: {pilastro.properties.rx:.2f}")
        print(f"    ry: {pilastro.properties.ry:.2f}")

    # FASE 3: Modifica una sezione
    print("\n[FASE 3] Modifica sezione 'Palo d=60'")
    print("-" * 70)

    palo = next((s for s in repo.get_all_sections() if s.name == "Palo d=60"), None)
    if palo:
        print(f"\nSezione originale:")
        print(f"  Nome: {palo.name}")
        print(f"  Diametro: {palo.diameter}")
        print(f"  Area: {palo.properties.area:.2f}")

        # Modifica il palo
        palo_modificato = CircularSection(
            name="Palo d=60 (cavo)", diameter=60, note="Tubo acciaio cavo - sezione corretta"
        )
        repo.update_section(palo.id, palo_modificato)

        print(f"\nSezione modificata e salvata:")
        print(f"  Nome: {palo_modificato.name}")
        print(f"  Diametro: {palo_modificato.diameter}")
        print(f"  Area: {palo_modificato.properties.area:.2f}")

    # FASE 4: Elimina una sezione
    print("\n[FASE 4] Eliminazione sezione 'Angolare L 50x50'")
    print("-" * 70)

    angolare = next((s for s in repo.get_all_sections() if "Angolare" in s.name), None)
    if angolare:
        print(f"\nPrima dell'eliminazione: {len(repo.get_all_sections())} sezioni")
        print(f"  Eliminazione: {angolare.name}")
        repo.delete_section(angolare.id)
        print(f"Dopo l'eliminazione: {len(repo.get_all_sections())} sezioni")

    # FASE 5: Simula chiusura e riapertura dell'applicazione
    print("\n[FASE 5] Simulazione riavvio applicazione")
    print("-" * 70)

    print("\nChiusura applicazione...")
    del repo
    print("✓ Repository distrutto")

    print(f"\nRiapertura applicazione...")
    repo2 = SectionRepository(json_file=json_file)
    print(f"✓ Repository ripristinato")

    print(f"\nSezioni caricate dal file:")
    for i, section in enumerate(repo2.get_all_sections(), 1):
        print(f"  {i}. {section.name} ({section.section_type})")

    print(f"\n✓ {len(repo2.get_all_sections())} sezioni ripristinate da {json_file}")

    # FASE 6: Mostra il contenuto del JSON
    print("\n[FASE 6] Contenuto del file JSON")
    print("-" * 70)

    if os.path.isfile(json_file):
        import json

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\nFile: {json_file}")
        print(f"Formato: JSON")
        print(f"Sezioni salvate: {len(data)}")
        print(f"\nPrima sezione (struttura JSON):")
        if data:
            first = data[0]
            print(f"  id: {first.get('id')[:8]}...")
            print(f"  name: {first.get('name')}")
            print(f"  section_type: {first.get('section_type')}")
            print(f"  area: {first.get('area')}")
            print(f"  Ix: {first.get('Ix')}")
            print(f"  Iy: {first.get('Iy')}")
            print(f"  rotation_angle_deg: {first.get('rotation_angle_deg')}")

    # FASE 7: Statistiche finali
    print("\n[FASE 7] Statistiche finali")
    print("-" * 70)

    print(f"\nFile creato: {os.path.abspath(json_file)}")
    print(f"Dimensione: {os.path.getsize(json_file)} bytes")
    print(f"Sezioni salvate: {len(repo2.get_all_sections())}")

    total_area = sum(s.properties.area for s in repo2.get_all_sections())
    print(f"Area totale: {total_area:.2f}")

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETATA")
    print("=" * 70)
    print("\nCaratteristiche dimostrate:")
    print("  ✓ Creazione automatica del file JSON")
    print("  ✓ Salvataggio automatico di add_section()")
    print("  ✓ Salvataggio automatico di update_section()")
    print("  ✓ Salvataggio automatico di delete_section()")
    print("  ✓ Caricamento automatico all'avvio")
    print("  ✓ Persistenza dei dati tra sessioni")
    print("  ✓ Conservazione di tutte le proprietà geometriche")
    print("  ✓ JSON formattato e leggibile")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
