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
| Test totali        | 2717    |
| Test falliti       | 6       |
| Test saltati       | 7       |
| Moduli implementati| 95+     |
| Norme coperte      | 10      |

**Nota:**
- I test falliti sono dovuti a errori di importazione della CLI (`typer` non trovato) e a un test FEM che non solleva l’eccezione attesa.
- I test saltati sono legati a dipendenze opzionali non presenti (PyQt6/PySide6, Hypothesis, Shapely).

---

## Avanzamento fasi

| Fase | Stato | %   | Ultimo commit | Dettaglio                | Argomento |
|------|-------|-----|---------------|--------------------------|-----------|
| A    | ✅    | 100 | a0f05aa       | [piano_fase_A.md](piano_fase_A.md) | Setup progetto |
| B    | ✅    | 100 | bdd8c6a       | [piano_fase_B.md](piano_fase_B.md) | Materiali storici |
| C    | ✅    | 100 | c24f6f2       | [piano_fase_C.md](piano_fase_C.md) | Sezioni strutturali |
| D    | ✅    | 100 | 368910a       | [piano_fase_D.md](piano_fase_D.md) | Carichi e combinazioni |
| E    | ✅    | 100 | 0b9a83d       | [piano_fase_E.md](piano_fase_E.md) | Verifiche RD2229 |
| F    | ✅    | 100 | 1b5e32d       | [piano_fase_F.md](piano_fase_F.md) | DM96 e DM92 |
| G    | ✅    | 100 | 394dc31       | [piano_fase_G.md](piano_fase_G.md) | NTC2018 |
| H    | ✅    | 100 | 99aaf55       | [piano_fase_H.md](piano_fase_H.md) | Eurocodici |
| I    | ✅    | 100 | 3bed1a7       | [piano_fase_I.md](piano_fase_I.md) | Interfaccia utente |
| J    | ✅    | 100 | 73482f0       | [piano_fase_J.md](piano_fase_J.md) | Report e tabulati |
| K    | ✅    | 100 | 23f60cf       | [piano_fase_K.md](piano_fase_K.md) | Grafici e inviluppi |
| L    | ✅    | 100 | f041b45       | [piano_fase_L.md](piano_fase_L.md) | Telai piani |
| M    | ✅    | 100 | 1711c73       | [piano_fase_M.md](piano_fase_M.md) | FEM 2D |
| N    | ✅    | 100 | 8f52479       | [piano_fase_N.md](piano_fase_N.md) | Validazione |
| O    | ✅    | 100 | 3d560d3       | [piano_fase_O.md](piano_fase_O.md) | Benchmark |
| P    | ✅    | 100 | fb83147       | [piano_fase_P.md](piano_fase_P.md) | Geotecnica |
| Q    | ✅    | 100 | af80fb9       | [piano_fase_Q.md](piano_fase_Q.md) | Report normativo |
| R    | 🟨    | 90  | —             | [piano_fase_R.md](piano_fase_R.md) | R.1–R.3, R.5–R.7 completate; R.4 parziale (LV3 modale/cantonali in dipendenza E.6/U) |
| S    | ⬜    | 0   | —             | [piano_fase_S.md](piano_fase_S.md) | Normative aggiuntive |
| S1   | ✅    | 100 | 2026-03-11    | [piano_fase_S1.md](piano_fase_S1.md) | Tamponamenti — DOCUMENTAZIONE ARRICCHITA ✅ |
| S2   | ✅    | 100 | 2026-03-11    | [piano_fase_S2.md](piano_fase_S2.md) | Tramezzi — DOCUMENTAZIONE ARRICCHITA ✅ |
| S3   | ✅    | 100 | 2026-03-11    | [piano_fase_S3.md](piano_fase_S3.md) | Parapetti — DOCUMENTAZIONE ARRICCHITA ✅ |
| S4   | ✅    | 100 | 2ab5c7c       | [piano_fase_S4.md](piano_fase_S4.md) | Controsoffitti — DOCUMENTAZIONE ARRICCHITA ✅ |
| S5   | ✅    | 100 | 2ab5c7c       | [piano_fase_S5.md](piano_fase_S5.md) | Impianti — DOCUMENTAZIONE ARRICCHITA ✅ |
| S6   | ✅    | 100 | 2ab5c7c       | [piano_fase_S6.md](piano_fase_S6.md) | Facciate — DOCUMENTAZIONE ARRICCHITA ✅ |
| S7   | ✅    | 100 | 2ab5c7c       | [piano_fase_S7.md](piano_fase_S7.md) | Camini — DOCUMENTAZIONE ARRICCHITA ✅ |
| S8   | ✅    | 100 | 2ab5c7c       | [piano_fase_S8.md](piano_fase_S8.md) | Scaffalature — DOCUMENTAZIONE ARRICCHITA ✅ |
| S9   | ✅    | 100 | 2ab5c7c       | [piano_fase_S9.md](piano_fase_S9.md) | Insegne — DOCUMENTAZIONE ARRICCHITA ✅ |
| T    | ⬜    | 0   | —             | [piano_fase_T.md](piano_fase_T.md) | Da definire |
| U    | ⬜    | 0   | —             | [piano_fase_U.md](piano_fase_U.md) | Da definire |
| V    | ⬜    | 0   | —             | [piano_fase_V.md](piano_fase_V.md) | Da definire |
| W    | ⬜    | 0   | —             | [piano_fase_W.md](piano_fase_W.md) | Da definire |
| X    | ⬜    | 0   | —             | [piano_fase_X.md](piano_fase_X.md) | Da definire |
| Y    | ⬜    | 0   | —             | [piano_fase_Y.md](piano_fase_Y.md) | Da definire |

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
| 2026-03-10 | M    | M.1       | 1711c73 | Implementato nucleo locale FEM beam 2D (`src/fem/elemento_beam.py`), carichi equivalenti modulari, 16 test dedicati superati |
| 2026-03-10 | M    | M.2–M.7   | 1711c73 | Completata pipeline FEM 2D (`src/fem/assemblaggio.py`, `condizioni_contorno.py`, `solutore.py`, `postprocessing.py`, `src/grafici/spostamenti.py`), 2350+ test aggiuntivi, validazione Cross-Pozzati, benchmark, storicizzazione |
| 2026-03-10 | P    | P.1 + P.2 (avvio) | fb83147 | Avviata Fase P geotecnica: creato package `src/geotecnica` (models, utils, norme, fondazioni_superficiali, cedimenti), decisioni architetturali recepite (kg/cm² + conversione, DA1 set1/set2, Robertson-Campanella default), 12 test mirati verdi |
| 2026-03-10 | P    | P.3–P.5 + P.6 | fb83147 | Completata Fase P: implementati `pali.py` (argilla/SPT/CPT, gruppo Converse-Labarre), `muri_sostegno.py` (Rankine, Coulomb, ribaltamento, scorrimento), `liquefazione.py` (CSR, CRR, MSF, IL, classificazione); 71 nuovi test (83 totali Fase P); aggiornato `__init__.py` e `models.py` con nuovi dataclass |
| 2026-03-11 | Q    | Q.1–Q.2 | —       | Avviata Fase Q: implementati `src/report/template_a4.py`, `src/report/pipeline.py`, `src/report/decorators.py`; aggiunti 9 test (`tests/test_template_a4.py`, `tests/test_report_pipeline.py`) tutti verdi |
| 2026-03-11 | Q    | Q.3 (core) | —       | Implementato motore citazioni normative (`src/report/citazioni_normative.py`): raccolta da dataclass/dict, deduplica, indice e appendice; aggiunti test `tests/test_citazioni.py` verdi |
| 2026-03-11 | Q    | Q.4–Q.10 | af80fb9 | Completata Fase Q: builder professionale (`src/report/report_builder.py`), sezioni obbligatorie (`src/report/sections.py`), export multi-formato (`src/report/export.py`, `export_pdf.py`, `export_docx.py`), confronto norme (`comparison.py`), custom sections + profili (`custom.py`), widget Qt (`src/ui/qt/report_widget.py`), documentazione (`docs/report_generator.md`) ed esempi (`examples/report/`), test reali (`tests/test_real_reports.py`) |
| 2026-03-11 | S0   | S0.1–S0.4 | —       | Riorganizzazione della pianificazione degli elementi secondari: esplosione delle tipologie §7.2 NTC2018 in fasi dedicate S1–S9, creazione dei file `piano_fase_S*.md`, vincoli su struttura documentale e meta-codice |
| 2026-03-11 | S1   | S1.1–S1.6 | — | **COMPLETATA Fase S1 — Verifiche tamponamenti secondari:** package `src/codes/ntc2018/secondary_elements/tamponamenti/` completo (models, checks_slu, checks_sle, presets, report_adapter); storage JSON `data/tamponamenti_presets.json` con 5 preset; test suite 40 test (unit, integration, benchmark); GUI Qt wizard 6-step + visualizzatore sezione 2D; export markdown/HTML; Q&A decisioni integrate (NTC2018 esclusivo, giunti completi, vincoli elastici, stato danno 4-livelli, preset JSON, GUI wizard+viewer). **Subfasi completate:** S1.1 input modellazione, S1.2 SLU ✓, S1.3 SLE ✓, S1.4 storage ✓, S1.5 test ✓, S1.6 GUI ✓. **Percentuale:** 100% avanzamento, tutte subfasi, 40+ test verdi. |
| 2026-03-11 | S2   | S2.1–S2.6 | — | **COMPLETATA Fase S2 — Verifiche tramezzi secondari:** package `src/codes/ntc2018/secondary_elements/tramezzi/` completo (models, checks_slu, checks_sle, presets, report_adapter); storage tipizzato aggiornato con `element_type`, `norm_code`, `phase_id`, `preset_id`, `trace_id`; dispatcher aggiornato per routing `partition/tramezzi`; JSON `data/tramezzi_presets.json` con 4 preset; widget dedicato `src/gui/secondary_elements/tramezzi_widget.py`; test suite dedicata + aggiornamento gating dispatcher. **Subfasi completate:** S2.1 input modellazione, S2.2 SLU ✓, S2.3 SLE ✓, S2.4 storage ✓, S2.5 test ✓, S2.6 GUI ✓. **Percentuale:** 100% avanzamento fase, commit reale non ancora presente quindi mantenuto `—` per coerenza documentale. |
| 2026-03-11 | S3–S9| S3.1–S9.6 | 2ab5c7c | **COMPLETATE Fasi S3–S9 in sessione unica:** 7 fasi (3-9) implementate end-to-end senza interruzioni (batch creation + batch testing). **Dettagli:** (S3) Parapetti: 8 file + JSON + 5 test ✓; (S4) Controsoffitti: 8 file + JSON + 4 test ✓; (S5) Impianti: 8 file + JSON + 4 test + widget ✓; (S6) Facciate: 6 file + JSON + 4 test; (S7) Camini: 6 file + JSON + 4 test; (S8) Scaffalature: 6 file + JSON + 4 test (enum typo fixed); (S9) Speciali: 5 file + JSON + 4 test + widget ✓. **Infrastruttura:** Dispatcher aggiornato per routing S3-S9 (7 if-block), imports aggiunti al package init, GUI exports aggiornati. **Validazione:** Batch pytest S3-S9 → **29/29 test PASSED** su 11 test file. **Percentuale:** 100% avanzamento S3-S9, tutte subfasi completate, infrastruttura integrata. |
| 2026-03-11 | S3–S9| Fase 2 (Documentazione) | — | **DOCUMENTAZIONE COMPRENSIVA S3–S9:** Creati 4 file di documentazione tecnica: (1) `docs/SECONDARY_ELEMENTS_API.md` (250+ linee): API reference unificata S1-S9 con enum, models, functions, dispatcher routing, presets JSON, storage contract; (2) `docs/SECONDARY_ELEMENTS_TECHNICAL.md` (380+ linee): architettura, 5 design pattern (Factory, Strategy, Composite, Dispatcher, Template), A1-A4 scelte critiche (unità, danno 4-livelli, presets, metadata), tabella modificatori (8 fattori), error handling, test strategy 5-livelli, roadmap V1.1-V2.1; (3) `docs/SECONDARY_ELEMENTS_VALIDATION.md` (420+ linee): quadro normativo (NTC, Circ, EC8, FEMA, ASCE), mapping norma→implementazione per S1-S9, test categorization (unit/integration/damage/pipeline/benchmark), 27 edge cases per fase, 3 benchmark cases numerati (FEMA E-74 parapetti, EN 13964 controsoffitti, NTC2018 impianti), CI/CD workflow, roadmap validazione V1.0-V2.1; (4) `docs/SECONDARY_ELEMENTS_README.md` (360+ linee): quick start API, formule principali per S3-S9, decisioni architetturali (A1-A4), roadmap estensioni V1.1-V2.0; (5) `docs/DOCSTRING_TEMPLATE.md` (400+ linee): template Google-style docstring per models/checks_slu/checks_sle/__init__/widget con esempi concreti da S3 parapetti (enum, dataclass, result, function, API, widget), checklist completamento; (6) `docs/SECONDARY_ELEMENTS_EXPANDED_PLAN.md` (800+ linee): espanso piano S3-S9 con letteratura (NTC primaria, FEMA, EN, formule provenienza), validazione benchmark numerici, edge cases per fase. **Totale:** 6 file, ~3000 linee documentazione, cross-referencing coerente, pronto per manutentori/sviluppatori. **Percentuale:** 100% completamento Fase 2. |
| 2026-03-12 | R    | R.1       | —       | Avviata implementazione Fase R con Q&A bloccante completata; creato package `src/esistenti` con `livelli_conoscenza.py` (LC/FC, adapter `MaterialeConFC`, helper `f_d_eff`), aggiornato `src/__init__.py`, aggiunto `tests/test_livelli_conoscenza.py`; test mirato eseguito: **11/11 PASS**. |
| 2026-03-12 | R    | R.2–R.7   | —       | Proseguita implementazione Fase R: creati moduli `vulnerabilita_ca.py`, `vulnerabilita_mur.py`, `modello_globale_mur.py`, `interventi.py`, `report_esistenti.py`; suite test dedicata riallineata ai contratti reali API/dataclass; validazione finale eseguita su 5 file (`test_vulnerabilita_ca.py`, `test_vulnerabilita_mur.py`, `test_modello_globale_mur.py`, `test_interventi.py`, `test_report_esistenti.py`) con esito **69/69 PASS**. |

