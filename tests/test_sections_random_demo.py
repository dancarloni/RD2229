"""
Test automatizzati per la verifica delle proprietà geometriche delle sezioni.

Questo modulo contiene test che:
- Generano dimensioni casuali plausibili per diverse tipologie di sezione
- Verificano che i calcoli producano risultati validi (no NaN, infinito, valori negativi)
- Confrontano i risultati con formule teoriche di riferimento per forme semplici

Non richiede interfaccia grafica, testa solo i modelli.
"""
from __future__ import annotations

import math
import random
import unittest

from sections_app.models.sections import (
    CircularSection,
    RectangularSection,
    TSection,
)


class TestRectangularSectionProperties(unittest.TestCase):
    """Test per sezioni rettangolari con dimensioni casuali."""

    def test_rectangular_random_dimensions(self):
        """Genera 3 sezioni rettangolari con dimensioni casuali e verifica proprietà."""
        for i in range(3):
            with self.subTest(iteration=i):
                # Dimensioni casuali tra 10 e 100 cm
                width = random.uniform(10.0, 100.0)
                height = random.uniform(10.0, 100.0)
                
                section = RectangularSection(
                    name=f"Rect_Random_{i+1}",
                    width=width,
                    height=height
                )
                
                props = section.compute_properties()
                
                # Verifica: area positiva
                self.assertGreater(props.area, 0, "Area deve essere positiva")
                
                # Verifica: momenti di inerzia non negativi
                self.assertGreaterEqual(props.ix, 0, "Ix deve essere >= 0")
                self.assertGreaterEqual(props.iy, 0, "Iy deve essere >= 0")
                
                # Verifica: raggi giratori positivi
                self.assertGreater(props.rx, 0, "rx deve essere positivo")
                self.assertGreater(props.ry, 0, "ry deve essere positivo")
                
                # Verifica: nessun valore NaN o infinito
                self.assertFalse(math.isnan(props.area), "Area non deve essere NaN")
                self.assertFalse(math.isinf(props.area), "Area non deve essere infinito")
                self.assertFalse(math.isnan(props.ix), "Ix non deve essere NaN")
                self.assertFalse(math.isinf(props.ix), "Ix non deve essere infinito")
                
                # Confronto con formule teoriche per rettangolo
                area_teorica = width * height
                self.assertAlmostEqual(
                    props.area,
                    area_teorica,
                    places=6,
                    msg="Area calcolata deve corrispondere a b*h"
                )
                
                ix_teorico = (width * height**3) / 12
                self.assertAlmostEqual(
                    props.ix,
                    ix_teorico,
                    places=6,
                    msg="Ix deve corrispondere a b*h³/12"
                )
                
                iy_teorico = (height * width**3) / 12
                self.assertAlmostEqual(
                    props.iy,
                    iy_teorico,
                    places=6,
                    msg="Iy deve corrispondere a h*b³/12"
                )
                
                # Baricentro al centro del rettangolo
                self.assertAlmostEqual(props.centroid_x, width / 2, places=6)
                self.assertAlmostEqual(props.centroid_y, height / 2, places=6)
                
                # Ixy = 0 per rettangolo con assi principali
                self.assertAlmostEqual(props.ixy, 0.0, places=6)


class TestCircularSectionProperties(unittest.TestCase):
    """Test per sezioni circolari piene con dimensioni casuali."""

    def test_circular_random_dimensions(self):
        """Genera 3 sezioni circolari con diametri casuali e verifica proprietà."""
        for i in range(3):
            with self.subTest(iteration=i):
                # Diametro casuale tra 10 e 100 cm
                diameter = random.uniform(10.0, 100.0)
                
                section = CircularSection(
                    name=f"Circle_Random_{i+1}",
                    diameter=diameter
                )
                
                props = section.compute_properties()
                radius = diameter / 2
                
                # Verifica: area positiva
                self.assertGreater(props.area, 0, "Area deve essere positiva")
                
                # Verifica: momenti di inerzia non negativi
                self.assertGreaterEqual(props.ix, 0, "Ix deve essere >= 0")
                self.assertGreaterEqual(props.iy, 0, "Iy deve essere >= 0")
                
                # Verifica: raggi giratori positivi
                self.assertGreater(props.rx, 0, "rx deve essere positivo")
                self.assertGreater(props.ry, 0, "ry deve essere positivo")
                
                # Verifica: nessun valore NaN o infinito
                self.assertFalse(math.isnan(props.area), "Area non deve essere NaN")
                self.assertFalse(math.isinf(props.area), "Area non deve essere infinito")
                self.assertFalse(math.isnan(props.ix), "Ix non deve essere NaN")
                self.assertFalse(math.isinf(props.ix), "Ix non deve essere infinito")
                
                # Confronto con formule teoriche per cerchio
                area_teorica = math.pi * radius**2
                self.assertAlmostEqual(
                    props.area,
                    area_teorica,
                    places=6,
                    msg="Area calcolata deve corrispondere a π*r²"
                )
                
                i_teorico = (math.pi * radius**4) / 4
                self.assertAlmostEqual(
                    props.ix,
                    i_teorico,
                    places=6,
                    msg="Ix deve corrispondere a π*r⁴/4"
                )
                
                self.assertAlmostEqual(
                    props.iy,
                    i_teorico,
                    places=6,
                    msg="Iy deve corrispondere a π*r⁴/4 (cerchio simmetrico)"
                )
                
                # Ix = Iy per simmetria
                self.assertAlmostEqual(props.ix, props.iy, places=6)
                
                # Baricentro al centro del cerchio
                self.assertAlmostEqual(props.centroid_x, radius, places=6)
                self.assertAlmostEqual(props.centroid_y, radius, places=6)
                
                # Ixy = 0 per sezione a simmetria circolare
                self.assertAlmostEqual(props.ixy, 0.0, places=6)


