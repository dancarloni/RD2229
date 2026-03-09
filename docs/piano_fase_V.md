# Fase V — Solai e scale

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~80 |
| **Norma/e di riferimento** | NTC2018 §4.1.9, §4.1.12, EC2 §5.7, DM 9/01/1996 |
| **Priorità** | Media |

---

## Descrizione

Verifica strutturale di solai (laterocemento, alveolari precompressi, gettati in opera) e scale (rampe in c.a., scale metalliche). Il modulo calcola le azioni trasmesse alle travi perimetrali, verifica flessione, taglio e deformazione per ogni tipo di solaio, e genera il tabulato di calcolo con i passaggi intermedi. Include widget Qt per input geometria e visualizzazione risultati.

---

## Teoria e fondamenti strutturali

### Solaio laterocemento (nervature + pignatte)

Sezione a T inversa: ala compressa in cls (spessore s), nervatura in cls (base b_n, altezza h), pignatte laterali.

**Larghezza efficace ala (EC2 §5.3.2):**

```text
b_eff = b_n + 2·b_eff,i
b_eff,i = min(0.2·b_i + 0.1·l_0 ; 0.2·l_0 ; b_i)
```

**Momento resistente (sezione a T, asse neutro nell'ala):**

```text
M_Rd = A_s · f_yd · (d - 0.5·x)    con x = A_s·f_yd/(0.8·b_eff·f_cd) ≤ s
```

Se l'asse neutro scende nella nervatura: schema a sezione composta.

**Verifica pignatta (NTC2018 §4.1.9.1.4):** contributo resistente della pignatta a taglio è nullo; le nervature resistono con le staffe.

### Solaio alveolare precompresso

Tipologie standard (larghezza 1200 mm): 20+4, 24+4, 28+4, 32+4 (altezza nervatura + cappa).

**Perdite di precompressione:**

```text
Δσ_p = Δσ_μ + Δσ_δ + Δσ_r    (attrito + scorrimento + rilassamento)
σ_p,eff = σ_p,0 - Δσ_p
```

**Momento resistente con precompressione:**

```text
M_Rd,pc = σ_p,eff · A_p · z_p + A_s · f_yd · z_s
```

**Verifica deformazione (NTC2018 §4.1.12):**

```text
δ_max = 5·q·L⁴/(384·E·I_eff) ≤ L/250    (carichi quasi-permanenti)
I_eff = I_fess + ζ·(I_gross - I_fess)    (interpolazione Eurocodice)
```

### Solaio in c.a. gettato in opera

**Lastra monodirezionale (L_x/L_y ≥ 2):**

```text
M_x = q·L_x²/8    (campata intera)
M_x = -q·L_x²/10  (appoggio elastico)
```

**Lastra bidirezionale (metodo dei coefficienti — Pozzati Tab. §6.3):**

```text
M_x = α_x · q · L_x²
M_y = α_y · q · L_x²
```

dove α_x, α_y funzione di β = L_x/L_y e condizioni di vincolo ai bordi.

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
V.1 — Solaio laterocemento (geometria nervature, M_Rd, V_Rd, pignatta)
 └── V.2 — Solaio alveolare (precompressione, perdite, M_Rd, freccia)
      └── V.3 — Solaio in c.a. gettato (lastra mono/bidirezionale, coefficienti Pozzati)
           └── V.4 — Scale in c.a. (rampa appoggiata/incastrata, N+M)
                └── V.5 — Scale metalliche (profilati, connessioni parapetto)
                     └── V.6 — GUI Qt widget solaio e scala
                          └── V.7 — Test e validazione
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| checks_ntc2018 | `src/checks_ntc2018.py` | Verifica flessione/taglio nervature e lastre |
| MaterialRepository | `src/materials/material_repository.py` | cls, acciaio, acciaio da precompressione |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Tabulato solaio con passaggi intermedi |
| EC3 acciaio (Fase S) | `src/methods/ec/ec3_acciaio.py` | Verifica scale metalliche (se S completata) |
| registro_log | `src/core/registro_log.py` | Log verifiche per ogni nervatura/lastra |
| aiuto_contestuale | `src/ui/qt/aiuto_contestuale.py` | Riferimenti normativi nel widget Qt |

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

### V.1 — Solaio laterocemento

**Stato**: TODO

- [ ] Dataclass `GeometriaLaterocemento` (h, s_ala, b_nervatura, i_passo, b_pignatta)
- [ ] Calcolo larghezza efficace ala b_eff (EC2 §5.3.2) in funzione di l_0
- [ ] Sezione a T: calcolo asse neutro e momento resistente M_Rd
- [ ] Gestione asse neutro nell'ala vs nella nervatura (due casi)
- [ ] Verifica taglio: V_Rd,c (senza staffe) e V_Rd,s (con staffe) per nervatura
- [ ] Verifica pignatta: resistenza minima a schiacciamento per carico concentrato
- [ ] Calcolo freccia: I_eff interpolato, δ ≤ L/250
- [ ] Aggiungere `passaggi_calcolo: list[str]` con formula per ogni verifica
- [ ] Test: solaio 20+4, nervatura 12 cm, L=5m — confronto con tabella produttore Predalle o Fert

### V.2 — Solaio alveolare precompresso

**Stato**: TODO

- [ ] Catalogo sezioni alveolari standard (20+4, 24+4, 28+4, 32+4): A, I, A_p, z_p
- [ ] Calcolo perdite iniziali: attrito (μ·α), scorrimento (Δl/L·E_p·A_p)
- [ ] Calcolo perdite differite: ritiro e fluage cls; rilassamento acciaio
- [ ] σ_p,eff dopo perdite totali
- [ ] Momento resistente M_Rd,pc con contributo armatura + precompressione
- [ ] Verifica allo stato limite di servizio: fessure (σ_c ≤ f_ctm per classe XC2)
- [ ] Calcolo freccia: I_eff con fessurazione, cambera da precompressione
- [ ] Test: alveolare 24+4, σ_p0=1200 MPa, L=8m — M_Rd e freccia a mezzeria

### V.3 — Solaio in c.a. gettato in opera

**Stato**: TODO

- [ ] Classificazione: monodirezionale (L_x/L_y ≥ 2) o bidirezionale
- [ ] Lastra monodirezionale: M_x in campo e all'appoggio per vari schemi di vincolo
- [ ] Coefficienti α_x, α_y per lastra bidirezionale (tabella Pozzati §6.3)
- [ ] Verifica flessione lastra: sezione rettangolare b=100cm, h, armatura
- [ ] Verifica taglio lastra: V_Rd,c (senza staffe — regola NTC2018 per lastre)
- [ ] Verifica deformazione: freccia ≤ L/250 (NTC2018 §4.1.12)
- [ ] Distribuzione carico su travi perimetrali (integrazione con aree_influenza.py)
- [ ] Test: lastra 15cm, 5×4m, carichi 6 kN/m² — M_x, M_y e armatura richiesta

### V.4 — Scale in c.a

**Stato**: TODO

- [ ] Dataclass `GeometriaRampa` (α angolo, L orizzontale, h spessore, alzata, pedata)
- [ ] Calcolo peso proprio rampa per unità di lunghezza orizzontale: g = γ·s/cosα
- [ ] Schema appoggiato su entrambe le estremità: reazioni, M_max, N assiale
- [ ] Schema incastrato: M agli incastri, M in campo (più piccolo)
- [ ] Verifica pressoflessione: sezione rettangolare con N+M (piccola eccentricità)
- [ ] Verifica taglio: V_Rd,c con contributo N (compressione riduce taglio critico)
- [ ] Piattaforma scala: soletta appoggiata su muri, carichi da rampa + peso proprio
- [ ] Test: rampa α=30°, L=3m, s=15cm — M_max, N, verifica pressoflessione

### V.5 — Scale metalliche

**Stato**: TODO

- [ ] Schema strutturale: profilo inclinato (IPE o UPN) come trave-colonna
- [ ] Calcolo M, V, N sulla rampa metallica inclinata
- [ ] Verifica flessione: M_Rd = W_pl·f_y/γ_M0 (classe 1-2)
- [ ] Verifica taglio: V_Rd = A_v·f_y/(√3·γ_M0)
- [ ] Verifica instabilità flessotorsionale (χ_LT per profili non irrigiditi lateralmente)
- [ ] Connessione parapetto: forza orizzontale q=1 kN/m a h=1.0m; verifica bulloni
- [ ] Test: IPE200 S275, L=4m, α=35° — verifica flessione e instabilità

### V.6 — GUI Qt widget solaio e scala

**Stato**: TODO

- [ ] Widget `SolaiScalaWidget` con tab: Laterocemento / Alveolare / Gettato / Scala
- [ ] Input geometria con validazione (dimensioni minime NTC2018)
- [ ] Dropdown tipo pignatta / catalogo sezioni alveolari standard
- [ ] Output: tabella verifiche (M_Rd, V_Rd, freccia) con semaforo verde/rosso/giallo
- [ ] Pulsante "Genera tabulato" → TabulatoCalcolo con passaggi intermedi
- [ ] Help contestuale per ogni campo (riferimento NTC2018)
- [ ] Test widget: input/output per ciascun tipo di solaio

### V.7 — Test e validazione

**Stato**: TODO

- [ ] Solaio laterocemento: confronto con tabelle portanza produttore (Fert, Predalle)
- [ ] Alveolare: confronto con schede tecniche elemento 24+4 da catalogo produttore
- [ ] Lastra bidirezionale: confronto con Santarella esempi §6 o Pozzati
- [ ] Rampa c.a.: confronto con esempio manuale Santarella "Il Cemento Armato"
- [ ] Scala metallica: confronto con progetto manuale da Ballio-Mazzolani
- [ ] Test regressione: risultati stabili dopo refactoring

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/solai/__init__.py` | 20 | Export pubblico modulo |
| `src/solai/laterocemento.py` | 250 | Geometria, M_Rd, V_Rd, pignatta |
| `src/solai/alveolare.py` | 250 | Precompressione, perdite, M_Rd, freccia |
| `src/solai/gettato_in_opera.py` | 200 | Lastra mono/bidirezionale, α Pozzati |
| `src/solai/aree_influenza.py` | 100 | Area influenza per travi perimetrali |
| `src/solai/scale.py` | 250 | Rampa c.a. e metallica, N+M, verifica |
| `src/ui/qt/solaio_scala_widget.py` | 400 | GUI Qt input/output solaio e scala |
| `tests/test_laterocemento.py` | 20 test | Nervature, M_Rd, tabelle produttori |
| `tests/test_alveolare.py` | 20 test | Perdite, M_Rd, freccia |
| `tests/test_gettato_in_opera.py` | 15 test | Lastra mono/bi, coefficienti Pozzati |
| `tests/test_aree_influenza.py` | 10 test | Aree influenza, carichi travi |
| `tests/test_scale.py` | 15 test | Rampa c.a. e metallica, N+M |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Catalogo sezioni alveolari: valori standard o input libero? | A) Catalogo JSON con sezioni standard più comuni / B) Solo input libero (A_p, I, z_p da utente) / C) Entrambi |
| Metodo lastra bidirezionale: Pozzati o EC2 §5.3? | A) Pozzati (tradizione italiana, tabelle note) / B) EC2 §5.3 (metodo delle strisce) / C) Entrambi con confronto |
| Perdite precompressione: calcolo completo o semplificate? | A) Semplificate (perdita totale % da norma) / B) Calcolo passo-passo (più complesso, necessario per progetto) |
| Scale metalliche: dipendenza da Fase S (EC3)? | A) Implementazione autonoma semplificata / B) Richiede S.4 (EC3 acciaio) completata |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Larghezza efficace ala b_eff | Dipende da l_0 (lunghezza di influenza) non sempre ovvia | Default l_0 = 0.85·L per campata interna; documentare assunzione |
| Freccia lastra bidirezionale | Calcolo esatto richiede FEM 2D (piastra) — molto complesso | Usare freccia in direzione x da lastra monodirezionale equivalente; TODO FEM piastra |
| Perdite precompressione in alveolare | Calcolo completo richiede dati produttore (Es, A_p, geometria cavi) | Catalogo sezioni con perdite già stimate (15-20% tipico) |
| Componente assiale N scala | Spesso trascurata in pratica ma fondamentale per rampe ripide | Calcolo sempre esplicito con flag warning se e/h > 0.1 |

---

## Note di pianificazione

- Il modulo solai è uno dei più richiesti in pratica: dare priorità a V.1 (laterocemento) e V.3 (gettato in opera) come sotto-fasi di maggior impatto.
- Le aree di influenza (V, aree_influenza.py) sono riutilizzate anche per il calcolo delle azioni sui muri e sulle fondazioni (Fase P).
- La scala metallica (V.5) dipende da EC3 (Fase S.4) per le verifiche di instabilità: se Fase S non è ancora completata, implementare V.5 con verifica elastica semplificata come stub.
- Il widget Qt (V.6) deve supportare entrambe le modalità: calcolo singolo solaio e calcolo multi-solaio per edificio completo con aree di influenza.

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
