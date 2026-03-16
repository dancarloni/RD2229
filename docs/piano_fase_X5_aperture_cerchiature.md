# Fase X5 — Aperture e Cerchiature

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | COMPLETATO |
| Commit | — |
| Data | 2026-03-16 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | 42 implementati/validati (24 check + 14 benchmark + 4 e2e), estensione modulare con suite dedicata X5 validata |
| Ambito | Aperture, riduzione rigidezza, trigger FEM locale, cerchiature, pareti murarie portanti, rinforzi cap. 8, pushover ante/post multi-metodo, livelli prestazionali DL/SLV/SLC |

---

## Scopo del modulo

Definire regole tecniche per aperture e cerchiature distinguendo chiaramente:
- prescrizioni normative (necessità di analisi locale)
- modello interno cautelativo (alpha_ap)
- attivazione FEM locale

Estensione implementata: supporto modulare a pareti murarie con aperture preesistenti/modificate,
valutazione rigidezza ante/post e contributo rinforzi (FRP, intonaco armato, betoncino, cerchiatura)
con architettura plugin orientata ad aggiornamenti futuri.

Estensione 2026-03-16: integrazione di analisi pushover ante/post in un check dedicato
(`x5_parete_pushover_ante_post`) con metodi selezionabili (bilineare/trilineare/numerico),
confronto risultati e criteri di arresto configurabili (capacità/drift/duttilità).

Estensione 2026-03-16 (step successivo stessa sessione): integrazione combinazioni sismiche
semplificate e verifica automatica per livelli prestazionali `DL`, `SLV`, `SLC`
con controllo combinato capacità+drift su ciascun metodo pushover.

---

## Dipendenze reali del repo

- src/core/registro_log.py
- src/core/combinations/ntc2018_combinations.py
- src/aree_influenza.py (non disponibile: fallback manuale)

---

## Fonti normative (parafrasi rigorosa)

- NTC2018 §7.2.6.2: modifiche locali, aperture e necessità di valutazione della rigidezza efficace.
- NTC2018 §7.8.2 e §8.3-§8.7: edifici esistenti in muratura, valutazione ante/post intervento,
  criteri prestazionali e verifiche in presenza di rinforzi.
- Circolare 7/2019 §7.5-§7.7: indicazioni applicative su analisi locale, drift, controllo del danno,
  criteri pratici su meccanismi locali e interventi.
- EN 1998-3 §7.5-§7.6: approccio di capacità per edifici esistenti e uso di curve forza-spostamento.
- EN 1996 (Eurocodice 6): riferimenti di supporto per verifica muratura (taglio/pressoflessione/interazione).
- CNR-DT 212/2013: linee guida su rinforzi FRP e limiti d'impiego (aderenza, ancoraggi, efficacia).
- Letteratura tecnica: criteri cautelativi in assenza di modellazione locale dettagliata.

---

## Schede operative

### Classificazione aperture

- piccola: area_ap/area_pannello < 10%
- media: 10%-25%
- grande: >25%
- estrema: >50%

### Modello cautelativo interno

- EI_eff = EI*(1-alpha_ap)
- alpha_ap: 0.05 / 0.20 / 0.40 per classi crescente di apertura

Nota: questa non e formula normativa diretta, ma modello prudenziale di V1.

### Modello pushover integrato (X5 esteso)

- Modelli disponibili: `bilineare`, `trilineare`, `numerico`.
- Esecuzione configurabile:
  - singolo metodo selezionato dall'utente;
  - esecuzione simultanea di tutti i metodi con confronto automatico.
- Grandezze restituite per ogni metodo:
  - `K0_kgf_cm` (rigidezza iniziale)
  - `Fy_kgf`, `Fu_kgf`
  - `dy_cm`, `du_cm`, `mu`
  - energia dissipata (`energia_kgf_cm`)
  - `drift_u`
- Confronto ante/post per metodo:
  - `ratio_K0`, `ratio_Fu`, `ratio_mu`, `ratio_energia`.
- Criteri di arresto (configurabili e disattivabili singolarmente):
  - capacità (carico ultimo),
  - drift,
  - duttilità.
- Verifica prestazionale per livello:
  - domanda orizzontale sismica semplificata da `Gk`, `Qk`, `ag/g`, `q`
  - confronto capacità/domanda (`capacity_ratio`) per metodo
  - controllo drift su limiti specifici di livello (`DL`, `SLV`, `SLC`)

### Trigger FEM locale

- apertura >25%
- apertura in prossimita appoggi/zone di picco taglio
- presenza cerchiatura con redistribuzione significativa

---

## Formula usata / fallback / motivo selezione

