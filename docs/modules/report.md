<<<<<<< HEAD
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
=======
# Documentazione Modulo: `report`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `report` |
| **Path** | `src/report` |
| **Tipo** | package |
| **File .py rilevati** | 5 |
| **Stato** | PARZIALE |
| **Maintainer** | TBD |
| **Ultima revisione** | 2026-03-01 |

---

## 2. Scopo

> Descrivere in 2-3 righe il *perché* esiste questo modulo e quale problema risolve.

TBD

---

## 3. File / Classi / Funzioni principali

> Elencare i simboli pubblici rilevanti. Non inventare: se non si conosce la firma esatta, annotare TBD.

| File | Classe/Funzione | Descrizione |
|------|-----------------|-------------|
| TBD | TBD | TBD |

---

## 4. Input / Output

| Direzione | Formato | Descrizione |
|-----------|---------|-------------|
| Input | TBD | TBD |
| Output | TBD | TBD |

---

## 5. Test correlati

| File test | Copertura stimata | Note |
|-----------|-------------------|------|
| `tests/test_mvp_report_builder.py` | TBD | — |
| `tests/test_reporting_smoke.py` | TBD | — |

---

## 6. Fonti normative

> Solo riferimenti a ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`. NESSUN testo copiato.

| ID fonte | Clausola/Articolo | Nota |
|----------|-------------------|------|
| TBD | TBD | — |

---

## 7. Dipendenze interne

> Moduli `src/` da cui questo modulo dipende (import diretti).

- TBD

---

## 8. Note e TODO

- [ ] Compilare sezioni TBD
- [ ] Verificare test correlati
- [ ] Tracciare fonti normative di riferimento
>>>>>>> d5ef881 (feat: audit/docs infrastructure - audit_repo, RTM, governance, normative catalog, module docs)
