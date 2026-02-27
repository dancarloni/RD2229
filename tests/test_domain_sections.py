from verification_table import VerificationInput, get_section_geometry


class DummySection:
    def __init__(self, id_, name, width=None, height=None):
        self.id = id_
        self.name = name
        self.width = width
        self.height = height


class DummyRepo:
    def __init__(self, sections):
        self._sections = sections

    def get_all_sections(self):
        return self._sections


def test_get_section_geometry_with_section():
    repo = DummyRepo([DummySection("S1", "S1", width=30, height=50)])
    inp = VerificationInput(section_id="S1")
    b, h = get_section_geometry(inp, repo, unit="cm")
    assert (b, h) == (30.0, 50.0)


def test_get_section_geometry_fallback():
    inp = VerificationInput(section_id="")
    b, h = get_section_geometry(inp, None, unit="cm")
    assert (b, h) == (30.0, 50.0)
