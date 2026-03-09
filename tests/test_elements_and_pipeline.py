"""Test per element_model, element_repo, resolve_inputs, export_results, report renderers."""

import json
import os
import tempfile

from src.elements.element_model import Constraint, Element, LoadCase
from src.elements.element_repo import ElementRepository
from src.elements.resolve_inputs import resolve_verification_inputs
from src.materials.material_repo import MaterialRepository
from src.report.renderer_html import HTMLReportRenderer
from src.report.renderer_md import MarkdownReportRenderer
from src.report.renderer_pdf import PDFReportRenderer
from src.tools.export_results import export_to_csv, export_to_json, results_to_table

# ===================================================================
# LoadCase
# ===================================================================


class TestLoadCase:
    def test_defaults(self):
        lc = LoadCase()
        assert lc.N == 0.0
        assert lc.Mx == 0.0

    def test_to_dict(self):
        lc = LoadCase(name="SLU", N=5000.0, Mx=2000.0)
        d = lc.to_dict()
        assert d["name"] == "SLU"
        assert d["N"] == 5000.0
        assert d["Mx"] == 2000.0


# ===================================================================
# Constraint
# ===================================================================


class TestConstraint:
    def test_defaults(self):
        c = Constraint()
        assert c.type == "fixed"
        assert c.position == "start"

    def test_to_dict(self):
        c = Constraint(type="pinned", position="end")
        assert c.to_dict() == {"type": "pinned", "position": "end"}


# ===================================================================
# Element
# ===================================================================


class TestElement:
    def setup_method(self):
        self.el = Element(
            element_id="T1",
            type="beam",
            length_cm=500.0,
            constraints=[
                Constraint(type="fixed", position="start"),
                Constraint(type="pinned", position="end"),
            ],
            load_cases=[LoadCase(name="SLU", N=0.0, Mx=3000.0, Tx=5000.0)],
            additional_params={"b": 30.0, "h": 50.0, "As": 6.28, "cover_cm": 4.0},
        )

    def test_basic_attrs(self):
        assert self.el.element_id == "T1"
        assert self.el.type == "beam"
        assert len(self.el.constraints) == 2
        assert len(self.el.load_cases) == 1

    def test_get_width_height(self):
        assert self.el.get_width_cm() == 30.0
        assert self.el.get_height_cm() == 50.0

    def test_effective_depth(self):
        assert self.el.get_effective_depth_cm() == 46.0

    def test_to_verification_dict(self):
        d = self.el.to_verification_dict()
        assert d["b"] == 30.0
        assert d["h"] == 50.0
        assert d["d"] == 46.0
        assert d["Mx"] == 3000.0
        assert d["Tx"] == 5000.0
        assert d["As"] == 6.28

    def test_to_dict(self):
        d = self.el.to_dict()
        assert d["element_id"] == "T1"
        assert d["type"] == "beam"
        assert len(d["constraints"]) == 2
        assert len(d["load_cases"]) == 1

    def test_from_dict(self):
        data = {
            "element_id": "P1",
            "type": "column",
            "length_cm": 300.0,
            "constraints": [{"type": "fixed", "position": "start"}],
            "load_cases": [{"name": "SLU", "N": 10000.0, "Mx": 500.0}],
            "additional_params": {"b": 40.0, "h": 40.0},
        }
        el = Element.from_dict(data)
        assert el.element_id == "P1"
        assert el.type == "column"
        assert len(el.constraints) == 1
        assert el.load_cases[0].N == 10000.0

    def test_section_area_none(self):
        assert self.el.get_section_area() is None

    def test_section_area_with_section(self):
        self.el.section = {"area_cm2": 1500.0}
        assert self.el.get_section_area() == 1500.0

    def test_material_param_none(self):
        assert self.el.get_material_param("f_ck") is None


# ===================================================================
# ElementRepository
# ===================================================================


