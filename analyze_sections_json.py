#!/usr/bin/env python3
"""Analizzatore file JSON salvato dal SectionRepository.
Mostra il contenuto e la struttura del file sections.json.
"""

import json
import os
import sys


def analyze_json_file(json_file: str = "sections.json") -> None:
    """Analizza il contenuto del file JSON salvato."""
    print("\n" + "=" * 70)
    print("ANALIZZATORE FILE JSON SECTION REPOSITORY")
    print("=" * 70)

    if not os.path.isfile(json_file):
        print(f"\n⚠️  File non trovato: {json_file}")
        print("\nPer generare il file:")
        print("  1. Eseguire demo_persistenza.py")
        print("  2. Oppure usare l'app GUI per aggiungere sezioni")
        return

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n✅ File caricato: {os.path.abspath(json_file)}")
        print(f"   Dimensione: {os.path.getsize(json_file)} bytes")
        print("   Encoding: UTF-8")

        # Statistiche
        print("\n[STATISTICHE]")
        print(f"  Sezioni salvate: {len(data)}")

        if not isinstance(data, list):
            print(f"\n❌ Formato JSON non valido: attesa lista, trovato {type(data).__name__}")
            return

        if not data:
            print("  (archivio vuoto)")
            return

        # Analizza ogni sezione
        print("\n[SEZIONI]")
        for i, section in enumerate(data, 1):
            print(f"\n  {i}. ID: {section.get('id', 'N/A')[:8]}...")
            print(f"     Nome: {section.get('name', 'N/A')}")
            print(f"     Tipo: {section.get('section_type', 'N/A')}")

            # Dimensioni
            dims = []
            if section.get("width"):
                dims.append(f"width={section['width']}")
            if section.get("height"):
                dims.append(f"height={section['height']}")
            if section.get("diameter"):
                dims.append(f"diameter={section['diameter']}")
            if section.get("flange_width"):
                dims.append(f"flange_width={section['flange_width']}")

            if dims:
                print(f"     Dimensioni: {', '.join(dims)}")

            # Proprietà geometriche
            if section.get("area"):
                print(f"     Area: {section['area']:.2f}")
            if section.get("ix"):
                print(f"     Ix: {section['ix']:.2f}")
            if section.get("iy"):
                print(f"     Iy: {section['iy']:.2f}")
            if section.get("rotation_angle_deg"):
                print(f"     Rotazione: {section['rotation_angle_deg']:.1f}°")
            if section.get("note"):
                print(f"     Note: {section['note']}")

        # Statistiche aggregate
        print("\n[STATISTICHE AGGREGATE]")
        total_area = sum(s.get("area", 0) for s in data if isinstance(s, dict))
        print(f"  Area totale: {total_area:.2f}")

        max_area = max((s.get("area", 0) for s in data if isinstance(s, dict)), default=0)
        max_section = next((s for s in data if s.get("area") == max_area), None)
        if max_section:
            print(f"  Sezione più grande: {max_section.get('name')} ({max_area:.2f})")

        # Conteggio per tipo
        types = {}
        for section in data:
            if isinstance(section, dict):
                section_type = section.get("section_type", "UNKNOWN")
                types[section_type] = types.get(section_type, 0) + 1

        print("  Sezioni per tipo:")
        for section_type, count in sorted(types.items()):
            print(f"    - {section_type}: {count}")

        # Struttura JSON
        print("\n[STRUTTURA JSON]")
        if data:
            first_section = data[0]
            print("  Campi salvati per sezione:")
            for key in sorted(first_section.keys()):
                value = first_section[key]
                value_type = type(value).__name__
                if value is None:
                    print(f"    - {key}: {value_type} (null)")
                else:
                    print(f"    - {key}: {value_type} = {value}")

        # Opzione per visualizzare JSON grezzo
        print("\n[OPZIONI]")
        print("  Per visualizzare il JSON grezzo:")
        print(f"    cat {json_file}")
        print("  O aprire con un editor di testo")

    except json.JSONDecodeError as e:
        print(f"\n❌ Errore parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ ANALISI COMPLETATA")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Se passato argomento, usa come nome file
    json_file = sys.argv[1] if len(sys.argv) > 1 else "sections.json"
    analyze_json_file(json_file)
