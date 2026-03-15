# Fase X2 — Carichi e Combinazioni

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | COMPLETATO |
| Commit | local (implementazione e test in-session) |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test eseguiti | unit tests X2 (tests/test_x2_carichi_combinazioni.py) |
| Ambito | Carichi, combinazioni, LC/FC applicativo |

---

## Obiettivo esecutivo

Implementare un modulo X2 che prenda in ingresso i carichi (G1, G2, Q, categoria, aree) e produca:

- carichi normalizzati in unità SI (kN/m² / MPa)
- combinazioni SLU + SLE secondo NTC2018 §2.5.3 (Tab. 2.5.I + 2.6.I)
- applicazione dei fattori LC/FC (NTC2018 §8.5.4) sui materiali esistenti
- avvisi/issue codificati (X2-XXX) per casi non pienamente normativi ma necessari (categoria mancante, area manuale, FC usato)
- output strutturato per la pipeline (X3) e per la GUI

---

## Dipendenze principali (codebase)

- `src/core/combinations/ntc2018_combinations.py` (generatore combinazioni)
- `src/codes/params/NTC2018.json` (coeff. psi/gamma, parametri materia)
- `src/codes/clauses/NTC2018.yml` (normativa / clausole)
- `src/core_calculus/lc_fc_adjustments.py` (LC/FC per esistenti)
- `src/core_calculus/units.py` (conversioni unità, già usata in X1)
- `src/core/registro_log.py` (tracciatura log operazioni)

---

## Specifica: schema input/output

### Input (carichi)

Il modulo X2 deve accettare un payload JSON/di dict con almeno queste sezioni:

- `G1`: float (carico permanente strutturale) *[kgf/m² o kN/m²]*
- `G2`: float (carico permanente non strutturale) *[kgf/m² o kN/m²]*
- `Q`: float (carico variabile principale) *[kgf/m² o kN/m²]* — opzionale se `variable_loads` è fornito
- `variable_loads`: list[dict] opzionale, ciascuno con:
  - `name`: string (es. "Q1", "neve", "vento")
  - `value`: float (carico) *[kgf/m² o kN/m²]*
  - `category`: string (es. `cat_A`, `cat_B`, …) — se assente si usa `cat_A` con warning X2-COMB-001
- `categoria`: string (categoria uso secondo NTC2018 Tab. 2.5.I). Se fornito, viene mappato a `cat_X` (es. `A` → `cat_A`).
- `lc`: string | None (LC1/LC2/LC3) – opzionale, per esistenti
- `fc`: float | None (fattore confidenza) – opzionale
- `area_influenza_m2`: float | None (area di influenza) – opzionale, warning X2-AREA-001 se assente

> Nota: il modulo accetta sia carichi in kgf/m² che in kN/m² e ne rileva automaticamente l’unità (auto-normalizzazione).
>
### Output (payload X2)

Output primario (dict) deve includere almeno:

- `normalized`: carichi in unità SI (kN/m²)
- `combinations`: elenco di combinazioni (SLU + SLE) con fattori e totale
- `lc_fc`: dati LC/FC applicati (se presenti) con `f_ck_adjusted`, `f_yk_adjusted`, `gamma_c`, `gamma_s`, `lc`, `fc`
- `warnings`: elenco di warning nei codici X2-XXX

---

## Normative / riferimenti precisi (rigorosi)

- **NTC2018 §2.5.3 eq. 2.5.1** — SLU fondamentale: `Ed = γ_G1·Gk1 + γ_G2·Gk2 + γ_Q·(Qk1 + Σψ_0i·Qki)`
- **NTC2018 §2.5.3 eq. 2.5.2** — SLE rara: `Ed = Gk + Qk1 + Σψ_0i·Qki`
- **NTC2018 §2.5.3 eq. 2.5.3** — SLE frequente: `Ed = Gk + ψ_1,1·Qk1 + Σψ_2i·Qki`
- **NTC2018 §2.5.3 eq. 2.5.4** — SLE quasi-permanente: `Ed = Gk + Σψ_2i·Qki`
- **NTC2018 §2.5.3 Tab. 2.5.I** — coefficienti ψ per categorie d’uso
- **NTC2018 §2.5.3 Tab. 2.6.I** — coefficienti parziali γ per carichi
- **NTC2018 §8.5.4** — applicazione FC / riduzione proprietà materiali per strutture esistenti

> Nota per implementazione: i coefficienti ψ/γ siano preferibilmente letti da `src/codes/params/NTC2018.json` per evitare hardcode e facilitare eventuali aggiornamenti.

---

## Formule e conversioni obbligatorie (da codificare)

- **Unità**
  - kgf/m² → kN/m²: `kN/m² = kgf/m² * 0.00980665`
  - kgf/cm² → MPa: `MPa = kgf/cm² * 0.0980665`
  - cm → m: `m = cm * 0.01`

- **Superficie → linea** (usata in precedenza per solai):
  - `q_l (kgf/cm) = q_s (kgf/m²) * i (cm) / 10_000`

