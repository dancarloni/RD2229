from sections_app.models.sections import RectangularSection
from sections_app.section_calculations import compute_section_properties_from_section


def test_shear_meta_set():
    sec = RectangularSection(name="r", width=10.0, height=20.0)
    props = compute_section_properties_from_section(sec, shear_factor=0.75)
    assert "shear_factor" in props.meta
    assert abs(props.meta["shear_factor"] - 0.75) < 1e-9
    assert "shear_area" in props.meta
    assert abs(props.meta["shear_area"] - (props.area * 0.75)) < 1e-9
