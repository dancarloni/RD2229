from sections_app.section_graphics import SectionViewTransform


def test_uniform_scale_and_centering():
    # bbox for rectangle 10 x 20 centered at origin
    bbox = (-5.0, -10.0, 5.0, 10.0)
    canvas_w = 200
    canvas_h = 200
    transform = SectionViewTransform(bbox, canvas_w, canvas_h, margin=10)

    # available width/height = 200 - 2*10 = 180
    # bbox width = 10, bbox height = 20 -> scale = min(180/10=18, 180/20=9) = 9
    assert abs(transform.scale - 9.0) < 1e-9

    # center should map world center (0,0) to canvas center
    sx, sy = transform.world_to_screen(0.0, 0.0)
    assert abs(sx - (canvas_w / 2.0)) < 1e-9
    assert abs(sy - (canvas_h / 2.0)) < 1e-9

    # one corner
    sx1, sy1 = transform.world_to_screen(5.0, 10.0)
    # sx = 9*5 + tx -> should be 100 + 45 = 145
    assert abs(sx1 - 145.0) < 1e-9
    # sy = -9*10 + ty -> should be -90 + 100 = 10
    assert abs(sy1 - 10.0) < 1e-9
