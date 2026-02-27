from apps.sections.section_graphics import SectionViewTransform


def test_world_length_to_screen_and_flip_y_false():
    bbox = (-5.0, -10.0, 5.0, 10.0)
    canvas_w = 200
    canvas_h = 200
    transform = SectionViewTransform(bbox, canvas_w, canvas_h, margin=10, flip_y=False)

    # scale should match previous expected value
    assert abs(transform.scale - 9.0) < 1e-9

    # center mapping should not flip y
    sx, sy = transform.world_to_screen(0.0, 0.0)
    assert abs(sx - (canvas_w / 2.0)) < 1e-9
    assert abs(sy - (canvas_h / 2.0)) < 1e-9

    # world length to screen should be proportional to scale
    assert abs(transform.world_length_to_screen(2.5) - abs(transform.scale * 2.5)) < 1e-9
