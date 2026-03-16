from src.methods.ntc2018.models import Apertura
from src.methods.ntc2018.x5_editor import ApertureEditorState


def test_editor_add_move_resize_remove_cycle():
    st = ApertureEditorState.empty()
    st.add_apertura(
        Apertura(
            id="a1",
            posizione={"x": 10.0, "y": 20.0},
            dimensioni={"h": 100.0, "b": 80.0},
        )
    )
    assert len(st.aperture) == 1

    assert st.move_apertura("a1", 40.0, 50.0) is True
    assert st.resize_apertura("a1", 120.0, 90.0) is True
    item = st.to_canvas_items()[0]
    assert item["x"] == 40.0
    assert item["h"] == 120.0

    st.remove_apertura("a1")
    assert len(st.aperture) == 0
