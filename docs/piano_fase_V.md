# Fase V — Scale (rampe in c.a. e metalliche)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~40 |
| **Norma/e di riferimento** | NTC2018 §4.1.4, EC2 §5.7, DM 9/01/1996 |
| **Priorità** | Media |

---

## Descrizione

Verifica strutturale di scale (rampe in c.a., scale metalliche). Il modulo calcola le azioni trasmesse alle travi e ai pianerottoli, verifica flessione, taglio, pressoflessione e deformazione per ogni tipo di scala, e genera il tabulato di calcolo con i passaggi intermedi. Include widget Qt per input geometria e visualizzazione risultati. Il calcolo delle aree di influenza è demandato al modulo trasversale (Fase Y).

---

## Teoria e fondamenti strutturali

### Scale in c.a

Schema strutturale rampa appoggiata su entrambe le estremità (muro o trave di piano):

**Azione assiale nella rampa (componente orizzontale della reazione):**

```text
N = H = V · tanα = (q·L_orizzontale/2) · tanα
```

**Momento massimo (campo):**

```text
M_max = q·L_orizzontale²/8    (misurato sull'asse orizzontale)
```

**Verifica pressoflessione:** la rampa è soggetta a N + M → verifica sezione rettangolare con sforzo normale.

**Peso proprio rampa per unità di lunghezza orizzontale:**

```text
g_rampa = γ_cls · s / cosα    [kN/m²]
```

dove s = spessore solaio rampa, α = angolo inclinazione.

---

## Diagramma dipendenze subfasi

```text
V.1 — Scale in c.a. (rampa appoggiata/incastrata, N+M)
 └── V.2 — Scale metalliche (profilati, connessioni parapetto)
      └── V.3 — GUI Qt widget scala
           └── V.4 — Test e validazione
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| checks_ntc2018 | `src/checks_ntc2018.py` | Verifica flessione/taglio scale |
| MaterialRepository | `src/materials/material_repository.py` | cls, acciaio |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Tabulato scala con passaggi intermedi |
| EC3 acciaio (Fase S) | `src/methods/ec/ec3_acciaio.py` | Verifica scale metalliche (se S completata) |
| registro_log | `src/core/registro_log.py` | Log verifiche per ogni rampa |
| aiuto_contestuale | `src/ui/qt/aiuto_contestuale.py` | Riferimenti normativi nel widget Qt |
| Aree di influenza (modulo condiviso) | `src/aree_influenza.py` | Calcolo area influenza per scale (vedi Fase Y) |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §4.1.9 | Solai: criteri generali, pignatte, limitazioni geometriche |
| NTC2018 §4.1.9.1 | Solai in latero-cemento: armatura minima, verifiche |
| NTC2018 §4.1.12 | Deformazioni ammissibili, freccia limite |
| NTC2018 §4.1.4 | Scale in c.a.: verifiche strutturali |
| EC2 §5.3.2 | Larghezza efficace dell'ala per sezioni a T |
| EC2 §7.4 | Deformazioni: calcolo freccia con I_eff |
| EN 15037-1 | Solaio laterocemento: classificazione e geometria |
| Santarella L. — Il Cemento Armato (1968) | Tabelle MIP per carichi solaio, scale |
| Pozzati P. — Teoria e Tecnica delle Strutture Vol.3 (1980) | Coefficienti α per lastre bidirezionali |
| DM 9/01/1996 | Esecuzione delle opere in c.a. — rinterazioni solaio |

---

## Struttura file/directory prevista

```text
src/solai/
├── __init__.py                    # Export pubblico modulo
├── laterocemento.py               # (~250 righe) geometria, M_Rd, V_Rd, pignatta
├── alveolare.py                   # (~250 righe) precompressione, perdite, M_Rd, freccia
├── gettato_in_opera.py            # (~200 righe) lastra mono/bidirezionale, coefficienti Pozzati
├── aree_influenza.py              # (~100 righe) calcolo area influenza per travi perimetrali
└── scale.py                       # (~250 righe) rampa c.a. e metallica, N+M, verifica

src/ui/qt/
└── solaio_scala_widget.py         # (~400 righe) GUI Qt input geometria + output verifiche

