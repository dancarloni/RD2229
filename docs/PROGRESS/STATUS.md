# RD2229 — Stato Avanzamento Globale

Ultimo aggiornamento: 2026-03-05

## Tabella Globale

| FASE | Descrizione | Stato | % | Ultima modifica | Note |
|------|-------------|-------|---|-----------------|------|
| INFRA | Infrastruttura trasversale | ⚠️ In corso | 80% | 2026-03-05 | Debug log, help, sezione, tabulati, unità |
| A | Modello materiale + Editor Qt | ❌ Da fare | 0% | — | Parametri derivati, Qt editor |
| B | Torsione | ❌ Da fare | 0% | — | VB + ricerca online |
| C | Instabilità | ❌ Da fare | 0% | — | ω method + NTC2018 |
| D | Fessurazione (multi-norm) | ❌ Da fare | 0% | — | NTC2018, DM92, DM96, EC2 |
| E | Deformazioni (multi-norm) | ❌ Da fare | 0% | — | Limiti editabili |
| F | Muratura + cordoli metallici | ❌ Da fare | 0% | — | F1÷F7 + cerchiature |
| G | Normative aggiuntive | ❌ Da fare | 0% | — | DM92, DM96, NTC2008, EC |
| H | Elementi secondari + fuoco | ❌ Da fare | 0% | — | |
| I | Cross-Pozzati | ❌ Da fare | 0% | — | Con snap e coordinate nodi |
| J | FEM beam 2D | ❌ Da fare | 0% | — | scipy sparse |
| K | FEM sismico (pred.) | ❌ Da fare | 0% | — | Solo interfacce |
| L | Telai 3D (pred.) | ❌ Da fare | 0% | — | Solo interfacce |
| M | Report/relazione | ❌ Da fare | 0% | — | Template completa |
| N | Edifici esistenti | ❌ Da fare | 0% | — | LC/FC, ζ_E |
| O | Testing/validazione | ❌ Da fare | 0% | — | Santarella/Giangreco |
| P | OCR manuali | ❌ Da fare | 0% | — | Tesseract + pix2tex |
| R | Sezioni parametri statici | ❌ Da fare | 0% | — | 10 tipi sezione |
| S | Pressoflessione retta/dev. | ❌ Da fare | 0% | — | NTC2018 + RD2229 |
| T | Taglio senza armatura | ❌ Da fare | 0% | — | + cls non armato |
| U | Grafici sollecitazioni | ❌ Da fare | 0% | — | M/V/N, inviluppi, N-M |
| V | Solai | ❌ Da fare | 0% | — | Laterocemento, alveolare |
| W | Scale | ❌ Da fare | 0% | — | Rampa, pianerottolo |
| X | Fondazioni + geotecnica | ❌ Da fare | 0% | — | 6 normative × 14 verifiche |
| X-BIS | Carote cls in sito | ❌ Da fare | 0% | — | 9 formulazioni |
| X-TER | Indagini in situ | ❌ Da fare | 0% | — | Sclerometro, SonReb, pull-out, martinetti |
| X-QUAT | Durabilità/copriferro | ❌ Da fare | 0% | — | Carbonatazione, cloruri |
| X-QUINT | Modulo carichi | ❌ Da fare | 0% | — | Archivio pesi + combinazioni |
| X-SEX | Connessioni acciaio | ❌ Da fare | 0% | — | Struttura base |
| X-SEPT | SismaBonus (pred.) | ❌ Da fare | 0% | — | Solo interfaccia |
| X-OCT | Relazione template | ❌ Da fare | 0% | — | Capitoli standard |
| X-NOV | Versionamento progetti | ❌ Da fare | 0% | — | Cronologia salvataggi |
| Y | Sismica dettagliata | ❌ Da fare | 0% | — | Y0÷Y5 |
| Z | Sviluppi futuri | 📋 Pianificato | 0% | — | Pushover, time-history |

## File Creati/Modificati — Sessione Corrente (2026-03-05)

### Nuovi file

- `src/core/registro_log.py` — Registro log centralizzato (RegistroLog, VoceLog, LivelloLog)
- `src/core/unita_misura.py` — Sistema unità di misura selezionabile (kg-cm / kN-m / N-mm)
- `src/ui/qt/aiuto_contestuale.py` — Aiuto contestuale dinamico Qt6 (caricamento YAML)
- `src/ui/qt/visualizzatore_sezione.py` — Rendering sezione strutturale (zone tese/compresse, asse neutro, armatura)
- `src/report/tabulati_calcolo.py` — Tabulati di calcolo (input → formule → passaggi → risultato)
- `docs/help/flessione_ntc2018.yaml` — Esempio file help per verifica flessione NTC2018
- `docs/PROGRESS/STATUS.md` — Questo file

### File modificati

- `src/ui/qt/debug_viewer.py` — Aggiornato con filtri, ricerca, export, collegamento a registro_log

## TODO Immediati (prossima sessione)

1. Aggiornare `src/ui/qt/__init__.py` con nuovi moduli
2. Commit e push su branch `claude/materials-database-structure-Fh726`
3. Iniziare FASE A: material_model.py con parametri derivati + editor Qt
4. Installare poppler-utils per leggere PDF CNR-DT

## Blocchi / Dipendenze

- poppler-utils non installato → non posso leggere PDF CNR-DT e riferimenti tecnici muratura
- PyYAML: verificare se installato (necessario per aiuto contestuale)
- PySide6/PyQt6: verificare disponibilità per test GUI