- **LC/FC (NTC 2018 §8.5.4)**
  - `f_ck_adj = f_ck / FC`
  - `f_yk_adj = f_yk / FC`

---

## Warning code del modulo (definizioni estese)

- **X2-COMB-001**: categoria d'uso mancante o vuota → usata categoria di default `cat_A` con warning
- **X2-COMB-002**: categoria d'uso non mappata → usata categoria di fallback `cat_A` + warning
- **X2-COMB-003**: assenza di carichi variabili (`Q` e `variable_loads`) → generate sole combinazioni permanenti
- **X2-LC-001**: applicato LC/FC (materiali ridotti) su struttura esistente
- **X2-LC-002**: LC/FC richiesto ma non applicabile (materiali assenti o input LC/FC non valido)
- **X2-AREA-001**: area di influenza non fornita (richiesta per output dimensionale)

---

## Sub-fasi implementative (dettagliate)

### X2.1 — Normalizzazione carichi (unità)

1. Definire data contract per l’input carichi (`G1`, `G2`, `Q`, `categoria`, `lc`, `fc`, `area_influenza_m2`).
2. Implementare funzione `normalize_loads` (o analogo) che: 
   - stabilisce unit system (`legacy_kgf_m2` vs `si`) tramite regole euristiche o input esplicito
   - converte G1/G2/Q in kN/m² usando `src/core_calculus/units.py` (coefficienti costanti)
   - normalizza categorie in formato `cat_X` per l’uso con `ntc2018_combinations`
3. Implementare test per:
   - conversione da kgf/m² a kN/m² (controllo valore)
   - rilevamento di unità legacy vs SI
   - mapping corretto da `A` → `cat_A` (e casi non mappati)

### X2.2 — Combinazioni NTC (wrapper)

1. Creare wrapper `generate_combinations` in `src/core_calculus/carichi_combinazioni.py`:
   - riceve carichi normalizzati + lista variabile (anche se monocarico)
   - legge coefficienti psi/γ da `src/codes/params/NTC2018.json` (fallback ai valori hardcoded in `ntc2018_combinations` se non presenti)
   - invoca `ntc2018_combinations.generate_all_combinations` con input strutturato
   - restituisce lista combinazioni con metadata (`type`, `dominant_action`, `factors`, `total`)
2. Gestire il caso “solo permanenti” (senza variabili) come previsto da `generate_slu_combinations`.
3. Generare warning `X2-COMB-002` se `categoria` non trova corrispondenza.

### X2.3 — Applicazione LC/FC

1. Ingestione input `lc` e `fc` (opzionale) dal payload carichi.
2. Se presenti, usare `apply_lc_fc_adjustments` per ottenere `AdjustedMaterialProperties`.
3. Esporre in output `lc_fc` con tutti i campi (original/adjusted/gamma/descrizione).
4. Produrre warning `X2-LC-001` quando LC/FC applicati.

### X2.4 — Test + benchmark base

1. Coprire con test unitari:
   - combinazioni SLU + SLE (X2-T01): oneri con categorie A/B, corroborare numero di combinazioni 
   - LC/FC: `fc=1.2` produce `f_ck_adjusted = f_ck/1.2` (X2-T02)
   - categoria mancante → warning X2-COMB-001 (X2-T03)
   - categoria ignota → warning X2-COMB-002 e fallback `cat_A` (X2-T03)
   - area mancante → warning X2-AREA-001 (X2-T04)
   - verif. conversione unità (kgf/m² → kN/m²) (X2-T05)
   - output schema (normalized + combinations + lc_fc + warnings)
2. Predisporre fixture JSON di input (simile a X1) per test end-to-end.
3. Valutare benchmark rapido (misura tempi di generazione per 1000 combinazioni) se richiesto.

---

## Dipendenze di implementazione da aggiornare

Di seguito lo stato preciso per ciascuna dipendenza/file coinvolto nella Fase X2.

- [src/core_calculus/carichi_combinazioni.py](src/core_calculus/carichi_combinazioni.py): **Completed** — modulo orchestratore implementato e testato (API `process_carichi_combinazioni`).
- [src/codes/params/NTC2018.json](src/codes/params/NTC2018.json): **Completed** — file di parametri disponibile e letto come fallback dai componenti X2.
- [Possibile catalogo categorie / mappatura esterna A→cat_A]: **Optional / TODO** — la mappatura semplice `A`→`cat_A` è già gestita in codice; creare un catalogo esterno è facoltativo per estensioni future.
- [src/core_calculus/units.py](src/core_calculus/units.py): **Completed** — funzioni di conversione centralizzate presenti e riutilizzate.
- [src/core_calculus/lc_fc_adjustments.py](src/core_calculus/lc_fc_adjustments.py): **Completed** — LC/FC engine presente e utilizzato da X2.
- [src/core/combinations/ntc2018_combinations.py](src/core/combinations/ntc2018_combinations.py): **Completed** — generatore combinazioni presente; esteso per accettare tabella `psi` da params.
- [src/core_calculus/solaio_input.py](src/core_calculus/solaio_input.py): **Completed (integration-ready)** — normalizzazione input X1 pronta e compatibile con X2.
- [src/core/registro_log.py](src/core/registro_log.py): **Completed** — API logging usata da X2 per `registro.calcolo` / `registro.debug`.
- [tests/test_x2_carichi_combinazioni.py](tests/test_x2_carichi_combinazioni.py): **Completed** — suite unit test creata e passata localmente.
- [tests/fixtures/carichi_combinazioni_valid.json](tests/fixtures/carichi_combinazioni_valid.json): **Completed** — fixture usata nei test.
- [docs/piano_fase_X2_carichi_combinazioni.md](docs/piano_fase_X2_carichi_combinazioni.md): **Completed (aggiornato)** — documento aggiornato con stato e file correlati.

