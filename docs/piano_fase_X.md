# Fase X — Solai (tutti i tipi, multi-campata, aperture, cerchiature)

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~100 |
| **Norma/e di riferimento** | NTC2018, EN 1992, DM96, DM92, RD2229 |
| **Priorità** | Alta (modulo fondamentale per edifici esistenti e nuovi) |

---

## Descrizione

Implementa il modulo di calcolo per solai di ogni tipologia (laterocemento, predalles, legno, acciaio, misti, getto pieno, ecc.), con supporto a:
- multi-campata
- aperture e fori
- cerchiature
- carichi variabili e combinazioni
- verifica a flessione, taglio, deformabilità, vibrazioni
- supporto multinorma e parametri personalizzabili
- gestione sia edifici esistenti che nuovi

---

## Teoria e fondamenti strutturali

- Modelli di calcolo per solai secondo le principali normative italiane e europee
- Analisi delle condizioni di vincolo e appoggio
- Calcolo delle sollecitazioni e delle deformazioni
- Verifica di resistenza e deformabilità
- Gestione delle aperture e delle cerchiature secondo NTC2018 e DM storici
- Riferimenti a prodotti commerciali e archivi materiali

---

## Diagramma dipendenze subfasi

```text
X.1 — Definizione tipologie solaio e parametri
 └── X.2 — Modello di calcolo e carichi
      └── X.3 — Verifica a flessione/taglio
           └── X.4 — Verifica deformabilità/vibrazioni
                └── X.5 — Gestione aperture/cerchiature
                     └── X.6 — Output risultati e report
                          └── X.7 — Test e validazione
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Archivio materiali | `src/materials/` | Parametri materiali e prodotti |
| Combinazioni carico | `src/combinations/` | Generazione combinazioni NTC2018 |
| Modulo report | `src/report/` | Output tabulati e relazioni |
| Normative | `src/core_calculus/core/` | Template verifiche |
| Log | `src/core/registro_log.py` | Log calcolo e warning |
| Aree di influenza (modulo condiviso) | `src/aree_influenza.py` | Calcolo area influenza per travi, solai, scale (vedi Fase Y) |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §7.2.6 | Verifica solai esistenti e nuovi |
| EN 1992-1-1 §9.3 | Solai in c.a. |
| DM 9/1/96 | Solai laterocemento |
| DM 16/1/96 | Solai legno |
| RD 2229/1939 | Solai storici |
| Santarella, Giangreco | Formule e metodi storici |
| Cataloghi commerciali | Parametri prodotti |

---

## Base scientifica e riferimenti strutturali

### Riferimenti normativi e bibliografici principali

| Norma/Riferimento         | Utilizzo chiave                                  |
|---------------------------|--------------------------------------------------|
| NTC2018 §7.2.6            | Verifica solai nuovi/esistenti                   |
| EN 1992-1-1 §9.3          | Solai in c.a. (Eurocodice 2)                     |
| DM 9/1/96                 | Solai laterocemento                              |
| DM 16/1/96                | Solai legno                                      |
| RD 2229/1939              | Solai storici                                    |
| Santarella, Giangreco     | Formule storiche, coefficienti di sicurezza      |
| Cataloghi commerciali     | Parametri prodotti prefabbricati                 |

### Tipologie di solaio e parametri principali

| Tipologia         | Parametri geometrici         | Parametri meccanici         | Note                       |
|-------------------|-----------------------------|-----------------------------|----------------------------|
| Laterocemento     | h, b, interasse, spessore    | f_ck, E_cm, γ               | Travetti, pignatte         |
| Predalles         | h, larghezza, armature       | f_ck, E_cm, γ               | Precompresso, prefabbricato|
| Legno             | sezione, interasse, lunghezza| f_mk, E_0, γ                | Massiccio/lamellare        |
| Acciaio           | profilo, interasse           | f_y, E, γ                   | Lamiere, travi IPE/HEA     |
| Getto pieno       | h, larghezza                 | f_ck, E_cm, γ               | Solaio pieno c.a.          |
| Misti             | parametri combinati          | dipende da materiali        | Collaboranti, CLT, ecc.    |

### Formule di base (metacodice)

**a) Carico massimo ammissibile (flessione):**
$$
M_{Ed} \leq M_{Rd}
$$
Dove:
- $M_{Ed}$ = momento sollecitante massimo (da combinazioni carico)
- $M_{Rd}$ = momento resistente di progetto (dipende da sezione e materiale)

**b) Verifica a taglio:**
$$
V_{Ed} \leq V_{Rd}
$$

**c) Freccia massima (deformabilità):**
$$
f_{max} \leq f_{lim}
$$
- $f_{max}$ = freccia calcolata (es. $qL^4/(8EI)$ per trave appoggiata)
- $f_{lim}$ = limite normativo (es. $L/250$)

**d) Combinazioni di carico (NTC2018):**
- Stato Limite Ultimo (SLU): $1.3G + 1.5Q$
- Stato Limite di Esercizio (SLE): $G + \psi Q$

### Tabella limiti deformabilità (NTC2018, EN 1992)

| Destinazione d’uso | Limite freccia $f_{lim}$ |
|--------------------|-------------------------|
| Solai ordinari     | $L/250$                 |
| Solai con tramezzi | $L/300$                 |
| Solai prefabbricati| $L/400$                 |

### Metacodice per verifica solaio (esempio Python-like)

```python
def verifica_solaio(M_Ed, V_Ed, f_max, params):
    # Verifica flessione
    M_Rd = calcola_M_Rd(params)
    ok_fless = M_Ed <= M_Rd

    # Verifica taglio
    V_Rd = calcola_V_Rd(params)
    ok_taglio = V_Ed <= V_Rd

    # Verifica deformabilità
    f_lim = params['L'] / params['limite_freccia']
    ok_freccia = f_max <= f_lim

    return {
        'flessione': ok_fless,
        'taglio': ok_taglio,
        'deformabilità': ok_freccia,
        'dettaglio': {
            'M_Ed': M_Ed, 'M_Rd': M_Rd,
            'V_Ed': V_Ed, 'V_Rd': V_Rd,
            'f_max': f_max, 'f_lim': f_lim
        }
    }
