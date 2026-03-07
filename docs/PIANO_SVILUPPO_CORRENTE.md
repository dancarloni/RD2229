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

## FASE E.6 — Cantonali e Aperture (Meccanismo Ribaltamento + Riduzione Resistenza)

**Stato**: TODO (analisi completata, sub-plan scritto)
**Priorita**: ALTA (collegamento diretto con E.3 + D.3)
**Obiettivo**: (A) Meccanismo di ribaltamento del cantonale (cuneo 3D semplificato),
(B) riduzione resistenza maschi d'angolo per aperture ravvicinate.

### Analisi Q&A completata (2026-03-06)

Tre sotto-problemi identificati, due in scope E.6:

1. **Ribaltamento cantonale** (priorita' A): cuneo 3D proiettato su piano a 45°,
   modulo separato `cantonale.py`. Carichi: peso cuneo + puntone tetto + solaio +
   catene + ritegno cordolo D.3. Integrato in analisi_tutti_meccanismi con flag "3D".

2. **Riduzione resistenza maschi d'angolo** (priorita' A): diagnostica distanza
   apertura-angolo (normativa + regola pratica + configurabile), coefficiente
   riduzione lineare, applicabile a V_Rd e/o alpha_0 a scelta utente.
   Flag `is_cantonale` automatico con override manuale.

3. **Apertura nuovi vani** (fase separata R): confronto prima/dopo, telaio cerchiatura.

