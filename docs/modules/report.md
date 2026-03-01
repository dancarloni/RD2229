# Modulo: `report`

## 1. Scopo e ambito

Renderer report alternativi (HTML, Markdown, PDF) con interfaccia `ReportData` → stringa. Diverso da `src/reporting/` che è il modulo di reporting principale.

## 2. Stato reale

**STUB**

Motivazione oggettiva: Tutti e tre i renderer sono marcati STUB S2. `renderer_html.py`: `render()` → `# TODO: implement`. `renderer_pdf.py`: `render()` → `raise NotImplementedError("PDF rendering non implementato (stub).")`. `renderer_md.py` ha minima logica string-building.

## 3. Evidenze

- `src/report/renderer_html.py` — "STUB S2"; `render()` TODO
- `src/report/renderer_pdf.py` — "STUB S2"; `render()` → NotImplementedError
- `src/report/renderer_md.py` — "STUB S2"; restituisce header minimale
- `src/report/templates/` — template HTML/MD presenti ma non usati da renderer
- Test: `src/tests/test_reporting.py` (STUB S2)

## 4. Input/parametri

- `ReportData` dataclass: TBD (campi non documentati)
- `render(data: ReportData) -> str`

## 5. Output

- `str` — contenuto HTML/MD/PDF

## 6. Dipendenze

- Importato da `src/tools/verify_cli.py` (anche questo STUB)
- Non usato dal pipeline principale (che usa `src/reporting/report_builder.py`)

## 7. Fonti normative collegate

Nessuna trovata nel codice del modulo.

## 8. Gap/TODO/Limitazioni

- HTML e PDF renderers completamente non funzionali
- Template in `templates/` non usati dai renderer
- Dualismo con `src/reporting/` (che è funzionale) crea confusione architetturale

## 9. Next steps

- [ ] Chiarire se `src/report/` debba sostituire o integrare `src/reporting/`
- [ ] Implementare `renderer_html.py` usando i template in `templates/`
- [ ] Eliminare dualismo oppure deprecare uno dei due moduli
