# Fase O — Griglia sismica INGV + Spettro NTC2018

## Subfasi, checklist e storico

### O.1 Import dati pericolosità sismica INGV

**Stato**: PARZIALMENTE COMPLETATO — commit d6e589a

- [x] Import da webservice INGV (lat, lon -> ag, F0, TC*)
- [x] Tabella locale griglia INGV (fallback offline, CSV)
- [x] Funzione unificata con routing webservice/CSV
- [ ] File CSV griglia INGV NTC2018 Allegato B da fornire dall'utente
- [x] Import parametri da EdiLus-MS
- [x] Validazione e normalizzazione formato output

### O.2 Modulo spettro NTC2018

**Stato**: COMPLETATO

- [x] Enum CategoriaSuolo, CategoriaTopografica, ClasseUso
- [x] calcola_VR, calcola_CC, calcola_SS, calcola_ST, calcola_alpha_S, calcola_periodi
- [x] spettro_elastico, spettro_progetto, calcola_S_d_T1, spettro_da_hazard_row
- [ ] profilo_spettrale_completo (TODO futuro)
- [x] Integrazione con spectrum_paste_service, O.1 (INGV)
- [x] Test: test_spettro_ntc2018.py (47 test)

### O.3 Azioni sismiche multinorma

**Stato**: COMPLETATO — commit d6e589a

- [x] Package per 7 norme, distribuzione taglio alla base, dispatcher
- [x] Test: test_azioni_sismiche_multinorma.py (54 test)

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase O sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
