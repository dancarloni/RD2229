# Cronologia Fase X — Solai

Questo file raccoglie la storia delle attività, modifiche e decisioni per la Fase X.

## 2026-03-15

- Creati i file di memoria e contesto (fase_X_context.md, fase_X_history.md).
- Avviata la definizione del piano e delle finalità del modulo solai.

## 2026-03-15 (sessione di definizione)

- Decisione: il modulo deve coprire tutte le tipologie di solaio (laterocemento, predalles, legno, acciaio, misti, getto pieno).
- Decisione: il report deve essere completo e includere passaggi di calcolo e riferimenti normativi.
- Decisione: i test prioritari comprendono solai laterocemento, predalles, legno, aperture/cerchiature e solai bidirezionali (U-Boot).
- Decisione: riferimento normativo primario NTC2018 (§7.2.6, §4.1.2.2).

## 2026-03-15 (sessione agent-ready plan)

**Obiettivo sessione:** trasformare piano_fase_X.md in specifica agent-ready completa.

**Discovery moduli riusabili (percorsi verificati):**
- `src/core/combinations/ntc2018_combinations.py` — combinazioni SLU/SLE NTC2018 pronte
- `src/core_calculus/lc_fc_adjustments.py` — LC/FC esistenti (FC range [1.0,1.5])
- `src/core/registro_log.py` — logging tracciabile con VoceLog
- `src/codes/ntc2018/secondary_elements/*/report_adapter.py` — pattern report adapter
- `docs/piano_fase_V.md` — template fase matura con fallback e limiti V1

**Gap critico identificato:**
- `src/aree_influenza.py` NON ESISTE (attende Fase Y). Fallback documentato: input manuale + warning `X-AREA-001`.

**Decisioni architetturali fissate (D1–D10) — vedere fase_X_context.md per tabella completa.**

**Aggiornamenti applicati a piano_fase_X.md:**
- Fix tabella dipendenze: path corretti per combinazioni, LC/FC, report, nota aree influenza
- Aggiunta sezione "Perimetro V1 implementabile" (incluso/escluso)
- Corrette formule SLU/SLE: coefficienti NTC2018 Tab.2.6.I espliciti, fonte citata
- Aggiunta formula frequenza fondamentale f₁ (Dunkerley)
- Aggiunta sezione "Contratto dati minimo" (SolaiInputSpec + SolaiOutputResult metacodice)
- Aggiunta sezione "Codici warning" (X-AREA-001 … X-COMP-001)
- Aggiornata sezione "Decisioni progettuali" con tabella D1–D10
- Aggiunta sezione "Pipeline a checkpoint" (X.1→X.8, criteri stop/go)
- Aggiunta sezione "Matrice test e benchmark" (5 casi, tolleranza ≤2%)
- Aggiunta sezione "Prompt agente AUTO"

## 2026-03-15 (sessione audit tecnico-scientifico + correzione piano)

**Q&A bloccante completata prima delle modifiche**

- Flessione: formula c.a. armato come riferimento principale; forma elastica mantenuta solo come fallback preliminare.
- Unità: introdurre sezione dedicata con convenzioni e conversioni.
- Deformabilità: usare $q_l$ come formula principale con $q_s$ come input di interfaccia.
- Vibrazioni: mantenere formulazione primaria in SI e formulazione comparativa storica con conversione esplicita.
- Aperture: classificare la riduzione $EI$ come modello interno cautelativo, non come formula normativa diretta.
- DM96/DM 16/1/96: mantenerli come fallback documentale con TODO sulla trascrizione completa delle tabelle.
- Dipendenze: aggiungere sia sorgenti dati normative JSON/YML sia moduli Python applicativi.
- Storicizzazione: richiesta voce dettagliata con errori, motivazioni e impatti.
- Ampliamenti prioritari: quick reference testabile, diagrammi ASCII, casi speciali predalles/collaboranti/CLT, matrice formule per fonte.

**Errori tecnici corretti nel piano**

- Corretto errore dimensionale nella conversione del carico superficiale per la freccia: 300 kgf/m² = 0,03 kgf/cm²; la formula ora usa $q_l$ derivato dall'interasse.
- Corretta la sezione vibrazioni: eliminata la massa lineare errata $m=\gamma b h /100$; introdotta formulazione coerente in SI con conversione esplicita.
- Rafforzata la verifica a flessione: sostituita la forma elastica come formula principale con equilibrio di sezione in c.a. armato.
- Esplicitata la conversione $d_{mm}=10\,d_{cm}$ per taglio e punzonamento.
- Riclassificata la riduzione di rigidezza per aperture come modello interno cautelativo con trigger FEM.

**Dipendenze aggiornate nel piano**

- Aggiunti `src/codes/params/NTC2018.json` e `src/codes/clauses/NTC2018.yml` come sorgenti normative dirette.
- Mantenuti `src/core/combinations/ntc2018_combinations.py`, `src/core_calculus/lc_fc_adjustments.py`, `src/core/registro_log.py` e il pattern `report_adapter.py` come layer applicativi.

**Ampliamenti introdotti nel piano**

- Sezione "Convenzioni di unità e conversioni".
- Sezione "Matrice formule per fonte e affidabilità".
- Sezione "Diagrammi di flusso (ASCII)".
- Sezione "Quick Reference Testabile".
- Sezione "Casi speciali da espandere in implementazione".

## 2026-03-15 (secondo giro Q&A di messa a punto)

**Decisioni aggiuntive fissate**

- Benchmark: usare doppia rappresentazione input storici + input SI.
- Appendici tabellari future: sì, ma come estratti minimi implementativi per DM96 e DM 16/1/96.
- Casi speciali: predalles, collaboranti e CLT restano fuori dal perimetro V1 minima ma devono essere documentati.
- Diagrammi: livello molto dettagliato, non solo alto livello.
- Matrice formule: aggiungere colonna `Validato numericamente`.
- Report futuro: mostrare formula usata + fallback disponibile.
- Esigenza strutturale aggiuntiva: introdurre nel piano una sezione che governi la scomposizione di Fase X in file modulo autonomi, ognuno con propria struttura e sub-fasi.

**Delta applicato al piano**

- Aggiunta sezione "Strategia di scomposizione documentale della Fase X" con naming dei futuri file modulo e struttura minima obbligatoria.
- Aggiornata la matrice benchmark con doppia colonna `Input storici` / `Input SI`.
- Aggiornata la matrice formule con colonna `Validato numericamente`.
