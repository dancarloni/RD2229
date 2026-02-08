#!/usr/bin/env python3
"""Test di integrazione: verifica persistenza con GUI."""

import os
import tempfile

from sections_app.models.sections import (
    CircularSection,
    RectangularSection,
    TSection,
)
from sections_app.services.repository import CsvSectionSerializer, SectionRepository


def test_integration_with_csv_serializer():
    """Test: persistenza JSON e export/import CSV."""
    print("=" * 70)
    print("TEST: Integrazione JSON + CSV")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "sections.json")
        csv_file = os.path.join(tmpdir, "sections.csv")

        # FASE 1: Crea sezioni e salva in JSON
        print("\n[1] Creazione sezioni e salvataggio JSON...")
        repo1 = SectionRepository(json_file=json_file)

        rect = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
        circ = CircularSection(name="Circolare d=25", diameter=25)
        t_sec = TSection(
            name="Sezione a T",
            flange_width=40,
            flange_thickness=5,
            web_thickness=8,
            web_height=25,
        )

        for section in [rect, circ, t_sec]:
            repo1.add_section(section)
            print(f"  ✓ Aggiunta: {section.name}")

        assert os.path.isfile(json_file), "JSON non creato"
        print(f"  ✓ JSON salvato: {json_file}")

        # FASE 2: Esporta in CSV
        print("\n[2] Export CSV...")
        serializer = CsvSectionSerializer()
        serializer.export_to_csv(csv_file, repo1.get_all_sections())

        assert os.path.isfile(csv_file), "CSV non creato"
        print(f"  ✓ CSV esportato: {csv_file}")

        # FASE 3: Carica JSON in nuovo repository
        print("\n[3] Caricamento JSON...")
        repo2 = SectionRepository(json_file=json_file)
        loaded = repo2.get_all_sections()
        assert len(loaded) == 3, f"Caricate {len(loaded)} sezioni, attese 3"
        print(f"  ✓ Caricate {len(loaded)} sezioni da JSON")

        # FASE 4: Import CSV e salva in JSON diverso
        print("\n[4] Import CSV e salvataggio in nuovo JSON...")
        json_file2 = os.path.join(tmpdir, "sections2.json")
        repo3 = SectionRepository(json_file=json_file2)

        imported = serializer.import_from_csv(csv_file)
        for section in imported:
            repo3.add_section(section)

        assert len(repo3.get_all_sections()) == 3, "Sezioni non importate"
        print("  ✓ Importate 3 sezioni da CSV e salvate in JSON")

        # FASE 5: Verifica che i due JSON siano equivalenti
        print("\n[5] Verifica equivalenza JSON...")
        repo4 = SectionRepository(json_file=json_file)
        repo5 = SectionRepository(json_file=json_file2)

        sections4 = sorted(repo4.get_all_sections(), key=lambda s: s.name)
        sections5 = sorted(repo5.get_all_sections(), key=lambda s: s.name)

        for s4, s5 in zip(sections4, sections5):
            assert s4.name == s5.name, f"Nome diverso: {s4.name} vs {s5.name}"
            assert s4.section_type == s5.section_type, "Type diverso"
            print(f"  ✓ {s4.name}: equivalente")

    print("\n✅ TEST INTEGRAZIONE PASSATO\n")


