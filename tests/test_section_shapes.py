try:
    from hypothesis import given, strategies as st
except Exception:  # pragma: no cover - Hypothesis not installed
    import pytest

    pytest.skip("Hypothesis not available; skipping circular section invariants test", allow_module_level=True)

from src.core_calculus.core.geometry import CircularHollowSection


@given(
    outer=st.floats(min_value=0.01, max_value=100.0),
    inner=st.floats(min_value=0.0, max_value=99.99),
)
def test_circular_hollow_inertia_invariant(outer, inner):
    # Ensure inner is less than outer
    if inner >= outer:
        inner = outer / 2.0
    sec = CircularHollowSection(outer_diameter=outer, inner_diameter=inner)
    area = sec.area()
    assert area > 0
    ix, iy = sec.inertia()
    # For circular sections Ix and Iy are equal
    assert abs(ix - iy) < 1e-9
