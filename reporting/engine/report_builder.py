"""Report builder — Compone la relazione tecnica."""

from typing import Optional


class ReportBuilder:
    """Costruisce la relazione tecnica da risultati raccolti."""

    def __init__(self):
        """Inizializza il builder."""
        self.title = "Relazione Tecnica Strutturale"
        self.sections = []

    def add_section(self, title: str, content: str) -> None:
        """Aggiunge una sezione alla relazione."""
        self.sections.append({"title": title, "content": content})

    def generate_markdown(self) -> str:
        """Genera relazione in formato Markdown."""
        md = f"# {self.title}\n\n"
        for section in self.sections:
            md += f"## {section['title']}\n\n"
            md += f"{section['content']}\n\n"
        return md

    def generate_html(self) -> str:
        """Genera relazione in formato HTML."""
        html = f"<html><body><h1>{self.title}</h1>"
        for section in self.sections:
            html += f"<h2>{section['title']}</h2>"
            html += f"<p>{section['content']}</p>"
        html += "</body></html>"
        return html

    def export_markdown(self, filepath: str) -> None:
        """Esporta relazione in Markdown."""
        md = self.generate_markdown()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

    def export_html(self, filepath: str) -> None:
        """Esporta relazione in HTML."""
        html = self.generate_html()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
