# Fase E — Muratura: Verifiche Locali

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | ✅ COMPLETATO |
| Commit | corrente (E.1–E.5, E.7), E.6 commit separato |
| Data completamento | 2026-03-09 |
| Test totali | 49+ (cinematica) + test standalone E.6 |
| File principali | `src/methods/muratura/cinematica.py`, `src/methods/muratura/cantonale.py` |

---

## Descrizione

La Fase E implementa le **verifiche locali per pareti in muratura** secondo NTC2018 §7.8 e Circ. n.7/2019 §C8A. Copre sette categorie:

- **E.1** Compressione con riduzione per snellezza e eccentricità
- **E.2** Taglio nel piano (tre criteri: diagonale, scorrimento, pressoflessione)
- **E.3** Meccanismi locali fuori piano e ribaltamento (cinematica lineare e non lineare)
- **E.4** Spanciamento (snellezza limite)
- **E.5** Catene e paletti (trazione + punzonamento)
- **E.6** Cantonali: ribaltamento 3D + riduzione resistenza aperture (alta priorità)
- **E.7** Muratura multipiano: carichi verticali, combinazioni, verifiche compressione

---

## Teoria e formule chiave

### E.1 — Compressione e snellezza

```text
Verifica compressione:
  σ = N / (t · L)  ≤  Φ · f_d / γ_M

Riduzione per snellezza ed eccentricità:
  λ = h_eff / t         (snellezza geometrica)
  Φ = f(λ, e/t)         (Tab. 4.5.V NTC2018 — interpolazione bilineare)
  h_eff = ρ · h         (ρ fattore di vincolo: 1.0, 0.75, 0.5)
  e/t = M / (N · t)     (eccentricità relativa)
```

### E.2 — Taglio nel piano (formule)

```text
Criterio Turnšek-Čačovič (diagonale):
  V_Rd = (f_vk / γ_M) · L · t / b
  f_vk = f_vk0 + 0.4 · σ_n   (legge di Coulomb estesa)
  b = fattore di forma (1.0÷1.5 per pannelli snelli/tozzi)

Criterio di scorrimento (Mohr-Coulomb):
  V_Rd,s = (f_vk0 + μ · σ_n) / γ_M · L · t

Criterio pressoflessione nel piano:
  V_pf = (L² · t · σ₀) / (2 · h₀) · (1 - σ₀ / (0.85 · f_d))

V_Rd = min(V_Rd_diag, V_Rd_scorrimento, V_pf)
```

### E.3 — Cinematica lineare (Circ. n.7/2019 §C8A.4.1)

```text
Analisi cinematica lineare:
  α₀ = moltiplicatore di collasso attivazione
  M*  = massa partecipante efficace  [kg]
  e*  = eccentricità efficace        [m]
  a₀* = accelerazione spettrale di attivazione = α₀ · g / e*

Verifica a terra:
  a₀*  ≥  max(a_g · S, Se(T1) · ψ(z) · γ)

Verifica in quota (z > 0):
  a₀*  ≥  Se(T_s)

Cinematica non lineare (§C8A.4.2):
  d₀*  = spostamento di collasso attivazione
  d*_u = 0.4 · d₀*
  T_s  = 2π · √(d*_u / (1.5 · Se(T_s)))
```

### E.5 — Catene e paletti (formule)

```text
Verifica trazione catena:
  σ = F_catena / A_barra  ≤  σ_s_adm

Verifica punzonamento piastra:
  σ_p = F_catena / A_piastra  ≤  f_d_muratura

A_piastra:
  circolare: π(d/2)²
  quadrata:  l²
  a paletto: l·t
```

### E.6 — Ribaltamento cantonale 3D

