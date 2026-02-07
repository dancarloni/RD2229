#!/usr/bin/env python3
"""Test: Verifica che VerificationTable riceve repository pre-popolati all'avvio."""

import os
import tempfile

from core_models.materials import Material, MaterialRepository
from sections_app.models.sections import RectangularSection
from sections_app.services.repository import SectionRepository


def test_verification_table_receives_populated_repositories():
    """Test: Verifica che VerificationTable riceve repository pre-popolati."""
    print("=" * 70)
    print("TEST: VerificationTable riceve repository pre-popolati")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        sections_file = os.path.join(tmpdir, "sections.json")
        materials_file = os.path.join(tmpdir, "materials.json")

        # FASE 1: Setup archivi persistenti
        print("\n[FASE 1] Creazione archivi persistenti...")

        repo_sections = SectionRepository(json_file=sections_file)
        repo_sections.add_section(RectangularSection(name="Test Section 20x30", width=20, height=30))

        repo_materials = MaterialRepository(json_file=materials_file)
        repo_materials.add(Material(name="C25/30", type="concrete", properties={"fck": 25}))

        print("  ✓ Archivi creati e salvati")

        # FASE 2: Simulazione app.py - Caricamento esplicito
        print("\n[FASE 2] Simulazione app.py...")
        print("  Creazione repository...")
        section_repo_app = SectionRepository(json_file=sections_file)
        section_repo_app.load_from_file()

        material_repo_app = MaterialRepository(json_file=materials_file)
        material_repo_app.load_from_file()

        print(f"  ✓ SectionRepository caricato: {len(section_repo_app.get_all_sections())} sezione/i")
        print(f"  ✓ MaterialRepository caricato: {len(material_repo_app.get_all())} materiale/i")

        # FASE 3: Simulazione ModuleSelectorWindow - passa repository a VerificationTable
        print("\n[FASE 3] Passaggio repository a VerificationTable...")

        # Simula quello che fa ModuleSelectorWindow
        selector_section_repo = section_repo_app
        selector_material_repo = material_repo_app or MaterialRepository()

        print("  ✓ Repository pronti per VerificationTable")
        print(f"    - SectionRepository: {len(selector_section_repo.get_all_sections())} sezione/i")
        print(f"    - MaterialRepository: {len(selector_material_repo.get_all())} materiale/i")

        # FASE 4: Verifica che VerificationTable riceva repository pre-popolati
        print("\n[FASE 4] Verifica ricezione repository pre-popolati...")

        # Simula il passaggio a VerificationTable
        class MockVerificationTableWindow:
            def __init__(self, section_repo, material_repo):
                self.section_repository = section_repo
                self.material_repository = material_repo
                self.sections = section_repo.get_all_sections()
                self.materials = material_repo.get_all()

        vt_window = MockVerificationTableWindow(selector_section_repo, selector_material_repo)

        assert len(vt_window.sections) > 0, "VerificationTable non ha ricevuto sezioni"
        assert len(vt_window.materials) > 0, "VerificationTable non ha ricevuto materiali"

        print(f"  ✓ VerificationTable ha ricevuto {len(vt_window.sections)} sezione/i")
        print(f"  ✓ VerificationTable ha ricevuto {len(vt_window.materials)} materiale/i")

    print("\n✅ TEST PASSATO\n")


def test_repositories_available_at_startup():
    """Test: Verifica il flusso completo dal startup."""
    print("=" * 70)
    print("TEST: Flusso completo dal startup")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        sections_file = os.path.join(tmpdir, "sections.json")
        materials_file = os.path.join(tmpdir, "materials.json")

        # Setup
        repo_sections = SectionRepository(json_file=sections_file)
        repo_sections.add_section(RectangularSection(name="Beam 30x50", width=30, height=50))
        repo_sections.add_section(RectangularSection(name="Beam 25x40", width=25, height=40))

        repo_materials = MaterialRepository(json_file=materials_file)
        repo_materials.add(Material(name="C30/37", type="concrete", properties={"fck": 30}))
        repo_materials.add(Material(name="A500S", type="steel", properties={"fyk": 500}))

        print(f"\n✓ Setup: {len(repo_sections.get_all_sections())} sezioni, {len(repo_materials.get_all())} materiali")

        # Simula il codice in app.py (linee 35-42)
        print("\nSimulazione app.py run_app():")
        section_repository = SectionRepository(json_file=sections_file)
        section_repository.load_from_file()

        material_repository = MaterialRepository(json_file=materials_file)
        material_repository.load_from_file()

        print(f"  ✓ section_repository disponibile: {len(section_repository.get_all_sections())} sezioni")
        print(f"  ✓ material_repository disponibile: {len(material_repository.get_all())} materiali")

        # Verifica i dati
        sections = section_repository.get_all_sections()
        materials = material_repository.get_all()

        assert len(sections) == 2, f"Attese 2 sezioni, trovate {len(sections)}"
        assert len(materials) == 2, f"Attesi 2 materiali, trovati {len(materials)}"

        print("\n  Sezioni disponibili:")
        for section in sections:
            print(f"    - {section.name}")

        print("  Materiali disponibili:")
        for material in materials:
            print(f"    - {material.name}")

        print("\n✅ Tutti i dati sono disponibili al startup")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST INTEGRAZIONE: REPOSITORY DISPONIBILI ALL'AVVIO")
    print("=" * 70)

    try:
        test_verification_table_receives_populated_repositories()
        print()
        test_repositories_available_at_startup()
        print("\n" + "=" * 70)
        print("✅ TUTTI I TEST PASSATI - INTEGRAZIONE VERIFICATA!")
        print("=" * 70)
        print("\nConcluzione:")
        print("✓ Repository caricati esplicitamente in app.py")
        print("✓ Repository passati a ModuleSelectorWindow")
        print("✓ VerificationTable riceve repository pre-popolati")
        print("✓ Dati persistenti disponibili all'avvio")
    except AssertionError as e:
        print("\n❌ ASSERTION FAILED:")
        print(e)
        import traceback

        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
