# COMPLIANCE OVERVIEW – RD2229

## Usabilità Reale per Modulo

> **Metodologia**: questo documento deriva direttamente da `docs/RTM/RTM_MASTER.md` e `docs/modules/*.md`.
> "Utilizzabile in pratica?" = SI se il modulo ha entry point funzionante + test + nessun TODO critico nelle funzioni core.
> Data: 2026-03-01 | Moduli analizzati: 27

---

## Tabella Usabilità

| Modulo | Stato | Norme (ID) | Utilizzabile in pratica? | Limitazioni principali |
|--------|-------|------------|--------------------------|------------------------|
| **actions** | STUB | — | NO | `run()` → NotImplementedError; nessun test |
| **calc** | STUB | — | NO (solo fallback κ=5/6) | `SECTION_REGISTRY` vuoto; gestori forme TODO |
| **checks** | PARZIALE | RD2229, DM96, NTC2018 | Solo pre-studio | Registry infrastruttura reale; tutti `compute=None` |
| **cli** | PARZIALE | RD2229 | SI (comandi base) | `run`/`export` dipendono da pipeline incompleta |
| **codes** | PARZIALE | NTC2018 | Solo pre-studio | `code_registry.py` STUB; `spectrum_paste_service` SI |
| **config** | STUB | — | NO | Solo YAML; nessuna API Python |
| **core** | PARZIALE | NTC2018, RD2229 | SI (pipeline base) | `ntc2018_combinations` SKELETON; Step5 parziale |
| **core_calculus** | COMPLETO | NTC2018, RD2229, DM96, EC2 | SI | Tabella fire asse-distanza non caricata da file |
| **domain** | PARZIALE | — | Solo pre-studio | Test non usano `src.domain` come percorso |
| **elements** | STUB | — | NO | Repository tutto TODO |
| **fire** | PARZIALE | EN1992_1_2, NTC2018 | SI (eligibility+curva) | Tabella asse-distanza placeholder |
| **gui** | INCOMPLETO | RD2229, NTC2018 | Solo pre-studio | `secondary_elements/` quasi vuoti |
| **launcher** | INCOMPLETO | RD2229 | NO | Dipende da `apps/` fuori src; nessun `__init__.py` |
| **legacy** | COMPLETO | TBD | SI (legacy app Tkinter) | DO NOT MODIFY; non testato nella nuova suite |
| **materials** | STUB | — | NO | Repository tutto TODO |
| **methods** | COMPLETO | RD2229, DM92/96, NTC2018, EC2 | SI | `check_pressoflessione` PARZIALE; `dispatcher` percorso legacy |
| **plugins** | COMPLETO | RD2229 | SI | Plugin `run`/`export` dipendono da pipeline |
| **project** | COMPLETO | RD2229, NTC2018 | SI | Dipendenza Pydantic ≥ 2.0 (non sempre in CI) |
| **rd2229** | PARZIALE | RD2229, RD2229_39, NTC2018 | SI (MVP + seismic) | UI non headless; `cli.py` dipende da `app/` |
| **report** | STUB | — | NO | HTML/PDF TODO; solo MD minimale |
| **reporting** | COMPLETO | RD2229, NTC2018 | SI | Solo HTML+MD (no PDF); no grafici |
| **repositories** | STUB | — | NO | Solo dati JSON; nessuna API |
| **tests** (src/) | PARZIALE | — | SI (come smoke test) | Solo STUB coverage |
| **tools** (src/) | STUB | — | NO | Tutte le funzioni chiave TODO |
| **ui** | PARZIALE | RD2229 | Solo pre-studio (headless) | Widget Qt skeleton; PyQt6 opzionale |
| **utils** | COMPLETO | — | SI | Solo Tkinter callback; no equivalente Qt |
| **wind** | PARZIALE | NTC2018, EN1991_1_4, CNR_DT207 | SI (calcolo base) | Parametri zona placeholder; Cd non implementato |

---

## Riepilogo per Utilizzo Pratico

### Moduli utilizzabili in produzione (SI)

| Modulo | Caso d'uso | Vincoli |
|--------|------------|---------|
| **cli** | CLI base (new/load/info) | run/export non completati |
| **core** | Pipeline calcolo strutturale base | Step NTC2018 combinations SKELETON |
| **core_calculus** | Verifiche TA/SLU/SLE/fire sezioni CA | Tabella fire da completare |
| **fire** | Curva incendio ISO 834 + eligibility | Tabella asse-distanza da caricare |
| **legacy** | Applicazione Tkinter storica completa | DO NOT MODIFY; solo Tkinter |
| **methods** | Verifiche RD2229/DM96/DM92/NTC2018 | pressoflessione dominio incompleto |
| **plugins** | Sistema plugin con discovery | Plugin run/export dipendono da pipeline |
| **project** | Caricamento/salvataggio ProjectModel | Pydantic ≥ 2.0 richiesto |
| **rd2229** | MVP pipeline + seismico RD2229/1939 | UI non headless |
| **reporting** | Generazione report HTML+MD | No grafici, no PDF |
| **utils** | BackgroundExecutor threading | Solo Tkinter callback |
| **wind** | Calcolo vento NTC2018/EN/CNR | Parametri zona da completare |

### Moduli solo per pre-studio / non in produzione (Solo pre-studio / NO)

| Modulo | Motivo |
|--------|--------|
| **actions** | STUB — NotImplementedError |
| **calc** | STUB — registro vuoto |
| **checks** | Infrastruttura senza calcoli |
| **codes** | `code_registry` STUB |
| **config** | Solo YAML senza API |
| **domain** | Test disallineati |
| **elements** | Repository TODO |
| **gui** | Widget quasi vuoti |
| **launcher** | Percorso rotto |
| **materials** | Repository TODO |
| **report** | HTML/PDF TODO |
| **repositories** | Solo dati, no API |
| **tools** (src/) | Tutte funzioni TODO |
| **ui** | Widget skeleton; PyQt6 opzionale |

---

## Note su CI / Build Failures

**KNOWN LIMITATIONS (pre-esistenti, non risolvibili in questa sub-issue):**

1. **Pydantic mancante**: alcuni test che importano `src/project/schema.py` richiedono `pydantic >= 2.0` non sempre installata in CI. Vedere issue debito tecnico separata.
2. **Tkinter in CI headless**: test che usano Tkinter vengono ignorati via `conftest.py` (`_TKINTER_DEPENDENT`).
3. **PyQt6 in CI**: test GUI marcati `@pytest.mark.gui` vengono esclusi con `-m "not gui"`.
4. **`app/` fuori src/**: `src/launcher/bootstrap.py` e `src/rd2229/cli.py` dipendono da `apps.sections.app` — non risolvibile senza refactoring.

---

## Come Rigenerare

```bash
python tools/rtm_build.py
```

Genera `docs/RTM/RTM_MASTER.md` e aggiorna questo file con analisi statica del repo.
Non esegue codice del progetto — solo analisi testuale/import.

---

*Per dettagli per modulo: `docs/modules/<modulo>.md`*
*Per fonti normative: `docs/NORMATIVE_SOURCES/sources.catalog.json`*
*Per RTM completa: `docs/RTM/RTM_MASTER.md`*