---

## Riorganizzazione elementi secondari (§7.2 NTC2018)

Dal 2026-03-11 la pianificazione degli elementi secondari e non strutturali non e piu mantenuta come sottoparte implicita di fasi generali. La scomposizione documentale e ora articolata in una famiglia di fasi dedicate S1-S9, una per ciascuna tipologia operativa principale del §7.2 NTC2018 e categorie affini richieste in sessione. Questa famiglia convive con la gia esistente Fase S (`piano_fase_S.md`), che resta dedicata alle normative aggiuntive e al multinorma avanzato.

### Criteri di riorganizzazione

- Ogni tipologia ha una fase propria, un file di piano proprio e sub-fasi dedicate per input, SLU, SLE, storage, test e GUI.
- Ogni file `docs/piano_fase_S*.md` deve rispettare la struttura dei file `piano_fase_*.md` gia presenti: diagrammi, dipendenze, riferimenti normativi, tabelle, struttura file, storicizzazione e checklist.
- Ogni file `docs/piano_fase_S*.md` deve includere meta-codice coerente con i contenuti da realizzare: strutture dati, interfacce, pseudocodice di flusso, input/output attesi.
- I riferimenti preesistenti a G.1-G.5 restano validi come storico di implementazione tecnica, ma la pianificazione operativa di dettaglio confluisce da ora nelle fasi S1-S9.

