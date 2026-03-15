# Contesto Fase X — Solai

Questo file contiene il contesto persistente per lo sviluppo della Fase X (solai).
Serve a conservare:

- obiettivi generali e requisiti principali,
- vincoli architetturali e decisioni di base,
- collegamenti normativi e bibliografici principali,
- note operative che devono sopravvivere oltre le singole modifiche.

## Aggiornamenti

- 2026-03-15: creato file di contesto iniziale.
- 2026-03-15: aggiornato con tutte le decisioni architetturali fissate in sessione (D1–D10).
  Aggiornato piano_fase_X.md con sezioni: Perimetro V1, Contratto dati minimo, Codici warning,
  Decisioni progettuali (tabella), Pipeline a checkpoint, Matrice benchmark, Prompt agente AUTO.
- 2026-03-15: aggiornato dopo audit tecnico-scientifico del piano con correzione errori dimensionali,
  ampliamento dipendenze normative e nuove sezioni su unità, affidabilità formule, quick reference,
  diagrammi ASCII e casi speciali.

## Decisioni architetturali fissate (D1–D10)

| # | Decisione | Valore | Data |
|---|-----------|--------|------|
| D1 | Modello strutturale | 2D grigliato/piastra ortotropa | 2026-03-15 |
| D2 | Gestione aperture | Penalizzazione semplificata + FEM locale | 2026-03-15 |
| D3 | Gestione cerchiature | Doppio binario: travi equivalenti + libreria tipologica | 2026-03-15 |
| D4 | Vibrazioni | Risposta dinamica estesa (f₁ + acc. RMS) | 2026-03-15 |
| D5 | LC/FC | Configurabile per norma; automatico da LC; override manuale possibile | 2026-03-15 |
| D6 | Confronto storico/moderno | Automatico solo per edifici esistenti | 2026-03-15 |
| D7 | Unità interne | cm, kg, kg/cm² (conversioni tracciate in output) | 2026-03-15 |
| D8 | Benchmark obbligatori | 5 casi (BM-X01–BM-X05) | 2026-03-15 |
| D9 | Soglia errore target | ≤2% sui casi con soluzione nota | 2026-03-15 |
| D10 | Esecuzione agente | Sequenza a step con checkpoint, non single-shot | 2026-03-15 |

## Gap critici

- `src/aree_influenza.py` NON DISPONIBILE (attende Fase Y). Fallback: input manuale + warning `X-AREA-001`.
  Precedente in Fase V: `V-AREA-002`.

## Convenzioni dimensionali chiarite

- Nel piano Fase X, `kg` nelle verifiche statiche va inteso come `kgf`.
- Le formule EC2/NTC con coefficienti normativi numerici devono essere preferibilmente valutate in SI locale,
  con riconversione finale in unità storiche per report e benchmark.
- Per la deformabilità si assume `q_s` come input di interfaccia [kgf/m²] e `q_l` come carico lineare di calcolo [kgf/cm].
- Per la dinamica si distingue tra massa volumica `ρ [kg/m³]` e azioni gravitazionali in `kgf`.

## Decisioni audit 2026-03-15

- Flessione c.a.: formula di equilibrio di sezione come riferimento principale; formula elastica solo fallback preliminare.
- Aperture: modello `α_ap` classificato come cautelativo interno con trigger FEM locale.
- DM96 e DM 16/1/96: mantenuti come fallback documentale con TODO sulla trascrizione tabellare completa.
- Ampliamenti prioritari approvati: quick reference testabile, diagrammi ASCII, casi speciali predalles/collaboranti/CLT, matrice formule per fonte.
- Benchmark: doppia colonna input storici + SI.
- Report futuro: mostrare formula usata + fallback disponibile.
- Modularizzazione documentale: il file master Fase X deve poter essere scomposto in file figlio uno per modulo, ciascuno con struttura autonoma e proprie sub-fasi.

## Path dipendenze verificati

- Combinazioni NTC2018: `src/core/combinations/ntc2018_combinations.py`
- Parametri normativi NTC2018: `src/codes/params/NTC2018.json`
- Clausole normative NTC2018: `src/codes/clauses/NTC2018.yml`
- LC/FC: `src/core_calculus/lc_fc_adjustments.py` (FC range [1.0, 1.5]; LC1=1.35, LC2=1.20, LC3=1.00)
- Log: `src/core/registro_log.py` (VoceLog con formula, fonte, esito)
- Pattern report: `src/codes/ntc2018/secondary_elements/*/report_adapter.py`
- Template fase matura: `docs/piano_fase_V.md`
