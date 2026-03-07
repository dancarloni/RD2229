# MEMORY.md — Indice memoria persistente RD2229

## Fonte di verita'

- `docs/PIANO_LAVORO.md` — stato avanzamento, sub-plan dettagliati, checkbox
- `docs/PIANO_SVILUPPO_CORRENTE.md` — registro sessioni e decisioni Q&A

## File di memoria tematici

| File | Contenuto |
| ---- | --------- |
| `subplan_O_spettro_ntc2018.md` | FASE O: gap critico spettro NTC2018, catena §3.2.3, Tab. SS/ST/Cu, architettura spectrum.py, integrazione INGV + spectrum_paste_service |
| `subplan_multinorm_seismic.md` | FASE O.3: azioni sismiche multinorma (src/codes/seismic/), 7 norme, forza base + distribuzione piani, 54 test |
| `subplan_fase_I.md` | FASE I: sezioni parametri statici (n per norma, omogenizzata, fessurata, SLE, IPE composita, disegno matplotlib), 91 test |
| `subplan_D3_traliccio.md` | Cordolo reticolare orizzontale: Q&A completo, decisioni, architettura, dipendenze, file da creare/modificare |
| `subplan_E6_cantonali.md` | Ribaltamento cantonale + riduzione resistenza aperture: Q&A, decisioni, formule, letteratura |
| `subplan_A2_material_source.md` | MaterialSource strutturata: analisi legacy, 3 entita' parallele, migrazione dati |
| `subplan_fase_J.md` | FASE J: pressoflessione deviata multinorma (6 norme), dominio 3D, TA+SLU, instabilita' biassiale, 70 test |
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
- Test: pytest, ~2093 test attuali, 0 falliti
