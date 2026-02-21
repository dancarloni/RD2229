# SECONDARY_ELEMENTS_MASTER — Modulo “Elementi Secondari / Non Strutturali” (PLAN‑ONLY)

> **NOTA (vincolante)**: questo documento è **PLAN‑ONLY**. Non contiene codice eseguibile.
> È la **SPEC master** del modulo “Elementi Secondari / Non Strutturali”.
> Deve restare coerente con:
> - separazione Core/GUI/I‑O, modularità estrema, tracciabilità normativa completa
> - input comune unico e output comune unico (VerificationResultItem)
> - GUI thin: nessuna logica normativa in UI; solo raccolta input/validazione e visualizzazione risultati
> Riferimenti interni: `PLAN_MASTER.md`, `PLAN_INPUT_COMUNE.md`, `PLAN_OUTPUT_COMUNE.md`, `PLAN_GUI_SECONDARY_ELEMENTS.md`, `STEP2.md`.

---

## 0. Metadati del documento

- **Documento**: `docs/MEGAPLAN/SECONDARY_ELEMENTS_MASTER.md`
- **Scope**:
  - Elementi strutturali secondari (NTC2018 Cap.7 §7.2.3)
  - Elementi costruttivi non strutturali (NTC2018 Cap.7 §7.2.3 + verifiche §7.3.6.2)
  - Integrazioni ammesse solo dove NTC non è prescrittiva (Ta, drift): EC8/ASCE/letteratura tecnica, con tracciabilità.
- **Status**: DRAFT (vincolante per implementazione)
- **Policy normativa**:
  - **Forza sismica / domanda inerziale**: sempre **NTC2018** (spettro NTC + formulazione NTC)
  - **Periodo proprio Ta** dell’elemento non strutturale: selezionabile (modelli esterni), sempre tracciato
  - **Drift**: verificato a SLE; ammessa stima semplificata (Metodo B) con warning e confidence LOW
  - **Ancoraggi**: ETA‑first (oggi manuale), ACI/altro solo opzioni avanzate

---

## 1. Obiettivi e non‑obiettivi

### 1.1 Obiettivi
1. Gestire in modo unificato elementi “SECONDARY_STRUCTURAL” e “NONSTRUCTURAL” nel workflow di verifica.
2. Calcolare la domanda inerziale sugli elementi non strutturali con **NTC2018** (vincolo non negoziabile).
3. Consentire scelta esplicita del **modello Ta** (poiché NTC non fornisce metodo chiuso) con decision log.
4. Eseguire verifica **SLE drift‑compatibility** includendo stima semplificata (Metodo B) quando manca il drift globale.
5. Supportare verifica domanda/capacità degli ancoraggi in modo **ETA‑first** (manuale oggi), pianificando ETA Library.

### 1.2 Non‑obiettivi (espliciti)
- Nessuna implementazione di modello globale FEM dell’edificio in questo modulo.
- Nessuna “auto‑scelta” del modello più corretto: il software espone alternative e traccia la scelta.
- Nessuna capacità ancoraggi calcolata automaticamente da normative esterne come default (ACI/EN1992‑4): solo opzioni avanzate o future estensioni.

---

## 2. Definizioni e classificazioni (NTC‑first)

### 2.1 Elementi strutturali secondari (NTC Cap.7 §7.2.3)
- Elementi per i quali le azioni orizzontali possono essere trascurate.
- Progettati per carichi verticali e per seguire gli spostamenti della struttura senza perdita di capacità.
- Vincoli: contributo rigidezza/resistenza orizzontale ≤ 15% dei primari; non possono “regolarizzare” strutture irregolari.

### 2.2 Elementi non strutturali (NTC Cap.7 §7.2.3 + §7.3.6.2)
- Componenti significativi per la sicurezza/incolumità o influenti sulla risposta globale.
- Verifica per stati limite; domanda inerziale mediante forza orizzontale Fa (NTC).

### 2.3 Tassonomia operativa (software)
- `role`:
  - `SECONDARY_STRUCTURAL`
  - `NONSTRUCTURAL`
  - `REQUIRES_GLOBAL_MODEL` / `OUT_OF_SCOPE`
- `demand_type`:
  - `ACCELERATION_SENSITIVE`
  - `DRIFT_SENSITIVE`
  - `MIXED`

