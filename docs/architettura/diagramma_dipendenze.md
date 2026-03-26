# Diagramma Dipendenze — Architettura Modulare RD2229

## Albero Dipendenze Moduli

```
                        ┌─────────────────┐
                        │    DASHBOARD     │
                        │  (entry point)   │
                        └────────┬────────┘
                                 │ lancia
                    ┌────────────┼────────────┐
                    │            │             │
              ┌─────▼─────┐ ┌───▼────┐  ┌────▼─────┐
              │  MODULI    │ │PIPELINE│  │ REPORTING │
              │  (N gui)   │ │(orchest)│  │(relazione)│
              └─────┬─────┘ └───┬────┘  └────┬─────┘
                    │            │             │
        ┌───────────┼───────────┼─────────────┤
        │           │           │             │
   ┌────▼────┐ ┌───▼───┐ ┌────▼────┐  ┌────▼────┐
   │Verifiche│ │Sismica│ │  Vento  │  │  Fuoco  │
   │  c.a.   │ │Pushov.│ │ NTC2018 │  │ISO 834  │
   └────┬────┘ └───┬───┘ └────┬────┘  └────┬────┘
        │          │           │             │
        └──────────┴───────────┴─────────────┘
                        │ usano
              ┌─────────┼─────────┐
              │         │         │
         ┌────▼────┐ ┌──▼───┐ ┌──▼────┐ ┌──▼────┐
         │MATERIALI│ │SEZIONI│ │ NORME │ │CARICHI│
         │(archivio│ │(12 tip│ │(10 cod│ │(N cond│
         │+LC/FC)  │ │condiv)│ │ condiv)│ │×M SL) │
         └─────────┘ └──────┘ └───────┘ └───────┘
```

## Descrizione Livelli

### 1. **DASHBOARD** (entry point)
- Punto di ingresso principale dell'applicazione
- Launcher per moduli disponibili
- Selezione/apertura progetti
- Monitor stato pipeline

### 2. **MODULI DI CALCOLO** (13 moduli)
- **Prioritari (Fase 1-2):**
  - Verifiche c.a. (TA/SLU/SLE × 10 norme)
  - Sismica/Pushover (spettro + analisi)

- **Secondari (Fase 3):**
  - Vento (NTC2018/EN1991)
  - Fuoco (ISO 834 tabellare)
  - Muratura (cinematica, scorrimento, POR)
  - Geotecnica (5 sotto-domini)
  - Combinazioni (SLU/SLE/SLV)
  - Scale (calcolo rampe)
  - FEM/Telai (modello telaio)
  - Esistenti (vulnerabilità, LV1/LV2/LV3)

### 3. **PIPELINE** (orchestrator)
- Coordina esecuzione moduli in sequenza
- Legge configurazione stato limite
- Aggregazione risultati

### 4. **REPORTING** (generatore relazioni)
- Raccoglie risultati da tutti i moduli
- Genera relazione tecnica (MD/HTML/PDF)
- Include formule e passaggi intermedi

### 5. **SHARED MODULES** (archivi e utilities)
- **Materiali** — Archivio centralizzato con LC/FC
- **Sezioni** — Archivio 12 tipi sezione + proprietà
- **Norme** — Mapping norma→materiali compatibili
- **Carichi** — Gestione N condizioni × M stati limite
- **Project** — Modello progetto e serializzazione
- **UI** — Componenti Qt comuni (base_module_window, widgets)
- **Config** — Impostazioni utente e persistenza

---

## Ordine Implementazione

```
Fase 0: Shared infrastructure (materials, sections, norms, loads, ui)
  ↓
Fase 1: Verifiche c.a. (prioritario)
  ↓
Fase 2: Sismica (prioritario)
  ↓
Fase 3: Moduli secondari
  ↓
Fase 4: Reporting
  ↓
Fase 5: Pipeline + Dashboard
```

---

## Note Architetturali

1. **Isolamento moduli**: Ogni modulo ha engine/ + gui/ + docs/ + tests/
2. **Interfaccia standard**: ModuleInfo, ModuleEngine, ModuleResult
3. **Filtri normativi**: NormMaterialMap filtra materiali per norma selezionata
4. **LC/FC integrato**: KnowledgeLevel factory per strutture esistenti
5. **N condizioni × M SL**: LoadConditionManager per gestire combinazioni
6. **Inviluppo verifiche**: Envelope su tutti i checks per ogni SL
7. **Tabulati professionali**: Formule, passaggi, riferimenti normativi
8. **Zero dipendenze circolari**: Moduli dipendono da shared, non da altri moduli