TODO operazioni residue (raccomandate):

- Integrazione pipeline X1→X2→X3: **TODO** — collegare `solaio_input.as_ready_dict()` a chiamata a `process_carichi_combinazioni` e verificare flusso end-to-end con test di integrazione.
- Test di integrazione end-to-end (pipeline): **TODO** — aggiungere test che eseguano X1→X2 e controllino payload X3 risultante.
- Commit & push su remoto (branch di feature + PR): **TODO** — le modifiche sono salvate localmente nel repository, manca il push/PR.
- Documentazione aggiuntiva sul catalogo categorie (se si crea): **TODO/Optional** — se si crea il catalogo esterno, aggiungere schema e test di caricamento.

---

## File correlati e dipendenze (lista completa)

Elenco dei file sorgente, dati e test direttamente coinvolti nella Fase X2.

- [src/core_calculus/carichi_combinazioni.py](src/core_calculus/carichi_combinazioni.py): modulo orchestratore X2 (normalizzazione carichi, wrapper combinazioni, LC/FC, warning).
- [src/core/combinations/ntc2018_combinations.py](src/core/combinations/ntc2018_combinations.py): generatore combinazioni SLU/SLE (coeff. psi/γ, logica combinatoria).
- [src/core_calculus/units.py](src/core_calculus/units.py): conversioni unità (kgf→kN, kgf/m²→kN/m², kgf/cm²→MPa, cm→m).
- [src/core_calculus/lc_fc_adjustments.py](src/core_calculus/lc_fc_adjustments.py): applicazione LC/FC su materiali esistenti (AdjustedMaterialProperties).
- [src/core_calculus/solaio_input.py](src/core_calculus/solaio_input.py): ordine e normalizzazione input X1 → utile per pipeline verso X2.
- [src/core/registro_log.py](src/core/registro_log.py): API di logging/tracciatura usata da X2 (`registro.calcolo`, `registro.debug`).
- [src/codes/params/NTC2018.json](src/codes/params/NTC2018.json): coefficenti `combination_coefficients` e `partial_factors` (psi/γ) utilizzati da X2; fallback ai valori di default se assente.
- [tests/test_x2_carichi_combinazioni.py](tests/test_x2_carichi_combinazioni.py): suite unit test per X2 (normalizzazione, combinazioni, LC/FC, warning codes).
- [tests/fixtures/carichi_combinazioni_valid.json](tests/fixtures/carichi_combinazioni_valid.json): fixture JSON usata nei test X2.
- [docs/piano_fase_X2_carichi_combinazioni.md](docs/piano_fase_X2_carichi_combinazioni.md): specifica e stato (questo file).

Nota: la lista include i file creati/modificati durante l'implementazione X2 in-session; altri moduli del codice (es. `src/methods/*`, `src/core/*`) possono interagire con X2 ma non sono modificati da questa fase.

## Decisioni chiuse (per il plan corrente)

- **Formato categorie**: usiamo `cat_A`, `cat_B`, … in input (mappatura automatica da `A` → `cat_A` supportata).
- **Azioni variabili multiple**: supporto esteso con lista `variable_loads` (multi-Q) + supporto compatto con campo singolo `Q`.
- **Unità in input**: supportiamo sia kgf/m² sia kN/m² con rilevamento automatico e normalizzazione.
- **Area influenza**: campo opzionale `area_influenza_m2`; se assente viene emesso warning `X2-AREA-001` e il modulo procede comunque.

---

## Stato avanzamento sub-fasi (updated)

- [x] X2.1 — Normalizzazione carichi (unità & categorie)
- [x] X2.2 — Wrapper combinazioni NTC (psi/γ da params)
- [x] X2.3 — LC/FC (NTC2018 §8.5.4) + warning X2-LC-001
- [x] X2.4 — Test unitari + fixture + oggetto output verificabile

---

## Diagramma dipendenze subfasi

```text
X2.1 → X2.2 → X2.3 → X2.4
```

---

## Rischi normativi residui

- Categorie d'uso non mappate nel catalogo locale.
- Incoerenze tra dati manuali e classificazione azioni permanenti.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X2 da split master Fase X.
