# CHANGELOG (v0.1.0)

## Versione 0.1.0 — Ristrutturazione completa (A1 Migration)

### Modifiche Principali

- **Creazione package `/src/`**: Nuova struttura modulare professionale
- **Creazione `legacy/`**: Tutti i file originali preservati senza modifiche
- **Creazione package moderni**:
  - `calc/` - Registry area a taglio e sezioni
  - `materials/` - Modelli materiali, validazione, repository
  - `elements/` - Modelli elementi, repository, risoluzione input
  - `codes/` - Registry normative con parametri e clausole (NTC2018, EC2)
  - `actions/` - Azioni di verifica (FlexureCheck, ShearCheck)
  - `report/` - Renderer HTML/MD/PDF e template
  - `config/` - Configurazioni YAML (units, numerics, app, features)
  - `tools/` - CLI e exporter risultati
  - `tests/` - Suite di test minimi

### File Generati

- **Stub S2 completi**: Tutti i moduli con docstring estese e TODO
- **Template HTML/MD**: Template pronti per rendering report
- **CLI e exporter**: Strumenti command-line
- **Configurazioni YAML**: units.yml, numerics.yml, app.yml, features.yml
- **Test minimi**: 6 moduli di test per validazione architettura

### Unità di Misura (Standard Fisso)

- Lunghezze: cm
- Aree: cm²
- Inerzie: cm⁴
- Tensioni: kg/cm²
- Densità: kg/m³

### Architettura

Pipeline completa:

```
repository → resolve_inputs → action_repo → report renderers → export
```

### Prossimi Passi

1. Implementare i TODO nei moduli S2
2. Popolare registry con dati reali
3. Completare implementazione verifiche
4. Estendere suite di test
5. Implementare rendering PDF

---

**Data**: 2026-02-11  
**Tipo**: Ristrutturazione completa (A1)  
**Stato**: Struttura base completata, implementazione da espandere