| Voce | Formula usata | Fallback | Motivo |
| --- | --- | --- | --- |
| Riduzione EI | modello alpha_ap | FEM locale | copertura V1 in assenza modulo completo |
| Cerchiatura | trave equivalente | modellazione FEM dettagliata | robustezza e semplicità |
| Area influenza | input manuale | modulo Y futuro | dipendenza mancante |
| Curva pushover | bilineare/trilineare/numerico con parametri configurabili | FEM non lineare completo | confronto rapido ante/post con tracciabilità |
| Resistenza di capacità | proxy da area resistente, alpha_ap e gain rinforzi | calibrazione su benchmark esterni | motore modulare V1 orientato a estensione |
| Domanda sismica di livello | Fh=(Gk+0.3*Qk)*(ag/g)*q*demand_factor | analisi dinamica non lineare completa | verifica rapida per DL/SLV/SLC tracciabile |

---

## Equazioni implementate (sintesi tecnica)

1) Rigidezza iniziale del modello equivalente:

K0 = EI / h^3

2) Capacità resistente di proxy (V1 modulare):

F_cap = tau_base * A_res * (1 - 0.8*alpha_ap) * (1 + c_gain * ratio_delta_ei)

3) Duttitlità e drift:

mu = du / dy

drift_u = du / h

4) Energia dissipata (curva pushover):

E_diss = area sotto la curva F-u (integrazione trapezi)

5) Domanda sismica semplificata per livello prestazionale:

Fh_lvl = (Gk + 0.3*Qk) * (ag/g) * q * demand_factor_lvl

6) Verifica di livello per metodo:

capacity_ratio = Fu / Fh_lvl

ok_lvl = (capacity_ratio >= 1.0) AND (drift_u <= drift_limit_lvl)

Nota: le equazioni 1-4 costituiscono un modello computazionale prudenziale e tracciabile,
non sostituiscono una FEM non lineare specialistica quando prescritta dalla norma.

---

## Warning code del modulo

| Warning code | Condizione | Check correlato |
| --- | --- | --- |
| X5-APE-001 | apertura >25% (attivare FEM) | x5_aperture_classificazione |
| X5-APE-002 | apertura >50% (verifica manuale obbligatoria) | x5_aperture_classificazione |
| X5-CER-001 | cerchiatura non coerente con schema statico | x5_cerchiatura_redistribuzione |
| X5-AREA-001 | area influenza manuale | x5_aperture_rigidezza |
| X5-RIG-001 | rigidezza post-intervento sotto soglia | x5_parete_rigidezza_ante_post |
| X5-PUSH-001 | drift ultimo oltre limite in almeno un metodo | x5_parete_pushover_ante_post |
| X5-PUSH-002 | duttilità insufficiente in almeno un metodo | x5_parete_pushover_ante_post |
| X5-PUSH-003 | livello prestazionale non verificato in almeno un metodo | x5_parete_pushover_ante_post |

---

## Quick reference testabile

| Test | Check | Input | Output atteso |
| --- | --- | --- | --- |
| X5-T01 | x5_aperture_classificazione | area ratio 8% | classe piccola + alpha_ap=0.05 |
| X5-T02 | x5_aperture_classificazione | area ratio 30% | warning X5-APE-001 |
| X5-T03 | x5_aperture_rigidezza | area ratio 60% | warning X5-APE-002 + riduzione EI_eff |
| X5-T04 | x5_cerchiatura_redistribuzione | cerchiatura attiva | redistribuzione + check warning |
| X5-T05 | x5_parete_rigidezza_ante_post | aperture preesistenti+modificate + rinforzi | EI_ante/EI_post, ratio_post_ante, warning X5-RIG-001 |
| X5-T06 | x5_parete_pushover_ante_post | metodi=[bilineare,trilineare,numerico] | curve ante/post + compare per metodo |
| X5-T07 | x5_parete_pushover_ante_post | stop criteria tutti OFF | errore input con contratto standard |
| X5-T08 | x5_parete_pushover_ante_post | drift_limit severo | warning X5-PUSH-001 |
| X5-T09 | x5_parete_pushover_ante_post | input sismico Gk/Qk/ag/q | output `seismic_combinations` + `performance_levels` |
| X5-T10 | x5_parete_pushover_ante_post | domanda molto alta + drift stretti | warning X5-PUSH-003 |

---

## Sub-fasi implementative

## Stato avanzamento sub-fasi

- [x] X5.1 — Classificazione aperture
- [x] X5.2 — Modello cautelativo EI
- [x] X5.3 — Trigger FEM locale
- [x] X5.4 — Cerchiature equivalenti
- [x] X5.5 — Test specifici
- [x] X5.6 — Motore modulare rinforzi e gestione aperture preesistenti/modificate
- [x] X5.7 — Backend editor geometrico aperture (pronto per integrazione GUI Qt)
- [x] X5.8 — Pushover ante/post multi-metodo con confronto risultati e warning dedicati

---

## Domande, risposte e decisioni

