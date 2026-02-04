import unittest

from sections_app.models.sections import create_section_from_dict
from sections_app.models.sections import LSection


class TestLSectionParserCompatibility(unittest.TestCase):
    def test_l_section_uses_t_horizontal_and_t_vertical_when_present(self):
        data = {
            'section_type': 'L_SECTION',
            'name': 'L test',
            'width': '10',
            'height': '20',
            't_horizontal': '3.3',
            't_vertical': '2.2',
        }
        sec = create_section_from_dict(data)
        self.assertIsInstance(sec, LSection)
        self.assertAlmostEqual(sec.t_horizontal, 3.3)
        self.assertAlmostEqual(sec.t_vertical, 2.2)

    def test_l_section_fallback_uses_flange_and_web_if_missing(self):
        data = {
            'section_type': 'L_SECTION',
            'name': 'L fallback',
            'width': '12',
            'height': '24',
            'flange_thickness': '4.0',
            'web_thickness': '1.5',
        }
        sec = create_section_from_dict(data)
        self.assertIsInstance(sec, LSection)
        # fallback allowed for backward compatibility
        self.assertAlmostEqual(sec.t_horizontal, 4.0)
        self.assertAlmostEqual(sec.t_vertical, 1.5)


if __name__ == '__main__':
    unittest.main()
