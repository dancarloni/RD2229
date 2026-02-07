import unittest

from sections_app.models.sections import LSection, create_section_from_dict


class TestLSectionParserCompatibility(unittest.TestCase):
    def test_l_section_uses_t_horizontal_and_t_vertical_when_present(self):
        data = {
            "section_type": "L_SECTION",
            "name": "L test",
            "width": "10",
            "height": "20",
            "t_horizontal": "3.3",
            "t_vertical": "2.2",
        }
        sec = create_section_from_dict(data)
        self.assertIsInstance(sec, LSection)
        self.assertAlmostEqual(sec.t_horizontal, 3.3)
        self.assertAlmostEqual(sec.t_vertical, 2.2)

    def test_l_section_fallback_uses_flange_and_web_if_missing(self):
        data = {
            "section_type": "L_SECTION",
            "name": "L fallback",
            "width": "12",
            "height": "24",
            "flange_thickness": "4.0",
            "web_thickness": "1.5",
        }
        sec = create_section_from_dict(data)
        self.assertIsInstance(sec, LSection)
        # fallback allowed for backward compatibility
        self.assertAlmostEqual(sec.t_horizontal, 4.0)
        self.assertAlmostEqual(sec.t_vertical, 1.5)

    def test_csv_with_Ay_Az_and_no_kappa_preserves_values_by_deriving_kappa(self):
        data = {
            "section_type": "RECTANGULAR",
            "name": "CSV R",
            "width": "10",
            "height": "20",
            "area": "200",
            "A_y": "150.0",
            "A_z": "150.0",
            # no kappa_y/kappa_z provided
        }
        sec = create_section_from_dict(data)
        # After creation, the derived kappa should be A_y/area = 150/200 = 0.75
        self.assertAlmostEqual(sec.shear_factor_y, 0.75)
        self.assertAlmostEqual(sec.shear_factor_z, 0.75)


if __name__ == "__main__":
    unittest.main()