Decisioni chiave:
- Modulo separato `src/methods/muratura/cantonale.py` (massima modularita')
- Modello 2D semplificato (proiezione 45°), 3D completo come TODO futuro
- Spinta puntone: 2 formulazioni + input generico
- Coperture: padiglione, capanna, generica
- Collegamento D.3: ritegno generico (default) + nodo angolo specifico (evoluzione)

### Sub-plan (6 sotto-fasi E.6.1 — E.6.6)

Dettaglio completo in `docs/PIANO_LAVORO.md` sezione E.6.

---

## FASE P — Azioni Sismiche Multinorma

**Stato**: COMPLETATO (2026-03-06)
**Priorita**: IMMEDIATA (eseguita)
**Obiettivo**: Package `src/codes/seismic/` per calcolo azioni sismiche con
forza alla base + distribuzione piani per 7 norme: RD2229, DM92, DM96,
OPCM3274, EC8, NTC2008, NTC2018.

### Architettura

```text
src/codes/seismic/
├── __init__.py       # PianoEdificio, calcola_azione_sismica (re-export)
├── base.py           # PianoEdificio, distribuzione_triangolare, _base_contract
├── rd2229.py         # Coefficienti storici 0.0/0.05/0.07/0.10
├── dm92.py           # F_h = C*I*eps*W, zone 1/2/3 (DM 3/6/1981 + agg.1992)
├── dm96.py           # F_h = C*I*eps*W, zone 1/2/3 (DM 16/1/1996)
├── opcm3274.py       # 4 zone ag fisso, F0=2.5, spettro via spectrum.py
├── ec8.py            # Tipo1/Tipo2, S fisso per cat suolo, F0=2.5
├── ntc2008.py        # Riusa spectrum.py NTC2018, norm_ref=NTC2008
└── dispatcher.py     # routing multinorma su norma_attiva
```

### Attivita completate

- [x] **P.1** `base.py`: PianoEdificio, distribuzione_triangolare, `_base_contract`
- [x] **P.2** `rd2229.py`: calcola_azione_sismica_rd2229 (STATICO_EQUIVALENTE)
- [x] **P.3** `dm92.py` + `dm96.py`: metodo statico equivalente, zone 1-3
- [x] **P.4** `opcm3274.py`: 4 zone, spettro elastico via spectrum.py
- [x] **P.5** `ec8.py`: Tipo1/Tipo2, `_spettro_elastico_ec8` locale
- [x] **P.6** `ntc2008.py`: riusa spectrum.py, solo norm_ref diverso
- [x] **P.7** `dispatcher.py`: routing per norma_attiva (case-insensitive)
- [x] **P.8** `tests/test_azioni_sismiche_multinorma.py` (54 test)
  - TestDistribuzionePiani (5), TestAzioneRD2229 (8), TestAzioneDM92 (8)
  - TestAzioneDM96 (6), TestAzioneOPCM3274 (6), TestAzioneEC8 (8)
  - TestAzioneNTC2008 (5), TestDispatcher (8)
- [x] **P.9** Aggiornamento documentazione

### Valori di riferimento verificati

- DM96 zona 2, W_tot=1500 kN: F_base = 105 kN (C=0.07 * 1500)
- EC8 Tipo1 cat B, ag=0.25g, T_1=TC=0.5s, q=1.5: V_b = 750 kN
  (Se = 0.25*9.81*1.2*2.5 = 7.3575 m/s²; Sd = 4.905 m/s²)
- NTC2008 e NTC2018 con stessi parametri → stesso V_b (verificato in test)

---

## Fasi Successive

| Fase | Descrizione | Note |
|------|-------------|------|
| O | Griglia INGV + **Spettro NTC2018** (SS, ST, classe uso, vita nominale) | **Gap critico** identificato 2026-03-06: G.1/G.5/POR/cinematica usano S_a/alpha_S esterni |
| E.6 | Cantonali e aperture (ribaltamento + riduzione) | Sub-plan pronto, da implementare |
| D.3 | Traliccio reticolare piano (cordolo muratura) | Sub-plan pronto, da implementare |
| A.2 | MaterialSource strutturata | Sub-plan pronto, da implementare |
| N | Carote cls in sito (9 formulazioni) | Da implementare |
| J | Pressoflessione deviata multinorma (6 norme, dominio 3D, TA+SLU) | COMPLETATO — commit `[pending]` |
| I | Parametri statici sezioni completi | COMPLETATO — commit `3bed1a7` |
| L | Cross-Pozzati telai piani | Da implementare |
| R | Edifici esistenti LC/FC, vulnerabilita | Dipende da N |
| H | Riorganizzazione methods/ per norma | Solo se necessario |
| K | Grafici | Da implementare |

### Gap critico — Spettro NTC2018 (identificato 2026-03-06)

Tutti i moduli che calcolano forze sismiche (G.1 check_slu, G.5 spectral_acceleration_floor
e drift Metodo B, F.5 POR forze in altezza, E.3 cinematica) ricevono S_a/alpha_S/S_d
come parametri gia' calcolati esternamente dall'utente (da EdiLus-MS o manualmente).

Il software NON calcola autonomamente la catena NTC2018 SS3.2.3:
  cat. suolo (A-E) + cat. topogr. (T1-T4) + classe d'uso + vita nominale
    -> SS, ST, Cu, VR -> ag, F0, TC* (da INGV) -> alpha_S = (ag/g)*SS*ST
    -> Se(T), Sd(T), S_a piano (eq.7.2.5), S_d(T_1)

Stato attuale `spectrum_paste_service.py`: importa ag, F0, TC* da EdiLus-MS
(parsing/storage), memorizza class_of_use e vita_nominale_years, ma NON
calcola SS, ST, alpha_S. E' il punto di integrazione per O.2.

Modulo da creare: `src/codes/ntc2018/spectrum.py` (sub-plan completo in FASE O di PIANO_LAVORO.md).

---

## FASE I — Sezioni parametri statici completi (COMPLETATO)

**Stato**: COMPLETATO — commit `[pending]`
**Test**: 91 test, 0 falliti

### Attivita completate

- `src/codes/section_params/norme_n.py`: `get_n_for_norm()` per RD2229/DM92/DM96/NTC2008/NTC2018/EC2
- `src/codes/section_params/omogenizzata.py`: sezione integra + fessurata + tensioni SLE
- `src/codes/section_params/composita.py`: IPE_TABLE (18 profili) + sezione composta IPE+soletta
- `src/codes/section_params/disegno_sezione.py`: matplotlib headless (profilo+barre+AN+diagramma)
- `src/gui/widgets/sezione_canvas.py`: widget Qt (PySide6/PyQt6) anteprima real-time
- `tests/test_sezione_omogenizzata.py`: 91 test (norma n, omogenizzata, fessurata, SLE, composita, disegno)

### Decisioni progettuali

- n per RD2229 selezionabile 8/10/12/15 (default 15); NTC2018 default 15 (§4.1.2.1.4.2 long-term)
- Asse neutro fessurato: formula analitica per rettangolare+N=0+singola fila, bisect generale
- Duck typing su section_type tramite section_fiber.py (stessa interfaccia per tutti i tipi)
- Disegno matplotlib separato da Qt (nessun backend forzato); Qt canvas via FigureCanvasQTAgg

---

## FASE J — Pressoflessione deviata multinorma (COMPLETATO)

**Stato**: COMPLETATO — commit `[pending]`
**Test**: 70 test in `tests/test_pressoflessione_deviata.py`, 0 falliti
**Retrocompat**: 91 test `test_sezione_omogenizzata.py` invariati

### Attivita completate

- `src/codes/section_params/omogenizzata.py`: aggiunto `x: float = 0.0` a BarraArmatura (retrocompat)
- `src/codes/pressoflessione/base.py`: PressoflessSpec, PressoflessResult, DominioNMy, omogenizzata biassiale
- `src/codes/pressoflessione/ta_cls.py`: sovrapposizione elastica + Bresler TA (RD2229/DM92/DM96)
- `src/codes/pressoflessione/slu.py`: wrapper SLU checks_ntc2018 (NTC2018/NTC2008/EC2)
- `src/codes/pressoflessione/dominio.py`: dominio 3D + 3 funzioni matplotlib
- `src/codes/pressoflessione/instabilita_biassiale.py`: amplificazione omega biassiale
- `src/codes/pressoflessione/dispatcher.py`: entry-point unico multinorma
- `src/gui/widgets/dominio_canvas.py`: widget Qt interattivo (3 viste, slider N/theta)

### Decisioni progettuali

- Codice esistente (checks_rd2229, checks_ntc2018) non modificato: nuovo package e' motore puro parallelo
- BarraArmatura estesa con x=0.0 (backward-compatible)
- Sezione omogenizzata biassiale: I_y_c via integrazione strip b(y)^3/12
- Duck typing su tutti i tipi sezione via section_fiber.py
- SLU delega a check_pressoflessione_slu (no duplicazione codice)
- Instabilita' riusa omega_ca() da instabilita.py (no copia)
