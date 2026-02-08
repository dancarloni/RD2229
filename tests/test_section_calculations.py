from sections_app.geometry_model import SectionGeometry
from sections_app.section_calculations import compute_section_properties_from_geometry


def test_rectangle_properties_area_centroid_and_principal_axes():
    geom = SectionGeometry.from_rectangle(b=10.0, h=20.0, name="rect1")
    props = compute_section_properties_from_geometry(geom)

    # area should be close to 200 (10 * 20)
    assert abs(props.area - 200.0) < 1e-6

    # centroid of centered rectangle should be near (0,0)
    assert abs(props.x_c) < 1e-6
    assert abs(props.y_c) < 1e-6

    # moments should be positive
    assert props.Ix >= 0
    assert props.Iy >= 0
    assert props.I1 >= props.I2

    # r1/r2 positive or zero
    assert props.r1 >= 0
    assert props.r2 >= 0


def test_section_conversion_and_properties_from_section_model():
    # Ensure adapter from sections_app.models.Section works
    from sections_app.models.sections import RectangularSection
    from sections_app.section_calculations import compute_section_properties_from_section

    sec = RectangularSection(name="test", width=10.0, height=20.0)
    props = compute_section_properties_from_section(sec)
    assert abs(props.area - 200.0) < 1e-6
    assert abs(props.x_c) < 1e-6
    assert props.I1 >= props.I2
