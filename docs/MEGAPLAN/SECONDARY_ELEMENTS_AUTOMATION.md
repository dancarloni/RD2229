# SECONDARY ELEMENTS – Automation Plan

> **PLAN‑ONLY – FILE DI AUTOMAZIONE**
> Questo documento definisce **in modo dichiarativo e vincolante**
> le operazioni che l’implementazione deve eseguire per attuare
> il modulo “Elementi Secondari / Non Strutturali”.
>
> ❗ Nessuna decisione progettuale deve essere presa fuori da quanto
> qui specificato.  
> ❗ Nessun codice di calcolo deve essere introdotto in questa fase.

## 0-bis. Decisione di consolidamento (VINCOLANTE) — Mapping 2A‑1

### 0-bis.1 Decisione

- È stata assunta la decisione **2A‑1 (conservativa)**.
- **Source of truth** del modulo “Secondary Elements” nella Fase 2 è: **`src/codes/secondary_elements/*`**.
- Le directory e i file eventualmente presenti in:
  - `methods/verification/secondary_elements/*`
  NON devono essere creati in questa fase (evitare duplicazioni).

### 0-bis.2 Interpretazione del presente file di automazione

Tutte le azioni di creazione/estensione definite nelle sezioni successive (A…H) devono essere interpretate come segue:

- **TOUCH (adattare/estendere)** file già esistenti sotto:
  - `src/codes/secondary_elements/models.py`
  - `src/codes/secondary_elements/checks.py`
  - `src/codes/secondary_elements/storage_adapter.py`
  - `verifications/secondary_elements/dispatcher.py`

- **CREATE (creare solo se necessario)** file mancanti, ma **solo** sotto `src/codes/secondary_elements/`:
  - `ta_models.py` (stub/interfacce)
  - `drift_models.py` (stub/interfacce; Metodo B drift proxy)
  - `anchors_capacity.py` (stub ETA‑first)

- **CONFIG** (sempre in `config/`):
  - `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode`

- **DOC** (sempre in `docs/MEGAPLAN/`):
  - `STEP2_INTEGRATION_SECONDARY_ELEMENTS.md` (da creare prima di qualunque implementazione STEP2)
  - `SECONDARY_ELEMENTS_MASTER.md` (già presente; resta vincolante)

### 0-bis.3 Divieti espliciti (anti‑doppioni)

- NON creare `methods/verification/secondary_elements/`.
- NON duplicare dispatcher/registry in due alberi diversi.
- NON introdurre un “secondary_elements_v2”.

### 0-bis.4 Invarianti (richiamo)

- Forza sismica: sempre NTC2018.
- Drift: solo SLE, Metodo B (shear‑building proxy + soft_storey_factor), confidence LOW, warning obbligatorio.
- Output: sempre `trace.run_id` e `norm_references[]`.

---

## A. Creazione struttura del modulo

### A1. Directory

Creare la seguente directory (se non esistente):

- `methods/verification/secondary_elements/`

### A2. File skeleton da creare (vuoti o boilerplate minimale)

All’interno di `methods/verification/secondary_elements/` creare:

- `__init__.py`
- `dispatcher.py`
- `models.py`
- `checks_slu.py`
- `checks_sle.py`
- `ta_models.py`
- `drift_models.py`
- `anchors_capacity.py`

> I file devono essere creati **senza logica di calcolo**.
> Sono ammessi solo:
>
> - docstring
> - TODO
> - classi/interfacce vuote
> - commenti strutturali

---

## B. Configurazione normativa (JSONCODE)

### B1. File da creare

Creare il file:

- `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode`

### B2. Contenuto concettuale obbligatorio

Il file deve dichiarare:

- `checks`:
  - `NS_SLU_InertialForce`
  - `NS_SLE_DriftCompatibility`