---

## 3. Teoria “software‑ready” (domanda/capacità)

### 3.1 Domanda inerziale (vincolo NTC)
- Forza orizzontale `Fa` sempre secondo NTC2018 usando spettro NTC2018.
- Il periodo `Ta` dell’elemento influenza la domanda tramite Sa(Ta) e quindi Fa.
- Poiché NTC non fornisce metodo completo per Ta, `Ta` è stimato tramite modelli selezionabili e tracciati (ASCE/NEHRP/FEMA/EC8/Manuale).

### 3.2 Domanda deformativa (drift)
- Il drift è una domanda deformativa che può governare il danno di componenti fragili/interferenti.
- Se manca un modello globale, si usa un proxy semplificato dichiarato (Metodo B), con warning e confidence LOW.

### 3.3 Capacità (ancoraggi e resistenze locali)
- Capacità ancoraggi: fonte primaria **ETA/DoP/dati produttore** (oggi manuale).
- Capacità locale (sezione/elemento): gestita come demand/capacity nel formato standard di output.

---

## 4. Input canonico: SecondaryElementSpec (estratto + estensioni additive)

> Lo schema completo è definito nel documento SPEC dedicato. Qui si richiamano campi minimi e integrazioni additive richieste.

### 4.1 Campi minimi (MVP)
- Identità: `id`, `element_type`, `description`
- Geometria: campi minimi per tipo (`length`, `height`, `thickness`, `diameter`, ecc.)
- Massa/Peso: `mass` o `Wa` derivabile
- Quota: `z_level`
- Vincoli/Supporti: `boundary_conditions`, `support_type`
- Ancoraggi: `attachment` + `anchor_capacity` (ETA manuale) se richiesto
- Flags: `influence_on_global_model`, `requires_seismic_check`

### 4.2 Estensioni additive (obbligatorie per Ta e drift)
- `ta_model` (selezione modello periodo):
  - `RIGID`
  - `CANTILEVER_EQ`
  - `SDOF_EQ`
  - `DATASHEET`
  - `MANUAL`
- `drift` (block):
  - `source`: `GLOBAL` | `ESTIMATED` | `USER`
  - `method`: `SHEAR_BUILDING_PROXY` (MVP default)
  - `soft_storey_factor` (>= 1.0)
  - `confidence`: `LOW` | `MED` | `HIGH`
  - `assumptions`: elenco stringhe (per decision log/report)

---

## 5. Architettura modulo (file mapping e separazione funzioni)

### 5.1 Regole architetturali (vincolanti)
- Core di calcolo non dipende dalla GUI; GUI non contiene logica normativa.
- Tutti i risultati passano da `VerificationResultItem` (output unico).
- Ogni risultato deve includere `norm_references[]` e `trace.run_id` (contratto test).

### 5.2 Posizionamento nel workspace (MVP)
- Directory: `methods/verification/secondary_elements/`
- File logici:
  - `dispatcher` (routing e registrazione)
  - `models` (SecondaryElementSpec + gating fields)
  - `checks_slu` (domanda inerziale/SLV‑SLU)
  - `checks_sle` (drift compatibility)
  - `ta_models` (catalogo modelli Ta)
  - `drift_models` (catalogo drift estimators)
  - `anchors_capacity` (ETA‑first / manual now)

---

## 6. Procedure di calcolo (flow) — SLU/SLV e SLE

### 6.1 Flow SLU/SLV (domanda inerziale — NTC)
1. Validazione input e gating (campi obbligatori per tipo).
2. Determinazione `Ta`:
   - da modello selezionato (`ta_model`)
   - loggare fonte/assunzioni
3. Calcolo `Fa` con spettro NTC2018 e formulazione NTC.
4. Mappatura `Fa` → effetti locali (V, M, forze ancoraggi, ribaltamento) in base allo schema statico.
5. Capacità ancoraggi:
   - ETA manuale se disponibile
   - altrimenti warning “capacity missing” (o opzione avanzata)
6. Output `VerificationResultItem`:
   - `demand`, `capacity`, `utilisation`
   - `norm_references` (NTC per Fa + fonte Ta + eventuali note)
   - `decision_log` (Ta, assunzioni, capacità ETA)
   - `trace.run_id`

