"""Telai piani c.a. — Metodo di Cross-Pozzati (RD 2229/39).

Modulo per il calcolo di telai piani in cemento armato con il metodo storico
della distribuzione dei momenti (Hardy Cross, 1930), nella trattazione italiana
di Pozzati ("Teoria e Tecnica delle Strutture") e Santarella ("Il Cemento Armato").

Struttura:
- modello_telaio.py   — dataclass: Nodo, Asta, Vincoli, Rilasci, ModelloTelaio
- carichi_fissi.py    — formule MIP per tutti i tipi di carico
- cross_pozzati.py    — algoritmo Cross iterativo + correzione sway n-piani
- solver_telaio.py    — sollecitazioni M/V/N per 3 sezioni per asta
- combinazioni_rd2229 — combinazioni di carico RD2229/39 e inviluppo
- sisma_telaio.py     — forze sismiche ondulatorio + sussultorio per piano
- verifiche_telaio.py — verifiche TA (flessione, pressoflessione, taglio)
- armature_telaio.py  — progetto armature + copia/incolla + serializzazione
- export_telaio.py    — tabulati storici (7 tabelle) + HTML + scheda Santarella

Unità: cm per geometria, kg per forze, kg/cm² per tensioni.
"""
