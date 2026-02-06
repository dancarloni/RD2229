import unittest

from historical_ta.checks import AllowableStresses, check_allowable_stresses_ta
from historical_ta.geometry import SectionGeometry, compute_section_properties
from historical_ta.materials import ConcreteLawTA, SteelLawTA, sigma_c, sigma_s
from historical_ta.stress import LoadState, StressResult, compute_normal_stresses_ta


class TestHistoricalTA(unittest.TestCase):
    def test_rectangle_section_properties(self):
        # rectangle 30 x 15 cm
        poly = [[(0.0, 0.0), (30.0, 0.0), (30.0, 15.0), (0.0, 15.0)]]
        geom = SectionGeometry(polygons=poly, bars=[], n_homog=10.0)
        props = compute_section_properties(geom)
        self.assertAlmostEqual(props.area_concrete, 450.0)
        self.assertAlmostEqual(props.yG, 15.0)
        self.assertAlmostEqual(props.zG, 7.5)

    def test_material_laws(self):
        conc = ConcreteLawTA(
            fcd=30.0, Ec=30000.0, eps_c2=0.002, eps_c3=0.003, eps_c4=0.004, eps_cu=0.0035
        )
        self.assertLess(sigma_c(-0.002, conc), 0)
        self.assertEqual(sigma_c(0.0001, conc), 0.0)  # tension not allowed
        steel = SteelLawTA(Es=210000.0, fyd=500.0, eps_yd=0.00238, eps_su=0.1)
        self.assertAlmostEqual(sigma_s(0.001, steel), 210000.0 * 0.001)
        self.assertAlmostEqual(sigma_s(0.005, steel), 500.0)

    def test_simple_ta_check(self):
        poly = [[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]]
        # single bar at centroid
        geom = SectionGeometry(polygons=poly, bars=[(5.0, 5.0, 1.0)], n_homog=10.0)
        props = compute_section_properties(geom)
        conc = ConcreteLawTA(
            fcd=30.0, Ec=30000.0, eps_c2=0.002, eps_c3=0.003, eps_c4=0.004, eps_cu=0.0035
        )
        steel = SteelLawTA(Es=210000.0, fyd=500.0, eps_yd=0.00238, eps_su=0.1)

        loads = LoadState(Nx=0.0, My=0.0, Mz=0.0)
        res = compute_normal_stresses_ta(
            geom, props, loads, conc, steel, allow_concrete_tension=False
        )
        # with zero loads expect near zero stresses
        self.assertAlmostEqual(res.sigma_c_max, 0.0, delta=1e-6)
        self.assertAlmostEqual(res.sigma_s_max, 0.0, delta=1e-6)

    def test_allowable_check(self):
        sr = StressResult(
            sigma_c_max=-10.0,
            sigma_c_min=-20.0,
            sigma_c_pos=0,
            sigma_c_neg=-20,
            sigma_c_med=-5,
            sigma_s_max=100,
            sigma_s_array=[100],
            sigma_vertices=[-10],
        )
        limits = AllowableStresses(sigma_c_allow=30.0, sigma_s_allow=250.0, sigma_c_med_allow=10.0)
        out = check_allowable_stresses_ta(sr, limits)
        self.assertTrue(out.ok)


if __name__ == "__main__":
    unittest.main()
