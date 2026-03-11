# PIANO DI LAVORO — RD2229 Software di Calcolo Strutturale

## Vincoli operativi permanenti

> **Introdotti il 2026-03-08 — sessione chat Copilot (utente: DanieleCarloni)**

**Vincolo operativo obbligatorio (hard constraint) — applicato a tutto il workspace:**

- **Sessione unica:** Tutte le attività di sviluppo, pianificazione, revisione e Q&A devono essere completate in una singola sessione di chat, senza interruzioni, per ottimizzare l’uso delle risorse premium e garantire la massima tracciabilità e coerenza delle decisioni.
- **Domande a scelta multipla obbligatorie:** Prima di ogni fase operativa, l’agent deve sempre proporre all’utente una serie di domande a scelta multipla (cliccabili), con possibilità di inserire note libere, per:
  - chiarire le intenzioni,
  - perfezionare le proposte,
  - raccogliere preferenze e vincoli,
  - evitare ambiguità o assunzioni arbitrarie.
- **Tracciabilità e storicizzazione:** Tutte le domande, risposte e decisioni devono essere riportate e storicizzate in questo file, con riferimento alla sessione e al contesto operativo.
- **Blocco esecuzione:** Nessuna implementazione o modifica può essere avviata senza che l’utente abbia risposto a tutte le domande proposte.
- **Applicazione universale:** Questi vincoli sono validi per tutte le fasi, sub-fasi, moduli e task del workspace, senza eccezioni.
- **Visibilità e permanenza:** L’agent deve aggiungere una sezione ben visibile all’inizio di questo file (“Vincoli operativi permanenti”) che riporti integralmente questi vincoli, con data di introduzione e riferimento alla sessione/chat che li ha generati. Ogni modifica o deroga deve essere tracciata e motivata in questa sezione.
- **Nota:** L’agent deve sempre ricordare e far rispettare questi vincoli in ogni prompt, output e proposta operativa.

---

## Stato Generale

| Indicatore         | Valore  |
|--------------------|---------|
| Test totali        | 2449    |
| Test falliti       | 0       |
| Moduli implementati| 83+     |
| Norme coperte      | 10      |

---

## Avanzamento fasi

| Fase | Stato | %   | Ultimo commit | Dettaglio                |
|------|-------|-----|---------------|--------------------------|
| A    | ✅    | 100 | a0f05aa       | [piano_fase_A.md](piano_fase_A.md) |
| B    | ✅    | 100 | bdd8c6a       | [piano_fase_B.md](piano_fase_B.md) |
| C    | ✅    | 100 | c24f6f2       | [piano_fase_C.md](piano_fase_C.md) |
| D    | ✅    | 100 | 368910a       | [piano_fase_D.md](piano_fase_D.md) |
| E    | ✅    | 100 | 0b9a83d       | [piano_fase_E.md](piano_fase_E.md) |
| F    | ✅    | 100 | 1b5e32d       | [piano_fase_F.md](piano_fase_F.md) |
| G    | ✅    | 100 | 394dc31       | [piano_fase_G.md](piano_fase_G.md) |
| H    | ✅    | 100 | 99aaf55       | [piano_fase_H.md](piano_fase_H.md) |
| I    | ✅    | 100 | 3bed1a7       | [piano_fase_I.md](piano_fase_I.md) |
| J    | ✅    | 100 | 73482f0       | [piano_fase_J.md](piano_fase_J.md) |
| K    | ✅    | 100 | 23f60cf       | [piano_fase_K.md](piano_fase_K.md) |
| L    | ✅    | 100 | f041b45       | [piano_fase_L.md](piano_fase_L.md) |
| M    | ✅    | 100 | <hash-cloud>  | [piano_fase_M.md](piano_fase_M.md) |
| N    | ✅    | 100 | 8f52479       | [piano_fase_N.md](piano_fase_N.md) |
| O    | ✅    | 100 | 3d560d3       | [piano_fase_O.md](piano_fase_O.md) |
| P    | ✅    | 100 | —             | [piano_fase_P.md](piano_fase_P.md) |
| Q    | ⬜    | 0   | —             | [piano_fase_Q.md](piano_fase_Q.md) |
| R    | ⬜    | 0   | —             | [piano_fase_R.md](piano_fase_R.md) |
| S    | ⬜    | 0   | —             | [piano_fase_S.md](piano_fase_S.md) |
| T    | ⬜    | 0   | —             | [piano_fase_T.md](piano_fase_T.md) |
| U    | ⬜    | 0   | —             | [piano_fase_U.md](piano_fase_U.md) |
| V    | ⬜    | 0   | —             | [piano_fase_V.md](piano_fase_V.md) |
| W    | ⬜    | 0   | —             | [piano_fase_W.md](piano_fase_W.md) |
| Y    | ⬜    | 0   | —             | [piano_fase_Y.md](piano_fase_Y.md) |
| X    | ⬜    | 0   | —             | [piano_fase_X.md](piano_fase_X.md) |

