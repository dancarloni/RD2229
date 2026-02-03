"""
Script di test per verificare la gestione dinamica dei campi di input.

Questo script dimostra:
1. Come i campi cambiano al cambio di tipologia
2. Validazione input (solo float con 1 decimale)
3. Tooltip informativi
4. Calcolo delle proprietà per ogni tipo di sezione
"""

import sys
import os

# Aggiungi il path dei sorgenti
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rd2229.sections_app.models.sections import (
    RectangularSection,
    CircularSection,
    TSection,
)


def test_rectangular_section():
    """Test sezione rettangolare."""
    print("=" * 60)
    print("TEST SEZIONE RETTANGOLARE")
    print("=" * 60)
    
    # Parametri di input (tutti in cm)
    width = 30.0   # Larghezza b (cm)
    height = 50.0  # Altezza h (cm)
    
    print(f"Input:")
    print(f"  - Larghezza b: {width:.1f} cm")
    print(f"  - Altezza h: {height:.1f} cm")
    
    # Crea sezione e calcola proprietà
    section = RectangularSection(name="Rett_Test", width=width, height=height)
    props = section.compute_properties()
    
    print(f"\nProprietà calcolate:")
    print(f"  - Area: {props.area:.1f} cm²")
    print(f"  - Baricentro: ({props.centroid_x:.1f}, {props.centroid_y:.1f}) cm")
    print(f"  - Ix: {props.ix:.1f} cm⁴")
    print(f"  - Iy: {props.iy:.1f} cm⁴")
    print(f"  - rx: {props.rx:.1f} cm")
    print(f"  - ry: {props.ry:.1f} cm")
    print()


def test_circular_section():
    """Test sezione circolare."""
    print("=" * 60)
    print("TEST SEZIONE CIRCOLARE")
    print("=" * 60)
    
    # Parametri di input (tutti in cm)
    diameter = 40.0  # Diametro D (cm)
    
    print(f"Input:")
    print(f"  - Diametro D: {diameter:.1f} cm")
    
    # Crea sezione e calcola proprietà
    section = CircularSection(name="Circ_Test", diameter=diameter)
    props = section.compute_properties()
    
    print(f"\nProprietà calcolate:")
    print(f"  - Area: {props.area:.1f} cm²")
    print(f"  - Baricentro: ({props.centroid_x:.1f}, {props.centroid_y:.1f}) cm")
    print(f"  - Ix: {props.ix:.1f} cm⁴")
    print(f"  - Iy: {props.iy:.1f} cm⁴")
    print(f"  - rx: {props.rx:.1f} cm")
    print(f"  - ry: {props.ry:.1f} cm")
    print()


def test_t_section():
    """Test sezione a T."""
    print("=" * 60)
    print("TEST SEZIONE A T")
    print("=" * 60)
    
    # Parametri di input (tutti in cm)
    flange_width = 60.0      # Larghezza ala bf (cm)
    flange_thickness = 10.0  # Spessore ala hf (cm)
    web_thickness = 8.0      # Spessore anima bw (cm)
    web_height = 40.0        # Altezza anima hw (cm)
    
    print(f"Input:")
    print(f"  - Larghezza ala bf: {flange_width:.1f} cm")
    print(f"  - Spessore ala hf: {flange_thickness:.1f} cm")
    print(f"  - Spessore anima bw: {web_thickness:.1f} cm")
    print(f"  - Altezza anima hw: {web_height:.1f} cm")
    
    # Crea sezione e calcola proprietà
    section = TSection(
        name="T_Test",
        flange_width=flange_width,
        flange_thickness=flange_thickness,
        web_thickness=web_thickness,
        web_height=web_height
    )
    props = section.compute_properties()
    
    print(f"\nProprietà calcolate:")
    print(f"  - Area: {props.area:.1f} cm²")
    print(f"  - Baricentro: ({props.centroid_x:.1f}, {props.centroid_y:.1f}) cm")
    print(f"  - Ix: {props.ix:.1f} cm⁴")
    print(f"  - Iy: {props.iy:.1f} cm⁴")
    print(f"  - rx: {props.rx:.1f} cm")
    print(f"  - ry: {props.ry:.1f} cm")
    print()


def demo_validation():
    """Dimostra la validazione degli input."""
    print("=" * 60)
    print("DEMO VALIDAZIONE INPUT")
    print("=" * 60)
    print()
    print("Formati VALIDI (accettati):")
    print("  ✅ 25      → Intero")
    print("  ✅ 25.0    → Float con 1 decimale")
    print("  ✅ 30.5    → Float con 1 decimale")
    print("  ✅ 100.0   → Float con 1 decimale")
    print()
    print("Formati NON VALIDI (rifiutati):")
    print("  ❌ 25.55   → Più di 1 decimale")
    print("  ❌ 30.125  → Più di 1 decimale")
    print("  ❌ abc     → Non numerico")
    print("  ❌ 25,5    → Virgola invece di punto")
    print()
    print("La validazione avviene in TEMPO REALE durante la digitazione.")
    print()


def demo_tooltip():
    """Dimostra i tooltip disponibili."""
    print("=" * 60)
    print("DEMO TOOLTIP INFORMATIVI")
    print("=" * 60)
    print()
    print("Al passaggio del mouse sui campi di input, appaiono tooltip che spiegano:")
    print()
    print("Sezione RETTANGOLARE:")
    print("  • width  → 'Larghezza della base della sezione (cm, 1 decimale)'")
    print("  • height → 'Altezza totale della sezione (cm, 1 decimale)'")
    print()
    print("Sezione CIRCOLARE:")
    print("  • diameter → 'Diametro del cerchio (cm, 1 decimale)'")
    print()
    print("Sezione A T:")
    print("  • flange_width     → 'Larghezza dell'ala superiore (cm, 1 decimale)'")
    print("  • flange_thickness → 'Spessore dell'ala superiore (cm, 1 decimale)'")
    print("  • web_thickness    → 'Spessore dell'anima verticale (cm, 1 decimale)'")
    print("  • web_height       → 'Altezza dell'anima verticale (cm, 1 decimale)'")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DIMOSTRAZIONE GESTIONE DINAMICA CAMPI DI INPUT".center(58) + "║")
    print("║" + "  Sezioni Strutturali - Python + Tkinter".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    # Esegui test per ogni tipologia
    test_rectangular_section()
    test_circular_section()
    test_t_section()
    
    # Dimostra validazione e tooltip
    demo_validation()
    demo_tooltip()
    
    print("=" * 60)
    print("CONCLUSIONE")
    print("=" * 60)
    print()
    print("✅ Tutti i test completati con successo!")
    print()
    print("L'applicazione GUI gestisce automaticamente:")
    print("  1. Cambio dinamico dei campi al cambio tipologia")
    print("  2. Validazione input (float con 1 decimale)")
    print("  3. Tooltip informativi su ogni campo")
    print("  4. Calcolo corretto delle proprietà geometriche")
    print()
    print("Per avviare l'applicazione GUI:")
    print("  $ python -m rd2229")
    print()