class TestElementRepository:
    def setup_method(self):
        self.repo = ElementRepository()
        self.el1 = Element(element_id="T1", type="beam", length_cm=500.0)
        self.el2 = Element(element_id="P1", type="column", length_cm=300.0)

    def test_add_and_get(self):
        self.repo.add_element(self.el1)
        assert self.repo.get("T1") is not None
        assert self.repo.get("T1").type == "beam"

    def test_list_all(self):
        self.repo.add_element(self.el1)
        self.repo.add_element(self.el2)
        assert len(self.repo.list_all()) == 2

    def test_list_by_type(self):
        self.repo.add_element(self.el1)
        self.repo.add_element(self.el2)
        beams = self.repo.list_by_type("beam")
        assert len(beams) == 1
        assert beams[0].element_id == "T1"

    def test_remove(self):
        self.repo.add_element(self.el1)
        assert self.repo.remove("T1") is True
        assert self.repo.get("T1") is None
        assert self.repo.remove("T1") is False

    def test_len(self):
        assert len(self.repo) == 0
        self.repo.add_element(self.el1)
        assert len(self.repo) == 1

    def test_load_from_json(self):
        data = [
            {"element_id": "T1", "type": "beam", "length_cm": 500.0},
            {"element_id": "P1", "type": "column", "length_cm": 300.0},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name

        try:
            mat_repo = MaterialRepository()
            count = self.repo.load_from_json(path, mat_repo)
            assert count == 2
            assert self.repo.get("T1") is not None
            assert self.repo.get("P1") is not None
        finally:
            os.unlink(path)

    def test_save_to_json(self):
        self.repo.add_element(self.el1)
        self.repo.add_element(self.el2)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            self.repo.save_to_json(path)
            with open(path) as f:
                data = json.load(f)
            assert len(data["elements"]) == 2
        finally:
            os.unlink(path)


# ===================================================================
# resolve_verification_inputs
# ===================================================================


class TestResolveInputs:
    def test_empty_repos(self):
        el_repo = ElementRepository()
        mat_repo = MaterialRepository()
        result = resolve_verification_inputs(el_repo, mat_repo, {})
        assert "Nessun elemento nel repository." in result["error_list"]

    def test_with_elements(self):
        el_repo = ElementRepository()
        el_repo.add_element(Element(
            element_id="T1", type="beam", length_cm=500.0,
            additional_params={"b": 30.0, "h": 50.0},
        ))
        mat_repo = MaterialRepository()
        result = resolve_verification_inputs(
            el_repo, mat_repo, {"norm_code": "NTC2018", "project_name": "Test"}
        )
        assert result["project_name"] == "Test"
        assert result["norm_code"] == "NTC2018"
        assert len(result["elements"]) == 1
        assert "Elemento 'T1': materiale non assegnato." in result["error_list"]


# ===================================================================
# HTMLReportRenderer
# ===================================================================


class TestHTMLRenderer:
    def test_empty_data(self):
        r = HTMLReportRenderer()
        html = r.render({})
        assert "<!DOCTYPE html>" in html
        assert "Nessun elemento definito." in html

    def test_with_elements_and_results(self):
        data = {
            "project_name": "Ponte Test",
            "norm_code": "NTC2018",
            "elements": [{"id": "T1", "b": 30, "h": 50}],
            "results": [
                {"action_id": "flexure_check", "ok": True,
                 "messages": ["M_Ed OK"], "partials": {"utilization": 0.5}},
                {"action_id": "shear_check", "ok": False,
                 "messages": ["NON VERIFICATO"], "partials": {"utilization": 1.2}},
            ],
        }
        html = r = HTMLReportRenderer().render(data)
        assert "Ponte Test" in html
        assert "NTC2018" in html
        assert "1/2 verificate" in html
        assert "flexure_check" in html

    def test_escaping(self):
        data = {"project_name": "<script>alert(1)</script>"}
        html = HTMLReportRenderer().render(data)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ===================================================================
# MarkdownReportRenderer
# ===================================================================


class TestMarkdownRenderer:
    def test_empty_data(self):
        r = MarkdownReportRenderer()
        md = r.render({})
        assert "# Report di Verifica" in md
        assert "Nessun elemento definito." in md

    def test_with_results(self):
        data = {
            "project_name": "Test",
            "results": [
                {"action_id": "flexure_check", "ok": True,
                 "messages": ["OK"], "partials": {"utilization": 0.5}},
            ],
        }
        md = MarkdownReportRenderer().render(data)
        assert "**OK**" in md
        assert "1/1 verificate" in md


# ===================================================================
# PDFReportRenderer
# ===================================================================


class TestPDFRenderer:
    def test_render_html_only(self):
        r = PDFReportRenderer()
        html = r.render_html_only({"project_name": "Test"})
        assert "<!DOCTYPE html>" in html

    def test_render_fallback_to_html(self):
        r = PDFReportRenderer()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            result = r.render({"project_name": "Test"}, path)
            # WeasyPrint not available → fallback to HTML
            assert result.endswith(".html")
            assert os.path.exists(result)
        finally:
            if os.path.exists(path):
                os.unlink(path)
            if os.path.exists(result):
                os.unlink(result)


# ===================================================================
# export_results
# ===================================================================


class TestExportResults:
    def test_export_to_json(self):
        data = {"results": [{"action_id": "test", "ok": True}]}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(data, path)
            with open(path) as f:
                loaded = json.load(f)
            assert loaded["results"][0]["ok"] is True
        finally:
            os.unlink(path)

    def test_export_to_csv(self):
        data = {
            "results": [
                {"action_id": "flexure_check", "ok": True,
                 "messages": ["M OK"], "partials": {"utilization": 0.5}},
                {"action_id": "shear_check", "ok": False,
                 "messages": ["NON VERIFICATO"], "partials": {"utilization": 1.2}},
            ]
        }
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            n = export_to_csv(data, path)
            assert n == 2
            with open(path) as f:
                lines = f.readlines()
            assert len(lines) == 3  # header + 2 rows
            assert "flexure_check" in lines[1]
        finally:
            os.unlink(path)

    def test_results_to_table(self):
        results = [
            {"action_id": "test", "ok": True, "messages": ["OK"],
             "partials": {"utilization": 0.5}},
        ]
        table = results_to_table(results)
        assert table[0] == ["#", "Verifica", "Esito", "Utilizzazione", "Note"]
        assert table[1][2] == "OK"
        assert table[1][3] == "0.500"

    def test_empty_results(self):
        data = {"results": []}
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            n = export_to_csv(data, path)
            assert n == 0
        finally:
            os.unlink(path)


# ===================================================================
# Fire check standalone
# ===================================================================


class TestFireCheckStandalone:
    def test_beam_r60(self):
        from src.fire.rc_fire_check import run_fire_check_standalone
        result = run_fire_check_standalone(
            element_type="beam",
            rating_minutes=60,
            b_mm=200.0,
            cover_mm=50.0,
        )
        assert result["ok"] is True

    def test_beam_r60_fail_width(self):
        from src.fire.rc_fire_check import run_fire_check_standalone
        result = run_fire_check_standalone(
            element_type="beam",
            rating_minutes=60,
            b_mm=50.0,
            cover_mm=50.0,
        )
        assert result["ok"] is False
        assert "KO" in result["messages"][0]

    def test_column_r90(self):
        from src.fire.rc_fire_check import run_fire_check_standalone
        result = run_fire_check_standalone(
            element_type="column",
            rating_minutes=90,
            b_mm=350.0,
            cover_mm=55.0,
        )
        assert result["ok"] is True

    def test_column_r90_fail_cover(self):
        from src.fire.rc_fire_check import run_fire_check_standalone
        result = run_fire_check_standalone(
            element_type="column",
            rating_minutes=90,
            b_mm=350.0,
            cover_mm=20.0,
        )
        assert result["ok"] is False

    def test_unknown_high_rating(self):
        from src.fire.rc_fire_check import run_fire_check_standalone
        result = run_fire_check_standalone(
            element_type="beam",
            rating_minutes=999,
            b_mm=500.0,
            cover_mm=100.0,
        )
        # Should not find tabular data for R999
        assert result["ok"] is False