- Core X5 completo.
- Modello cautelativo: conservative primary.
- Cerchiature: livello esteso V1.
- Unità: output primario in sistema storico cm/kgf (SI come supporto opzionale).
- Test: unit + benchmark + e2e.
- Naming allineato a prefisso `x5_`.
- Pushover: metodi bilineare+trilineare+numerico con confronto in un'unica esecuzione.
- Arresto analisi: primo criterio verificato (capacity/drift/ductility), con flag di attivazione per criterio.
- Verifica livelli: DL/SLV/SLC con output strutturato per metodo e livello.

---

## Implementazione effettuata (file creati/modificati)

- src/methods/ntc2018/checks_x5.py
- src/methods/ntc2018/models.py
- src/methods/ntc2018/x5_core.py
- src/methods/ntc2018/x5_pushover.py
- src/methods/ntc2018/x5_editor.py
- src/methods/ntc2018/plugins/__init__.py
- src/codes/ntc2018/code_module.py
- src/codes/params/NTC2018.json
- tests/codes/test_x5_aperture_cerchiature_checks.py
- tests/codes/test_x5_aperture_cerchiature_benchmark.py
- tests/codes/test_x5_aperture_cerchiature_e2e.py
- tests/codes/test_x5_models.py
- tests/codes/test_x5_core.py
- tests/codes/test_x5_editor.py

---

## Risultati test e regressione

- Checks X5: **24/24 PASS**.
- Benchmark X5: **14/14 PASS**.
- E2E X5: **4/4 PASS**.
- Totale X5 checks+benchmark+e2e: **42/42 PASS**.
- Regressione check X3+X4+X5: comando `pytest -q tests/codes/test_x3_slu_checks.py tests/codes/test_x4_sle_checks.py tests/codes/test_x5_aperture_cerchiature_checks.py` con esito **74/74 PASS**.
- Suite estesa implementazione modulare X5 (check+benchmark+e2e+core+models+editor): **52/52 PASS** (validazione mirata corrente).

---

## Teoria e fondamenti (riferimenti sintetici)

- Classificazione aperture per area relativa; criterio di attivazione FEM >25%.
- Curva pushover come strumento di confronto ante/post (rigidezza, resistenza, deformabilità).
- Distinzione esplicita tra modello prudenziale software e verifica specialistica FEM non lineare.

---

## Diagramma dipendenze subfasi

```text
X5.1 → X5.2 → X5.3 → X5.4 → X5.5
```

---

## Rischi normativi residui

- Uso del modello cautelativo oltre il campo geometrico previsto.
- Mancata analisi locale nei casi con forte concentrazione di tensione.
- Necessità di calibrazione con benchmark esterni per applicazioni ad alta responsabilità.
- Per interventi complessi resta necessaria verifica specialistica con modello non lineare avanzato.

---

## Cronologia e decisioni

- 2026-03-15: completate sub-fasi X5.1–X5.5; implementati `x5_aperture_classificazione`, `x5_aperture_rigidezza`, `x5_cerchiatura_redistribuzione`; validazione **31/31 PASS** e regressione check X3+X4+X5 **74/74 PASS**.
- 2026-03-15: estensione completata con `x5_parete_rigidezza_ante_post`, motore plugin rinforzi, gestione aperture preesistenti/modificate e backend editor aperture; validazione suite estesa X5 **44/44 PASS**.
- 2026-03-16: implementato `x5_parete_pushover_ante_post` con motore `x5_pushover.py` (bilineare/trilineare/numerico), confronto ante/post, criteri di arresto configurabili e warning `X5-PUSH-*`; validazione complessiva suite X5 mirata aggiornata a **49/49 PASS**.
- 2026-03-16: estensione stessa sessione con combinazioni sismiche semplificate (`Gk`, `Qk`, `ag/g`, `q`) e verifica livelli prestazionali `DL/SLV/SLC` (capacità+drift) nel check pushover; validazione complessiva suite X5 mirata aggiornata a **52/52 PASS**.

---

## Esempi numerici (estratti da letteratura normativa)

1) Apertura rettangolare: solaio L = 6.00 m, apertura 120×120 cm (predalles/lamiera) — stima carico redistribuito sulla trave equivalente: area apertura 1.2×1.2 = 1.44 m²; carico equivalente se q = 300 kgf/m² → Q_ap = 300·1.44 = 432 kgf.

2) Cerchiatura trave equivalente: usare riduzione rigidezza cautelativa per cerchiature di tipo rigido: per un esempio pratico trave equivalente 30×50 cm, E=30 GPa → calcolo EI per redistribuzione (rif. DM96 e prassi RD2229).

3) Effetto bordo e punteggio: per aperture > (L/4) applicare warning X5-APE-001 e usare modello cautelativo; esempio L=6.00 m, ap=1.2 m → ap/L = 0.20 (soglia di attenzione secondo linee storiche).

Riferimenti: DM96, NTC2018 suggerimenti applicativi, letteratura RD2229 su cerchiature.
