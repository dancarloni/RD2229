# NTC2018 — Spectrum Paste Service (EdiLus‑MS) — PLAN‑ONLY

> **Obiettivo**: introdurre nel software un servizio “Spettro NTC2018” che **non calcola** la pericolosità di base, ma consente di:
> 1) impostare **Classe edificio/uso**, **Vita Nominale (VN)**, **Periodo di Riferimento (VR)**;
> 2) fare **paste in blocco** della tabella testuale proveniente da EdiLus‑MS;
> 3) parsare e salvare i parametri **Tr, ag/g, F0, Tc\*** per gli stati limite.
>
> EdiLus‑MS espone questi campi e la tabella “Parametri di pericolosità Sismica” con colonne **Tr, ag/g, F0, Tc\*** e righe per stati limite (Operatività, Danno, Salvaguardia Vita, Prevenzione Collasso), copiabili come testo. [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)

---

## 0) Vincoli (non negoziabili)

- **PLAN‑ONLY**: in questa fase si definiscono file, percorsi, contratti, test e UI; **nessun calcolo numerico avanzato** e nessuna logica di interpolazione per pericolosità. [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- **Input dati esterni**: i parametri (ag, F0, Tc\*) sono ottenuti da applicativo esterno (EdiLus‑MS). [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- **Paste robusto**: accettare decimali con **punto** e tollerare anche **virgola** (dipendenza da locale/browser). [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- **Tracciabilità**: salvare anche il **testo originale incollato** (`raw_paste`) + timestamp + fonte. [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)

---

## 1) Decisioni vincolanti (freeze)

- **Percorso canonico del servizio** (VINCOLANTE):
  - `src/codes/ntc2018/spectrum_paste_service.py`
- **Persistenza nel progetto** (VINCOLANTE):
  - singolo profilo `project.seismic_inputs.ntc2018_hazard_profile`

---

## 2) Deliverable (cosa creare)

### 2.1 Documenti MEGAPLAN (repository)
Creare/aggiornare i seguenti file:

1) `docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_SERVICE_PLAN.md`  
   - (questo documento)

2) `docs/MEGAPLAN/SPEC_NTC2018_HAZARD_PASTE.md`  
   - specifica vincolante: schema dati + etichette + regole parsing + validazioni minime

3) `docs/MEGAPLAN/NTC2018_SPECTRUM_PASTE_AUTOMATION.md`  
   - automazione vincolante: lista file target (create/touch), integrazione UI, persistenza, test

---

## 3) Scopo del servizio (MVP)

### 3.1 Funzioni richieste (MVP)
- Inserimento controllato di:
  - `class_of_use` (I–IV)
  - `vita_nominale_years`
  - `vr_years`
- Paste del testo tabellare completo (`raw_paste`)
- Parsing deterministico della tabella per ricavare, per ciascun stato limite:
  - `Tr`, `ag/g`, `F0`, `Tc*` [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- Salvataggio nel progetto come singolo profilo:
  - `project.seismic_inputs.ntc2018_hazard_profile`

### 3.2 Funzioni esplicitamente NON richieste (oggi)
- Calcolo/interpolazione della pericolosità (ag, F0, Tc* da coordinate)
- Scraping/integrazione web
- Calcolo numerico completo dello spettro Sa(T) (opzionale in fase successiva)

---

## 4) Modello dati (overview)
La struttura dati “profilo” deve includere:
- metadati di input (classe uso, VN, VR, label sito facoltativa)
- `raw_paste` integrale
- righe parsate (4 stati limite)
- `quality` + `messages[]`
- timestamp import

(Dettagli completi nello SPEC dedicato.)

---

## 5) Parser — requisiti chiave (overview)

- Riconoscere le etichette degli stati limite come presenti nella tabella (match robusto su spazi/case). [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- Estrarre 4 numeri per riga: `Tr`, `ag/g`, `F0`, `Tc*`.
- Normalizzare decimali:
  - `.` come preferenziale
  - `,` ammesso come fallback (locale/browser).
- Non inventare valori: se righe mancanti o token non numerici → `WARNING/ERROR` e messaggi.

(Dettagli completi nello SPEC dedicato.)

---

## 6) UI (Thin) — “Parametri sismici NTC2018 (Paste)”

### 6.1 Collocazione
- Inserire come pannello/scheda in **Impostazioni progetto → Azioni sismiche (NTC2018)**.

### 6.2 Componenti minimi
- Dropdown `class_of_use` (I–IV) coerente con EdiLus‑MS. [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- Input numerici VN e VR. [1](http://ntc.archliving.it/2019/02/18/capitolo-7-progettazione-per-azioni-sismiche/)
- Input facoltativo `site_label`
- TextArea `raw_paste` con supporto paste in blocco
- Bottone `Analizza` → preview righe parsate
- Indicator `quality` + elenco `messages`
- Bottone `Salva nel progetto`

---

## 7) Persistenza (singolo profilo) — requisiti
- Il project model deve contenere `project.seismic_inputs.ntc2018_hazard_profile`.
- Il repository/adapter deve garantire round‑trip:
  - nessuna perdita di `raw_paste`
  - preservazione di `timestamp_import`, `source`, `parsed_rows`.

---

## 8) Test (minimi e vincolanti)
- Unit test parser:
  - decimali con punto → OK
  - decimali con virgola → OK (normalizzazione)
  - righe mancanti → WARNING
  - token non numerici/mancanti → ERROR
- Test persistenza round‑trip:
  - salva profilo → ricarica → identico (incluso raw_paste)

---

## 9) Checklist di chiusura PLAN
Il PLAN è considerato chiuso quando:
- [ ] Sono presenti i tre file MEGAPLAN (PLAN + SPEC + AUTOMATION)
- [ ] Percorso servizio e persistenza sono riportati come VINCOLANTI
- [ ] Sono definiti: schema dati, regole parsing, UI minima, test minimi
- [ ] Non sono previste interpolazioni o calcoli pericolosità

Solo dopo questa checklist si procede all’implementazione.