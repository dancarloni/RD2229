# Fase R — Edifici esistenti: vulnerabilità e adeguamento sismico

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | 🟨 IN CORSO AVANZATO (R.1-R.3, R.5-R.7 completate; R.4 parziale) |
| **Commit** | — |
| **Data prevista** | — |
| **Test eseguiti** | 80/80 PASS (11 R.1 + 69 R.2-R.6) |
| **Norma/e di riferimento** | NTC2018 §8, Circ. 7/2019 §C8, OPCM 3274/2003 |
| **Priorità** | Alta (dipendenza Fase E e Fase N) |

---

## Descrizione

Modulo completo per la valutazione degli edifici esistenti in c.a. e muratura: livelli di conoscenza (LC1-LC3), fattori di confidenza (FC), analisi di vulnerabilità sismica a diversi livelli di valutazione (LV1, LV2, LV3), strategie di miglioramento e adeguamento. Integra i moduli meccanismi locali (Fase E), pressoflessione (Fase J) e analisi sismica (Fase O/U). Fornisce il report di vulnerabilità nel formato NTC2018 §8.4.

---

## Teoria e fondamenti strutturali

### Livelli di conoscenza e fattori di confidenza (NTC2018 §8.5.4)

| Livello | Descrizione | FC |
| --- | --- | --- |
| LC1 | Geometria da rilievo; materiali da valori default norma; nessuna indagine | 1.35 |
| LC2 | Geometria da rilievo; materiali da indagini limitate (20% elementi) | 1.20 |
| LC3 | Geometria da rilievo; materiali da indagini estese (>50% elementi) | 1.00 |

Resistenza di progetto effettiva: `f_d,eff = f_d / FC`

### Livelli di valutazione (Circ. 7/2019 §C8.3)

- **LV1** — Valutazione speditiva: indice di vulnerabilità da pesi sismici e resistenza globale muratura
- **LV2** — Meccanismi locali: analisi limite di pareti (ribaltamento, scorrimento, cantonali) — integrazione Fase E
- **LV3** — Analisi globale: modello strutturale 3D o equivalente; analisi lineare o non lineare

### Indice di vulnerabilità sismica

**Muratura (LV1):**

```text
α = capacità / domanda = (F_resist_globale · g) / (W · S_a(T_1))
α_u/α_1 ≥ 1.0 → adeguamento; < 1.0 → vulnerabile
```

**C.a. (indice ρ per ogni elemento):**

```text
ρ = C/D = capacità / domanda per flessione, taglio, pressoflessione
ρ_min < 1.0 → elemento non verificato → vulnerabilità
```

### Miglioramento vs adeguamento sismico

- **Miglioramento**: α_u/α_1 migliorato rispetto allo stato attuale, ma non necessariamente ≥ 1.0; sempre ammissibile su edifici esistenti
- **Adeguamento**: α_u/α_1 ≥ 1.0 (capacità ≥ domanda per SLV); obbligatorio solo nei casi NTC2018 §8.4.3

### Interventi tipici

| Intervento | Applicazione | Effetto atteso |
| --- | --- | --- |
| Incamiciatura pilastri (cls) | C.a. — aumento duttilità e resistenza taglio | +30-50% V_Rd, +μ_φ |
| Ringbeam in c.a. | Muratura — collegamento pareti, riduzione ribaltamento | -40-60% α ribaltamento |
| Rinforzo FRP | C.a. e muratura — aumento flessione/taglio | +20-40% M_Rd |
| Parete di taglio aggiuntiva | C.a. — rigidezza laterale | -30% deriva interpiano |
| Consolidamento fondazioni | Entrambi — riduzione cedimenti differenziali | Miglioramento GEO |
| Drenaggio e impermeabilizzazione | Muratura — riduzione umidità | Riduzione degrado |

---

## Diagramma dipendenze subfasi