- policy globali del modulo:
  - `allow_estimated_drift = true`
  - `drift_method_default = SHEAR_BUILDING_PROXY`
  - `allow_soft_storey_factor = true`
  - `block_if_influence_on_global_model = true`

- mapping:
  - `element_type → drift_sensitive`
  - `element_type → drift_fragility_class`

- default:
  - `drift_limits` (EC8‑based, override ammesso e tracciato)

> ❗ La forza sismica resta **sempre NTC2018**.
> Questo file **non** deve ridefinire formulazioni di Fa.

---

## C. Registrazione nel Verification Engine

### C1. Dispatcher di verifica

Aggiornare il dispatcher centrale dei metodi di verifica per:

- registrare il namespace `secondary_elements`
- instradare:
  - SLU → `checks_slu`
  - SLE → `checks_sle`

> ❗ `core/verification_engine.py` **NON va modificato**.

---

## D. Input / Output comuni

### D1. Input (schema comune)

Estendere lo schema di input comune con:

- `secondary_elements[]`

Ogni elemento deve supportare almeno:

- `element_id`
- `element_type`
- `z_level`
- `weight`
- `ta_model`
- `drift`:
  - `source = GLOBAL | ESTIMATED | USER`
  - `method = SHEAR_BUILDING_PROXY`
  - `soft_storey_factor`
  - `confidence`
- `anchor_capacity` (ETA manuale)

> ❗ Le estensioni devono essere **additive** (no breaking changes).

---

### D2. Output (schema comune)

Ogni verifica deve produrre un `VerificationResultItem` con:

- `check_id`
- `demand`
- `capacity`
- `utilisation`
- `norm_references`
- `decision_log`
- `trace.run_id`

> ❗ `decision_log` è **obbligatorio** per:
>
> - metodo Ta
> - metodo drift
> - assunzioni e warning

---

## E. GUI (thin)

### E1. Module selector

Aggiornare:

- `ui/module_selector.py`
- `modules_config.json`

Aggiungendo il modulo:

- `id: secondary_elements`
- `label: Elementi Secondari`

---

### E2. Verification table

Aggiornare `ui/verification_table_app.py` per:

- aggiungere colonne:
  - `Ta method`
  - `Drift method`
  - `Soft‑storey factor`
  - `Drift confidence`
- visualizzare warning se:
  - `drift.source = ESTIMATED`

> ❗ La GUI **non** deve contenere formule o calcoli normativi.

---

## F. Test (obbligatori)

### F1. File di test da creare

In `tests/` creare:

- `test_secondary_elements_slu.py`
- `test_secondary_elements_sle.py`
- `test_secondary_elements_gating.py`

### F2. Comportamenti da testare

- drift stimato → warning presente
- `soft_storey_factor > 1.0` → warning informativo additivo
- `influence_on_global_model = true` → `NOT_APPLICABLE`
- ogni risultato ha `trace.run_id`

> ❗ I test possono essere **comportamentali** (status, warning, tracciabilità),
> non è richiesto verificare numeri di calcolo.

---

## G. Documentazione

### G1. File da creare

Creare:

- `docs/MEGAPLAN/SECONDARY_ELEMENTS_MASTER.md`

Usare **esclusivamente** il contenuto definito nel file:
`SECONDARY_ELEMENTS_MASTER.md (SPEC master)`.

---

## H. Invarianti globali (NON negoziabili)

- **Forza sismica**: sempre NTC2018
- **Ta**: modello selezionabile, mai implicito
- **Drift**:
  - solo SLE
  - Metodo B (shear‑building proxy + soft‑storey)
  - `confidence = LOW`
  - warning obbligatorio
- **Ancoraggi**: ETA‑first (manuale oggi)
- **Tracciabilità**: sempre `norm_references` + `trace.run_id`

---

## I. Fine del piano di automazione

Ogni implementazione che **non** rispetta questo file:

- è da considerarsi **non conforme al piano**
- deve essere corretta prima di procedere oltre.
