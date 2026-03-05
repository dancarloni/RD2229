import unittest

from sections_app.models.sections import RectangularSection, TSection


class TestShearAreas(unittest.TestCase):
    def test_rectangular_default_shear_area(self):
        # Rectangular 10 x 20 => area = 200 cm2, default kappa = 5/6
        rect = RectangularSection(name="R", width=10.0, height=20.0)
        props = rect.compute_properties()
        expected = (5.0 / 6.0) * 200.0
        self.assertAlmostEqual(props.shear_area_y, expected, places=6)
        self.assertAlmostEqual(props.shear_area_z, expected, places=6)

    def test_t_section_web_reference_area(self):
        # T-section with web_thickness=2, web_height=10 -> web area = 20 cm2
        # default kappa_y for T_SECTION is 1.0 (web direction); A_y should equal web area
        t = TSection(
            name="T", flange_width=10.0, flange_thickness=2.0, web_thickness=2.0, web_height=10.0
        )
        props = t.compute_properties()
        self.assertAlmostEqual(props.shear_area_y, 2.0 * 10.0, places=6)
        # A_z uses total area times default kappa_z (0.9 by default mapping)
        total_area = props.area
        self.assertAlmostEqual(props.shear_area_z, t.shear_factor_z * total_area, places=6)


if __name__ == "__main__":
    unittest.main()
