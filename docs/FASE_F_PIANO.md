# FASE F — Metodo POR / Telaio Equivalente: Piano Dettagliato

**Data**: 2026-03-06
**Branch**: `claude/materials-database-structure-Fh726`

---

## Decisioni progettuali

| Aspetto | Decisione |
|---------|-----------|
| **Piani** | Multipiano |
| **Input geometria** | Entrambi (pianta+aperture e maschi diretti) |
| **Fasce** | Deformabili (telaio equivalente vero) |
| **Forze sismiche** | Entrambe le distribuzioni NTC2018 |
| **Drift limite** | Configurabile, default NTC2018 + Circolare §C8.7.1 |
| **Direzioni** | X, Y separati + combinazione 100%+30% |
| **Eccentricità acc.** | ±5% dimensione in pianta |
| **Fattore q** | Tabelle automatiche NTC2018 + override manuale |
| **Report** | Tabella maschi stile 3Muri/Aedes |
| **POR ↔ Cinematica** | Analisi separate, confronto ζ_E automatico |
| **Diaframma** | Rigido/deformabile con selezione utente |
| **Vincoli maschi** | Automatico da rigidezza fasce + override manuale |
| **Carichi N** | Automatico da aree influenza + override manuale |
| **Bilinearizzazione** | Equipartizione energetica (NTC2018 §7.8.1.6) |
| **Torsione pianta** | 3 GDL per piano (ux, uy, θz) |
| **Fasce resistenza** | Auto-detect da cordoli (biella/trave) |
| **LC / FC** | Selezione LC + override FC |
| **Collasso** | Configurabile dall'utente |
| **Struttura file** | 6-7 file modulari ≤400 righe ciascuno |
| **Approccio** | Incrementale per sotto-fasi |
| **Tabella C8.5.I** | Database JSON completo |
| **Grafico** | Matplotlib curva pushover + bilineare |

---

## Riferimenti normativi

| Topic | NTC2018 | Circolare 7/2019 |
|-------|---------|-------------------|
| Meccanismi globali + locali | Cap. 8 | C8.7.1 |
| Cinematica locale | — | C8.7.1.2 |
| Analisi globale | 7.8.2, 7.8.3 | C8.7.1.3 |
| Drift limite (non armata) | §7.8.2.2.1 (1.0% pflex), §7.8.2.2.2 (0.5% taglio) | — |
| Drift limite (armata) | §7.8.3.2.1 (1.6% pflex), §7.8.3.2.2 (0.8% taglio) | — |
| Fattore q | §7.8.1.3, Tab 7.3.II | C8.5.5.1 |
| Resistenza taglio esistente | — | C8.7.1.3.1.1 |
| Parametri meccanici | — | Tabella C8.5.I |
| Fattori di confidenza | §8.5.4 | C8.5.4 |
| Bilinearizzazione | §7.8.1.6 | — |

### Drift limits default

| Criterio | Muratura non armata | Muratura armata |
|----------|--------------------|-----------------|
| Taglio (SLC) | 0.5% h | 0.8% h |
| Pressoflessione (SLC) | 1.0% h | 1.6% h |

### Fattore di comportamento q

- Muratura ordinaria nuova: q₀ = 1.75 × (α_u/α_1), con α_u/α_1 ≤ 2.50
- Muratura esistente: α_u/α_1 ≤ 1.50 (Circ. §C8.5.5.1)
- K_R = 1.0 regolare, 0.8 irregolare in altezza
- q massimo esistente: ~3.0

---

## Architettura: collegamento POR ↔ Cinematica

Seguendo la prassi dei software commerciali (3Muri, Aedes PCM, CDMa Win):
- Le analisi globale (POR) e locale (cinematica) sono **SEPARATE**
- Condividono lo stesso modello geometrico (maschi, fasce, materiali, carichi)
- I carichi per i blocchi cinematici vengono dal modello dei carichi, NON dal POR
- L'indice di rischio ζ_E si riporta per entrambe
- Il **minimo ζ_E** governa la sicurezza dell'edificio
- Prassi: prima cinematica (stabilità locale), poi POR (comportamento globale)

---

## Sotto-fasi incrementali

### Blocco 1 (F.1-F.3): Modello + discretizzazione + rigidezza
**File**:
- `src/methods/muratura/modello_edificio.py` — dataclass Edificio, Piano, Parete, Apertura
- `src/methods/muratura/discretizzazione.py` — algoritmo maschi/fasce da geometria
- `src/methods/muratura/rigidezza.py` — rigidezza maschio/fascia, assemblaggio matrice
- `data/materials/tabella_c85i.json` — parametri meccanici muratura esistente
- `tests/test_modello_edificio.py`
- `tests/test_discretizzazione.py`
- `tests/test_rigidezza.py`
- **Test stimati**: ~40-50

### Blocco 2 (F.4-F.5): Pushover + resistenza
**File**:
- `src/methods/muratura/resistenza.py` — curva bilineare maschio/fascia, integrazione E.2
- `src/methods/muratura/por_analisi.py` — pushover incrementale, 3 GDL/piano, distribuzioni
- `tests/test_resistenza.py`
- `tests/test_por_analisi.py`
- **Test stimati**: ~30-40

### Blocco 3 (F.6-F.8): Verifiche, q, report, grafico
**File**:
- `src/methods/muratura/fattore_comportamento.py` — tabelle q NTC2018, override
- `src/methods/muratura/por_verifiche.py` — tabella maschi D/C, ζ_E, grafico matplotlib
- `tests/test_fattore_comportamento.py`
- `tests/test_por_verifiche.py`
- **Test stimati**: ~20-30

**Totale stimato**: ~90-120 test, ~2000-2500 righe di codice

---

## Modello dati principale

```
Edificio
├── nome: str
├── piani: list[Piano]
│   ├── id_piano: int
│   ├── quota_z: float [cm]
│   ├── altezza_interpiano: float [cm]
│   ├── pareti: list[Parete]
│   │   ├── id_parete: int
│   │   ├── x_ini, y_ini, x_fin, y_fin: float [cm]
│   │   ├── spessore: float [cm]
│   │   ├── materiale: MaterialeMuratura
│   │   └── aperture: list[Apertura]
│   │       ├── x_offset: float [cm] (distanza da x_ini)
│   │       ├── z_offset: float [cm] (distanza dal pavimento)
│   │       ├── larghezza, altezza: float [cm]
│   │       └── tipo: "porta" | "finestra"
│   ├── massa: float [kg]
│   └── tipo_diaframma: "rigido" | "deformabile"
├── parametri_sismici: ParametriSismici
├── livello_conoscenza: LC1 | LC2 | LC3
├── FC: float (override o da LC)
└── config: ConfigPOR
    ├── drift_taglio: float (default 0.005)
    ├── drift_pflex: float (default 0.010)
    ├── criterio_collasso: str
    ├── soglia_collasso: float
    └── tipo_diaframma_default: str

Maschio → riutilizza InputTaglio (E.2) per verifiche
Fascia → accoppiamento con Cordolo (E.5) per resistenza
```