```text
Il cantonale è modellato come cuneo 3D formato dall'intersezione di
due pareti ortogonali. La cerniera di rotazione è lungo lo spigolo.

Carichi agenti:
  W_c  = peso cantonale            (geometria prismatica del cuneo)
  W_copertura = spinta puntone copertura (InputSpinta — angolo θ)
  F_catena = contributo catena/tirante (ForzaCatena — angolo inclinazione)

Moltiplicatore di collasso:
  α₀ = Σ(F_i · d_i_stab) / Σ(W_j · d_j_dest)
  con contributo stabilizzante catena e ritegno cordolo D.3

Riduzione resistenza aperture d'angolo:
  k_rid = coefficiente_riduzione_angolo(distanza_apertura, t_muro, d_min)
  k_rid → 0 per distanza → 0  (funzione asintotica)
```

---

## Diagramma dipendenze

```text
Fase E — flusso dati

  NTC2018 §7.8 + Circ. n.7/2019 §C8A
         │
         ▼
  src/methods/muratura/
  ├── cinematica.py        ─── E.3 — analisi cinematica lin/nonlin
  │     α₀, M*, e*, a₀*, d*_u, T_s, verifica a terra e quota
  │         │
  ├── cantonale.py         ─── E.6 — cuneo 3D + riduzione aperture
  │     RibaltamentoCantonale, diagnostica_apertura_angolo()
  │         │
  └── muratura_ta.py       ─── E.1/E.2 — σ, Φ, V_Rd criteri
        │
        ├──▶  src/methods/muratura/catene.py   (E.5)
        ├──▶  data/muratura/tabelle_phi.json   (Tab. 4.5.V)
        └──▶  Fase D (cordolo reticolare D.3) ─ ritegno_cordolo_kg
                      │
                      ▼
             Fase R (modello globale) ─ integrazione meccanismi E.6
```

---

## Dipendenze da altri moduli

| Modulo | Ruolo |
| --- | --- |
| Fase D — `src/steel/modello_cordolo.py` | Contributo cordolo reticolare in E.6 (`ritegno_cordolo_kg`) |
| Fase O — `src/seismic/spettro_ntc2018.py` | Parametri sismici (a_g, S, Se) per E.3 cinematica |
| Fase R — modello globale | Integrazione `analisi_tutti_meccanismi()` futura |
| `src/report/tabulato.py` | Formattazione tabulato verifiche |

---

## Riferimenti normativi

| Norma | Articolo | Contenuto |
| --- | --- | --- |
| NTC2018 | §7.8.2.1 | Compressione muratura con Φ snellezza |
| NTC2018 | Tab. 4.5.V | Fattore Φ in funzione di λ e e/t |
| NTC2018 | §7.8.2.2.1 | Taglio Turnšek-Čačovič e Mohr-Coulomb |
| NTC2018 | §7.8.1.6 | Minimi cordoli CA |
| Circ. n.7/2019 | §C8A.4.1 | Cinematica lineare: α₀, M*, e*, a₀* |
| Circ. n.7/2019 | §C8A.4.2 | Cinematica non lineare: d*_u, T_s |
| Circ. n.7/2019 | §C8.7.1.5 | Meccanismi locali fuori piano |
| DM 20/11/1987 | §2.2 | Tensioni ammissibili muratura (TA legacy) |

---

## Struttura file

```text
src/methods/muratura/
├── cinematica.py           # E.3 — analisi cinematica lin/nonlin, tutti i meccanismi
├── cantonale.py            # E.6 — RibaltamentoCantonale, diagnostica_apertura_angolo
├── muratura_ta.py          # E.1/E.2 — verifica_compressione, verifica_taglio_piano
├── catene.py               # E.5 — VerificaCatena, VerificaPunzonamento
├── spanciamento.py         # E.4 — verifica_snellezza_muro
└── multipiano.py           # E.7 — CaricoSolaio, GestoreCombinazioni, TabellaVerifiche

data/muratura/
└── tabelle_phi.json        # Tab. 4.5.V NTC2018 — fattori Φ riduzione

tests/
├── test_cinematica_muratura.py      # 49 test (E.3 — retrocompatibili E.6)
├── test_cantonale_muratura.py       # E.6 test standalone
├── test_verifiche_muratura_ta.py    # E.1, E.2
└── test_muratura_multipiano.py      # E.7
```

