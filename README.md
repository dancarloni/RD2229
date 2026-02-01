# RD2229

Progetto per digitalizzare e rendere calcolabili i metodi storici (Regio Decreto 2229/1939, Santarella, Giangreco) con una GUI che riproduca i passaggi di progetto dell’epoca.

## Obiettivo
Creare un motore di calcolo che:
- gestisca materiali, sezioni, armature e tabelle/abachi storici;
- mostri tutti gli step del calcolo (coefficiente, interpolazione, formula);
- consenta una GUI grafica chiara e “storica”.

## Struttura del progetto
- [src/rd2229](src/rd2229) — logica di calcolo e modelli
- [data](data) — tabelle e coefficienti digitalizzati
- [docs](docs) — note, roadmap e fonti
- [tests](tests) — test dei calcoli

## Struttura logica dei moduli

### 1. Moduli fondamentali (core)
Elementi comuni a tutte le tipologie di calcolo:

- **Materiali** (`core/materials.py`)
  - Calcestruzzo (resistenze, modulo elastico, coefficienti storici)
  - Acciaio (resistenze, modulo elastico, tipologie storiche)
  - Proprietà fisiche (peso specifico, coefficienti di dilatazione)

- **Geometria delle sezioni** (`core/geometry.py`)
  - Rettangolare
  - Circolare
  - A T
  - Ad L
  - Ad I
  - Altre forme composite

- **Armatura** (`core/reinforcement.py`)
  - Ordini di armatura (superiore/inferiore)
  - Area dei ferri per strato
  - Copriferro (superiore/inferiore)
  - Diametro delle barre
  - Staffe (diametro, passo)
  - Ferri piegati
  - Armature aggiuntive

- **Proprietà della sezione** (`core/section_properties.py`)
  - Area
  - Momento statico
  - Momento di inerzia
  - Peso proprio
  - Baricentro

- **Interpolazione** (`core/interpolation.py`)
  - Interpolazione lineare
  - Interpolazione bilineare (per tabelle a due variabili)
  - Lettura e gestione abachi storici

### 2. Moduli di calcolo specifici
Ciascun modulo implementa le procedure storiche per un elemento strutturale.

**Struttura tipo per ogni modulo:**
```
calculations/
├── travi/
│   ├── __init__.py
│   ├── flessione_semplice.py      # Trave inflessa
│   ├── taglio.py                  # Calcolo a taglio
│   ├── torsione.py                # Torsione
│   └── presso_tenso_flessione.py  # Pressoflessione/tensoflessione
├── pilastri/
│   ├── __init__.py
│   ├── compressione_semplice.py
│   ├── pressoflessione_retta.py
│   └── pressoflessione_deviata.py
├── solette/
│   ├── __init__.py
│   ├── piastra_appoggiata.py
│   └── piastra_incastrata.py
├── solai/
│   ├── __init__.py
│   ├── latero_cemento.py
│   └── putrelle_e_voltine.py
└── fondazioni/
    ├── __init__.py
    ├── plinti.py
    ├── travi_rovesce.py
    └── platee.py
```

**Moduli previsti** (da integrare progressivamente):
- `travi/` — Travi (flessione, taglio, torsione)
- `pilastri/` — Pilastri (compressione, pressoflessione)
- `solette/` — Solette e piastre
- `solai/` — Solai (latero-cemento, putrelle e voltine)
- `fondazioni/` — Fondazioni (plinti, travi rovesce, platee)
- `scale/` — Scale
- `muri/` — Muri di sostegno
- Altri moduli specifici da definire

### 3. Moduli di verifica
Verifiche secondo RD 2229/1939 e normative storiche dell'epoca:

```
verifications/
├── __init__.py
├── rd2229/
│   ├── __init__.py
│   ├── tensioni_ammissibili.py    # Verifiche alle tensioni ammissibili
│   ├── deformazioni.py            # Verifiche deformative
│   ├── fessurazione.py            # Controllo fessurazione
│   └── stabilita.py               # Verifiche di stabilità
└── coefficienti/
    ├── __init__.py
    ├── sicurezza.py               # Coefficienti di sicurezza storici
    └── carico.py                  # Coefficienti di carico
```

### 4. Database tabelle storiche
```
data/
├── tables.schema.json             # Schema generale
├── rd2229/
│   ├── coefficienti_rigidezza.json
│   ├── tensioni_ammissibili.json
│   └── coefficienti_sicurezza.json
├── santarella/
│   ├── tabelle_cemento_armato.json
│   └── abachi_flessione.json
└── giangreco/
    ├── tabelle_sezioni.json
    └── diagrammi_interazione.json
```

### Note per integrazioni future
- Ogni nuovo modulo di calcolo deve seguire la struttura `calculations/<elemento>/<sottoargomento>.py`
- Le funzioni di calcolo devono documentare: formule usate, riferimenti normativi, step intermedi
- Le verifiche devono restituire sia il risultato (OK/NON OK) che i passaggi di calcolo
- Tutte le tabelle/coefficienti devono essere centralizzate in `data/` con schema JSON validabile

## Avvio rapido (solo logica)
1. Creare un ambiente Python.
2. Installare le dipendenze da [requirements.txt](requirements.txt).
3. Usare i modelli in [src/rd2229](src/rd2229).

## Prossimi passi suggeriti
- Digitalizzare le tabelle in [data/tables.schema.json](data/tables.schema.json).
- Implementare le procedure specifiche dei capitoli RD 2229/Santarella/Giangreco.
- Aggiungere GUI (desktop o web) con visualizzazione passo‑passo.