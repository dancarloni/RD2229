import math

from sections_app.models.sections import RectangularSection
from sections_app.services.calculations import compute_principal_inertia


def test_principal_inertia_rectangular():
    # Rectangle b=4, h=2
    b = 4.0
    h = 2.0
    Ix = (b * h**3) / 12.0
    Iy = (h * b**3) / 12.0
    Ixy = 0.0

    I1, I2, angle_rad = compute_principal_inertia(Ix, Iy, Ixy)

    assert math.isclose(I1, max(Ix, Iy), rel_tol=1e-9, abs_tol=1e-12)
    assert math.isclose(I2, min(Ix, Iy), rel_tol=1e-9, abs_tol=1e-12)
    # Angle points towards the principal inertia I1. If I1 == Iy the angle is pi/2
    expected_angle = 0.0 if I1 == Ix else math.pi / 2
    assert math.isclose(angle_rad, expected_angle, abs_tol=1e-9)


def _normalize_angle_deg(a):
    # Normalize angle to range [0, 180)
    a = a % 180.0
    if a < 0:
        a += 180.0
    return a


def test_principal_inertia_rotated_rectangular():
    # Geometry
    b = 4.0
    h = 2.0
    theta_deg = 30.0

    rect = RectangularSection(name="r", width=b, height=h, rotation_angle_deg=theta_deg)
    props = rect.compute_properties()

    # Principals computed should match unrotated I1/I2
    Ix_local = (b * h**3) / 12.0
    Iy_local = (h * b**3) / 12.0
    I1_ref, I2_ref, _ = compute_principal_inertia(Ix_local, Iy_local, 0.0)

    assert math.isclose(props.principal_ix, I1_ref, rel_tol=1e-9)
    assert math.isclose(props.principal_iy, I2_ref, rel_tol=1e-9)

    # Principal angle should be close to the rotation angle plus the base orientation
    angle_deg = props.principal_angle_deg
    assert angle_deg is not None

    # base orientation depends on which inertia is I1 (if I1 == Ix => base 0 deg, else 90 deg)
    base_deg = 0.0 if math.isclose(I1_ref, Ix_local, rel_tol=1e-12) else 90.0
    expected_deg = (base_deg + theta_deg) % 180.0

    diff = abs(_normalize_angle_deg(angle_deg) - _normalize_angle_deg(expected_deg))
    assert diff < 1e-6