tests/
├── test_laterocemento.py          # (~20 test) nervature, M_Rd, confronto tabelle produttori
├── test_alveolare.py              # (~20 test) perdite precompressione, M_Rd, freccia
├── test_gettato_in_opera.py       # (~15 test) lastra mono/bi, coefficienti Pozzati
├── test_aree_influenza.py         # (~10 test) area influenza, carichi travi perimetrali
└── test_scale.py                  # (~15 test) rampa c.a., metallica, N+M
```

---

## Subfasi pianificate

### V.1 — Scale in c.a

**Stato**: TODO

- [ ] Dataclass `GeometriaRampa` (α angolo, L orizzontale, h spessore, alzata, pedata)
- [ ] Calcolo peso proprio rampa per unità di lunghezza orizzontale: g = γ·s/cosα
- [ ] Schema appoggiato su entrambe le estremità: reazioni, M_max, N assiale
- [ ] Schema incastrato: M agli incastri, M in campo (più piccolo)
- [ ] Verifica pressoflessione: sezione rettangolare con N+M (piccola eccentricità)
- [ ] Verifica taglio: V_Rd,c con contributo N (compressione riduce taglio critico)
- [ ] Piattaforma scala: soletta appoggiata su muri, carichi da rampa + peso proprio
- [ ] Calcolo area di influenza tramite modulo condiviso (vedi Fase Y)
- [ ] Test: rampa α=30°, L=3m, s=15cm — M_max, N, verifica pressoflessione

### V.2 — Scale metalliche

**Stato**: TODO

- [ ] Schema strutturale: profilo inclinato (IPE o UPN) come trave-colonna
- [ ] Calcolo M, V, N sulla rampa metallica inclinata
- [ ] Verifica flessione: M_Rd = W_pl·f_y/γ_M0 (classe 1-2)
- [ ] Verifica taglio: V_Rd = A_v·f_y/(√3·γ_M0)
- [ ] Verifica instabilità flessotorsionale (χ_LT per profili non irrigiditi lateralmente)
- [ ] Connessione parapetto: forza orizzontale q=1 kN/m a h=1.0m; verifica bulloni
- [ ] Calcolo area di influenza tramite modulo condiviso (vedi Fase Y)
- [ ] Test: IPE200 S275, L=4m, α=35° — verifica flessione e instabilità

### V.3 — GUI Qt widget scala

**Stato**: TODO

- [ ] Widget `ScalaWidget` con input geometria e output verifiche
- [ ] Validazione dimensioni minime NTC2018
- [ ] Output: tabella verifiche (M_Rd, V_Rd, freccia) con semaforo
- [ ] Pulsante "Genera tabulato" → TabulatoCalcolo
- [ ] Help contestuale per ogni campo (riferimento NTC2018)
- [ ] Test widget: input/output per ciascun tipo di scala

### V.4 — Test e validazione

**Stato**: TODO

- [ ] Rampa c.a.: confronto con esempio manuale Santarella "Il Cemento Armato"
- [ ] Scala metallica: confronto con progetto manuale da Ballio-Mazzolani
- [ ] Test regressione: risultati stabili dopo refactoring

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/scale.py` | 250 | Rampa c.a. e metallica, N+M, verifica |
| `src/aree_influenza.py` | 120 | Algoritmi area influenza (vedi Fase Y) |
| `src/ui/qt/scala_widget.py` | 200 | GUI Qt input/output scala |
| `tests/test_scale.py` | 15 test | Rampa c.a. e metallica, N+M |
| `tests/test_aree_influenza.py` | 10 test | Area influenza, carichi scale |

---

## Decisioni architetturali e storicizzazione

- Decisione 2026-03-10: il calcolo delle aree di influenza è centralizzato nel modulo trasversale (Fase Y, src/aree_influenza.py), condiviso tra scale, solai e fondazioni, per evitare duplicazioni e garantire coerenza. Tutti i riferimenti e le dipendenze sono aggiornati di conseguenza.

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Componente assiale N scala | Spesso trascurata in pratica ma fondamentale per rampe ripide | Calcolo sempre esplicito con flag warning se e/h > 0.1 |
| Area di influenza | Geometrie complesse, aperture, casi bordo | Demandato a modulo trasversale (Fase Y) con override manuale |

---

## Note di pianificazione

- Il modulo scale utilizza il calcolo delle aree di influenza tramite Fase Y (modulo trasversale), garantendo coerenza con solai e fondazioni.
- La scala metallica (V.2) dipende da EC3 (Fase S.4) per le verifiche di instabilità: se Fase S non è ancora completata, implementare V.2 con verifica elastica semplificata come stub.
- Il widget Qt (V.3) deve supportare input/output per tutte le tipologie di scala.

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
