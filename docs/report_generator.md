# Generatore Relazione Professionale (Fase Q)

## Panoramica

Il modulo `src/report` genera una relazione di calcolo professionale in formato A4 con:

- sezioni obbligatorie (dati generali, materiali, azioni, analisi, verifiche, risultati, conclusioni)
- citazioni normative automatiche con appendice
- integrazione di sezioni dinamiche via decoratore `@contribuisce_report`
- personalizzazione sezioni e salvataggio profilo JSON
- export HTML, Markdown, ASCII; PDF e DOCX opzionali

## API principale

```python
from src.report.report_builder import ReportConfig, build_report
from src.report.export import export_html, export_md, export_ascii

artifact = build_report(project, results, ReportConfig(include_comparison=True))
export_html(artifact, "out/relazione.html")
export_md(artifact, "out/relazione.md")
export_ascii(artifact, "out/relazione.txt")
```

## Citazioni normative

Le citazioni sono estratte da `ResultsModel` (anche da dizionari annidati) e aggregate in appendice.

Funzioni utili:

- `collect_citations(source)`
- `build_citation_index(citations)`
- `render_formula_note(citation, citation_index)`
- `render_appendice(citations)`

## Sezioni dinamiche

Esempio registrazione automatica:

```python
from src.report.decorators import contribuisce_report

@contribuisce_report(key="allegato_speciale", order=850)
def build_special_section(project, results):
    return "## Allegato speciale\n\nContenuto tecnico..."
```

## Personalizzazione sezioni

```python
from src.report.custom import save_section_profile, load_section_profile

save_section_profile("report_profile.json", ["dati_generali", "verifiche", "conclusioni"])
sections = load_section_profile("report_profile.json")
```

## Export opzionali

- PDF: richiede `weasyprint`
- DOCX: richiede `python-docx`

Se la dipendenza non e disponibile viene restituito errore con istruzioni installazione.

## GUI Qt

Il widget `src/ui/qt/report_widget.py` supporta:

- checklist sezioni
- riordinamento drag-and-drop
- upload immagini
- anteprima HTML A4
- export multi-formato
- salvataggio/caricamento profilo sezioni

## Esempi

Esempi di progetto per test/report:

- `tests/real_projects/trave_ca_ntc2018.json`
- `tests/real_projects/pilastro_ca_dm96.json`
- `tests/real_projects/telaio_piano_rd2229.json`