```

### Strategie per aperture e cerchiature

- **Modello semplificato:** riduzione sezione efficace, verifica locale con coefficienti di penalizzazione (NTC2018 §7.2.6.2)
- **Modello avanzato:** analisi FEM locale (opzionale, per aperture grandi o irregolari)

| Tipo apertura | Riduzione sezione (%) |
|---------------|----------------------|
| Piccola (<10% area) | 5–10%           |
| Media (10–25%)      | 15–25%          |
| Grande (>25%)       | 30–50%          |

### Limiti di variazione di rigidezza (NTC2018 §4.1.2.2, §7.2.6)

La NTC2018 prescrive che la rigidezza dei solai esistenti sia valutata considerando:
- Possibile degrado dei materiali (legno, acciaio, c.a.)
- Collaborazione effettiva tra elementi (travetti, soletta, pignatte, ecc.)
- Presenza di aperture, modifiche locali, fessurazioni
- Mancanza di prove sperimentali o documentazione

In assenza di dati certi, la rigidezza flessionale (EI) deve essere ridotta rispetto al valore teorico secondo criteri prudenziali.

| Condizione solaio                        | Riduzione rigidezza EI (%) | Riferimento normativo/tecnico                |
|------------------------------------------|----------------------------|----------------------------------------------|
| Solaio nuovo, collaborazione piena        | 0%                         | NTC2018 §7.2.6, EN 1992-1-1 §9.3             |
| Solaio esistente, collaborazione incerta  | 20–30%                     | NTC2018 §7.2.6, CNR-DT 206/2007              |
| Solaio legno, degrado visibile            | 30–50%                     | NTC2018 §4.1.2.2, CNR-DT 206/2007            |
| Presenza aperture >10% area               | +10–20% (cumulabile)       | NTC2018 §7.2.6.2, letteratura                |
| Degrado/fessurazioni diffuse              | fino a 50%                 | NTC2018 §4.1.2.2, Santarella, Giangreco      |

**Note tecniche:**
- Le riduzioni sono cumulative: in presenza di più condizioni sfavorevoli, applicare la somma delle penalizzazioni.
- La scelta dei coefficienti deve essere motivata e documentata nel report di calcolo.
- In caso di incertezza, adottare sempre il valore più cautelativo.
- Per solai storici, è raccomandato il confronto tra valori attuali (NTC2018) e coefficienti storici (Santarella, Giangreco), riportando entrambi nel report.
- La verifica della rigidezza può essere affinata tramite prove sperimentali (carico, dinamica, endoscopia, ecc.).
- Per solai prefabbricati o con elementi innovativi, fare riferimento anche a manuali tecnici e certificazioni di prodotto.

**Riferimenti normativi:**
- NTC2018 §4.1.2.2: "Per le strutture esistenti... si deve tener conto di eventuali riduzioni di rigidezza dovute a degrado, fessurazioni, modifiche locali..."
- NTC2018 §7.2.6: "La rigidezza dei solai deve essere valutata considerando la reale efficacia collaborante tra gli elementi..."
- EN 1992-1-1 §9.3: "La rigidezza delle membrature deve essere valutata in funzione delle condizioni di vincolo e collaborazione..."
- CNR-DT 206/2007: "Per il legno strutturale esistente, si raccomanda una riduzione cautelativa della rigidezza in assenza di prove."
- Santarella, Giangreco: "Per solai storici, applicare coefficienti di sicurezza e riduzione secondo la letteratura tecnica."

---

## Decisioni progettuali e storicizzazione

- Tutte le tipologie di solaio storico sono supportate (legno massiccio, putrelle e tavelloni, voltine di mattoni, ferro e laterizio, ecc.).
- Verranno applicati sia i coefficienti di sicurezza storici (Santarella, Giangreco) sia i valori attuali (NTC2018) per confronto.
- Per la resistenza del legno storico si useranno sia tabelle semplificate (CNR, letteratura) sia l’inserimento manuale dei parametri.
- Per le aperture nei solai storici saranno disponibili sia la penalizzazione semplificata (riduzione sezione) sia l’analisi locale avanzata (FEM).
- Nei report saranno sempre inclusi riferimenti bibliografici e formule storiche esplicite.
- Tutte le scelte e i parametri saranno tracciati e motivati nel report di calcolo.
- La logica di calcolo e la knowledge base sono state personalizzate secondo le risposte fornite in sessione (10/03/2026).
- Decisione 2026-03-10: la logica delle aree di influenza è centralizzata nel modulo trasversale (Fase Y, src/aree_influenza.py), condiviso tra solai, scale e fondazioni, per evitare duplicazioni e garantire coerenza. Tutti i riferimenti e le dipendenze sono aggiornati di conseguenza.

---

## Subfasi pianificate

### X.1 — Analisi e classificazione tipologie di solaio

- [ ] Censimento e classificazione: prefabbricati, armatura lenta, storici, moderni (monodirezionali, bidirezionali, alleggeriti)
- [ ] Definizione parametri geometrici e meccanici per ciascuna tipologia
- [ ] Mappatura delle fonti normative e bibliografiche per ogni classe

### X.2 — Modelli di calcolo e parametri storici

- [ ] Raccolta e formalizzazione delle formule storiche (RD2229/39, Santarella, Giangreco)
- [ ] Tabelle armatura minima, coefficienti di omogeneizzazione, spessori equivalenti
- [ ] Implementazione delle relazioni storiche per verifica flessione, taglio, deformabilità
- [ ] Confronto diretto tra approccio storico e NTC2018 per casi tipici

### X.3 — Modelli di calcolo e parametri moderni

- [ ] Formalizzazione modelli per prefabbricati, monodirezionali, bidirezionali, U-Boot
- [ ] Definizione parametri di input/output e struttura dati
- [ ] Integrazione delle formule di verifica moderne (NTC2018, EN 1992, EN 15037-1, EN 13747)
- [ ] Gestione carichi, combinazioni, limiti deformabilità
- [ ] Calcolo aree di influenza tramite modulo condiviso (vedi Fase Y)

### X.4 — Caratteristiche della sollecitazione nella sezione

- [ ] Calcolo posizione asse neutro per ogni tipologia (metodo storico e moderno)
- [ ] Determinazione campo di rottura (compressione, trazione, crisi fragile/duro)
- [ ] Costruzione dominio di resistenza (M-N, diagrammi interazione)
- [ ] Output grafico e tabellare dei domini di resistenza
- [ ] Confronto tra dominio storico e dominio NTC2018

### X.5 — Gestione aperture, cerchiature e degrado

- [ ] Implementazione penalizzazione semplificata e FEM locale per aperture
- [ ] Algoritmo cumulativo per riduzione rigidezza (aperture, degrado, collaborazione incerta)
- [ ] Tabelle e warning automatici per condizioni critiche

### X.6 — Livelli di conoscenza e fattori di confidenza (NTC2018)

- [ ] Implementazione sistema livelli di conoscenza (LC1, LC2, LC3)
- [ ] Applicazione automatica dei fattori di confidenza (FC) su resistenze e parametri
- [ ] Output chiaro dei valori adottati e motivazione della scelta
- [ ] Integrazione con report e tracciabilità

### X.7 — Output, report e tracciabilità

- [ ] Generazione tabulati dettagliati (HTML/MD), con passaggi intermedi e riferimenti normativi
- [ ] Evidenziazione delle differenze tra verifica storica e moderna
- [ ] TODO: Strutturare template di report HTML/MD

### X.8 — Test, validazione e casi studio

- [ ] Test unitari per ogni tipologia e verifica (storica e moderna)
- [ ] Test di integrazione su casi reali e letteratura
- [ ] TODO: Definire casi studio di validazione e benchmark

---

## Guida operativa e checklist per ogni subfase

### X.1 — Analisi e classificazione tipologie di solaio

- [ ] Elencare e descrivere tutte le tipologie (storici, prefabbricati, moderni, ecc.)
- [ ] Definire per ciascuna: parametri geometrici, meccanici, materiali
- [ ] Collegare ogni tipologia a riferimenti normativi e bibliografici
- [ ] Strutturare classi Python e schema dati per ogni tipologia
- [ ] TODO: Validare la copertura di tutte le varianti note

### X.2 — Modelli di calcolo e parametri storici

- [ ] Implementare formule e tabelle RD2229/39 (flessione, taglio, deformabilità)
- [ ] Inserire coefficienti di omogeneizzazione, armature minime, spessori equivalenti
- [ ] Prevedere confronto automatico con NTC2018 per casi tipici
- [ ] TODO: Annotare ogni formula con fonte e validità

### X.3 — Modelli di calcolo e parametri moderni

- [ ] Implementare modelli secondo NTC2018 (SLU, SLE, combinazioni carico)
- [ ] Definire input/output coerenti con la struttura dati
- [ ] TODO: Integrare riferimenti EN 1992, EN 15037-1, EN 13747 se richiesto

### X.4 — Caratteristiche della sollecitazione nella sezione

- [ ] Calcolare posizione asse neutro, campo di rottura, dominio di resistenza (M-N)
- [ ] Generare grafici di interazione e output numerici
- [ ] TODO: Prevedere funzioni di plotting e confronto storico/moderno

### X.5 — Gestione aperture, cerchiature e degrado

- [ ] Offrire sia penalizzazione semplificata sia FEM locale come opzioni
- [ ] Implementare algoritmo cumulativo per riduzione rigidezza
- [ ] TODO: Warning automatici per condizioni critiche

### X.6 — Livelli di conoscenza e fattori di confidenza (NTC2018)

- [ ] Applicare livelli di conoscenza (LC1, LC2, LC3) e fattori di confidenza (FC) in modo automatico
- [ ] Esplicitare sempre i valori adottati e la motivazione
- [ ] TODO: Prevedere override manuale se richiesto in futuro

### X.7 — Output, report e tracciabilità

- [ ] Generare tabulati dettagliati, passaggi intermedi, riferimenti normativi e grafici
- [ ] Evidenziare differenze tra verifica storica e moderna
- [ ] TODO: Strutturare template di report HTML/MD

### X.8 — Test, validazione e casi studio

- [ ] Test unitari per ogni tipologia e verifica (storica e moderna)
- [ ] Confronto con letteratura tecnica
- [ ] TODO: Definire casi studio di validazione e benchmark

---

# Sottosezioni tecniche dettagliate

## 1. Solai prefabbricati

### Travetti Varese, pianelle, prefabbricati c.a.p./c.a.v

- Travetti prefabbricati in c.a.p. (precompresso), sezione a T rovescia, appoggio su murature o travi.
- Interposti elementi di alleggerimento (pignatte o pianelle in laterizio).
- Soletta collaborante superiore in c.a. gettata in opera (spessore tipico 4–5 cm).
- Collegamento tra travetto e soletta tramite armature di ripresa e staffe.
- Parametri: altezza totale solaio, larghezza travetto, interasse, altezza pignatta, spessore soletta, resistenza calcestruzzo, armatura pretesa.
- Verifiche: flessione (sezione omogeneizzata), taglio (staffe, collegamento), deformabilità (freccia), collaborazione.
- Normativa: NTC2018 §4.1.2.2, §7.2.6, UNI EN 15037-1, manuali tecnici produttori.
- Tabelle di portata e armatura minime da produttore.

## 2. Solai ad armatura lenta e storici (RD2229/39)

### Solai con/ senza soletta collaborante

- Travetti in c.a. gettati in opera, armatura longitudinale “lenta”
- Pignatte/mattoni di alleggerimento (altezza h_m)
- Soletta superiore: presente o assente
- Armatura minima prescritta in funzione di h_m e larghezza travetto
- Coefficienti di omogeneizzazione γ per soletta collaborante
- Spessore equivalente: $h_{eq} = h_{trave} + \gamma \cdot s_{soletta}$
- Tabelle di portata in funzione di interasse, altezza pignatta, presenza soletta
- Verifiche: flessione (sezione omogeneizzata), taglio, deformabilità
- Normativa: RD2229/39, tabelle e formule storiche, confronto con NTC2018

#### Esempio tabella armatura minima RD2229/39

| Altezza mattone (h_m) | Armatura min. (cm²/m) |
|-----------------------|-----------------------|
| 10 cm                 | 0.30                  |
| 12 cm                 | 0.35                  |
| 15 cm                 | 0.40                  |
| 18 cm                 | 0.45                  |
| 20 cm                 | 0.50                  |

#### Coefficienti di omogeneizzazione tipici

| Materiale soletta | γ (E_cls/E_pignatta) |
|-------------------|----------------------|
| Laterizio         | 5–8                  |
| Cemento alleggerito| 3–5                 |

## 3. Solai moderni

### Monodirezionali

- Travetti paralleli, carico portato in una sola direzione
- Alleggerimento con pignatte o blocchi in EPS
- Soletta collaborante superiore
- Verifiche: come sopra, attenzione a interasse e spessore soletta

### Bidirezionali

- Griglia di travetti ortogonali (grigliato, predalles bidirezionale)
- Alleggerimento con casseri plastici (U-Boot, Iglu, ecc.)
- Carico distribuito su entrambe le direzioni (analisi a piastra)
- Verifiche: flessione/taglio in entrambe le direzioni, punzonamento

### Alleggeriti tipo U-Boot

- Casseri plastici riciclati, getto monolitico in c.a.
- Spessore variabile, altezza totale anche >30 cm
- Analisi con metodo delle piastre (modello di piastra ortotropa)
- Vantaggi: riduzione peso proprio, grandi luci, flessibilità architettonica
- Normativa: NTC2018 §4.1.2.2, §7.2.6, EN 1992-1-1 §9.3, EN 13747

## 4. Tabelle e formule di supporto

### Spessore equivalente

$$
h_{eq} = h_{trave} + \gamma \cdot s_{soletta}
$$

### Esempio metacodice verifica solaio (già presente sopra)

## 5. Note operative e riferimenti normativi

- Tutti i parametri devono essere configurabili e tracciabili
- Per ogni verifica, documentare la scelta dei coefficienti e delle formule
- Estratti normativi e bibliografici sempre inclusi nel report
- Confronto tra verifica storica (RD2229/39) e attuale (NTC2018) per solai esistenti

---
