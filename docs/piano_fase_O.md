# Fase O — Griglia sismica INGV + Spettro NTC2018

## Stato: COMPLETATO ✅ — commit: (corrente) — 2026-03-09

## Subfasi, checklist e storico

### O.1 Import dati pericolosità sismica INGV

**Stato**: COMPLETATO — 2026-03-09

- [x] Import da webservice INGV (lat, lon -> ag, F0, TC*)
- [x] Tabella locale griglia INGV (fallback offline, CSV)
- [x] Funzione unificata con routing webservice/CSV
- [x] File CSV griglia INGV NTC2018 Allegato B — `data/seismic/griglia_ingv.csv` (spettri2008.csv)
- [x] Import parametri da EdiLus-MS
- [x] Validazione e normalizzazione formato output

**Note tecniche O.1**:
- Griglia irregolare ~10.751 punti (non regolare 0.05deg)
- ag in CSV: [m/s^2] — conversione automatica: ag_g = T{TR}ag / 9.81
- Interpolazione spaziale: nearest-neighbor (griglia irregolare)
- Interpolazione TR: log-lineare (NTC2018 §3.2.1) tra TR disponibili [30,50,72,101,140,201,475,975,2475]

### O.2 Modulo spettro NTC2018

**Stato**: COMPLETATO — 2026-03-09

- [x] Enum CategoriaSuolo, CategoriaTopografica, ClasseUso
- [x] calcola_VR, calcola_CC, calcola_SS, calcola_ST, calcola_alpha_S, calcola_periodi
- [x] spettro_elastico, spettro_progetto, calcola_S_d_T1, spettro_da_hazard_row
- [x] profilo_spettrale_completo() — curva completa Sa(T) per T in [0, T_max], 4 rami, punti esatti su TB/TC/TD
- [x] Integrazione con spectrum_paste_service, O.1 (INGV)
- [x] Test: test_spettro_ntc2018.py (47 test) + test_ingv_hazard_csv.py (38 test)

### O.3 Azioni sismiche multinorma

**Stato**: COMPLETATO — commit d6e589a

- [x] Package per 7 norme, distribuzione taglio alla base, dispatcher
- [x] Test: test_azioni_sismiche_multinorma.py (54 test)

---

## Storicizzazione domande/risposte e decisioni

### Sessione 2026-03-09

| Q | Domanda | Risposta | Decisione |
|---|---------|----------|-----------|
| Q-O1 | CSV griglia INGV | A — file fornito (spettri2008.csv) | Copiato in data/seismic/griglia_ingv.csv |
| Q-O2 | profilo_spettrale_completo() | A — implementa subito tutti i branch | Implementato con numpy linspace + punti speciali TB/TC/TD |
| Q-O3 | Aggiornamento documentazione | B — PIANO_LAVORO.md + PIANO_SVILUPPO_CORRENTE.md | Aggiornati entrambi |

---

## Note storiche/archivio (appendice)

### Formato CSV spettri2008.csv

- Riga 1: super-header (`,,,,,"TR = 30",...`) — saltata automaticamente
- Riga 2: nomi colonne (`OBJECTID, ID, LON, LAT, T30ag, T30F0, T30Tc, ...`)
- ag in [m/s^2]: verificato su punti noti (Norcia 0.261g, Calabria 0.268g, Sardegna 0.041g a TR=475)
- La griglia NON e' regolare 0.05deg x 0.05deg — lat/lon sono coordinate WGS84 di una mesh irregolare
