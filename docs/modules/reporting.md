# Modulo: `reporting`

## 1. Scopo e ambito

Generazione e export del report di verifica strutturale: `build_report()` costruisce `ReportArtifact` con contenuto HTML e Markdown; `export_report_html()` e `export_report_md()` scrivono su file.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `report_builder.py` (440 righe) ha logica reale di costruzione report (string templates, timestamp, info progetto, warnings, risultati elementi). `export.py` (74 righe) ha I/O file reale. Integrato nel CLI e nei servizi UI. Test presenti.

## 3. Evidenze

- `src/reporting/report_builder.py` — `build_report(project, results) -> ReportArtifact`
- `src/reporting/export.py` — `export_report_html()`, `export_report_md()`
- `src/reporting/__init__.py` — re-esporta tutte le API pubbliche
- Chiamato da `src/cli/entrypoint.py` comando `export`
- Test: `tests/test_reporting_smoke.py`, `tests/test_fire_selection_eligibility.py`

## 4. Input/parametri

- `build_report(project: ProjectModel, results: ResultsModel) -> ReportArtifact`
- `export_report_html(artifact: ReportArtifact, path: str)`
- `export_report_md(artifact: ReportArtifact, path: str)`

## 5. Output

- `ReportArtifact` — `html: str`, `markdown: str`, `metadata: dict`
- File HTML/MD su disco

## 6. Dipendenze

- `src/project/schema.py` — `ProjectModel`
- `src/core/results.py` — `ResultsModel`
- `src/cli/entrypoint.py` — consumer principale

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/reporting/report_builder.py` — `norm_code` default |
| NTC2018 | `src/reporting/export.py` — header report |

Clausole: TBD.

## 8. Gap/TODO/Limitazioni

- Nessun rendering grafico (diagrammi M/V/N) nel report
- Template report minimale (string concatenation, no Jinja2)
- `export_report_pdf()` non presente (solo HTML e MD)

## 9. Next steps

- [ ] Aggiungere sezione risultati dettagliati per elemento nel report
- [ ] Considerare template Jinja2 per report HTML più strutturato
- [ ] Aggiungere test con contenuto atteso specifico (verifica presenza norm_code nel report)
