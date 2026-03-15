# Fase X1 — Execution Plan

## Contesto

Questo file raccoglie il contesto persistente e le decisioni per l'esecuzione della Fase X1 (Tipologie e Input Solai). Deve essere aggiornato ogni volta che si prende una decisione o si modifica lo scope.

## Obiettivo

Implementare il parser/validator degli input per i solai in V1 (tutte le tipologie) con:
- schema JSON (documentato in `docs/piano_fase_X1_tipologie_input.md`)
- conversioni unità (cm/​kgf → SI)
- validazione rigorosa (errori se mancano campi obbligatori o se valori non coerenti)
- output in un dataclass `InputSolaio` + warnings (lista codici X1-INPUT-XXX)

## Decisioni chiave (Q&A)

- **Unità input**: cm/kgf/kgf·cm² (con conversione SI all'ingresso delle routine). (Decisione presa in `piano_fase_X1_tipologie_input.md`)
- **Tipologie**: tutte le tipologie elencate (laterocemento, predalles, getto pieno, legno, acciaio, misti).
- **Validazione**: rigorosa (errori bloccanti) + segnali warning quando possibile.

## Stato avanzamento

- [x] Implementazione X1 completata in `src/core_calculus/solaio_input.py` (validazione strict, payload nested `original` + `normalized`)
- [x] Sorgenti dati separate:
  - [x] `data/solai_tipologie.json` (catalogo tipologie)
  - [x] `data/solai_fields.json` (metadata GUI: label, tooltip, unità, norm_ref)
- [x] Test robusti in `tests/test_x1_input.py` con fixture stabile `tests/fixtures/solaio_input_valid.json`
- [x] Gate di validazione eseguito:
  - [x] `PYTHONPATH=. pytest tests/test_x1_input.py -q`
  - [x] Review diff manuale
  - [x] Controllo coerenza codici issue `X1-INPUT-00N`

**TODO:**
- [ ] Aggiornare la documentazione se cambiano struttura JSON o codici warning
- [ ] Aggiornare test/fixture se cambiano i requisiti di validazione

---

## File creati/modificati (Fase X1)

- `src/core_calculus/solaio_input.py`  ✅
- `data/solai_tipologie.json`           ✅
- `data/solai_fields.json`              ✅
- `tests/test_x1_input.py`              ✅
- `tests/fixtures/solaio_input_valid.json` ✅
- `docs/piano_fase_X1_tipologie_input.md` ✅
- `docs/memory/fase_X1_execution.md`    ✅ (questo file)

---

## Dipendenze

- Dipende da:
  - `src/core_calculus/solaio_input.py` (core parser/validator)
  - `data/solai_tipologie.json` (catalogo tipologie solai)
  - `data/solai_fields.json` (metadata campi solai)
  - `tests/test_x1_input.py` (test di validazione)
  - `tests/fixtures/solaio_input_valid.json` (fixture di test)
  - `docs/piano_fase_X1_tipologie_input.md` (specifica di riferimento)

---

## Note sull'EXECUTE

- L'EXECUTE (codice generato automaticamente) deve essere in grado di riprodurre il comportamento descritto nella sezione "Spec eseguibile".
- Qualsiasi cambiamento alla struttura JSON o ai codici warning deve essere tracciato in questo file.

## Esito implementazione corrente

- Modello data-driven senza hardcode tipologie nel core. ✅
- Validazione strict con aggregazione completa errori. ✅
- Output pronto per X2/X3 con struttura nested stabile. ✅
- Logging alto con tracciamento passaggi principali nel registro centrale. ✅