---

## Attività completate

| Data       | Fase | Subfase   | Commit  | Note sintetica                                                                                              |
|------------|------|-----------|---------|-------------------------------------------------------------------------------------------------------------|
| 2026-03-07 | A    | A.2.9     | a0f05aa | Test cataloghi materiali superati                                                                           |
| ...        | ...  | ...       | ...     | ...                                                                                                         |
| 2026-03-08 | Q    | Q.0       | —       | Storicizzazione domande/risposte/decisioni in [piano_fase_Q.md](piano_fase_Q.md) — % completamento: 0%      |
| 2026-03-09 | K    | K.1–K.4   | 23f60cf | Fase K completa: grafici, inviluppi, dominio interazione, spostamenti, export HTML                          |
| 2026-03-09 | L    | L.1–L.10  | f041b45 | Fase L completa: telai piani Cross-Pozzati, GUI Qt, 40 test                                                 |
| 2026-03-10 | X    | X.0       | —       | Creazione file piano_fase_X.md, separazione solai da Fase M, storicizzazione checklist e requisiti (sessione Copilot) |
| 2026-03-10 | M    | M.1       | —       | Implementato nucleo locale FEM beam 2D (`src/fem/elemento_beam.py`), carichi equivalenti modulari, 16 test dedicati superati |
| 2026-03-10 | M    | M.2–M.7   | <hash-cloud> | Completata pipeline FEM 2D (`src/fem/assemblaggio.py`, `condizioni_contorno.py`, `solutore.py`, `postprocessing.py`, `src/grafici/spostamenti.py`), 2350+ test aggiuntivi, validazione Cross-Pozzati, benchmark, storicizzazione |
| 2026-03-10 | P    | P.1 + P.2 (avvio) | — | Avviata Fase P geotecnica: creato package `src/geotecnica` (models, utils, norme, fondazioni_superficiali, cedimenti), decisioni architetturali recepite (kg/cm² + conversione, DA1 set1/set2, Robertson-Campanella default), 12 test mirati verdi |
| 2026-03-10 | P    | P.3–P.5 + P.6 | — | Completata Fase P: implementati `pali.py` (argilla/SPT/CPT, gruppo Converse-Labarre), `muri_sostegno.py` (Rankine, Coulomb, ribaltamento, scorrimento), `liquefazione.py` (CSR, CRR, MSF, IL, classificazione); 71 nuovi test (83 totali Fase P); aggiornato `__init__.py` e `models.py` con nuovi dataclass |

---

## Istruzioni operative

Per dettagli, consultare i file docs/piano_fase_X.md, docs/piano_fase_Y.md e docs/piano_fase_V.md corrispondenti a ciascuna fase.
La nuova fase X (solai) è documentata in [piano_fase_X.md](piano_fase_X.md), separata dalla Fase M (FEM) a partire dal 2026-03-10 (sessione Copilot).
La nuova fase Y (aree di influenza) è documentata in [piano_fase_Y.md](piano_fase_Y.md), centralizzando la logica condivisa tra solai, scale e fondazioni (decisione 2026-03-10, sessione Copilot).