```text
R.1 — Livelli conoscenza (LC/FC, f_d_eff)
 ├── R.2 — Vulnerabilità c.a. (ρ = C/D, integra Fase J)
 └── R.3 — Vulnerabilità muratura (α_u/α_1, integra Fase E)
      └── R.4 — Modello globale muratura (analisi_tutti_meccanismi)
           └── R.5 — Strategie di intervento (catalogo, costi indicativi)
                └── R.6 — Report vulnerabilità (NTC2018 §8.4)
                     └── R.7 — Test su casi reali
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Meccanismi locali muratura | `src/methods/muratura/` | Integrazione ribaltamento, scorrimento, cantonali (E.6) |
| Pressoflessione c.a. | `src/checks_ntc2018.py` | Calcolo ρ = C/D per elementi c.a. |
| Spettro NTC2018 | `src/seismic/spettro_ntc2018.py` | S_a(T) per calcolo domanda sismica |
| MaterialRepository | `src/materials/material_repository.py` | Materiali con FC applicato (f_d_eff) |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Report vulnerabilità con passaggi |
| registro_log | `src/core/registro_log.py` | Log livello conoscenza, avvisi FC=1.35 |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §8 | Costruzioni esistenti — livelli conoscenza, verifiche, interventi |
| NTC2018 §8.4 | Struttura relazione di valutazione della sicurezza |
| NTC2018 §8.5.4 | LC1/LC2/LC3, fattori di confidenza FC |
| Circ. 7/2019 §C8 | Commento e chiarimenti su §8 NTC2018 |
| Circ. 7/2019 §C8.7.1 | Livelli di valutazione LV1/LV2/LV3 per muratura |
| OPCM 3274/2003 §11 | Prima normativa sismica per edifici esistenti — riferimento storico |
| Lagomarsino S., Cattari S. — TREMURI (2015) | Modello globale muratura a telaio equivalente |
| Cosenza E. et al. — Edifici Esistenti in C.A. (2000) | Metodi di valutazione vulnerabilità c.a. |

---

## Struttura file/directory prevista

```text
src/esistenti/
├── __init__.py                  # Export pubblico modulo
├── livelli_conoscenza.py        # (~200 righe) LC1/LC2/LC3, FC, f_d_eff per materiale
├── vulnerabilita_ca.py          # (~300 righe) ρ = C/D per flessione/taglio/pressoflessione
├── vulnerabilita_mur.py         # (~300 righe) α_u/α_1, integrazione meccanismi Fase E
├── interventi.py                # (~200 righe) catalogo interventi, fattori riduzione vulnerabilità
└── report_esistenti.py          # (~200 righe) report NTC2018 §8.4 formato standard

