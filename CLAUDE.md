# CLAUDE.md — Istruzioni per l'assistente AI

## FONTE DI VERITÀ

**PRIMA DI QUALSIASI OPERAZIONE**, leggi il file `docs/PIANO_LAVORO.md`.
Questo file è la **unica fonte di verità** sullo stato di avanzamento del progetto.

- Contiene l'elenco completo delle fasi (A→W), con stato ✅/TODO per ciascuna
- Ogni fase ha un sub-plan dettagliato con checkbox [x]/[ ]
- Ogni completamento è marcato con il commit di riferimento
- In caso di compattazione del contesto, **rileggi sempre** `docs/PIANO_LAVORO.md`

**Regola operativa**: dopo ogni fase completata, aggiorna `docs/PIANO_LAVORO.md` con:

1. Stato → COMPLETATO + hash commit
2. Checkbox [x] per ogni sotto-punto completato
3. Contatore test aggiornato
4. Riga nella tabella "GIÀ COMPLETATO"

---

## Panoramica progetto

RD2229 è un software Python per il calcolo strutturale di edifici esistenti in c.a., muratura e acciaio, secondo le normative italiane storiche e vigenti.

**Norme coperte**: RD 2229/1939, DM 30/05/1972, DM 20/11/1987 (muratura), Circ. 30/07/1981, DM 14/02/1992, DM 09/01/1996, OPCM 3274/2003, NTC 2008, NTC 2018 + Circ. n.7/2019.

**Lingua**: italiano per UI, commenti, docstring, nomi variabili del dominio.

---

## Convenzioni critiche

### Unità di misura

- **Unità primarie**: kg/cm² per tensioni, cm per geometria
- Modulo `src/materials/adapter.py` per conversioni kg/cm² ↔ MPa
- Il sistema unità è selezionabile dall'utente (`src/core/unita_misura.py`)

### Architettura (vincoli duri)

1. **Modularità estrema** — ogni modulo sostituibile senza refactoring globale
2. **Zero duplicazione** — archivi centralizzati, unica fonte per ogni parametro
3. **SOLO Qt (PySide6/PyQt6)** — legacy Tkinter deprecato, non usare mai Tkinter per codice nuovo
4. **Dropdown + input manuale** — sempre entrambi per campi con archivio
5. **Log pervasivo** — `src/core/registro_log.py` collegato a tutto
6. **Help contestuale** — stralci normativi, §, formule (`src/ui/qt/aiuto_contestuale.py`)
7. **Formule nei tabulati** — passaggi intermedi, risultati, riferimenti normativi
8. **Rigore scientifico** — formula mancante → TODO + chiedi all'utente, mai inventare
9. **UI in italiano** — tutto il testo visibile all'utente in italiano

### Lettere greche

Il progetto usa caratteri Unicode (σ, τ, γ, etc.) in docstring e documentazione.

---

## Struttura directory (aggiornata)

```
RD2229/
├── src/
│   ├── core/                 # Log, unità misura, registries
│   ├── materials/            # Material model, repo, validation, adapter, editor Qt
│   ├── sections/             # 12 tipi sezione + parametri torsionali
│   ├── combinations/         # Combinazioni di carico NTC2018
│   ├── methods/
│   │   └── rd2229/           # Torsione TA, Instabilità TA
│   ├── checks_ntc2018.py     # Verifiche NTC2018 (flessione, taglio, torsione, SLE, elem. sec.)
│   ├── checks_dm96.py        # Verifiche DM96
│   ├── fire/                 # Fuoco tabellare
│   ├── wind/                 # Vento NTC2018 completo
│   ├── report/               # Tabulati calcolo ASCII/HTML
│   └── ui/qt/                # GUI Qt (debug_viewer, material_editor, visualizzatore_sezione)
├── data/
│   └── materials/            # Cataloghi JSON per tutte le norme (97 materiali, 9 norme)
├── docs/
│   └── PIANO_LAVORO.md       # ⭐ FONTE DI VERITÀ — stato avanzamento progetto
├── tests/                    # ~1293 test pytest
└── config/                   # Configurazioni
```

---

## Come eseguire

```bash
# Test
python -m pytest tests/ -v

# Test singolo modulo
python -m pytest tests/test_torsione_rd2229.py -v

# Tutti i test con report
python -m pytest tests/ --tb=short
```

---

## Pattern di sviluppo

### Aggiungere un nuovo modulo di calcolo

1. Crea file in `src/methods/<norma>/` o in `src/`
2. Usa dataclass per Input e Risultato
3. Includi `passaggi_calcolo: list[str]` nel risultato per tracciabilità
4. Aggiungi `to_dict()` per serializzazione report
5. Crea test in `tests/test_<modulo>.py`
6. Aggiorna `docs/PIANO_LAVORO.md`

### Aggiungere un catalogo materiali

1. Crea `data/materials/catalogo_<norma>.json`
2. Segui lo schema esistente (vedi `catalogo_ntc2018.json`)
3. Aggiungi test in `tests/test_cataloghi_materiali.py`
4. Aggiorna contatore in `docs/PIANO_LAVORO.md`

---

## Dipendenze principali

- pytest, PySide6/PyQt6, numpy, scipy (sparse), pyyaml
- NO pandas per codice nuovo (usare JSON/dict nativi)
