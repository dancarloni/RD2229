# PIANO DI SVILUPPO CORRENTE — Registro Attivita

> Questo file e la guida operativa e il registro delle attivita in corso.
> Ogni funzionalita completata e marcata con `[x]` e il commit hash.
> I sub-plan vengono aggiunti progressivamente sotto ogni TODO.

**Ultimo aggiornamento**: 2026-03-06
**Sessione iniziata da**: docs/CLAUDEPLAN/Conversazione.md + docs/CLAUDEPLAN2/

---

## Stato Moduli Esistenti (NON modificare senza approvazione)

I seguenti moduli sono gia completati e funzionanti. Non devono essere
ricreati. Possono essere modificati solo per collegamento/integrazione
con nuovi moduli, previa approvazione.

| Fase | Modulo | Stato |
|------|--------|-------|
| A | Database materiali multi-norma (97 materiali, 10 cataloghi) | COMPLETATO |
| B | Torsione RD2229 TA (`src/methods/rd2229/torsione.py`) | COMPLETATO |
| C | Instabilita RD2229 TA (`src/methods/rd2229/instabilita.py`) | COMPLETATO |
| D | Acciaio (sagomario, verifiche TA, traliccio 2D, connessioni) | COMPLETATO |
| E | Muratura verifiche locali (compressione, taglio, fuori piano, catene, multipiano) | COMPLETATO |
| F | POR telaio equivalente (modello, discretizzazione, rigidezza, pushover) | COMPLETATO |
| G.1 | Elementi secondari NTC2018 — SLU forza inerziale F_a | COMPLETATO |
| G.2 | Elementi secondari NTC2018 — SLE compatibilita drift | COMPLETATO |
| G.3 | Elementi secondari — Storage adapter CRUD | COMPLETATO |
| G.4 | Elementi secondari DM96/DM92 + RD2229 (40 test) | COMPLETATO |
| G.5 | Stima T_a (4 modelli) + drift Metodo B (37 test) | COMPLETATO |

---

## FASE G.4 — Elementi Secondari per Normative Storiche

**Stato**: COMPLETATO
**Priorita**: IMMEDIATA (eseguita)
**Obiettivo**: Estendere la copertura elementi secondari a DM96/DM92 e RD2229

### Analisi normativa

- **NTC2018** (gia completato in `src/codes/ntc2018/secondary_elements/checks.py`):
  F_a = (S_a * W_a * gamma_a) / q_a; drift limit h/200 per elementi fragili

- **DM96/DM92**: F_h = C * W (coefficiente sismico semplificato per piano);
  drift limit h/300 tipico

- **RD2229**: Nessun concetto di "elemento secondario" sismico (norma pre-sismica).
  Verifica di stabilita TA per elementi snelli sotto soli carichi gravitazionali.
  Riutilizza `src/methods/rd2229/instabilita.py` per lambda > 50.

### Struttura esistente (da non modificare)

- `src/codes/ntc2018/secondary_elements/checks.py` — pattern contratto base (_base_contract)
- `src/codes/ntc2018/secondary_elements/models.py` — SecondaryElementSpec, DriftSpec
- `src/codes/ntc2018/secondary_elements/storage_adapter.py` — CRUD in-memory
- `verifications/secondary_elements/dispatcher.py` — routing (attualmente solo NTC2018)
- `config/calculation_codes/SECONDARY_ELEMENTS.jsoncode` — configurazione check

### Sub-plan

- [x] **G.4.0** Verifica stato attuale codebase elementi secondari
  - Risultato: `src/codes/dm96/` e `src/codes/rd2229/` non esistono, da creare
  - Dispatcher ignora norma_attiva, instrada tutto a NTC2018
  - 5 test esistenti in `test_secondary_elements_gating.py`

- [x] **G.4.1** Creare package `src/codes/dm96/secondary_elements/`
  - `__init__.py`, `checks.py`, `models.py`
  - `check_slu_dm96()`: F_h = C * beta * W con C da zona sismica (0.10/0.07/0.04)
  - `check_sle_dm96()`: drift con limite h/300 = 0.00333
  - `SecondaryElementSpecDM96`: zona_sismica, piano, n_piani, beta_piano, validate()
  - Coefficienti: COEFFICIENTE_SISMICO_C = {1: 0.10, 2: 0.07, 3: 0.04}

