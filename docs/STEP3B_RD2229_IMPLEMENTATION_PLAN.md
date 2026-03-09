# STEP 3B — Implementazione MVP RD2229/39 (Azioni sismiche)

## Obiettivo

Implementare il minimo indispensabile per calcolare:

- ONDULATORY: F_i = p *M_i* g
- SUSSULTORY: F_i,sus = 1.25 * F_i,ond (derivato)

con:

- modularità (methods/policies/validators)
- tracciabilità (trace)
- test pytest (relazione 1.25, presenza trace)

## Struttura file (path confermato)

`src/rd2229/seismic/rd2229_39/`

## TODO normativi

Inserire riferimenti puntuali RD2229/39 in `docs_ref/norm_refs.py` e nei trace.
