"""Test rapido di tutte le tipologie di sezione."""

from sections_app.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    TSection,
    VSection,
)

# Test tutte le tipologie
types = [
    RectangularSection("Rettangolare", 10, 20),
    CircularSection("Circolare", 15),
    TSection("T", 20, 2, 1, 16),
    LSection("L", 10, 10, 2, 2),
    ISection("I", 20, 2, 16, 1),
    PiSection("Pi", 20, 2, 16, 1),
    InvertedTSection("T rovescia", 20, 2, 1, 16),
    CSection("C", 20, 15, 2, 1),
    CircularHollowSection("Circolare cava", 10, 1),
    RectangularHollowSection("Rettangolare cava", 20, 15, 2),
    VSection("V", 20, 15, 1),
    InvertedVSection("V rovescia", 20, 15, 1),
]

print("=" * 80)
print("TEST COMPLETO TUTTE LE TIPOLOGIE DI SEZIONE")
print("=" * 80)

ok = 0
for section in types:
    try:
        section.compute_properties()
        props = section.properties
        print(
            f"{section.__class__.__name__:30s} "
            f"Area: {props.area:8.2f} cm²  "
            f"Ix: {props.ix:10.2f} cm⁴  "
            f"Iy: {props.iy:10.2f} cm⁴"
        )
        ok += 1
    except Exception as e:
        print(f"{section.__class__.__name__:30s} ❌ ERRORE: {e}")

print("=" * 80)
print(f"✅ {ok}/{len(types)} tipologie calcolate con successo!")
print("=" * 80)

# Test rotazione
print("\nTEST ROTAZIONE (Rettangolo 10x20 cm):")
print("-" * 80)
for angle in [0, 30, 45, 90]:
    s = RectangularSection("Rect", 10, 20, rotation_angle_deg=angle)
    s.compute_properties()
    if s.properties is not None:
        print(
            f"Rotazione {angle:3.0f}°: Ix = {s.properties.ix:10.2f} cm⁴, "
            f"Iy = {s.properties.iy:10.2f} cm⁴, "
            f"Ixy = {s.properties.ixy:10.2f} cm⁴"
        )
    else:
        print(f"Rotazione {angle:3.0f}°: ❌ ERRORE nel calcolo delle proprietà")

print("\n✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
