try:
    from hypothesis import given
    from hypothesis import strategies as st
except Exception:  # pragma: no cover - Hypothesis not installed in this environment
    import pytest

    pytest.skip(
        "Hypothesis not available; skipping property-based invariants test",
        allow_module_level=True,
    )

from src.core_calculus.geometry_cache import section_inertia


@given(
    width=st.floats(min_value=0.001, max_value=10),
    height=st.floats(min_value=0.001, max_value=10),
)
def test_rectangle_inertia_symmetry(width, height):
    area1, ix1, iy1 = section_inertia(width, height)
    area2, ix2, iy2 = section_inertia(height, width)
    # Area should be symmetric
    assert abs(area1 - area2) < 1e-12
    # Ix and Iy should swap when swapping width/height
    assert abs(ix1 - iy2) < 1e-12
    assert abs(iy1 - ix2) < 1e-12
