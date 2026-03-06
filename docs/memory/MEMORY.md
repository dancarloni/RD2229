# MEMORY.md — Indice memoria persistente RD2229

## Fonte di verita'
- `docs/PIANO_LAVORO.md` — stato avanzamento, sub-plan dettagliati, checkbox
- `docs/PIANO_SVILUPPO_CORRENTE.md` — registro sessioni e decisioni Q&A

## File di memoria tematici

| File | Contenuto |
|------|-----------|
| `subplan_D3_traliccio.md` | Cordolo reticolare orizzontale: Q&A completo, decisioni, architettura, dipendenze, file da creare/modificare |
| `subplan_E6_cantonali.md` | Ribaltamento cantonale + riduzione resistenza aperture: Q&A, decisioni, formule, letteratura |
| `subplan_A2_material_source.md` | MaterialSource strutturata: analisi legacy, 3 entita' parallele, migrazione dati |
| `codebase_map.md` | Mappa moduli muratura/acciaio con file, righe chiave, interfacce tra moduli |

## Vincolo: posizione file memoria

- Tutti i file di memoria AI devono risiedere in `docs/memory/` nel repository
- Mai salvare in directory esterne (es. `.claude/projects/...`)
- Aggiornare dopo ogni fase completata

## Convenzioni utente confermate
- Lingua: italiano per UI, commenti, docstring, nomi variabili dominio
- Unita': cm geometria, kg/cm² tensioni (storiche), selezionabile via unita_misura.py
- GUI: SOLO Qt (PySide6/PyQt6), NO Tkinter per codice nuovo
- Legacy: analizzare, estrarre dati utili nella nuova struttura, ELIMINARE file legacy
- Domande: usare formato a scelta multipla, l'utente risponde con lettere
- Modularita': massima, ogni modulo sostituibile senza refactoring globale
- Formule mancanti: TODO + chiedere all'utente, mai inventare
- Test: pytest, ~1838 test attuali, 0 falliti