class TestTSectionProperties(unittest.TestCase):
    """Test per sezioni a T con dimensioni casuali."""

    def test_t_section_random_dimensions(self):
        """Genera 3 sezioni a T con dimensioni casuali e verifica proprietà."""
        for i in range(3):
            with self.subTest(iteration=i):
                # Dimensioni casuali con vincoli logici
                flange_width = random.uniform(20.0, 100.0)
                flange_thickness = random.uniform(5.0, 20.0)
                web_thickness = random.uniform(5.0, min(flange_width, 20.0))
                web_height = random.uniform(10.0, 80.0)
                
                section = TSection(
                    name=f"T_Random_{i+1}",
                    flange_width=flange_width,
                    flange_thickness=flange_thickness,
                    web_thickness=web_thickness,
                    web_height=web_height
                )
                
                props = section.compute_properties()
                
                # Verifica: area positiva
                self.assertGreater(props.area, 0, "Area deve essere positiva")
                
                # Verifica: momenti di inerzia non negativi
                self.assertGreaterEqual(props.ix, 0, "Ix deve essere >= 0")
                self.assertGreaterEqual(props.iy, 0, "Iy deve essere >= 0")
                
                # Verifica: raggi giratori positivi
                self.assertGreater(props.rx, 0, "rx deve essere positivo")
                self.assertGreater(props.ry, 0, "ry deve essere positivo")
                
                # Verifica: nessun valore NaN o infinito
                self.assertFalse(math.isnan(props.area), "Area non deve essere NaN")
                self.assertFalse(math.isinf(props.area), "Area non deve essere infinito")
                self.assertFalse(math.isnan(props.ix), "Ix non deve essere NaN")
                self.assertFalse(math.isinf(props.ix), "Ix non deve essere infinito")
                self.assertFalse(math.isnan(props.centroid_x), "Centroid_x non deve essere NaN")
                self.assertFalse(math.isnan(props.centroid_y), "Centroid_y non deve essere NaN")
                
                # Area approssimativa: ala + anima
                area_approssimativa = (flange_width * flange_thickness) + (web_height * web_thickness)
                # L'area calcolata deve essere ragionevole (entro 10% per approssimazione)
                self.assertAlmostEqual(
                    props.area,
                    area_approssimativa,
                    delta=area_approssimativa * 0.1,
                    msg="Area deve essere circa ala + anima"
                )
                
                # Baricentro deve essere all'interno delle dimensioni della sezione
                total_height = flange_thickness + web_height
                self.assertGreaterEqual(props.centroid_x, 0)
                self.assertLessEqual(props.centroid_x, flange_width)
                self.assertGreaterEqual(props.centroid_y, 0)
                self.assertLessEqual(props.centroid_y, total_height)


class TestSectionEdgeCases(unittest.TestCase):
    """Test per casi limite e validazione input."""

    def test_rectangular_invalid_dimensions(self):
        """Verifica che dimensioni non valide sollevano eccezioni."""
        section = RectangularSection(name="Invalid", width=-10, height=20)
        with self.assertRaises(ValueError):
            section.compute_properties()
        
        section2 = RectangularSection(name="Invalid2", width=10, height=0)
        with self.assertRaises(ValueError):
            section2.compute_properties()

    def test_circular_invalid_diameter(self):
        """Verifica che diametro non valido sollevi eccezioni."""
        section = CircularSection(name="Invalid", diameter=-5)
        with self.assertRaises(ValueError):
            section.compute_properties()
        
        section2 = CircularSection(name="Invalid2", diameter=0)
        with self.assertRaises(ValueError):
            section2.compute_properties()

    def test_very_small_dimensions(self):
        """Test con dimensioni molto piccole ma valide."""
        section = RectangularSection(name="Small", width=0.1, height=0.1)
        props = section.compute_properties()
        
        self.assertGreater(props.area, 0)
        self.assertFalse(math.isnan(props.area))
        self.assertFalse(math.isinf(props.area))

    def test_very_large_dimensions(self):
        """Test con dimensioni molto grandi."""
        section = RectangularSection(name="Large", width=1000, height=1000)
        props = section.compute_properties()
        
        self.assertGreater(props.area, 0)
        self.assertFalse(math.isnan(props.area))
        self.assertFalse(math.isinf(props.area))


if __name__ == "__main__":
    # Esegui i test con verbosità
    unittest.main(verbosity=2)

