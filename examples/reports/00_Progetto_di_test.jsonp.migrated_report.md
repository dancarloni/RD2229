# Rapporto RD2229

**Schema version:** `1.1.0`
**Generato:** 2026-03-26T15:09:59.317328+00:00
**App version:** 0.1.0
**Normativa:** RD2229
**Esito globale:** ✅ OK

## Indice

- [Informazioni Progetto](#informazioni-progetto)
- [Impostazioni Normativa](#impostazioni-normativa)
- [Riepilogo Input](#riepilogo-input)
- [Risultati Verifiche](#risultati-verifiche)
- [Traccia Calcolo](#traccia-calcolo)

## Informazioni Progetto


## Impostazioni Normativa

- **Normativa:** RD2229
- **Stati limite:** TA
- **Unità forza:** kN
- **Unità lunghezza:** cm
- **Struttura esistente:** Sì (LC: LC1)

## Riepilogo Input

- Elementi geometrici: 1
- Materiali: 2
- Combinazioni di carico: 1

## ⚠️ Avvisi

- X6-REP-001:WARN::TRACE::Errore pipeline vento: 'dict' object has no attribute 'method'

## Risultati Verifiche

| Elemento | Esito | Metriche principali |
|----------|-------|---------------------|
| SEED-L-2 | ✅ OK | norm_code: RD2229 |

## Traccia Calcolo

```
pipeline:start
pipeline:validation_done
seismic:skip(no_data)
element:SEED-L-2:ok=True
pipeline:checks_done
step5:start
step5:element:SEED-L-2:ok=True:checks=0.0
step5:done(results=1)
wind:start
wind:error
pipeline:complete
```

## Audit Trail X6

- **Input hash:** 2dfd5689db8ecac97d8185aefb83215ca73a236ee938a169d3b08e57733bf1eb
- **Output hash:** 50eba09968ed3a533afcc0e20e8eaa598b196f3c942da2e0acd826987a354459
- **Decision trace:** 5 voci
- **Payload JSON disponibile:** Sì
