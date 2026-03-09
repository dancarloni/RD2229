# Audit iniziale — consolidamento geometry/graphics

Data: 2026-02-14
Autore: Copilot (automated)

## Sommario rapido

Questo file elenca i file chiave, lo stato corrente (canonical / duplicate / test-covered) e le azioni raccomandate immediate.

## Inventario file critici

- `src/core_calculus/core/geometry_model.py`
  - Ruolo: modello dati canonico per sezioni polygon-based
  - Test presenti: `tests/test_core_improved.py`, `tests/test_geometry_model_extra.py`
  - Docs: da collegare a `docs/geometry.md`
  - Stato: CANONICO — **azione**: aggiungere docstring + esempi

- `src/core_calculus/section_calculations.py`
  - Ruolo: calcoli geometrici e conversioni Section→SectionGeometry
  - Test presenti: `tests/test_section_calculations.py`, `tests/test_section_calculations_extra.py`
  - Docs: da creare `docs/section-calculations.md`
  - Stato: CANONICO — **azione**: aggiungere test di regressione / rotazioni / fori

- `apps/sections/section_graphics.py`
  - Ruolo: controller grafico (world→screen + primitive draw)
  - Test presenti: `tests/test_section_graphics_fake_canvas.py`, `tests/test_graphics_flags.py`
  - Docs: da creare `docs/graphics.md` + demo script
  - Stato: CANONICO — **azione**: completare esempi e test headless

- `apps/sections/models/sections.py`
  - Ruolo: modelli Section usati dagli adattatori
  - Test presenti: parziali (varie test suite integration)
  - Stato: USATO — **azione**: verificare mapping attributi → SectionGeometry

## Gap / priorità immediata

1. Test di regressione numerica per `section_calculations` (rotazioni, fori, degenerati).
2. Documentazione API per `geometry_model` e `section_calculations` (doctest + snippet).
3. Esempi demo per GUI + test headless estesi.

## Azioni immediate (da eseguire ora)

- [x] Salvare questo audit in `docs/audit_report.md`.
- [ ] Aggiungere `docs/geometry.md` e `docs/section-calculations.md` (skeleton).
- [ ] Implementare 6–8 unit tests aggiuntivi per `section_calculations` (casi limite e rotazioni).
- [ ] Aggiornare `mkdocs.yml` per includere le nuove pagine docs.

## Note per reviewer

- La consolidazione principale è già sulla branch `consolidate/geometry-graphics-and-docs` (PR #22).
- Consiglio di approvare PR docs + audit come primo passo (basso impatto) prima di toccare i calcoli numerici.

---

Prossimo step eseguibile: creare skeleton delle pagine docs e aggiungere i test prioritari per `section_calculations` (se vuoi procedo io ora).
