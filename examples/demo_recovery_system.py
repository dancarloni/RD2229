"""Demo Sistema Recovery Automatico
=================================

Dimostra il funzionamento del sistema di recovery automatico a 3 livelli:
1. Tentativo di caricamento dal file principale
2. Se fallisce, caricamento dal backup
3. Se entrambi falliscono, inizializzazione archivio vuoto

Autore: Sistema automatico
Data: 2025
"""

import json
import tempfile
from pathlib import Path

from core_models.materials import Material, MaterialRepository
from sections_app.services.repository import SectionRepository


def print_section(title: str):
    """Stampa una sezione formattata."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def scenario_1_normal_load():
    """Scenario 1: Caricamento normale dal file principale."""
    print_section("SCENARIO 1: Caricamento Normale dal File Principale")

    with tempfile.TemporaryDirectory() as tmpdir:
        sections_file = Path(tmpdir) / "sections.json"

        # Crea file principale valido
        test_data = [
            {
                "id": "RECT-001",
                "section_type": "RECTANGULAR",
                "name": "Rettangolo Standard",
                "width": 300,
                "height": 500,
            }
        ]
        sections_file.write_text(json.dumps(test_data, indent=2), encoding="utf-8")

        # Carica repository
        repo = SectionRepository(json_file=str(sections_file))
        repo.load_from_file()

        # Verifica risultati
        sections = repo.get_all_sections()
        print("\n✓ File principale caricato correttamente")
        print(f"  - Numero sezioni caricate: {len(sections)}")
        print(f"  - Sezione: {sections[0].name}")
        print(f"  - Dimensioni: {sections[0].width}x{sections[0].height} mm")


def scenario_2_recover_from_backup():
    """Scenario 2: Recovery dal backup quando il file principale è corrotto."""
    print_section("SCENARIO 2: Recovery dal Backup (File Principale Corrotto)")

    with tempfile.TemporaryDirectory() as tmpdir:
        sections_file = Path(tmpdir) / "sections.json"
        backup_file = Path(tmpdir) / "sections_backup.json"

        # Crea file principale CORROTTO
        sections_file.write_text("{ invalid json", encoding="utf-8")
        print(f"\n⚠ File principale corrotto: {sections_file}")

        # Crea backup VALIDO
        backup_data = [
            {
                "id": "RECT-002",
                "section_type": "RECTANGULAR",
                "name": "Sezione da Backup",
                "width": 400,
                "height": 600,
            }
        ]
        backup_file.write_text(json.dumps(backup_data, indent=2), encoding="utf-8")
        print(f"✓ File backup valido: {backup_file}")

        # Carica repository (dovrebbe caricare dal backup)
        repo = SectionRepository(json_file=str(sections_file))
        repo.load_from_file()

        # Verifica risultati
        sections = repo.get_all_sections()
        print("\n✓ Recovery dal backup completato con successo!")
        print(f"  - Numero sezioni recuperate: {len(sections)}")
        print(f"  - Sezione: {sections[0].name}")
        print(f"  - Dimensioni: {sections[0].width}x{sections[0].height} mm")
        print("\n📝 NOTA: L'applicazione NON è andata in crash!")


def scenario_3_both_corrupted():
    """Scenario 3: Entrambi i file corrotti - inizializzazione archivio vuoto."""
    print_section("SCENARIO 3: Archivio Vuoto (Entrambi i File Corrotti)")

    with tempfile.TemporaryDirectory() as tmpdir:
        sections_file = Path(tmpdir) / "sections.json"
        backup_file = Path(tmpdir) / "sections_backup.json"

        # Crea entrambi i file CORROTTI
        sections_file.write_text("{ invalid", encoding="utf-8")
        backup_file.write_text("{ also bad }", encoding="utf-8")
        print(f"\n⚠ File principale corrotto: {sections_file}")
        print(f"⚠ File backup corrotto: {backup_file}")

        # Carica repository (dovrebbe inizializzare vuoto)
        repo = SectionRepository(json_file=str(sections_file))
        repo.load_from_file()

        # Verifica risultati
        sections = repo.get_all_sections()
        print("\n✓ Inizializzato archivio vuoto (graceful degradation)")
        print(f"  - Numero sezioni: {len(sections)}")
        print("\n📝 NOTA: L'applicazione è ancora funzionante e pronta per nuovi dati!")


def scenario_4_save_after_recovery():
    """Scenario 4: Salvataggio dopo recovery - il sistema torna operativo."""
    print_section("SCENARIO 4: Salvataggio Dopo Recovery")

    with tempfile.TemporaryDirectory() as tmpdir:
        materials_file = Path(tmpdir) / "materials.json"
        backup_file = Path(tmpdir) / "materials_backup.json"

        # Crea file principale CORROTTO
        materials_file.write_text("corrupted", encoding="utf-8")
        print(f"\n⚠ File principale corrotto: {materials_file}")

        # Crea backup VALIDO
        backup_data = [
            {
                "id": "C25/30",
                "name": "Calcestruzzo C25/30",
                "type": "concrete",
                "properties": {"fck": 25.0},
            }
        ]
        backup_file.write_text(json.dumps(backup_data, indent=2), encoding="utf-8")
        print(f"✓ File backup valido: {backup_file}")

        # Carica repository (dovrebbe caricare dal backup)
        repo = MaterialRepository(json_file=str(materials_file))
        repo.load_from_file()

        print("\n✓ Recovery completato dal backup")
        print(f"  - Materiali recuperati: {len(repo.get_all())}")

        # Aggiungi un nuovo materiale
        new_concrete = Material(
            id="C30/37", name="Calcestruzzo C30/37", type="concrete", properties={"fck": 30.0}
        )
        repo.add(new_concrete)

        print(f"\n✓ Aggiunto nuovo materiale: {new_concrete.name}")
        print(f"  - Totale materiali: {len(repo.get_all())}")

        # Salva (dovrebbe creare backup del vecchio backup e scrivere nuovo file)
        repo.save_to_file()

        # Verifica che il nuovo file sia stato scritto correttamente
        with materials_file.open("r", encoding="utf-8") as f:
            saved_data = json.load(f)

        print("\n✓ File principale salvato correttamente")
        print(f"  - Materiali nel file: {len(saved_data)}")
        print(f"  - File backup creato: {backup_file.exists()}")
        print("\n📝 NOTA: Il sistema è tornato completamente operativo!")


def main():
    """Esegue tutti gli scenari di demo."""
    print("\n" + "=" * 70)
    print("=" + " " * 68 + "=")
    print("=" + "  DEMO SISTEMA RECOVERY AUTOMATICO - 3 LIVELLI DI FALLBACK  ".center(68) + "=")
    print("=" + " " * 68 + "=")
    print("=" * 70)

    print("\nQuesto demo mostra come il sistema di recovery automatico gestisce")
    print("file corrotti o mancanti senza mandare in crash l'applicazione.\n")

    input("Premi INVIO per iniziare...")

    # Esegui tutti gli scenari
    scenario_1_normal_load()
    input("\nPremi INVIO per continuare con lo Scenario 2...")

    scenario_2_recover_from_backup()
    input("\nPremi INVIO per continuare con lo Scenario 3...")

    scenario_3_both_corrupted()
    input("\nPremi INVIO per continuare con lo Scenario 4...")

    scenario_4_save_after_recovery()

    print_section("CONCLUSIONI")
    print("\n✓ Il sistema di recovery automatico funziona correttamente:")
    print("  1. ✓ Carica dal file principale se disponibile")
    print("  2. ✓ Recupera dal backup se il principale è corrotto")
    print("  3. ✓ Inizializza archivio vuoto se entrambi sono corrotti")
    print("  4. ✓ Permette salvataggio dopo recovery")
    print("\n✓ L'applicazione NON va mai in crash, anche con file corrotti!")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