- [x] **G.4.2** Creare package `src/codes/rd2229/secondary_elements/`
  - `__init__.py`, `checks.py`
  - `check_stabilita_ta()`: sigma_c = omega * N / A <= sigma_c_adm
  - Riutilizza `omega_ca()` da `src/methods/rd2229/instabilita.py`
  - `check_sle_rd2229()`: ritorna NOT_APPLICABLE (norma pre-sismica)

- [x] **G.4.3** Estendere dispatcher per routing multi-norma
  - Modifica a `verifications/secondary_elements/dispatcher.py`
  - Routing basato su `norma_attiva`: NTC2018 (default), DM96/DM92, RD2229
  - 3 funzioni private: `_dispatch_ntc2018()`, `_dispatch_dm96()`, `_dispatch_rd2229()`
  - Test originali (5) continuano a passare senza modifiche

- [x] **G.4.4** Test `tests/test_secondary_elements_historical.py` (35 test)
  - TestDM96Models: 6 test (coefficienti, beta, validazione)
  - TestDM96CheckSLU: 6 test (forza zona 1/2/3, resistenza, contratto)
  - TestDM96CheckSLE: 5 test (drift ok/non ok, default h/300, estimated, non fornito)
  - TestRD2229CheckSLU: 9 test (compressione, snellezza, non compresso, lambda calcolata, contratto)
  - TestRD2229CheckSLE: 1 test (NOT_APPLICABLE)
  - TestDispatcherRouting: 8 test (NTC2018, DM96, DM92, RD2229 SLU/SLE, gating, trace)

- [x] **G.4.5** Aggiornare `docs/PIANO_LAVORO.md` con completamento G.4
  - Stato G.4 -> COMPLETATO
  - Checkbox [x] per tutti i sotto-punti
  - Aggiornato contatore test: ~1801
  - 3 righe aggiunte alla tabella "GIA COMPLETATO"

---

## FASE G.5 — Stima Periodo T_a e Drift Metodo B

**Stato**: COMPLETATO
**Priorita**: IMMEDIATA (eseguita)
**Obiettivo**: Implementare gli stub ta_models.py e drift_models.py con calcoli reali

### Analisi normativa

- **T_a (periodo fondamentale elemento)**: NTC2018 §7.2.3 richiede T_a per calcolare
  l'accelerazione spettrale al piano S_a. Quattro modelli disponibili:
  - RIGID: T_a = 0 (elemento rigido, nessuna amplificazione)
  - CANTILEVER_EQ: T_a = 2*pi*sqrt(m*H^3/(3*E*I)) — mensola equivalente
  - SDOF_EQ: T_a = 2*pi*sqrt(m/k) — oscillatore semplice equivalente
  - MANUAL: valore fornito dall'utente

- **S_a al piano** (NTC2018 eq. 7.2.5):
  S_a = alpha_S * max(3*(1+z/H)/(1+(1-T_a/T_1)^2) - 0.5, 1.0)

- **Drift Metodo B** (shear-building proxy semplificato):
  delta_r = S_d(T_1) * (z/H) * soft_storey_factor / h_interpiano
  Confidence = LOW. Input S_d come valore numerico (no dipendenze circolari).

### Sub-plan

- [x] **G.5.1** Implementare `ta_models.py` (da stub a implementazione)
  - `estimate_ta(spec)`: dispatcher per ta_model (RIGID/CANTILEVER_EQ/SDOF_EQ/MANUAL)
  - `spectral_acceleration_floor(z, H, T_a, T_1, alpha_S)`: NTC2018 eq. 7.2.5
  - Validazione parametri con `_require_positive()`, messaggi errore chiari
  - decision_log tracciabile per ogni modello

- [x] **G.5.2** Implementare `drift_models.py` (da stub a implementazione)
  - `estimate_drift_metodo_b(spec, soft_storey_factor)`: Metodo B con confidence=LOW
  - `estimate_drift_user(value)`: valore utente, confidence=HIGH
  - `estimate_drift_global(value)`: valore da analisi globale, confidence=HIGH
  - soft_storey_factor < 1.0 forzato a 1.0

