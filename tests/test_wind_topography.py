"""Test per il modulo topografia del vento."""

from __future__ import annotations

import pytest

from src.wind.models import TopographyParams
from src.wind.topography import compute_topography_factor


class TestTopographyFlat:
    def test_none_topo(self):
        assert compute_topography_factor(10.0, None) == 1.0

    def test_flat_type(self):
        topo = TopographyParams(topo_type="flat")
        assert compute_topography_factor(10.0, topo) == 1.0

    def test_unknown_type(self):
        topo = TopographyParams(topo_type="unknown")
        assert compute_topography_factor(10.0, topo) == 1.0


class TestTopographyHill:
    def test_hill_at_crest(self):
        topo = TopographyParams(
            topo_type="hill",
            crest_height_m=100.0,
            slope_upwind_deg=15.0,
            x_from_crest_m=0.0,
            lu_m=300.0,
        )
        ct = compute_topography_factor(10.0, topo)
        assert ct > 1.0
        assert ct < 1.7

    def test_hill_far_downwind(self):
        topo = TopographyParams(
            topo_type="hill",
            crest_height_m=100.0,
            slope_upwind_deg=15.0,
            x_from_crest_m=1000.0,
            lu_m=300.0,
        )
        ct = compute_topography_factor(10.0, topo)
        # Far downwind, effect should be minimal
        assert ct >= 1.0
        assert ct < 1.1

    def test_hill_zero_height(self):
        topo = TopographyParams(topo_type="hill", crest_height_m=0.0)
        assert compute_topography_factor(10.0, topo) == 1.0

    def test_hill_low_slope(self):
        topo = TopographyParams(
            topo_type="hill",
            crest_height_m=10.0,
            slope_upwind_deg=1.0,
            lu_m=500.0,
        )
        ct = compute_topography_factor(10.0, topo)
        # phi = 10/500 = 0.02 < 0.05 → no effect
        assert ct == 1.0

    def test_ct_increases_with_steepness(self):
        ct_gentle = compute_topography_factor(
            10.0,
            TopographyParams(topo_type="hill", crest_height_m=50.0, slope_upwind_deg=10.0, lu_m=200.0),
        )
        ct_steep = compute_topography_factor(
            10.0,
            TopographyParams(topo_type="hill", crest_height_m=100.0, slope_upwind_deg=20.0, lu_m=200.0),
        )
        assert ct_steep >= ct_gentle


class TestTopographyRidge:
    def test_ridge_at_crest(self):
        topo = TopographyParams(
            topo_type="ridge",
            crest_height_m=100.0,
            slope_upwind_deg=15.0,
            lu_m=300.0,
        )
        ct = compute_topography_factor(10.0, topo)
        assert ct > 1.0

    def test_ridge_less_than_hill(self):
        """Ridge speed-up should be lower than hill for same geometry."""
        hill = TopographyParams(topo_type="hill", crest_height_m=100.0, slope_upwind_deg=15.0, lu_m=300.0)
        ridge = TopographyParams(topo_type="ridge", crest_height_m=100.0, slope_upwind_deg=15.0, lu_m=300.0)
        ct_hill = compute_topography_factor(10.0, hill)
        ct_ridge = compute_topography_factor(10.0, ridge)
        assert ct_hill >= ct_ridge


class TestTopographyEscarpment:
    def test_escarpment_at_crest(self):
        topo = TopographyParams(
            topo_type="escarpment",
            crest_height_m=50.0,
            slope_upwind_deg=20.0,
            lu_m=150.0,
        )
        ct = compute_topography_factor(10.0, topo)
        assert ct > 1.0

    def test_escarpment_zero_height(self):
        topo = TopographyParams(topo_type="escarpment", crest_height_m=0.0)
        assert compute_topography_factor(10.0, topo) == 1.0


class TestTopographyValley:
    def test_valley_narrow(self):
        topo = TopographyParams(
            topo_type="valley",
            crest_height_m=100.0,
            lu_m=200.0,
        )
        ct = compute_topography_factor(10.0, topo)
        assert ct > 1.0

    def test_valley_wide(self):
        topo = TopographyParams(
            topo_type="valley",
            crest_height_m=10.0,
            lu_m=2000.0,
        )
        ct = compute_topography_factor(10.0, topo)
        # Very wide valley → minimal effect
        assert ct == 1.0

    def test_valley_decays_with_height(self):
        topo = TopographyParams(topo_type="valley", crest_height_m=100.0, lu_m=200.0)
        ct_low = compute_topography_factor(5.0, topo)
        ct_high = compute_topography_factor(200.0, topo)
        assert ct_low >= ct_high
