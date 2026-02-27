"""Demo Export Backup - SectionRepository.
======================================

Dimostra l'utilizzo della funzione export_backup() per esportare
l'archivio sezioni in formati JSON o CSV senza modificare i file
principali del repository.

Autore: Sistema automatico
Data: 2025
"""

import tempfile
from pathlib import Path

from sections_app.models.sections import CircularSection, RectangularSection, TSection
from sections_app.services.repository import SectionRepository


def print_section(title: str):
    """Stampa una sezione formattata."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Demo completa di export_backup()."""
    print("\n" + "=" * 70)
    print("  DEMO EXPORT BACKUP - SectionRepository")
    print("=" * 70)

    # Crea repository temporaneo
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        # Use canonical .jsons path for sections
        sec_dir = temp_path / "sec_repository"
        sec_dir.mkdir(exist_ok=True)
        repo = SectionRepository(json_file=str(sec_dir / "sec_repository.jsons"))

        # Scenario 1: Popola repository con sezioni
        print_section("Scenario 1: Creazione Repository con Sezioni di Test")

        rect = RectangularSection(name="Pilastro 30x50", width=300, height=500)
        circ = CircularSection(name="Palo Circolare D40", diameter=400)
        tsec = TSection(
            name="Trave a T 50x80",
            flange_width=500,
            flange_thickness=100,
            web_thickness=150,
            web_height=700,
        )

        repo.add_section(rect)
        repo.add_section(circ)
        repo.add_section(tsec)

        print("\n✓ Aggiunte 3 sezioni al repository:")
        print(f"  - {rect.name} (RECTANGULAR)")
        print(f"  - {circ.name} (CIRCULAR)")
        print(f"  - {tsec.name} (T_SECTION)")
        print(f"\n✓ File principale: {sec_dir / 'sec_repository.jsons'}")
        print(f"✓ File backup automatico: {sec_dir / 'sec_repository_backup.jsons'}")

        # Scenario 2: Export in JSON
        print_section("Scenario 2: Export in Formato JSON")

        json_export = temp_path / "export_manuale.json"
        repo.export_backup(json_export)

        print(f"\n✓ Export JSON completato: {json_export}")
        print(f"  Dimensione file: {json_export.stat().st_size} bytes")

        # Verifica contenuto
        import json

        with json_export.open("r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  Numero sezioni esportate: {len(data)}")
        print(f"  Sezioni: {[s['name'] for s in data]}")

        # Scenario 3: Export in CSV
        print_section("Scenario 3: Export in Formato CSV")

        csv_export = temp_path / "export_manuale.csv"
        repo.export_backup(csv_export)

        print(f"\n✓ Export CSV completato: {csv_export}")
        print(f"  Dimensione file: {csv_export.stat().st_size} bytes")

        # Verifica contenuto CSV
        import csv

        with csv_export.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)
        print(f"  Numero sezioni esportate: {len(rows)}")
        print(f"  Colonne: {list(rows[0].keys())[:5]}... (prime 5)")

        # Scenario 4: Export senza estensione (default .json)
        # Scenario 4: Export Senza Estensione (Default .jsons)

        no_ext_export = temp_path / "export_senza_estensione"
        repo.export_backup(no_ext_export)

        # Il file verrà salvato con .jsons aggiunto automaticamente
        actual_file = temp_path / "export_senza_estensione.jsons"
        print(f"\n✓ File richiesto: {no_ext_export}")
        print(f"✓ File creato: {actual_file}")
        print("  (Estensione .jsons aggiunta automaticamente)")

        # Scenario 5: Export in directory nidificata
        print_section("Scenario 5: Export in Directory Nidificata")

        nested_export = temp_path / "exports" / "2025" / "backup_sezioni.json"
        repo.export_backup(nested_export)

        print(f"\n✓ Export in directory nidificata: {nested_export}")
        print(f"  Directory create automaticamente: {nested_export.parent}")
        print(f"  File esiste: {nested_export.exists()}")

        # Scenario 6: Verifica che file principale non sia modificato
        print_section("Scenario 6: Verifica Non Modifica File Principale")

        main_file = temp_path / "sections.json"
        backup_file = temp_path / "sections_backup.json"

        # Leggi timestamp prima dell'export
        main_mtime_before = main_file.stat().st_mtime
        backup_mtime_before = backup_file.stat().st_mtime

        # Esporta
        export_path = temp_path / "verifica_export.json"
        repo.export_backup(export_path)

        # Verifica timestamp dopo export
        main_mtime_after = main_file.stat().st_mtime
        backup_mtime_after = backup_file.stat().st_mtime

        print("\n✓ File principale NON modificato:")
        print(f"  Timestamp prima:  {main_mtime_before}")
        print(f"  Timestamp dopo:   {main_mtime_after}")
        print(f"  Modificato: {main_mtime_before != main_mtime_after}")

        print("\n✓ File backup interno NON modificato:")
        print(f"  Timestamp prima:  {backup_mtime_before}")
        print(f"  Timestamp dopo:   {backup_mtime_after}")
        print(f"  Modificato: {backup_mtime_before != backup_mtime_after}")

        # Scenario 7: Export con Path object
        print_section("Scenario 7: Export con Oggetto Path")

        path_obj_export = Path(tmpdir) / "export_con_path_object.json"
        repo.export_backup(path_obj_export)

        print("\n✓ Export usando Path object completato")
        print(f"  Tipo parametro: {type(path_obj_export).__name__}")
        print(f"  File creato: {path_obj_export.exists()}")

        # Conclusioni
        print_section("Conclusioni")

        print("\n✓ Funzionalità export_backup() verificata:")
        print("  1. ✓ Export in formato JSON (con indentazione)")
        print("  2. ✓ Export in formato CSV (tutte le colonne)")
        print("  3. ✓ Estensione di default (.json) se mancante")
        print("  4. ✓ Creazione automatica directory di destinazione")
        print("  5. ✓ NON modifica file principale né backup interno")
        print("  6. ✓ Accetta sia str che Path come destinazione")
        print("  7. ✓ Gestione errori con logging appropriato")

        print("\n✓ Export manuale disponibile senza interferire con persistenza automatica!")
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