---

## Subfasi, checklist e storico

### E.1 — Compressione + snellezza

**Stato**: ✅ COMPLETATO

- [x] σ ≤ f_d / γ_M con riduzione snellezza Φ
- [x] Tabella Φ da NTC2018 Tab. 4.5.V (interpolazione bilineare λ×e/t)
- [x] Eccentricità e/t da momento flettente
- [x] Fattore vincolo ρ per altezza efficace

### E.2 — Taglio nel piano

**Stato**: ✅ COMPLETATO

- [x] Criterio diagonale (Turnšek-Čačovič) — NTC2018 §7.8.2.2.1
- [x] Criterio di scorrimento (Mohr-Coulomb: fvk = fvk0 + μ·σ_n)
- [x] Pressoflessione nel piano — V_pf = (L²×t×σ₀)/(2h₀)×(1-σ₀/(0.85fd))
- [x] Verifica combinata con ordinamento per V_Rd (criterio più restrittivo)

### E.3 — Fuori piano + ribaltamento (meccanismi locali)

**Stato**: ✅ COMPLETATO

- [x] Ribaltamento semplice (parete ruota alla base)
- [x] Ribaltamento composto (parete + cuneo sovrastante)
- [x] Flessione verticale (cerniera a metà altezza, meccanismo a 2 corpi)
- [x] Flessione orizzontale (arco a 3 cerniere tra vincoli laterali)
- [x] Cinematica lineare (§C8A.4.1): α₀, M*, e*, a₀*, verifica a terra e in quota
- [x] Cinematica non lineare (§C8A.4.2): d₀*, d*_u = 0.4·d₀*, T_s, domanda spostamento
- [x] Integrazione catene/tiranti (ForzaCatena con angolo, contributo stabilizzante)
- [x] Analisi completa tutti i meccanismi ordinati per α₀ crescente
- [x] Parametri sismici manuali (a_g, S, q, FC) + predisposizione INGV

### E.4 — Spanciamento

**Stato**: ✅ COMPLETATO

- [x] Verifica snellezza muro λ = h_eff/t ≤ λ_max
- [x] Limiti configurabili (20 ordinario, 15 esistente, 12 sismico)

### E.5 — Catene e paletti

**Stato**: ✅ COMPLETATO

- [x] Tipi piastre (circolare, quadrata, a paletto)
- [x] Verifica trazione catena (σ = F/A ≤ σ_s_adm)
- [x] Verifica punzonamento locale piastra (σ_p ≤ fd_mur)

### E.6 — Cantonali e aperture

**Stato**: ✅ COMPLETATO — commit corrente
**Priorità**: ALTA (collegamento diretto con E.3 + D.3)

#### E.6.1 — Ribaltamento cantonale (cuneo 3D)

- [x] Analisi fonti normative e letteratura
- [x] Definizione dataclass e input 3D
- [x] Inserimento warning automatici
- [x] Funzioni di calcolo carichi agenti
- [x] Calcolo cinematica ribaltamento 3D
- [x] Gestione tipologie copertura associata (`TipoCopertura` enum)
- [x] Gestione contributo cordolo D.3 (`ritegno_cordolo_kg`)
- [x] Output e serializzazione risultati
- [x] Test standalone
- [x] Documentazione decisioni architetturali
- [ ] Integrazione futura in `analisi_tutti_meccanismi()` (rinviato a Fase R)

#### E.6.2 — Riduzione resistenza maschi d'angolo per aperture

- [x] `diagnostica_apertura_angolo(parete, aperture)`
- [x] `coefficiente_riduzione_angolo(distanza, t, d_min)`
- [x] Dataclass separata `DiagnosticaAngolo`
- [x] Integrazione futura con Modello Globale (Fase R)
- [x] Test standalone su soglie metriche

#### E.6.3 — Spinta puntoni copertura

- [x] Integrato in E.6.1 (`InputSpinta`, enum `TipoCopertura`)

