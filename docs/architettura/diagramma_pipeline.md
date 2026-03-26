# Diagramma Flusso — Pipeline di Calcolo RD2229

## Flusso Esecuzione Pipeline

```
┌──────────────┐
│ INIZIO       │
│ Carica .jsonp│
└──────┬───────┘
       │
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 1. VALIDAZIONE│───▶│ Controlla: norm_code, geometry, │
│              │    │ loads, materials presenti        │
└──────┬───────┘    └─────────────────────────────────┘
       │ ok
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 2. SISMICO   │───▶│ Se abilitato: calcola spettro,  │
│   (opzionale)│    │ combinazioni sismiche, q        │
└──────┬───────┘    └─────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 3. PER OGNI ELEMENTO:                        │
│  ┌──────────────────────────────────────────┐│
│  │ a. Trova sezione + materiale             ││
│  │ b. Trova carichi (N, M, T)               ││
│  │ c. Determina tipo verifica               ││
│  │ d. Chiama ModuleEngine.run()             ││
│  │ e. Raccogli CheckResult[]                ││
│  │ f. Accumula calculation_steps[]          ││
│  └──────────────────────────────────────────┘│
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 4. FUOCO     │───▶│ Se fire.enabled: verifica       │
│   (opzionale)│    │ tabellare ISO 834 per ogni elem │
└──────┬───────┘    └─────────────────────────────────┘
       │
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 5. VENTO     │───▶│ Se wind presente: profilo       │
│   (opzionale)│    │ velocità/pressione NTC2018      │
└──────┬───────┘    └─────────────────────────────────┘
       │
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 6. MURATURA  │───▶│ Se plugins.muratura: cinematica, │
│   (opzionale)│    │ scorrimento, cantonale          │
└──────┬───────┘    └─────────────────────────────────┘
       │
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 7. AGGREGAZ. │───▶│ global_ok = all(elem.ok)        │
│              │    │ Produce ResultsModel             │
└──────┬───────┘    └─────────────────────────────────┘
       │
       ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ 8. REPORTING │───▶│ Raccoglie da tutti i moduli,    │
│              │    │ genera relazione tecnica         │
└──────┬───────┘    │ MD/HTML/PDF con formule          │
       │            └─────────────────────────────────┘
       ▼
┌──────────────┐
│ FINE         │
│ Salva .jsonp │
│ + Report     │
└──────────────┘
```

## Dettaglio Step 3 — Esecuzione Verifiche per Elemento

```
Per ogni elemento element:
    state_limite = project.limit_states  # [SLU, SLE_rara, SLE_freq, SLE_qp, SLV]

    for limit_state in state_limite:
        # Filtra condizioni di carico per questo stato limite
        load_conditions = LoadConditionManager.get_by_limit_state(limit_state)

        # Esegui verifica per ogni condizione
        for load_cond in load_conditions:
            # Dispatcher per norma
            match norm_code:
                "RD2229", "DM72", "DM74" → engine = TensAmmEngine(norm_code)
                "DM92", "DM96"           → engine = MixedEngine(norm_code)
                "NTC2008"                → engine = SLU_NTC2008Engine()
                "NTC2018"                → engine = SLU_SLE_NTC2018Engine()

            # Esegui verifiche
            results = [
                engine.check_flessione_retta(load_cond, section, material),
                engine.check_flessione_deviata(load_cond, section, material),
                engine.check_pressoflessione(load_cond, section, material),
                engine.check_taglio(load_cond, section, material),
                engine.check_torsione(load_cond, section, material),
                engine.check_taglio_torsione_combinata(load_cond, section, material),
                # SLE specifiche
                engine.check_tensioni(load_cond, section, material, limit_state),
                engine.check_fessurazione(load_cond, section, material, limit_state),
                engine.check_deformabilita(load_cond, section, material),
            ]

        # Inviluppo per questo stato limite
        envelope = max(results, key=lambda r: r.utilization)

    # Risultato finale per elemento
    return ModuleResult(
        ok = all(envelope.ok for envelope in envelopes_slu + envelopes_sle),
        checks_slu = envelopes_slu,
        checks_sle = envelopes_sle,
        envelope_utilization = max(e.utilization for e in all_envelopes),
        envelope_check_name = worst_check.name,
    )
```

## Parametri Pipeline (ConfigYAML)

```yaml
pipeline:
  norm_code: "NTC2018"              # Norma di calcolo
  limit_states:                     # Stati limite da calcolare
    - "SLU"
    - "SLE_rara"
    - "SLE_freq"
    - "SLE_qp"
    - "SLV"                          # Solo se sismico

  modules_enabled:
    verifiche_ca: true
    sismica: true
    vento: true
    fuoco: false
    muratura: false
    geotecnica: false
    combinazioni: true

  calculation:
    envelope: true                   # Calcola inviluppo?
    report_format: "pdf"             # pdf, html, md
    save_intermediate: true          # Salva passaggi intermedi?
```

## Flusso Risultati

```
Element 1 ──┐
Element 2 ──┤
 ...        ├─▶ ModuleEngine.run_batch() ──▶ ModuleResult[]
Element N ──┘                                   │
                                                ▼
                                        ┌──────────────────┐
                                        │ Aggregazione     │
                                        │ ResultsModel     │
                                        └────────┬─────────┘
                                                 │
                         ┌───────────────────────┼───────────────────────┐
                         │                       │                       │
                         ▼                       ▼                       ▼
                    ┌──────────┐           ┌──────────┐           ┌──────────┐
                    │ Reporting│           │ Dashboard│           │ Archivio │
                    │(Relazione│           │(Visualiz.│           │(Project) │
                    │ Tecnica) │           │ Risultati│           │ Salvat. │
                    └──────────┘           └──────────┘           └──────────┘
```
