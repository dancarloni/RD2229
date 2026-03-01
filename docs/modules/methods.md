<<<<<<< HEAD
# Modulo: `methods`

## 1. Scopo e ambito

Implementazione delle verifiche strutturali normative: RD2229 (metodo TA), DM96 (TA/SLU/SLE), NTC2018 (SLU/SLE), incendio DM96/EC2. Dispatcher e controller per routing normativo.

## 2. Stato reale

**COMPLETO**

Motivazione oggettiva: `checks_rd2229.py` (1443 righe), `checks_dm96.py` (1483 righe), `checks_ntc2018.py` (809 righe), `checks_fire_dm96.py` (369 righe) hanno implementazione reale con formule strutturali. Status esplicito "COMPLETE" o "IMPROVED" nel codice. Test su 6+ file.

## 3. Evidenze

- `src/methods/checks_rd2229.py` — `check_flessione_ta_rett()` (COMPLETE), `check_pressoflessione_ta_rett()` (IMPROVED PARTIAL), `check_taglio_ta_rett()`, `check_minimi_armatura_ta()`
- `src/methods/checks_dm96.py:8-9` — "DM96-specifiche", riferimento "EC2 Parte 1-1" alla riga 24
- `src/methods/checks_ntc2018.py` — check SLU/SLE NTC2018
- `src/methods/checks_fire_dm96.py` — fire DM96/EC2 Parte 1-2
- `src/methods/verification/dispatcher.py` — routing verifiche
- Test: `tests/test_rd2229_checks.py`, `tests/test_dm96_checks.py`, `tests/test_ntc2018_checks.py`, `tests/test_fire_checks.py`, `tests/test_ta_method.py`, `tests/test_golden_rd2229.py`

## 4. Input/parametri

- `check_flessione_ta_rett(b, h, As, fck, fyk, MEd, sigma_c_adm, sigma_s_adm) -> dict`
- Parametri specifici per ogni tipo di verifica

## 5. Output

- `dict` con: `passed: bool`, `ratio: float`, `details: dict`, messaggi

## 6. Dipendenze

- `src/methods/checks_rd2229.py` — autosufficiente
- `src/methods/verification/dispatcher.py` — importa da `app.domain.models` (percorso legacy)
- `src/methods/verification/engine_adapter.py` — NTC2018

## 7. Fonti normative collegate

| ID | Evidenza nel codice |
|----|---------------------|
| RD2229 | `src/methods/checks_rd2229.py` — estensivamente |
| DM92 | `src/methods/checks_dm96.py:73-77` — "sigma_c_adm_kg_cm2 ecc. DM92" |
| DM96 | `src/methods/checks_dm96.py:8-9` — "Check TA DM96", "Check SLU DM96" |
| NTC2018 | `src/methods/checks_ntc2018.py`, `verification/engine_adapter.py` |
| EC2 Parte 1-1 | `src/methods/checks_dm96.py:24` — "EC2 Parte 1-1 (formule generali)" |
| EC2 Parte 1-2 | `src/methods/checks_fire_dm96.py` — fire design |

Clausole: TBD (non compaiono come §articolo verificabile nel codice delle funzioni).

## 8. Gap/TODO/Limitazioni

- `checks_rd2229.py:check_pressoflessione_ta_rett()` marcato "IMPROVED PARTIAL" — dominio di interazione non completo
- `dispatcher.py` importa da `app.domain.models` (percorso legacy/esterno)
- Alcune funzioni in `checks_dm96.py` marcate "PARTIAL+" — copertura non totale

## 9. Next steps

- [ ] Completare dominio di interazione M-N in `check_pressoflessione_ta_rett()`
- [ ] Riallineare importazioni di `dispatcher.py` da `app.domain` a `src.domain`
- [ ] Aggiungere test golden con valori attesi per DM96 SLE
=======
# Documentazione Modulo: `methods`

> **Generato automaticamente** da `tools/generate_module_docs.py` — 2026-03-01 00:52 UTC
> Stub iniziale: compilare manualmente le sezioni TBD.
> Non eliminare questo file; aggiornarlo incrementalmente.

---

## 1. Identificazione

| Campo | Valore |
|-------|--------|
| **Nome modulo** | `methods` |
| **Path** | `src/methods` |
| **Tipo** | package |
| **File .py rilevati** | 15 |
| **Stato** | INCOMPLETO |
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
| — | — | Nessun test rilevato meccanicamente. |

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
