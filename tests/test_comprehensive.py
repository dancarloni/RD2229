#!/usr/bin/env python3
"""Test completo della nuova architettura delle sezioni."""

import os
import sys
import tempfile

import pytest

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sections_app.domain import (
    CircularHollowSection,
    CircularSection,
    ISection,
    LSection,
    RectangularHollowSection,
    RectangularSection,
    TSection,
)
from sections_app.io import export_sections_to_csv, import_sections_from_csv


@pytest.fixture
def sections():
    """Fixture che fornisce una lista di sezioni di test."""
    return test_all_section_types()


def test_all_section_types():
    """Test di creazione di tutti i tipi di sezione."""
    print("Testing all section types...")

    sections = []

    # Rettangolare
    rect = RectangularSection(
        section_id="rect1", name="Rectangle 10x20", dimensions={"width": 10.0, "height": 20.0}
    )
    sections.append(rect)
    print(f"✓ Rectangular: Area={rect.properties.area}")

    # Circolare
    circ = CircularSection(section_id="circ1", name="Circle D=15", dimensions={"diameter": 15.0})
    sections.append(circ)
    print(f"✓ Circular: Area={circ.properties.area:.1f}")

    # T
    t_sec = TSection(
        section_id="t1",
        name="T Section",
        dimensions={
            "flange_width": 20.0,
            "flange_thickness": 2.0,
            "web_thickness": 1.5,
            "web_height": 15.0,
        },
    )
    sections.append(t_sec)
    print(f"✓ T-Section: Area={t_sec.properties.area:.1f}")

    # L
    l_sec = LSection(
        section_id="l1",
        name="L Section",
        dimensions={"width": 10.0, "height": 15.0, "t_horizontal": 2.0, "t_vertical": 1.5},
    )
    sections.append(l_sec)
    print(f"✓ L-Section: Area={l_sec.properties.area:.1f}")

    # I
    i_sec = ISection(
        section_id="i1",
        name="I Section",
        dimensions={
            "flange_width": 15.0,
            "flange_thickness": 2.0,
            "web_height": 10.0,
            "web_thickness": 1.0,
        },
    )
    sections.append(i_sec)
    print(f"✓ I-Section: Area={i_sec.properties.area:.1f}")

    # Circolare cava
    circ_h = CircularHollowSection(
        section_id="ch1",
        name="Hollow Circle",
        dimensions={"outer_diameter": 20.0, "thickness": 2.0},
    )
    sections.append(circ_h)
    print(f"✓ Circular Hollow: Area={circ_h.properties.area:.1f}")

    # Rettangolare cava
    rect_h = RectangularHollowSection(
        section_id="rh1",
        name="Hollow Rectangle",
        dimensions={"width": 12.0, "height": 8.0, "thickness": 1.5},
    )
    sections.append(rect_h)
    print(f"✓ Rectangular Hollow: Area={rect_h.properties.area:.1f}")

    return sections


def test_csv_roundtrip(sections):
    """Test esportazione e importazione CSV."""
    print("\nTesting CSV export/import roundtrip...")

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Esporta
        export_sections_to_csv(sections, tmp_path)
        print(f"✓ Exported {len(sections)} sections to CSV")

        # Importa
        imported_sections = import_sections_from_csv(tmp_path)
        print(f"✓ Imported {len(imported_sections)} sections from CSV")

        # Verifica
        assert len(imported_sections) == len(sections), "Different number of sections"

        for orig, imp in zip(sections, imported_sections):
            assert (
                orig.section_type == imp.section_type
            ), f"Type mismatch: {orig.section_type} vs {imp.section_type}"
            assert (
                abs(orig.properties.area - imp.properties.area) < 1e-6
            ), f"Area mismatch for {orig.section_type}"
            assert (
                abs(orig.properties.Ix - imp.properties.Ix) < 1e-3
            ), f"Ix mismatch for {orig.section_type}"

        print("✓ All sections match after roundtrip")

    finally:
        os.unlink(tmp_path)


def test_area_calculations(sections):
    """Test calcoli area shear."""
    print("\nTesting area calculations...")

    for section in sections:
        kappa_y, kappa_z = section.get_default_shear_kappas()
        assert kappa_y > 0 and kappa_z > 0, f"Invalid shear factors for {section.section_type}"

        # Verifica che le aree shear siano calcolate
        assert section.properties.A_y > 0, f"A_y not calculated for {section.section_type}"
        assert section.properties.A_z > 0, f"A_z not calculated for {section.section_type}"

        print(f"✓ {section.section_type}: kappa_y={kappa_y:.3f}, kappa_z={kappa_z:.3f}")


if __name__ == "__main__":
    print("=== Comprehensive Test of New Sections Architecture ===\n")

    try:
        # Test creazione sezioni
        sections = test_all_section_types()

        # Test CSV
        test_csv_roundtrip(sections)

        # Test shear
        test_area_calculations(sections)

        print("\n🎉 All comprehensive tests passed!")
        print("✅ Modular architecture successfully implemented")
        print("✅ All section types working")
        print("✅ CSV import/export functional")
        print("✅ Shear calculations operational")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