### 6.2 Flow SLE (drift compatibility — Metodo B)
1. Gating: se `influence_on_global_model=true` → `NOT_APPLICABLE` (richiede modello globale).
2. Determinazione drift:
   - `GLOBAL` (future hook)
   - `USER` (dichiarato dall’utente)
   - `ESTIMATED` (Metodo B)
3. Metodo B (ESTIMATED):
   - shear‑building proxy con rigidezza uniforme base
   - applicare `soft_storey_factor` (default 1.0; >1 warning additivo)
   - `confidence=LOW`, warning obbligatorio
4. Confronto drift vs `drift_limit`:
   - default da config (EC8‑based) o override utente tracciato
5. Output `VerificationResultItem` con decision log drift.

---

## 7. Decisione architetturale vincolante — Metodo B (Shear‑Building Proxy + Soft‑Storey)

### 7.1 Scelta
- Il modulo adotta come default MVP **Metodo B**:
  - shear‑building proxy con possibilità di soft‑storey indicator
- Motivazioni:
  - evita sottostime tipiche della rigidezza uniforme pura
  - input minimo (un solo coefficiente)
  - maggiore difendibilità tecnico‑legale
  - upgrade path naturale verso drift globale

### 7.2 Regole
- `soft_storey_factor`:
  - default = 1.0 (uniform)
  - se >1.0: warning informativo additivo
- sempre: `drift.source=ESTIMATED`, `confidence=LOW`, warning obbligatorio
- NOT_APPLICABLE se elemento influenza risposta globale

---

## 8. GUI (thin) — requisiti minimi

- Editor form‑driven (schema → form), nessun calcolo in UI.
- Campi UI obbligatori:
  - scelta `ta_model`
  - drift: scelta `source` e input `soft_storey_factor` se `ESTIMATED`
  - badge “Estimated – low confidence” se `ESTIMATED`
- Pannello risultati:
  - mostra utilisation, demand/capacity
  - mostra `norm_references` e `trace.run_id`
  - mostra `decision_log` (Ta e drift)

---

## 9. Config / Registry / Storage

### 9.1 Config `.jsoncode`
- `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` deve definire:
  - check ids (SLU/SLE)
  - mapping `element_type → drift_sensitive`
  - mapping `element_type → drift_fragility_class`
  - drift limits default (EC8‑based) + policy Metodo B
  - gating: block if influence_on_global_model

### 9.2 Storage progetto
- Persistenza in `project.secondary_elements[]` (spec + results), con `schema_version`.

### 9.3 ETA‑first (oggi manuale, domani library)
- Oggi: `anchor_capacity` manuale con `source=ETA_MANUAL`.
- Futuro: `eta_id` referenziato a registry ETA (con revisione, allegato, metadati).

---

## 10. Testing (contrattuale + golden)

### 10.1 Invarianti test (sempre)
- Ogni risultato include `trace.run_id` e almeno una entry in `norm_references`.
- GUI tests: solo smoke (selection → run → results), nessuna asserzione normativa in GUI.

### 10.2 Test minimi (MVP)
- SLU/SLV: caso base OK/FAIL (anche solo status) + presenza decision log + norm refs.
- SLE: drift ESTIMATED con `soft_storey_factor=1.0` → warning obbligatorio.
- Gating: `influence_on_global_model=true` → NOT_APPLICABLE.

---

## 11. Rischi e mitigazioni

- Rischio: drift stimato = incertezza → mitigazione: confidence LOW + warning + decision log + possibilità di usare USER/GLOBAL.
- Rischio: uso improprio su elementi globalmente influenti → mitigazione: gating NOT_APPLICABLE + messaggio “richiede modello globale”.

---

## 12. Checklist implementazione (link automation)

- Vedi `docs/MEGAPLAN/SECONDARY_ELEMENTS_AUTOMATION.md` per la sequenza dichiarativa di creazione file/cartelle/config/test/documentazione.

---

## 13. Allegati e riferimenti (placeholder)

- NTC2018 Cap.7: §7.2.3; §7.3.6.2; definizione Fa.
- EC8 (EN1998‑1): §4.3.5 (non structural elements), §4.4.3.2 (drift limitation).
- ASCE/NEHRP/FEMA: fonti per modelli Ta e classificazioni rigido/flessibile.
- ACI 318 Chapter 17: solo opzione avanzata per capacity anchors (non default).