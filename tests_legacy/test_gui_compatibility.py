#!/usr/bin/env python3
"""Test di compatibilità: verifica che il codice GUI continua a funzionare."""

import os
import sys
import tempfile

from sections_app.models.sections import CircularSection, RectangularSection
from sections_app.services.repository import CsvSectionSerializer, SectionRepository


def test_gui_compatibility():
    """Test: verifica che il repository funziona come prima dalla GUI."""
    print("=" * 70)
    print("TEST: Compatibilità con codice GUI")
    print("=" * 70)

    # Simula l'inizializzazione della GUI (come in sections_app/app.py)
    print("\n[1] Inizializzazione repository (come in GUI)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Cambia directory di lavoro per simulare l'ambiente reale
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Questo è il codice esatto da sections_app/app.py
            repository = SectionRepository(
                "sections.json"
            )  # Usa file sections.json nella cartella corrente
            serializer = CsvSectionSerializer()

            print("  ✓ Repository inizializzato")
            print("  ✓ Serializer inizializzato")
            print(f"  ✓ Cartella di lavoro: {os.getcwd()}")

            # Aggiungi sezioni (come dall'interfaccia GUI)
            print("\n[2] Aggiunta sezioni via GUI...")

            # Simula click su "Nuovo > Rettangolare"
            section1 = RectangularSection(name="Test Rectangle", width=30, height=40)
            result1 = repository.add_section(section1)
            assert result1, "Aggiunta sezione 1 fallita"
            print("  ✓ Sezione 1 aggiunta (via GUI)")

            # Simula click su "Nuovo > Circolare"
            section2 = CircularSection(name="Test Circle", diameter=50)
            result2 = repository.add_section(section2)
            assert result2, "Aggiunta sezione 2 fallita"
            print("  ✓ Sezione 2 aggiunta (via GUI)")

            # Verifica che il file JSON sia stato creato
            assert os.path.isfile("sections.json"), "File sections.json non creato"
            print("  ✓ File sections.json creato automaticamente")

            # Simula export CSV (click su "Esporta CSV")
            print("\n[3] Export CSV (da GUI)...")
            serializer.export_to_csv("sections.csv", repository.get_all_sections())
            assert os.path.isfile("sections.csv"), "CSV non creato"
            print("  ✓ Esportato in sections.csv")

            # Crea nuovo repository (simula riavvio applicazione)
            print("\n[4] Riavvio applicazione (nuovo repository)...")
            repository2 = SectionRepository("sections.json")
            loaded_sections = repository2.get_all_sections()
            assert len(loaded_sections) == 2, f"Caricate {len(loaded_sections)} sezioni, attese 2"
            print(f"  ✓ Caricate {len(loaded_sections)} sezioni dal file JSON")

            for section in loaded_sections:
                print(f"    - {section.name}")

            # Modifica una sezione (simula click su "Modifica")
            print("\n[5] Modifica sezione (da GUI)...")
            section1_modified = RectangularSection(
                name="Test Rectangle Modified", width=35, height=45
            )
            repository2.update_section(loaded_sections[0].id, section1_modified)
            print("  ✓ Sezione modificata")

            # Verifica persistenza della modifica
            repository3 = SectionRepository("sections.json")
            final_sections = repository3.get_all_sections()
            modified_section = next((s for s in final_sections if "Modified" in s.name), None)
            assert modified_section is not None, "Modifica non persistita"
            print("  ✓ Modifiche persistite nel file JSON")

            # Elimina una sezione (simula click su "Elimina")
            print("\n[6] Eliminazione sezione (da GUI)...")
            section_to_delete = final_sections[1]
            repository3.delete_section(section_to_delete.id)
            print("  ✓ Sezione eliminata")

            # Verifica persistenza dell'eliminazione
            repository4 = SectionRepository("sections.json")
            final_count = len(repository4.get_all_sections())
            assert final_count == 1, f"Rimaste {final_count} sezioni, attesa 1"
            print("  ✓ Eliminazione persistita nel file JSON")

        finally:
            os.chdir(original_cwd)

    print("\n✅ TEST COMPATIBILITÀ GUI PASSATO\n")


if __name__ == "__main__":
    try:
        test_gui_compatibility()
        print("\n✅ COMPATIBILITÀ GUI VERIFICATA!")
        print("\nIl codice GUI continua a funzionare esattamente come prima,")
        print("ma ora con persistenza automatica su file JSON.")
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