- [x] **G.5.3** Test `tests/test_ta_drift_models.py` (37 test)
  - TestEstimateTaRigid (3), TestEstimateTaCantilever (4), TestEstimateTaSdof (2)
  - TestEstimateTaManual (4), TestEstimateTaUnknown (3)
  - TestSpectralAccelerationFloor (7): base, sommita, risonanza, minimo, zero, errori
  - TestDriftMetodoB (9): calcolo, confidence, source, ssf, z=0, decision_log, errori
  - TestDriftUser (3), TestDriftGlobal (2)

- [x] **G.5.4** Aggiornare documentazione
  - PIANO_LAVORO.md: G.5 COMPLETATO, test ~1838, 2 righe GIA COMPLETATO
  - PIANO_SVILUPPO_CORRENTE.md: registro dettagliato

---

## FASE D.3 — Traliccio Reticolare Piano (Cordolo Metallico Reticolare)

**Stato**: TODO (analisi completata, sub-plan scritto)
**Priorita**: ALTA (collegamento diretto con E.3 meccanismi fuori piano)
**Obiettivo**: Modulo tralicci piani in acciaio, caso d'uso primario come cordolo
reticolare orizzontale su muratura, utilizzabile anche standalone.

### Analisi Q&A completata (2026-03-06)

Concetto chiave: il traliccio e' disposto **orizzontalmente in pianta** sulla sommita'
del muro. Entrambi i correnti sono nello spessore della muratura. Il cordolo si oppone
ai meccanismi fuori piano (ribaltamento, spanciamento, cuneo d'angolo) con la rigidezza
nel piano di maggiore inerzia.

Decisioni principali:
- Schemi: Warren, Pratt, custom (disegno grafico libero in fase futura)
- Profili: piatti, angolari, profili standard da sagomario
- Solutore: riuso `traliccio_2d.py` (piano XY reinterpretato come orizzontale)
- F da `cinematica.py` (automatico), distribuzione proporzionale o discreta
- Vincoli: appoggi estremi + molle distribuite (configurabili)
- Collaborazione muro: grado configurabile dall'utente
- Verifiche: SLU + SLE + fatica (TODO placeholder)
- Instabilita': entrambi i piani, selezionabile
- Normativa: selezionabile (NTC2018 SLU / TA storica)
- Integrazione cinematica: cordolo = vincolo sommitale, ricalcolo alpha_0
- Flusso iterativo cinematica <-> traliccio: TODO futuro
- Uso standalone: si'

### Sub-plan (9 sotto-fasi D.3.1 — D.3.9)

Dettaglio completo in `docs/PIANO_LAVORO.md` sezione D.3.

Ordine di priorita' consigliato:
1. D.3.1 Generatore schemi (Warren/Pratt + pre-dimensionamento)
2. D.3.2 Adattamento solutore (molle, carichi distribuiti, rigidezza globale)
3. D.3.3 Modulo cordolo reticolare (dataclass, integrazione F da cinematica)
4. D.3.4 Verifiche aste (compressione, trazione, instabilita', connessioni)
5. D.3.5 Integrazione cinematica (ritegno sommitale, ricalcolo alpha_0)
6. D.3.6 Nodo d'angolo (cantonali)
7. D.3.7 Report e tabulato
8. D.3.8 Test
9. D.3.9 Tool disegno grafico avanzato (FASE FUTURA)

---

## Fasi Successive

| Fase | Descrizione | Note |
|------|-------------|------|
| D.3 | Traliccio reticolare piano (cordolo muratura) | Sub-plan pronto, da implementare |
| A.2 | MaterialSource strutturata | Sub-plan pronto, da implementare |
| N | Carote cls in sito (9 formulazioni) | Da implementare |
| J | Pressoflessione deviata (Bresler, N-Mx-My) | Da implementare |
| I | Parametri statici sezioni completi | Da verificare cosa esiste |
| L | Cross-Pozzati telai piani | Da implementare |
| R | Edifici esistenti LC/FC, vulnerabilita | Dipende da N |
| H | Riorganizzazione methods/ per norma | Solo se necessario |
| K | Grafici | Da implementare |