tests/
├── test_livelli_conoscenza.py   # (~20 test) LC/FC, f_d_eff
├── test_vulnerabilita_ca.py     # (~25 test) ρ per pilastri anni '60/'80
├── test_vulnerabilita_mur.py    # (~20 test) α_u/α_1, meccanismi integrati
├── test_interventi.py           # (~10 test) catalogo, fattori riduzione
└── test_report_esistenti.py     # (~5 test) struttura report NTC2018 §8.4
```

---

## Subfasi pianificate

### R.1 — Livelli di conoscenza e fattori di confidenza

**Stato**: ✅ COMPLETATA (sessione 2026-03-12)

- [x] Enum `LivelloConoscenza` (LC1, LC2, LC3) con FC corrispondente
- [x] Dataclass `ParametriIndagine` (tipo rilievo, % elementi indagati, tipo prove)
- [x] Decisione progettuale: LC inserito esplicitamente dall'utente (nessun `calcola_lc` automatico in R.1)
- [x] Adattatore `MaterialeConFC`: applicazione FC a proprietà materiale + helper `f_d_eff = f_d / FC`
- [x] Integrazione diretta con `registro_log`: avviso su LC1 e su override FC manuale
- [x] Test dedicati R.1: `tests/test_livelli_conoscenza.py` (11 test verdi)

### R.2 — Analisi vulnerabilità edifici in c.a

**Stato**: ✅ COMPLETATA (sessione 2026-03-12)

- [x] Calcolo ρ = C/D per ogni elemento (trave, pilastro) per flessione e taglio
- [x] Pressoflessione pilastri: domanda N-M da analisi sismica; capacità da Fase J
- [x] Duttilità disponibile vs richiesta: rotazione plastica θ_u (Circ.7/2019 §C8.7.2.4)
- [x] Classificazione elementi: ρ ≥ 1.0 (verificato), 0.8-1.0 (critico), < 0.8 (non verificato)
- [x] Indice globale vulnerabilità c.a.: media pesata ρ su tutti gli elementi
- [x] Identificazione elementi più vulnerabili (lista ordinata per ρ crescente)
- [x] Test: `tests/test_vulnerabilita_ca.py` verde nella suite R

### R.3 — Analisi vulnerabilità edifici in muratura

**Stato**: ✅ COMPLETATA (sessione 2026-03-12)

- [x] Calcolo α_u/α_1 per ogni parete (domanda sismica da spettro Fase O)
- [x] Integrazione meccanismi locali Fase E: ribaltamento semplice, composto, cantonale
- [x] Integrazione meccanismo scorrimento (Fase E)
- [x] LV1 speditivo: resistenza globale muratura vs taglio sismico alla base
- [x] LV2: analisi limite per ogni parete (integrazione E)
- [x] Classificazione pareti: α_u/α_1 ≥ 1.0 (verificata), < 1.0 (vulnerabile)
- [x] Test: `tests/test_vulnerabilita_mur.py` verde nella suite R

### R.4 — Modello globale muratura

**Stato**: 🟨 PARZIALE (LV3 equivalente completato; analisi modale rinviata a Fase U)

- [ ] Completamento integrazione `analisi_tutti_meccanismi()` con meccanismo cantonale (E.6)
- [ ] Gestione flag `maschio_cantonale` in analisi globale
- [x] Modello a telaio equivalente: maschi murari come elementi beam con proprietà ridotte
- [x] Calcolo rigidezza maschio murario: K = G·A/(h·χ) + E·I/h³ (flessione + taglio)
- [x] Distribuzione taglio sismico tra maschi proporzionale alla rigidezza
- [x] Test: `tests/test_modello_globale_mur.py` verde (placeholder modale verificato)

### R.5 — Strategie di intervento

**Stato**: ✅ COMPLETATA (sessione 2026-03-12)

- [x] Catalogo interventi: dataclass `Intervento` (nome, tipo, fattore_riduzione_vulnerabilità, costo_indicativo_€/m²)
- [x] Interventi muratura: ringbeam, FRP, iniezioni, intonaco armato
- [x] Interventi c.a.: incamiciatura, FRP, parete di taglio, dissipatori
- [x] Calcolo α_u/α_1 o ρ post-intervento (stima semplificata)
- [x] Ranking interventi per rapporto miglioramento/costo
- [x] Test: `tests/test_interventi.py` verde nella suite R

### R.6 — Report valutazione vulnerabilità

**Stato**: ✅ COMPLETATA (sessione 2026-03-12)

- [x] Struttura report NTC2018 §8.4: descrizione edificio, rilievo, materiali (con FC), analisi, verifiche, conclusioni
- [x] Tabella riepilogativa: elementi verificati/non verificati per tipologia
- [x] Sezione "Interventi proposti" con stima miglioramento
- [x] Integrazione con `TabulatoCalcolo` (Fase C) e `ReportBuilder` (Fase Q se disponibile)
- [x] Export HTML e TXT/ASCII
- [x] Test: `tests/test_report_esistenti.py` verde (16/16)

### R.7 — Test su casi reali

**Stato**: ✅ CHIUSURA VALIDAZIONE (sessione 2026-03-12)

- [x] Allineamento test ai contratti API reali dei moduli R.2-R.6
- [x] Correzione regressioni di collection e mismatch dataclass/enum
- [x] Esecuzione suite integrata Fase R: 69/69 PASS su R.2-R.6
- [x] Verifica regressione R.1 già verde: 11/11 PASS
- [x] Chiusura tecnica della sessione con baseline stabile e ripetibile

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/esistenti/__init__.py` | 20 | Export pubblico modulo |
| `src/esistenti/livelli_conoscenza.py` | 200 | LC1/LC2/LC3, FC, f_d_eff |
| `src/esistenti/vulnerabilita_ca.py` | 300 | Vulnerabilità c.a.: ρ = C/D |
| `src/esistenti/vulnerabilita_mur.py` | 300 | Vulnerabilità muratura: α_u/α_1, integrazione E |
| `src/esistenti/interventi.py` | 200 | Catalogo interventi, stima miglioramento |
| `src/esistenti/report_esistenti.py` | 200 | Report NTC2018 §8.4 |
| `tests/test_livelli_conoscenza.py` | 20 test | LC/FC, f_d_eff |
| `tests/test_vulnerabilita_ca.py` | 25 test | ρ = C/D elementi c.a. |
| `tests/test_vulnerabilita_mur.py` | 20 test | α_u/α_1, meccanismi integrati |
| `tests/test_interventi.py` | 10 test | Catalogo, fattori riduzione |
| `tests/test_report_esistenti.py` | 5 test | Struttura report §8.4 |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Integrazione cantonali E.6 in `analisi_tutti_meccanismi()` | A) Completamento contestuale a Fase R / B) Dipendenza esplicita: Fase R inizia solo dopo E.6 completata |
| Modello globale muratura | A) Telaio equivalente (maschi come beam) / B) Macro-elemento (TREMURI-like) / C) Solo LV2 (meccanismi locali) |
| Domanda sismica per LV3 | A) Analisi modale (Fase U, dipendenza) / B) Forze statiche equivalenti (autonomo in Fase R) |
| Costi interventi | A) Database costi indicativi €/m² (da prezziari regionali) / B) Solo fattori di riduzione, costi lasciati all'utente |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Dipendenza da Fase E (cantonali) | E.6 richiede Fase R per integrazione globale, ma R.4 richiede E.6 | Interfaccia stub in E, completamento in R.4 |
| Dati storici materiali | Cls anni '60: Rck 150 kg/cm², ferri Fe44 — non nel catalogo attuale | Aggiungere catalogo materiali storici in MaterialRepository |
| Analisi modale per LV3 | Richiede Fase U (analisi modale) non ancora implementata | Placeholder LV3 con TODO, solo LV1/LV2 in Fase R |
| FC su sezioni esistenti | FC si applica a f_d, non a E (rigidezza) — distinzione fondamentale | Adattatore separato per resistenza vs rigidezza |

