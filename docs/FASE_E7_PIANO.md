# FASE E.7 — Muratura Multipiano: Piano Dettagliato

## Decisioni dell'utente

1. **Carichi verticali**: aree di influenza geometriche (metà luce tra maschi)
2. **Input solaio**: per parete (G1, G2, Q, luce_sx, luce_dx)
3. **Combinazioni**: NTC2018 §2.5.3 SLU + personalizzabili (attivabili/disattivabili, modificabili, eliminabili, ripristino default)
4. **Output**: doppio — tabella sintetica per piano + tabella dettagliata per maschio
5. **Eccentricità fuori piano**: tutte e 4 (geometrica snellezza, da carico solaio, accidentale NTC2018, da vento/sisma)
6. **Struttura**: 3 file ≤300 righe ciascuno

## Architettura 3 file

### File 1: `carichi_verticali.py` (~280 righe)

Modello carichi e distribuzione sui maschi.

- `CaricoSolaio` dataclass: G1, G2, Q, luce_sx, luce_dx, id_parete, id_piano
- `CaricoParete` dataclass: carichi da solaio sx/dx su una parete
- `calcola_area_influenza()`: metà luce tra maschi adiacenti × profondità solaio
- `distribuisci_carichi_solaio()`: da CaricoSolaio a N per maschio
- `calcola_N_multipiano()`: accumulo top-down realistico (peso proprio + solaio + sovrastante)
  - Sostituisce/migliora `calcola_N_gravitazionale()` di discretizzazione.py

### File 2: `combinazioni_muratura.py` (~250 righe)

Combinazioni di carico personalizzabili.

- `CombinazioneCarico` dataclass: nome, gamma_G1, gamma_G2, gamma_Q, psi_0, attiva, predefinita
- `COMBINAZIONI_DEFAULT_NTC2018`: SLU fondamentale, SLE rara/frequente/quasi-perm
- `GestoreCombinazioni` class:
  - `genera_default()`: crea combinazioni NTC2018 §2.5.3
  - `aggiungi()`, `modifica()`, `elimina()`: CRUD
  - `attiva()`, `disattiva()`: toggle senza eliminare
  - `ripristina_default()`: reset a NTC2018
  - `combinazioni_attive()`: lista solo quelle attive
  - `calcola_N_combinato()`: N_Ed = γ_G1×G1 + γ_G2×G2 + γ_Q×ψ₀×Q

### File 3: `verifiche_multipiano.py` (~300 righe)

Verifica compressione + fuori piano, piano per piano.

- `Eccentricita` dataclass: e_geom, e_carico, e_accidentale, e_vento, e_totale
- `calcola_eccentricita()`: somma tutte le fonti
  - e_geom = da snellezza (tabella Φ, NTC2018 §4.5.6.2)
  - e_carico = da posizione appoggio solaio
  - e_accidentale = max(h_eff/200, 2 cm) per NTC2018
  - e_vento = M_vento / N
- `RigaVerificaPiano`: N_Ed, σ_0, Φ, N_Rd, D/C, esito (sintetica)
- `RigaVerificaMaschio`: tutti i dettagli (N, σ, e/t, λ, Φ, fd, D/C, esito)
- `TabellaVerificheMultipiano`: tabelle per piano + per maschio
- `verifica_multipiano()`: ciclo dall'alto al basso, verifica ogni maschio
- `formato_testo()`: output ASCII stile tabulato commerciale

## Riferimenti normativi

- NTC2018 §4.5.6 — Resistenza a compressione muratura
- NTC2018 §4.5.6.2 — Eccentricità e snellezza
- NTC2018 Tab. 4.5.V — Coefficiente Φ
- NTC2018 §2.5.3 — Combinazioni di carico
- NTC2018 §7.8.1.5.2 — Carichi verticali analisi sismica
- Circolare n.7/2019 §C4.5.6.2 — Eccentricità di calcolo

## Sotto-fasi incrementali

1. Block 1: `carichi_verticali.py` + test (~30 test)
2. Block 2: `combinazioni_muratura.py` + test (~25 test)
3. Block 3: `verifiche_multipiano.py` + test (~30 test)
4. Aggiornamento PIANO_LAVORO.md, commit, push
