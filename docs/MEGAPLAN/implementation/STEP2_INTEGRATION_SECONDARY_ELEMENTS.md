# STEP2 — Integrazione specifica per il Modulo “Secondary Elements” (PLAN‑ONLY)

## 0. Scopo

Questo documento estende STEP2.md applicando le invarianti **norma_attiva** e
**routing safe / no‑mixing** al Modulo **Secondary Elements / Non‑Structural**.

Il documento è **vincolante** per la Fase 2 ed è **PLAN‑ONLY**:
non contiene codice e non autorizza implementazioni operative.

### Riferimenti

- STEP2.md (contratto norma_attiva e no‑mixing)
- PLAN_MASTER.md
- PLAN_INPUT_COMUNE.md
- PLAN_OUTPUT_COMUNE.md
- PLAN_GUI_SECONDARY_ELEMENTS.md
- SECONDARY_ELEMENTS_MASTER.md
- SECONDARY_ELEMENTS_AUTOMATION.md (con addendum 2A‑1)

> Regola: questo documento è PLAN‑ONLY; nessun codice, nessuna logica eseguibile.

---

## 1. Invarianti STEP2 applicate al Modulo Secondary Elements

### 1.1 Norma canonica di progetto

- Il Modulo Secondary Elements **deve leggere la norma attiva esclusivamente**
  da `project_model.norma_attiva`.
- Il modulo **non deve** introdurre campi alternativi, alias o override locali
  della norma.
- La norma attiva governa:
  - il routing delle verifiche,
  - la validità del report,
  - le regole di no‑mixing.

---

### 1.2 Routing safe (Engine / Report)

Ogni esecuzione di verifiche del Modulo Secondary Elements deve produrre
risultati che includono **obbligatoriamente**:

- `VerificationResultItem.norm_references[]`
- `trace.run_id`

Regole:

- La **forza inerziale** sugli elementi non strutturali è **sempre**
  riferita a **NTC2018**.
- Fonti esterne (EC8 / ASCE / FEMA) sono ammesse **solo come metodo**
  per:
  - modello Ta,
  - verifica drift SLE,
  e **mai** come sostituzione della norma della forza.

Il ReportBuilder deve applicare la regola di omogeneità:

- se `project_model.norma_attiva = NTC2018`,
  risultati con riferimenti incoerenti **bloccano la generazione del report**
  (SAFETY‑BLOCK).

---

### 1.3 Regola di no‑mixing (specifica per Secondary Elements)

È ammesso l’uso di fonti esterne **solo** per:

- scelta/stima del periodo proprio Ta dell’elemento,
- definizione della verifica di drift (SLE) e dei drift limits.

In tal caso:

- `norm_references[]` deve distinguere chiaramente:
  - **Norma della forza**: NTC2018
  - **Fonte del metodo**: EC8 / ASCE / FEMA
- `decision_log` deve riportare:
  - metodo scelto,
  - assunzioni,
  - livello di confidenza.

---

## 2. Impatti sullo schema Input / Output (coerenza STEP2)

### 2.1 Input comune

Lo schema `SecondaryElementSpec` deve includere informazioni sufficienti a:

- ereditare la `norma_attiva` dal contesto di progetto,
- tracciare il modello Ta:
  - `ta_model`
  - fonte del metodo,
- tracciare il drift:
  - `drift.source`
  - `drift.method`
  - `soft_storey_factor`
  - `confidence`,
- dichiarare se l’elemento influenza il modello globale
  (`influence_on_global_model`).

Le estensioni allo schema devono essere **additive** e non rompere
retro‑compatibilità.

---

### 2.2 Output comune

Ogni verifica del Modulo Secondary Elements deve produrre
un `VerificationResultItem` conforme allo schema comune, contenente almeno:

- `check_id`
- `demand`
- `capacity`
- `utilisation`
- `norm_references[]`
- `decision_log`
- `trace.run_id`

---

## 3. Test contrattuali aggiuntivi (Fase 2)

### 3.1 Contract tests (obbligatori)

Devono essere definiti e mantenuti i seguenti contratti:

- **CT‑SE‑01**
  Ogni risultato include `trace.run_id`.

- **CT‑SE‑02**
  Ogni risultato include almeno una entry in `norm_references[]`.

- **CT‑SE‑03**
  Se `drift.source = ESTIMATED`:
  - warning obbligatorio,
  - `confidence = LOW`.

- **CT‑SE‑04**
  Se `influence_on_global_model = true`,
  la verifica SLE con drift stimato restituisce `NOT_APPLICABLE`.

---

### 3.2 Report safety test (no‑mixing)

- **RT‑SE‑01**
  Se `project_model.norma_attiva = NTC2018` e nel report sono presenti
  risultati con riferimenti normativi incoerenti,
  la generazione del report deve essere **bloccata**.

---

## 4. Checklist di adozione (prima dell’implementazione STEP2)

Prima di procedere a qualunque implementazione operativa:

- [ ] Il modulo legge la norma **solo** da `project_model.norma_attiva`.
- [ ] `norm_references[]` distingue sempre:
      NTC2018 (forza) vs fonte del metodo (Ta / drift).
- [ ] I contratti CT‑SE‑01 .. CT‑SE‑04 sono definiti come Definition of Done.
- [ ] Il presente file è stato creato e versionato nel repository.

Solo dopo il soddisfacimento di questa checklist è consentito
avviare l’implementazione operativa di STEP2.
