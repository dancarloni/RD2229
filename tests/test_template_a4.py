"""Test per il template A4 del report professionale."""

from src.report.template_a4 import TemplateA4


def test_template_css_contains_a4_print_rules():
    template = TemplateA4()
    css = template.css()

    assert "@page" in css
    assert "size: A4" in css
    assert ".a4-page" in css
    assert ".rd2229-footer .page-number::after" in css


def test_render_header_and_footer_include_metadata():
    template = TemplateA4()

    header = template.render_header(
        progetto="Relazione Prova",
        professionista="Ing. Rossi",
        committente="Comune",
        numero_pratica="Q-001",
        data_stampa="2026-03-11",
    )
    footer = template.render_footer(data_stampa="2026-03-11")

    assert "Relazione Prova" in header
    assert "Ing. Rossi" in header
    assert "Comune" in header
    assert "Q-001" in header
    assert "2026-03-11" in footer
    assert "page-number" in footer
    assert "page-total" in footer


def test_render_single_page_wraps_header_content_footer():
    template = TemplateA4()
    page = template.render_page(
        content_html="<p>Contenuto tecnico</p>",
        header_html="<header>HEADER</header>",
        footer_html="<footer>FOOTER</footer>",
        page_id="pag-1",
    )

    assert 'class="a4-page"' in page
    assert 'id="pag-1"' in page
    assert "HEADER" in page
    assert "Contenuto tecnico" in page
    assert "FOOTER" in page


def test_render_document_includes_all_pages_and_css():
    template = TemplateA4()
    page_1 = template.render_page(
        content_html="<p>Pagina uno</p>",
        header_html="<header>H1</header>",
        footer_html="<footer>F1</footer>",
    )
    page_2 = template.render_page(
        content_html="<p>Pagina due</p>",
        header_html="<header>H2</header>",
        footer_html="<footer>F2</footer>",
    )

    html = template.render_document(title="Relazione A4", pages_html=[page_1, page_2])

    assert "<!DOCTYPE html>" in html
    assert "<title>Relazione A4</title>" in html
    assert "<style>" in html
    assert html.count('class="a4-page"') == 2
    assert "Pagina uno" in html
    assert "Pagina due" in html
