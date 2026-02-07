#!/usr/bin/env python3
"""Demo: Mostra il funzionamento del sistema di backup automatico."""

import json
import os
import tempfile
from pathlib import Path

from core_models.materials import Material, MaterialRepository
from sections_app.models.sections import CircularSection, RectangularSection
from sections_app.services.repository import SectionRepository


def print_file_content(file_path: Path, title: str):
    """Stampa il contenuto di un file JSON in modo leggibile."""
    if not file_path.exists():
        print(f"\n[{title}] ❌ FILE NON ESISTE: {file_path.name}")
        return

    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n[{title}] 📄 {file_path.name}")
        print(f"  Elementi: {len(data)}")
        for idx, item in enumerate(data, 1):
            name = item.get("name", "N/A")
            print(f"  {idx}. {name}")
    except Exception as e:
        print(f"\n[{title}] ❌ ERRORE LETTURA: {e}")


def demo_section_backup():
    """Demo del sistema di backup per le sezioni."""
    print("=" * 70)
    print("DEMO: Sistema Backup Automatico - SectionRepository")
    print("=" * 70)

    # Crea directory temporanea
    temp_dir = tempfile.mkdtemp()
    sections_file = os.path.join(temp_dir, "demo_sections.jsons")

    print(f"\n📁 Directory temporanea: {temp_dir}")
    print("📄 File principale: demo_sections.jsons")
    print("💾 File backup: demo_sections_backup.jsons")

    # Crea repository (canonical .jsons)
    repo = SectionRepository(json_file=sections_file)

    # FASE 1: Prima aggiunta
    print("\n" + "-" * 70)
    print("FASE 1: Aggiungi prima sezione")
    print("-" * 70)

    rect1 = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
    repo.add_section(rect1)

    file_path = Path(sections_file)
    backup_path = file_path.with_name("demo_sections_backup.json")

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n💡 Nota: Il backup non esiste ancora (primo salvataggio)")

    # FASE 2: Seconda aggiunta
    print("\n" + "-" * 70)
    print("FASE 2: Aggiungi seconda sezione")
    print("-" * 70)

    rect2 = RectangularSection(name="Rettangolare 25x40", width=25, height=40)
    repo.add_section(rect2)

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n✅ Ora il backup contiene lo stato precedente (1 sezione)")

    # FASE 3: Terza aggiunta
    print("\n" + "-" * 70)
    print("FASE 3: Aggiungi terza sezione")
    print("-" * 70)

    circ = CircularSection(name="Circolare d=30", diameter=30)
    repo.add_section(circ)

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n✅ Il backup contiene lo stato precedente (2 sezioni)")

    # FASE 4: Modifica sezione
    print("\n" + "-" * 70)
    print("FASE 4: Modifica prima sezione")
    print("-" * 70)

    sections = repo.get_all_sections()
    first_id = sections[0].id

    updated = RectangularSection(name="Rettangolare MODIFICATA 20x30", width=20, height=30)
    repo.update_section(first_id, updated)

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n✅ Il backup preserva il nome originale")

    # FASE 5: Elimina sezione
    print("\n" + "-" * 70)
    print("FASE 5: Elimina seconda sezione")
    print("-" * 70)

    sections = repo.get_all_sections()
    second_id = sections[1].id
    repo.delete_section(second_id)

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n✅ Il backup contiene la sezione eliminata")

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETATA")
    print("=" * 70)


def demo_material_backup():
    """Demo del sistema di backup per i materiali."""
    print("\n\n")
    print("=" * 70)
    print("DEMO: Sistema Backup Automatico - MaterialRepository")
    print("=" * 70)

    # Crea directory temporanea
    temp_dir = tempfile.mkdtemp()
    materials_file = os.path.join(temp_dir, "demo_materials.json")

    print(f"\n📁 Directory temporanea: {temp_dir}")
    print("📄 File principale: demo_materials.json")
    print("💾 File backup: demo_materials_backup.json")

    # Crea repository
    repo = MaterialRepository(json_file=materials_file)

    # FASE 1: Prima aggiunta
    print("\n" + "-" * 70)
    print("FASE 1: Aggiungi primo materiale")
    print("-" * 70)

    mat1 = Material(name="C25/30", type="concrete", properties={"fck": 25})
    repo.add(mat1)

    file_path = Path(materials_file)
    backup_path = file_path.with_name("demo_materials_backup.json")

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n💡 Nota: Il backup non esiste ancora (primo salvataggio)")

    # FASE 2: Seconda aggiunta
    print("\n" + "-" * 70)
    print("FASE 2: Aggiungi secondo materiale")
    print("-" * 70)

    mat2 = Material(name="C30/37", type="concrete", properties={"fck": 30})
    repo.add(mat2)

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n✅ Ora il backup contiene lo stato precedente (1 materiale)")

    # FASE 3: Terza aggiunta
    print("\n" + "-" * 70)
    print("FASE 3: Aggiungi terzo materiale")
    print("-" * 70)

    mat3 = Material(name="A500", type="steel", properties={"fyk": 500})
    repo.add(mat3)

    print_file_content(file_path, "File Principale")
    print_file_content(backup_path, "File Backup")

    print("\n✅ Il backup contiene lo stato precedente (2 materiali)")

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETATA")
    print("=" * 70)


def demo_safe_write():
    """Demo della scrittura sicura tramite file temporaneo."""
    print("\n\n")
    print("=" * 70)
    print("DEMO: Scrittura Sicura tramite File Temporaneo")
    print("=" * 70)

    print("\n📝 Strategia di sicurezza:")
    print("  1. Se esiste file principale → crea backup")
    print("  2. Scrivi dati su file temporaneo (.json.tmp)")
    print("  3. Rename atomico: .json.tmp → .json")
    print("  4. In caso di errore, elimina il file temporaneo")

    print("\n✅ Vantaggi:")
    print("  • Nessuna perdita di dati in caso di crash durante scrittura")
    print("  • Il file principale non viene mai corrotto")
    print("  • Operazione rename è atomica nel filesystem")
    print("  • Il backup preserva sempre l'ultimo stato valido")

    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.json")

    repo = SectionRepository(json_file=test_file)

    print("\n📁 Directory temporanea:", temp_dir)
    print("\n🔄 Esecuzione salvataggio...")

    rect = RectangularSection(name="Test", width=20, height=30)
    repo.add_section(rect)

    # Verifica che il file temporaneo non esista
    tmp_path = Path(test_file).with_suffix(".json.tmp")

    if tmp_path.exists():
        print("\n❌ File temporaneo ESISTE (non dovrebbe!)")
    else:
        print("\n✅ File temporaneo NON esiste (corretto!)")
        print("   Il rename atomico ha funzionato correttamente")

    if Path(test_file).exists():
        print("✅ File principale esiste e contiene i dati")

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETATA")
    print("=" * 70)


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DEMO: SISTEMA BACKUP AUTOMATICO" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")

    demo_section_backup()
    demo_material_backup()
    demo_safe_write()

    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 22 + "TUTTE LE DEMO COMPLETATE!" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
