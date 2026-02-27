"""
test_reporting.py

Test minimi dei renderer Markdown e HTML.
"""

from src.report.renderer_html import HTMLReportRenderer
from src.report.renderer_md import MarkdownReportRenderer


def test_md_renderer_basic():
    renderer = MarkdownReportRenderer("src/report/templates/template.md")
    result = renderer.render({"elements": [], "results": []})
    assert isinstance(result, str)
    assert "Report di Verifica" in result


def test_html_renderer_basic():
    renderer = HTMLReportRenderer("src/report/templates/template.html")
    result = renderer.render({"elements": [], "results": []})
    assert "<html>" in result
    assert "</html>" in result
