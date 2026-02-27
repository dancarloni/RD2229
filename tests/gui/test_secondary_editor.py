from src.gui.secondary_elements.editor import build_form_schema, serialize_form


def test_editor_schema_and_serialization():
    s = build_form_schema('parapet')
    assert s['element_type'] == 'parapet'
    data = serialize_form({'element_type': 'parapet', 'width': 30})
    assert data['element_type'] == 'parapet'