def test_concurrent_repositories():
    """Test: più repository su file diversi."""
    print("=" * 70)
    print("TEST: Repository multipli")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        json1 = os.path.join(tmpdir, "sections1.json")
        json2 = os.path.join(tmpdir, "sections2.json")

        print("\n[1] Creazione due repository su file diversi...")
        repo1 = SectionRepository(json_file=json1)
        repo2 = SectionRepository(json_file=json2)

        # Aggiungi sezioni diverse a ogni repository
        print("\n[2] Aggiunta sezioni...")
        rect1 = RectangularSection(name="Rect1", width=10, height=20)
        rect2 = RectangularSection(name="Rect2", width=15, height=25)

        repo1.add_section(rect1)
        repo2.add_section(rect2)
        print(f"  ✓ Repo1: {len(repo1.get_all_sections())} sezione/i")
        print(f"  ✓ Repo2: {len(repo2.get_all_sections())} sezione/i")

        # Verifica che i file siano diversi
        print("\n[3] Verifica indipendenza dei repository...")
        repo1_loaded = SectionRepository(json_file=json1)
        repo2_loaded = SectionRepository(json_file=json2)

        assert len(repo1_loaded.get_all_sections()) == 1, "Repo1 non caricato correttamente"
        assert len(repo2_loaded.get_all_sections()) == 1, "Repo2 non caricato correttamente"

        s1 = repo1_loaded.get_all_sections()[0]
        s2 = repo2_loaded.get_all_sections()[0]

        assert s1.name == "Rect1", f"Nome errato repo1: {s1.name}"
        assert s2.name == "Rect2", f"Nome errato repo2: {s2.name}"

        print(f"  ✓ Repo1 isolato: {s1.name}")
        print(f"  ✓ Repo2 isolato: {s2.name}")

    print("\n✅ TEST REPOSITORY MULTIPLI PASSATO\n")


def test_large_dataset():
    """Test: persistenza con molte sezioni."""
    print("=" * 70)
    print("TEST: Dataset grande (100 sezioni)")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "large.json")

        print("\n[1] Creazione 100 sezioni...")
        repo1 = SectionRepository(json_file=json_file)

        for i in range(100):
            if i % 3 == 0:
                section = RectangularSection(name=f"Rect_{i}", width=10 + i, height=20 + i)
            elif i % 3 == 1:
                section = CircularSection(name=f"Circ_{i}", diameter=20 + i)
            else:
                section = TSection(
                    name=f"T_{i}",
                    flange_width=30 + i,
                    flange_thickness=5,
                    web_thickness=8,
                    web_height=25,
                )
            repo1.add_section(section)
            if (i + 1) % 25 == 0:
                print(f"  ✓ Aggiunte {i+1}/100 sezioni")

        assert len(repo1.get_all_sections()) == 100, "Sezioni non aggiunte"
        print("  ✓ Tutte 100 sezioni aggiunte e salvate")

        # Carica in nuovo repository
        print("\n[2] Caricamento 100 sezioni...")
        repo2 = SectionRepository(json_file=json_file)
        loaded = repo2.get_all_sections()

        assert len(loaded) == 100, f"Caricate {len(loaded)} sezioni, attese 100"
        print("  ✓ Caricate 100 sezioni da file JSON")

        # Modifica 10 sezioni (con dimensioni diverse per evitare conflitti)
        print("\n[3] Modifica 10 sezioni...")
        for i in range(10):
            section = loaded[i]
            # Usa dimensioni uniche basate su i per evitare duplicati
            width = 100 + i * 10
            height = 200 + i * 10
            modified = RectangularSection(
                name=f"{section.name}_modified", width=width, height=height
            )
            repo2.update_section(section.id, modified)
        print("  ✓ Modificate 10 sezioni e salvate")

        # Carica di nuovo
        print("\n[4] Verifica modifiche...")
        repo3 = SectionRepository(json_file=json_file)
        final = repo3.get_all_sections()

        modified_sections = [s for s in final if s.name.endswith("_modified")]
        assert (
            len(modified_sections) == 10
        ), f"Modificate {len(modified_sections)} sezioni, attese 10"
        print("  ✓ Verificate 10 sezioni modificate")

    print("\n✅ TEST DATASET GRANDE PASSATO\n")


if __name__ == "__main__":
    try:
        test_integration_with_csv_serializer()
        test_concurrent_repositories()
        test_large_dataset()
        print("\n✅ TUTTI I TEST DI INTEGRAZIONE PASSATI!")
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE in test suite: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
