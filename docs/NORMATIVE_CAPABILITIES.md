# Matrice Capabilities Normative (STEP 3)

## Scopo
Fornire una vista unificata delle **capabilities** disponibili per ciascuna normativa e ciascun metodo.

## Definizioni
- **Norma (NormativeCode)**
- **Metodo (SeismicMethodId)**
- **Prodotto**: `SPECTRUM`, `FLOOR_FORCES`, ...
- **Componenti**: `ONDULATORY`, `SUSSULTORY`, ...

## NTC2018 (esempio)
- Prodotto: `SPECTRUM`
- Metodo: `NTC2018_SPECTRUM_PASTE` (MVP)

## RD2229_39
### Prodotto: `FLOOR_FORCES`
- Metodo: `RD2229_39_FLOOR_FORCES_MASS_PERCENT`
  - Componenti: `ONDULATORY`
  - Input: masse di piano (breakdown o totale), coefficiente `p`, `g`

- Metodo: `RD2229_39_SUSSULTORY_DERIVED_125`
  - Componenti: `SUSSULTORY`
  - Derived from: `ONDULATORY`
  - Factor: `1.25`

### Policies supportate (MVP)
- MassAttributionPolicy (split verticali 0.5/0.5)
- EdgeFloorsPolicy (piano terra/ultimo piano)

### Quality level
- `LEGACY_APPROX` (default)
- `MVP_TRACE` (minimo garantito)

## DM92 / DM96 / EC8
Per lo STEP 3 possono essere registrate come provider stub:
- dichiarano capabilities previste;
- restituiscono NotSupported con trace coerente;
- oppure implementano un solo metodo MVP.

> Nota: EC2 non genera azioni sismiche.
