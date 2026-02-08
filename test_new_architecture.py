#!/usr/bin/env python3
"""Test semplice della nuova architettura delle sezioni."""

import os
import sys

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sections_app.domain import CircularSection, RectangularSection
from sections_app.io import create_section_from_dict


def test_rectangular_section():
    """Test sezione rettangolare."""
    print("Testing RectangularSection...")

    # Crea sezione
    section = RectangularSection(
        section_id="test_rect",
        name="Test Rectangle",
        dimensions={"width": 10.0, "height": 20.0},
        rotation_angle_deg=0.0,
        note="Test section"
    )

    print(f"ID: {section.id}")
    print(f"Name: {section.name}")
    print(f"Type: {section.section_type}")
    print(f"Area: {section.properties.area}")
    print(f"Centroid: ({section.properties.x_g}, {section.properties.y_g})")
    print(f"Ix: {section.properties.Ix}")
    print(f"Iy: {section.properties.Iy}")
    print("✓ RectangularSection OK\n")

def test_circular_section():
    """Test sezione circolare."""
    print("Testing CircularSection...")

    section = CircularSection(
        section_id="test_circ",
        name="Test Circle",
        dimensions={"diameter": 15.0},
        rotation_angle_deg=0.0,
        note="Test circular section"
    )

    print(f"ID: {section.id}")
    print(f"Name: {section.name}")
    print(f"Type: {section.section_type}")
    print(f"Area: {section.properties.area:.2f}")
    print(f"Centroid: ({section.properties.x_g:.2f}, {section.properties.y_g:.2f})")
    print(f"Ix: {section.properties.Ix:.2f}")
    print(f"Iy: {section.properties.Iy:.2f}")
    print("✓ CircularSection OK\n")

def test_csv_factory():
    """Test factory da dizionario CSV."""
    print("Testing CSV factory...")

    data = {
        "id": "csv_test",
        "name": "CSV Test Section",
        "section_type": "RECTANGULAR",
        "width": "12.5",
        "height": "25.0",
        "rotation_angle_deg": "30",
        "note": "From CSV"
    }

    section = create_section_from_dict(data)

    print(f"ID: {section.id}")
    print(f"Name: {section.name}")
    print(f"Type: {section.section_type}")
    print(f"Dimensions: {section.dimensions}")
    print(f"Rotation: {section.rotation_angle_deg}°")
    print("✓ CSV Factory OK\n")

if __name__ == "__main__":
    print("=== Testing New Sections Architecture ===\n")

    try:
        test_rectangular_section()
        test_circular_section()
        test_csv_factory()

        print("🎉 All tests passed! New architecture is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
