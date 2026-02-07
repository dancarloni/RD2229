"""Test per le nuove tipologie di sezione e rotazione."""

import unittest
from math import pi, radians

from sections_app.models.sections import (
    CircularHollowSection,
    ISection,
    LSection,
    RectangularHollowSection,
    RectangularSection,
)
from sections_app.services.calculations import rotate_inertia


class TestNewSectionTypes(unittest.TestCase):
    """Test per le nuove tipologie di sezione."""

    def test_l_section_basic(self):
        """Test sezione ad L: area e baricentro."""
        section = LSection(
            name="L Test",
            width=10.0,
            height=10.0,
            t_horizontal=2.0,
            t_vertical=2.0,
        )
        section.compute_properties()
        props = section.properties

        # Verifica che props non sia None
        self.assertIsNotNone(props, "section.properties è None dopo compute_properties()")

        # Area = ala orizzontale + ala verticale
        # Ala orizzontale: 10 * 2 = 20
        # Ala verticale: 2 * (10 - 2) = 2 * 8 = 16
        # Totale = 36
        self.assertAlmostEqual(float(props.area), 36.0, places=4)

        # Verifiche di base
        self.assertGreater(float(props.area), 0)
        self.assertGreater(float(props.ix), 0)
        self.assertGreater(float(props.iy), 0)

    def test_i_section_basic(self):
        """Test sezione ad I: area e simmetria."""
        section = ISection(
            name="I Test",
            flange_width=20.0,
            flange_thickness=2.0,
            web_height=16.0,
            web_thickness=1.0,
        )
        section.compute_properties()
        props = section.properties

        # Area = 2 ali + anima
        # Ali: 2 * (20 * 2) = 80
        # Anima: 1 * 16 = 16
        # Totale = 96
        self.assertAlmostEqual(props.area, 96.0, places=4)

        # Baricentro dovrebbe essere al centro per simmetria
        total_height = 2 * 2 + 16  # 20
        self.assertAlmostEqual(props.centroid_x, 10.0, places=4)
        self.assertAlmostEqual(props.centroid_y, 10.0, places=4)

    def test_circular_hollow_section(self):
        """Test sezione circolare cava."""
        outer_d = 10.0
        thickness = 1.0
        inner_d = outer_d - 2 * thickness  # 8.0

        section = CircularHollowSection(
            name="Tube Test",
            outer_diameter=outer_d,
            thickness=thickness,
        )
        section.compute_properties()
        props = section.properties

        # Area = π * (R_out² - R_in²)
        r_out = outer_d / 2
        r_in = inner_d / 2
        expected_area = pi * (r_out**2 - r_in**2)
        self.assertAlmostEqual(props.area, expected_area, places=4)

        # Inerzia = π/4 * (R_out⁴ - R_in⁴)
        expected_ix = (pi / 4) * (r_out**4 - r_in**4)
        self.assertAlmostEqual(props.ix, expected_ix, places=4)
        self.assertAlmostEqual(props.iy, expected_ix, places=4)

    def test_rectangular_hollow_section(self):
        """Test sezione rettangolare cava."""
        width = 20.0
        height = 15.0
        thickness = 2.0

        section = RectangularHollowSection(
            name="Rect Hollow Test",
            width=width,
            height=height,
            thickness=thickness,
        )
        section.compute_properties()
        props = section.properties

        # Area = esterna - interna
        w_in = width - 2 * thickness
        h_in = height - 2 * thickness
        expected_area = width * height - w_in * h_in
        self.assertAlmostEqual(props.area, expected_area, places=4)

        # Inerzia Ix = (b*h³ - b_in*h_in³) / 12
        expected_ix = (width * height**3 - w_in * h_in**3) / 12
        self.assertAlmostEqual(props.ix, expected_ix, places=4)


class TestRotationInertia(unittest.TestCase):
    """Test per rotazione delle inerzie."""

    def test_rotation_function(self):
        """Test funzione rotate_inertia."""
        # Rettangolo 10x20 cm (Ix > Iy)
        Ix = (10 * 20**3) / 12
        Iy = (20 * 10**3) / 12
        Ixy = 0.0

        # Rotazione di 0° deve lasciare invariato
        Ix_0, Iy_0, Ixy_0 = rotate_inertia(Ix, Iy, Ixy, radians(0))
        self.assertAlmostEqual(Ix_0, Ix, places=4)
        self.assertAlmostEqual(Iy_0, Iy, places=4)
        self.assertAlmostEqual(Ixy_0, 0.0, places=4)

        # Rotazione di 90° deve scambiare Ix e Iy
        Ix_90, Iy_90, Ixy_90 = rotate_inertia(Ix, Iy, Ixy, radians(90))
        self.assertAlmostEqual(Ix_90, Iy, places=2)
        self.assertAlmostEqual(Iy_90, Ix, places=2)

    def test_rectangular_section_with_rotation(self):
        """Test sezione rettangolare con rotazione."""
        section = RectangularSection(
            name="Rect Rotated",
            width=10.0,
            height=20.0,
            rotation_angle_deg=45.0,
        )
        section.compute_properties()
        props = section.properties

        # Inerzie locali
        Ix_local = (10 * 20**3) / 12
        Iy_local = (20 * 10**3) / 12

        # Con rotazione 45°, Ix e Iy dovrebbero avvicinarsi
        # (la sezione si "equalizza")
        self.assertNotAlmostEqual(props.ix, Ix_local, places=1)
        self.assertNotAlmostEqual(props.iy, Iy_local, places=1)

        # Verifica che siano state applicate le formule di rotazione
        Ix_rot, Iy_rot, Ixy_rot = rotate_inertia(Ix_local, Iy_local, 0.0, radians(45))
        self.assertAlmostEqual(props.ix, Ix_rot, places=4)
        self.assertAlmostEqual(props.iy, Iy_rot, places=4)
        self.assertAlmostEqual(props.ixy, Ixy_rot, places=4)


class TestEdgeCasesNewSections(unittest.TestCase):
    """Test casi limite per le nuove sezioni."""

    def test_invalid_dimensions_l_section(self):
        """Test dimensioni non valide per sezione L."""
        section = LSection(
            name="L Invalid",
            width=10.0,
            height=10.0,
            t_horizontal=-1.0,  # Invalido
            t_vertical=2.0,
        )
        with self.assertRaises(ValueError):
            section.compute_properties()

    def test_circular_hollow_thickness_too_large(self):
        """Test spessore troppo grande per sezione cava."""
        section = CircularHollowSection(
            name="Tube Invalid",
            outer_diameter=10.0,
            thickness=6.0,  # > outer_diameter/2
        )
        with self.assertRaises(ValueError):
            section.compute_properties()


if __name__ == "__main__":
    unittest.main()
