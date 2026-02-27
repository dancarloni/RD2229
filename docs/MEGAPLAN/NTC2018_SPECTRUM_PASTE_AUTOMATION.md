# NTC2018 — Spectrum Paste Service — Automation (PLAN‑ONLY)

> **Scopo**: definire in modo dichiarativo e vincolante **quali file** creare/modificare, **dove** integrare UI e persistenza, e **quali test** aggiungere per il servizio “Paste spettro NTC2018” basato su tabella EdiLus‑MS. [1](https://www.concrete.org/publications/getarticle.aspx?m=icap&pubid=51689626)

---

## A) Decisioni vincolanti (freeze)

- **Percorso canonico servizio**: `src/codes/ntc2018/spectrum_paste_service.py` (VINCOLANTE).
- **Persistenza**: `project.seismic_inputs.ntc2018_hazard_profile` (singolo) (VINCOLANTE).
- **Sorgente dati**: EdiLus‑MS (tabella copiata come testo con Tr, ag/g, F0, Tc* e stati limite). [1](https://www.concrete.org/publications/getarticle.aspx?m=icap&pubid=51689626)

---

## B) File target (create/touch)

### B1. CREATE — Service (dominio NTC2018)
Creare:
- `src/codes/ntc2018/spectrum_paste_service.py`

Contenuti ammessi:
- strutture dati (profile/row)
- parser deterministico
- validazioni minime
- API di accesso `get_hazard_params`

Contenuti vietati:
- interpolazioni di pericolosità
- fetch web o scraping
- calcolo completo dello spettro Sa(T) (opzionale in fase successiva)

### B2. TOUCH — Project model / schema
Individuare e aggiornare (additivo):
- file del **project model** dove risiede `project.seismic_inputs` (nome esatto da repo)

Aggiungere:
- `ntc2018_hazard_profile: Ntc2018HazardProfile | None`

### B3. TOUCH — Persistenza
Individuare e aggiornare:
- adapter/repository che salva/carica il project model

Requisiti:
- round‑trip del campo `ntc2018_hazard_profile` (con `raw_paste` conservato)

### B4. TOUCH — UI
Individuare e aggiornare la UI di impostazioni progetto (sezione “Azioni sismiche / NTC2018” o equivalente):
- aggiungere una nuova scheda/pannello: **Parametri sismici NTC2018 (Paste)**

Componenti UI minimi:
- dropdown `class_of_use` (I–IV) [1](https://www.concrete.org/publications/getarticle.aspx?m=icap&pubid=51689626)
- input VN e VR [1](https://www.concrete.org/publications/getarticle.aspx?m=icap&pubid=51689626)
- textarea `raw_paste` + bottone `Analizza`
- preview righe parsate (read‑only)
- indicatore `quality` e lista `messages`
- bottone `Salva nel progetto`

Vietato:
- modifiche alla GUI non correlate

---

## C) Test (obbligatori)

### C1. CREATE — Unit test parser
Creare un file test, ad es.:
- `tests/test_ntc2018_hazard_paste_parser.py`

Casi minimi:
1) decimali con punto → parse OK
2) decimali con virgola → parse OK (normalizzazione)
3) mancano 1+ righe → WARNING
4) token non numerici / mancanti → ERROR

### C2. CREATE — Persistenza round‑trip
Creare un file test, ad es.:
- `tests/test_ntc2018_hazard_profile_persistence.py`

Casi minimi:
- salva profilo → ricarica → `raw_paste` identico + 4 righe + metadati

### C3. UI smoke (se avete harness)
Se esiste harness di test UI nel repo:
- aggiungere smoke: incolla testo → analizza → preview popolata

---

## D) Contratti di tracciabilità

- Ogni import deve salvare:
  - `source = EDILUS_MS`
  - `timestamp_import`
  - `raw_paste` (integrale)

- Ogni parsing deve produrre:
  - `quality` + `messages[]`

---

## E) Criteri di accettazione (Automation)

- È presente il servizio `spectrum_paste_service.py` nel percorso canonico.
- Il project model contiene `project.seismic_inputs.ntc2018_hazard_profile`.
- Persistenza OK (round‑trip).
- Parser robusto (dot/comma).
- Test parser e persistenza verdi.
- UI consente incolla in blocco e mostra preview.

---

## F) Nota legale/tecnico‑prudenziale

L’utente è responsabile della verifica e dell’uso dei parametri importati dal servizio esterno; il software conserva `raw_paste` e la fonte per audit. [1](https://www.concrete.org/publications/getarticle.aspx?m=icap&pubid=51689626)