### Mappatura della nuova famiglia di fasi

| Fase | Tipologia | Ambito principale |
|------|-----------|-------------------|
| S1 | Tamponamenti | fuori piano, ancoraggi, giunti, danno da drift |
| S2 | Tramezzi e partizioni leggere | tramezzi tradizionali e in cartongesso, compatibilita deformativa |
| S3 | Parapetti e balaustre | verifica locale, urti, azioni orizzontali e ancoraggi |
| S4 | Controsoffitti | sospensioni, controventi, nodi pendinati |
| S5 | Impianti e componenti impiantistici | apparecchiature, staffaggi, piping, canalizzazioni |
| S6 | Facciate e rivestimenti | pannelli, sottostrutture, fissaggi, giunti |
| S7 | Camini, comignoli e canne fumarie | comportamento a mensola, snellezza, ancoraggi |
| S8 | Scaffalature, arredi fissati e contenuti | ribaltamento, scorrimento, ancoraggi, interazione col contenuto |
| S9 | Insegne, cancelli e componenti speciali | elementi esposti, chiusure tecniche, casi fuori catalogo |

### Sessione 2026-03-11 — Domande, risposte e decisioni

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| Codifica nuove fasi | Prefissi numerici aggiuntivi (`S1`, `S2`, `S3`, ...) | Adottata famiglia S1-S9 nel piano principale, mantenendo separata la Fase S gia esistente |
| Tipologie da istanziare | Tamponamenti, tramezzi, parapetti, controsoffitti, impianti, facciate, camini, scaffalature, insegne/cancelli | Creata una fase dedicata per ciascuna tipologia |
| Livello di meta-codice | Medio | Ogni piano include dataclass/interfacce essenziali + pseudocodice di flusso |
| Struttura documentale | Allineata agli altri `piano_fase_*.md` | Obbligo di diagrammi, dipendenze, riferimenti normativi, tabelle, struttura file, storicizzazione |
| Tranche implementativa reale | Prerequisiti comuni + S2 completo | Dispatcher tipizzato, storage arricchito, completamento verticale S2 |
| Commit documentali senza commit git reale | Usare `—` | Rimossi identificatori semantici non coerenti dalla colonna `Ultimo commit` |

---

## Istruzioni operative

Per dettagli, consultare i file docs/piano_fase_X.md, docs/piano_fase_Y.md e docs/piano_fase_V.md corrispondenti a ciascuna fase.
La nuova fase X (solai) è documentata in [piano_fase_X.md](piano_fase_X.md), separata dalla Fase M (FEM) a partire dal 2026-03-10 (sessione Copilot).
La nuova fase Y (aree di influenza) è documentata in [piano_fase_Y.md](piano_fase_Y.md), centralizzando la logica condivisa tra solai, scale e fondazioni (decisione 2026-03-10, sessione Copilot).
La famiglia di fasi S1-S9 documenta in modo granulare gli elementi secondari e non strutturali del §7.2 NTC2018 e categorie affini; sostituisce la pianificazione generica precedente sugli elementi secondari.
