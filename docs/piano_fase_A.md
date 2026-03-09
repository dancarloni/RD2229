# Fase A — Database Materiali Multi-Normativa

## Subfasi, checklist e storico

### A.1 Cataloghi JSON per tutte le norme

**Stato**: COMPLETATO — commit a0f05aa

- [x] Catalogo NTC2018: data/materials/catalogo_ntc2018.json (18 materiali)
- [x] Catalogo RD2229: data/materials/catalogo_rd2229.json (10 materiali)
- [x] Catalogo DM72: data/materials/catalogo_dm72.json (8 materiali)
- [x] Catalogo DM87: data/materials/catalogo_dm87_muratura.json (9 materiali)
- [x] Catalogo DM92: data/materials/catalogo_dm92.json (10 materiali)
- [x] Catalogo DM96: data/materials/catalogo_dm96.json (12 materiali)
- [x] Catalogo NTC2008: data/materials/catalogo_ntc2008.json (12 materiali)
- [x] Catalogo Circ81: data/materials/catalogo_circ81_muratura.json (5 materiali)
- [x] Catalogo Legno: data/materials/catalogo_legno.json (6 materiali)
- [x] Catalogo OPCM3274: data/materials/catalogo_opcm3274.json (7 materiali)
- [x] Totale materiali: 97
- [x] Metodi: list_by_norma(), list_norme_disponibili(), carica_tutti_cataloghi()
- [x] Test: tests/test_cataloghi_materiali.py (22 test)

### A.2 MaterialSource strutturata

**Stato**: COMPLETATO — commit a0f05aa

- [x] Creazione src/materials/material_source.py (dataclass, enum, serializzazione)
- [x] Creazione data/materials/material_sources.json (9 fonti migrate)
- [x] Collegamento MaterialNormRef a Material (campo source_refs)
- [x] Aggiornamento MaterialRepository per gestire MaterialSource tipizzata
- [x] Popolamento cataloghi JSON con riferimenti normativi
- [x] Integrazione riferimenti in report e GUI
- [x] Eliminazione file legacy (src/legacy/material_sources.py)
- [x] Test: serializzazione/deserializzazione, load_sources(), get_source()

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase A sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