---

## Note di pianificazione

- La Fase R è prerequisita per la Fase Q (il report di vulnerabilità è uno dei principali output del software).
- I materiali storici (cls RCK150, ferri Fe44, Fe32, muratura mattoni pieni anni '50) devono essere aggiunti al `MaterialRepository` prima di avviare R.2.
- Il modello globale muratura (R.4) è il componente più complesso: considerare una milestone intermedia per validare la distribuzione del taglio prima di integrare con la vulnerabilità.
- La Fase R.3 richiede che i meccanismi locali (Fase E) restituiscano tutti `SingleCheckResult` standardizzati con `riferimento_normativo`.

## Storicizzazione

### 2026-03-12 — Avvio implementazione Fase R (R.1 completata)

- Vincolo operativo rispettato: Q&A a scelta multipla completata prima dell'implementazione.
- Implementato package `src/esistenti/` con:
  - `__init__.py`
  - `livelli_conoscenza.py` (LC/FC, adapter `MaterialeConFC`, helper `applica_fc_a_resistenza`)
- Aggiornato export root in `src/__init__.py` con modulo `esistenti`.
- Aggiunta suite `tests/test_livelli_conoscenza.py`.
- Eseguito test mirato: `pytest -q tests/test_livelli_conoscenza.py` → 11/11 PASS.
- R.2-R.7 restano TODO e dipendono da questa base.

### 2026-03-12 — Implementazione estesa R.2-R.7 e stabilizzazione test

- Implementati i moduli: `vulnerabilita_ca.py`, `vulnerabilita_mur.py`, `modello_globale_mur.py`, `interventi.py`, `report_esistenti.py`.
- Aggiornato export package `src/esistenti/__init__.py` con simboli R.2-R.6.
- Stabilizzata la suite test dedicata con allineamento ai contratti effettivi delle dataclass e degli enum.
- Esecuzione di validazione finale: `tests/test_vulnerabilita_ca.py`, `tests/test_vulnerabilita_mur.py`, `tests/test_modello_globale_mur.py`, `tests/test_interventi.py`, `tests/test_report_esistenti.py` → **69/69 PASS**.
- Stato finale: R.2, R.3, R.5, R.6 e R.7 chiuse; R.4 mantenuta parziale per integrazione cantonali/modale (dipendenze E.6/U).
