# MANIFESTO GOVERNANCE — RD2229

> **Versione**: 1.0 — 2026-03-01
> **Stato**: VIGENTE

---

## 1. Scopo

Questo documento definisce le regole architetturali minime e le convenzioni di
sviluppo che governano il progetto RD2229.
Ogni contributo al repository deve rispettare questi principi. Nessuna eccezione
senza ADR (Architecture Decision Record) esplicita.

---

## 2. Regole architetturali

### 2.1 No monoliticità

- **Vietato** creare file singoli con più di 800 righe che mescolino responsabilità diverse.
- Ogni modulo ha una sola responsabilità principale (Single Responsibility).
- I moduli legacy in `legacy/` e `tests_legacy/` non devono essere modificati; sono
  segregati per scopo storico.

### 2.2 Segregazione del legacy

- Tutto il codice legacy risiede in `legacy/` (produzione) e `tests_legacy/` (test).
- Il legacy **non blocca** la suite standard di CI: pytest esclude `tests_legacy/`
  per default (vedi `pytest.ini`).
- Nuove funzionalità non devono essere aggiunte al legacy.

### 2.3 CI gating

- La suite di test `tests/` deve essere sempre verde su `main` e su ogni PR.
- I linter (ruff, mypy, flake8) sono informativi (continue-on-error) ma non devono
  peggiorare il conteggio di errori tra release.
- Il masking di test falliti (es. `|| true` su pytest) è **vietato** su `main`.

### 2.4 Documentazione obbligatoria

- Ogni nuovo modulo pubblico deve avere:
  1. Docstring del modulo (primo paragrafo = scopo).
  2. Un file `docs/modules/<nome_modulo>.md` generato tramite `tools/generate_module_docs.py`
     (o scritto manualmente seguendo `docs/templates/MODULO_TEMPLATE.md`).
- La RTM (`docs/RTM/RTM_MASTER.md`) deve essere aggiornata ad ogni nuova feature.

### 2.5 Nessun testo normativo copiato

- **Vietato** copiare testi di norme nel codice sorgente o nella documentazione.
- Sono ammessi solo: riferimenti (ID norma, articolo, paragrafo), link ufficiali,
  metadati descrittivi e hash di file locali lecitamente detenuti.
- Il catalogo delle fonti si gestisce in `docs/NORMATIVE_SOURCES/`.

### 2.6 Tracciabilità

- Ogni verifica strutturale implementata deve riportare la fonte normativa di riferimento
  (ID da `docs/NORMATIVE_SOURCES/sources.catalog.json`).
- Le dipendenze tra requisiti, implementazioni e test si traccia nella RTM.

---

## 3. Definizioni di stato modulo

Questi stati sono usati in `docs/_generated/MODULE_INDEX.md` e in `docs/RTM/RTM_MASTER.md`.

| Stato | Definizione |
|-------|-------------|
| **COMPLETO** | Implementazione verificabile, test unitari presenti, documentazione disponibile, fonti normative tracciate. |
| **PARZIALE** | Implementazione presente ma almeno uno tra test, documentazione o tracciabilità normativa è mancante o incompleto. |
| **INCOMPLETO** | Implementazione avviata ma non funzionale o con parti essenziali mancanti. |
| **STUB** | File/directory presenti ma senza contenuto funzionale (placeholder). |
| **NON PRESENTE** | Funzionalità attesa ma nessun file rilevato. |
| **TBD** | Stato non ancora determinato; richiede revisione manuale. |

---

## 4. Workflow di contribuzione

1. **Feature branch** da `main`.
2. Implementare i cambiamenti.
3. Aggiornare o creare il file `docs/modules/<modulo>.md`.
4. Aggiornare `docs/RTM/RTM_MASTER.md` con le nuove righe rilevanti.
5. Eseguire `python tools/audit_repo.py` per rigenerare `docs/_generated/`.
6. PR verso `main` con CI verde.

---

## 5. Riferimenti

- `docs/RTM/RTM_MASTER.md` — matrice di tracciabilità
- `docs/NORMATIVE_SOURCES/` — catalogo fonti normative
- `docs/_generated/MODULE_INDEX.md` — indice moduli (generato)
- `docs/templates/MODULO_TEMPLATE.md` — template documentazione modulo
- `docs/ADR/` — Architecture Decision Records