#### E.6.4 — Integrazione con cordolo reticolare D.3

- [x] Integrato in E.6.1 (`ritegno_cordolo_kg`)

#### E.6.5 — Test E.6

- [x] Effetto catena/tirante sul cantonale
- [x] Effetto ritegno cordolo D.3
- [x] Diagnostica apertura-angolo: OK, WARNING, FAIL
- [x] Coefficiente riduzione: asintotico
- [ ] Flag maschio cantonale: automatico e override (rinviato a Fase R)
- [ ] Integrazione in `analisi_tutti_meccanismi` (rinviato a Fase R)
- [x] Retrocompatibilità: `cinematica.py` test esistenti (49) invariati

#### E.6.6 — Report

- [x] Sezione "Meccanismo cantonale" nel tabulato
- [x] Sezione "Diagnostica aperture d'angolo" con warning
- [x] Passaggi calcolo tracciabili

### E.7 — Muratura multipiano

**Stato**: ✅ COMPLETATO

#### E.7.1 — Carichi verticali per aree di influenza

- [x] `CaricoSolaio`, `CaricoMaschio`, `_area_influenza_maschio()`, `distribuisci_carichi_solaio()`, `calcola_N_multipiano()`

#### E.7.2 — Combinazioni personalizzabili

- [x] `CombinazioneCarico`, `GestoreCombinazioni`, 6 combinazioni default NTC2018 §2.5.3, `calcola_N_tutte()`, `N_Ed_max()`

#### E.7.3 — Verifiche compressione multipiano

- [x] `Eccentricita`, `calcola_eccentricita()`, `verifica_multipiano()`, `RigaVerificaMaschio`, `RigaVerificaPiano`, `TabellaVerificheMultipiano`

---

## Decisioni architetturali

| Decisione | Motivazione |
| --- | --- |
| Cinematica lineare e non lineare separate | Approcci normativi distinti, uso selettivo |
| α₀ unico moltiplicatore per tutte le macro-tipologie | Confronto diretto tra meccanismi, ordinamento per criticità |
| Cuneo 3D separato da cinematica.py (cantonale.py) | Complessità geometrica 3D, dati input diversi |
| `coefficiente_riduzione_angolo` asintotico | Privo di discontinuità, sicuro per k_rid → 0 |
| Integrazione Fase R (non immediata) | Dipendenza da modello globale non ancora completato |
| `ritegno_cordolo_kg` come input scalare | Interfaccia minima verso D.3, disaccoppiamento |

---

## Bug corretti

| Bug | Causa | Fix |
| --- | --- | --- |
| Encoding UTF-8 `cantonale.py` riga 415 | Carattere non-ASCII nel sorgente | Ricodifica file con UTF-8 BOM |
| Errore interpolazione Φ fuori range λ | Clamp mancante su valori estremi | `λ = min(max(λ, λ_min), λ_max)` |

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Domanda | Risposta | Decisione |
| --- | --- | --- |
| E.6.A Modellazione cantonale | Cuneo 3D con cerniera sullo spigolo | `cantonale.py` separato da `cinematica.py` |
| E.6.B Riduzione aperture | Funzione asintotica di distanza | `coefficiente_riduzione_angolo()` senza soglia fissa |
| Integrazione `analisi_tutti_meccanismi` | Rinviata a Fase R | Flag `[ ]` in E.6.1 e E.6.5 |
| Parametri sismici | Manuali + predisposizione INGV | `a_g, S, q, FC` da input; INGV predisposto (Fase O) |

---

## Note storiche/archivio

- `tests/test_cantonale_muratura.py` aveva errore encoding UTF-8 in `cantonale.py` (riga 415) — preesistente, poi corretto
- Il meccanismo E.6 è documentato in dettaglio in `memory/subplan_E6_cantonali.md`
- Cinematica non lineare: T_s calcolato iterativamente (convergenza in 2–3 iterazioni tipicamente)
- Fase E collega direttamente a D (cordoli), O (spettri sismici), R (modello globale)
