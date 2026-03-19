# Material Editor — Progettazione e Architettura

**Data**: 19 Marzo 2026  
**Versione**: 1.0  
**Status**: In implementazione

---

## 1. Panoramica

L'**Editor Materiali** è un'interfaccia grafica PySide6 per la gestione dinamica dei parametri meccanici dei materiali strutturali (calcestruzzo, acciaio, legno, muratura) secondo le varie normative implementate in RD2229 (RD2229, DM72, DM87, DM92, DM96, Circ81, OPCM3274, NTC2008, NTC2018, Eurocode).

### Obiettivi
- Caricamento automatico di cataloghi materiali da JSON
- Interfaccia dinamica: colonne e campi adattabili ai parametri specifici di ogni materiale
- Editing in-place con calcolo automatico e flag di override manuale per ogni parametro
- Filtro per tipologia/famiglia (Calcestruzzi, Acciai, Legno, Muratura, ecc.) tramite schede (tabs)
- Esportazione in HTML/Markdown

---

## 2. Architettura dei File

### Albero file

```
src/ui/qt/material_editor/
├── material_editor_main.py          # Entry point, window principale, istanzia tabs e controller
├── controller.py                    # MaterialEditorController: orchestrazione logica
├── logic/
│   ├── material_repository.py       # MaterialRepository: caricamento cataloghi + CRUD
│   ├── material_export_logic.py     # Logica esportazione (HTML/MD/CSV)
│   └── material_validation_logic.py # Validazione parametri
└── widgets/
    ├── material_table_widget.py     # MaterialTableWidget: QTableView ordinabile
    ├── material_table_model.py      # MaterialTableModel: QAbstractTableModel dinamico
    ├── material_detail_frame.py     # MaterialDetailFrame: frame laterale editing dinamico
    └── material_export_widget.py    # MaterialExportWidget: combo formato + text area

data/materials/
├── catalogo_ntc2018.json            # ~30 materiali NTC2018
├── catalogo_dm96.json               # ~20 materiali DM96
├── catalogo_dm92.json               # ~15 materiali DM92
├── catalogo_legno.json              # ~10 materiali legno
├── catalogo_circ81_muratura.json    # ~15 murature Circ81
├── catalogo_dm72.json               # ~7 materiali DM72
├── catalogo_dm87_muratura.json      # ~5 murature DM87
└── ... (altri cataloghi)            # ~97 materiali totali
```

---

## 3. Flusso di Caricamento e Dipendenze

```
material_editor_main.py (entry point)
│
├─→ Crea 6 tabs (una per famiglia: Calcestruzzi, Acciai, Legno, Muratura, Compositi, Terreni)
│
└─→ (Per ogni tab)
    ├─→ MaterialEditorController(famiglia="calcestruzzo")
    │   │
    │   ├─→ MaterialRepository() nel __init__
    │   │   │
    │   │   └─→ __init__():
    │   │       └─→ Carica tutti i cataloghi da data/materials/*.json (97 materiali)
    │   │
    │   ├─→ attach_table(table):
    │   │   ├─→ Filtra materiali per famiglia: materials = [m for m in repo.materials if m["famiglia"] == famiglia]
    │   │   ├─→ Crea MaterialTableModel(repo.materials filtrati)
    │   │   │   └─→ _rebuild_columns(): unione di tutte le chiavi dei materiali
    │   │   ├─→ table.setModel(model)
    │   │   ├─→ model.refresh()
    │   │   └─→ Seleziona automaticamente la riga 0
    │   │
    │   ├─→ attach_detail(detail_frame):
    │   │   └─→ Collega i bottoni Save/Cancel
    │   │
    │   └─→ attach_export(export_widget):
    │       └─→ Collega combo formato + bottone Copia
    │
    ├─→ MaterialTableWidget (tabella ordinabile)
    │   └─→ Mostra una riga per materiale
    │       └─→ Quando selezionata → populate_detail_from_index()
    │
    ├─→ MaterialDetailFrame (frame laterale dinamico)
    │   ├─→ set_fields(material_dict):
    │   │   └─→ Crea dinamicamente QLineEdit + QCheckBox (override) per ogni chiave del materiale
    │   │
    │   └─→ Mostra tutti i parametri del materiale selezionato
    │       ├─→ material_id, descrizione, famiglia, norma_riferimento
    │       ├─→ densita_kg_m3, f_ck, sigma_c28, f_yk, f_k, f_vk0, ecc. (specifici per famiglia)
    │       └─→ Ogni campo + checkbox "Override manuale [nome_campo]"
    │
    └─→ MaterialExportWidget
        ├─→ Combo formato (HTML/Markdown/CSV/Testo)
        └─→ QTextEdit mostra anteprima esportazione
```

---

## 4. Classi Principali e Responsabilità

### 4.1 `MaterialRepository`

**File**: `src/ui/qt/material_editor/logic/material_repository.py`

**Responsabilità**:
- Caricamento automatico cataloghi da `data/materials/*.json` nel `__init__`
- CRUD: `add_material()`, `update_material()`, `delete_material()`
- Filtri: `filter_materials(filters_dict)`
- Ordinamento: `sort_materials(key, reverse)`
- Undo/redo: `undo()`, `redo()` con stack interno
- Audit log: `_log_audit(action, data)`
- Esportazione: `export_material(idx, fmt)` (HTML/MD/CSV/TXT)

**Dati**:
- `self.materials`: list[dict] — 97 materiali totali caricati
- `self.audit_log`: list[dict] — traccia di tutte le operazioni
- `self._undo_stack`, `self._redo_stack` — per undo/redo

---

### 4.2 `MaterialEditorController`

**File**: `src/ui/qt/material_editor/controller.py`

**Responsabilità**:
- Orchestrazione della logica: collega repository, tabella, frame laterale, export
- Filtraggio per famiglia: quando `attach_table()` viene chiamato, filtra i materiali
- Selezione: automaticamente seleziona il primo materiale (riga 0)
- Notifiche: quando cambia selezione nella tabella, popola il frame laterale dinamicamente
- Salvataggio: `on_save_clicked()` raccoglie dati dal frame e aggiorna il repository

**Metodi pubblici**:
- `__init__(repository=None, famiglia=None)` — input: famiglia (es. "calcestruzzo")
- `attach_table(table)` — collega la tabella, filtra, seleziona riga 0
- `attach_detail(detail_frame)` — collega frame laterale
- `attach_export(export_widget)` — collega export widget
- `populate_detail_from_index(idx: int)` — riempie il frame con i parametri del materiale all'indice idx

---

### 4.3 `MaterialTableModel`

**File**: `src/ui/qt/material_editor/widgets/material_table_model.py`

**Responsabilità**:
- Modello dati per la tabella (QAbstractTableModel)
- Colonne dinamiche: unione di tutte le chiavi presenti nei materiali caricati
- Sorting supportato (cliccando le intestazioni colonna)
- Validazione visuale: righe incomplet griallo highlights light yellow

**Attributi**:
- `self._columns`: list[str] — ordinamento deterministico delle colonne (material_id, descrizione, norma, famiglia, ..., resto alfabetico)

---

### 4.4 `MaterialTableWidget`

**File**: `src/ui/qt/material_editor/widgets/material_table_widget.py`

**Responsabilità**:
- Visualizzazione tabella ordinabile con drag&drop
- Context menu per batch edits su colonne selezionate
- Signals: `batchEditRequested(col_index, row_list)`

---

### 4.5 `MaterialDetailFrame`

**File**: `src/ui/qt/material_editor/widgets/material_detail_frame.py`

**Responsabilità**:
- Frame dinamico che genera widget editabili a runtime
- Per ogni materiale selezionato, crea:
  - QLineEdit per ogni parametro (material_id, descrizione, f_ck, gamma_c, ecc.)
  - QCheckBox "Override manuale [parametro]" per ogni campo calcolato
- Metodi:
  - `set_fields(material_dict)`: ricrea dinamicamente i widget in base ai parametri del materiale
  - `get_field_values()` → dict colonnati
  - `get_overrides()` → dict booleani (quali campi sono in override)

---

### 4.6 `MaterialExportWidget`

**File**: `src/ui/qt/material_editor/widgets/material_export_widget.py`

**Responsabilità**:
- Combo per scelta formato (HTML, Markdown, CSV, Testo semplice)
- QTextEdit con anteprima esportazione del materiale selezionato
- Bottone "Copia" per copiare negli appunti
- Persist format preference in QSettings

---

## 5. Diagramma di Interazione

```
┌─────────────────────────────────────────────────────────────────┐
│ Material Editor Main Window                                     │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ Tab "Calcestruzzi" ──┬─→ MaterialEditorController(famiglia="calcestruzzo")
         │                       │
         │                       ├─→ MaterialRepository (97 materiali)
         │                       │   └─ Filtra a 48 calcestruzzi
         │                       │
         │                       ├─→ MaterialTableWidget (70%)
         │                       │   └─ MaterialTableModel
         │                       │       └─ 48 righe, colonne dinamiche
         │                       │
         │                       └─→ Side Panel (30%)
         │                           ├─ MaterialDetailFrame (dinamico)
         │                           │  └─ set_fields() → crea QLineEdit + QCheckBox per ogni parametro
         │                           │
         │                           └─ MaterialExportWidget
         │                               └─ Mostra anteprima HTML/MD/CSV
         │
         ├─ Tab "Acciai" ────┬─→ MaterialEditorController(famiglia="acciaio")
         │                   └─ ... (stesso pattern)
         │
         ├─ Tab "Legno" ─────┬─→ MaterialEditorController(famiglia="legno")
         │                   └─ ... (stesso pattern)
         │
         ├─ Tab "Muratura" ──┬─→ MaterialEditorController(famiglia="muratura")
         │                   └─ ... (stesso pattern)
         │
         ├─ ... (altri tabs)
```

---

## 6. Flusso di Editing e Salvataggio

### Caso: Utente seleziona "C25/30" e modifica f_ck

1. **Utente clicca riga "C25/30" nella tabella**
   ```
   MaterialTableWidget → QItemSelectionModel.selectionChanged
   → Controller._on_table_selection_changed(selected, deselected)
   → Controller.populate_detail_from_index(0)  # riga 0 per esempio
   ```

2. **Controller popola il frame laterale**
   ```
   MaterialDetailFrame.set_fields({"material_id": "cls_C25/30", "f_ck": 254.9, "gamma_c": 1.5, ...})
   → Distrugge vecchi widget
   → Crea per ogni chiave:
      - QLabel("f_ck:")
      - QLineEdit (testo = "254.9")
      - QCheckBox("Override manuale f_ck")
      - (ripeti per tutti i parametri)
   ```

3. **Utente modifica il valore di f_ck (es. 260.0) e spunta "Override manuale f_ck"**

4. **Utente clicca "Salva"**
   ```
   MaterialDetailFrame.save_button.clicked
   → Controller.on_save_clicked()
   → Raccogli dati:
      data = frame.get_field_values()  # {"f_ck": "260.0", ...}
      overrides = frame.get_overrides()  # {"f_ck": True, ...}
   → Repository.update_material(idx, data)
   ```

5. **Tabella si aggiorna (solo se richiesto)**
   ```
   MaterialTableModel.refresh()
   → Emit layoutChanged signal
   → QTableView si ripinge
   ```

---

## 7. Parametri Specifici per Famiglia

### Calcestruzzo (familia="calcestruzzo")

Parametri comuni (NTC2018):
- `material_id`, `descrizione`, `famiglia`, `norma_riferimento`
- `densita_kg_m3`
- **f_ck** (resistenza caratteristica, calcolato da classe es. C25/30 → f_ck=25 MPa)
- **gamma_c** (coefficiente parziale del calcestruzzo, default 1.5)
- `alpha_cc`, `E`, `nu`, `note`

Parametri DM72/DM92 (scuola italiana antica):
- `sigma_c28` (resistenza a compressione a 28 giorni in kg/cm²)
- `sigma_c_adm` (ammissibile)
- `tau_c0_adm`, `tau_c1_adm` (ammissibili a torsione)
- `n_omogenizzazione` (coefficiente di omogeneizzazione ES: 10)

### Acciaio (famiglia="acciaio")

Parametri NTC2018/EC2:
- `material_id`, `descrizione`, `famiglia`, `norma_riferimento`
- `densita_kg_m3` (7850 kg/m³)
- **f_yk** (resistenza caratteristica a snervamento: 450, 500 MPa)
- **gamma_s** (coefficiente parziale acciaio, default 1.15)
- `E` (modulo elastico: 210000 MPa)
- `nu` (Poisson: 0.30)

### Legno (famiglia="legno")

Parametri EN 14080:
- `material_id`, `descrizione` (es. "GL24h")
- `densita_kg_m3` (~400-600)
- **f_m,k** (resistenza a flessione caratteristica)
- **f_c,0,k** (resistenza compressione parallela alle fibre)
- **f c,90,k**, **f t,0,k**, **f t,90,k** (altre resistenze)
- **gamma_M** (coefficiente di sicurezza materialeMateriale)
- `E_{0,mean}`, `E_{90,mean}` (moduli elastici)

### Muratura (famiglia="muratura")

Parametri NTC2018/Circ81:
- `material_id`, `descrizione` (es. "Mattoni pieni malta M10")
- `densita_kg_m3`
- **f_k** (resistenza caratteristica compressione verticale)
- **f_vk0** (resistenza taglio a compressione zero)
- **gamma_M** (coefficiente di sicurezza, NTC2018: 2.0; Circ81 senza prove: 5.0)
- `E` (modulo elastico)
- `G` (modulo taglio)

---

## 8. Cataloghi Materiali (data/materials/)

| File | Norma | Famiglia | Materiali | Note |
|------|-------|----------|-----------|------|
| `catalogo_ntc2018.json` | NTC2018 | tutte | 30 | Standard attuale |
| `catalogo_dm96.json` | DM96 | c.a. | 20 | Precedente versione |
| `catalogo_dm92.json` | DM92 | c.a. | 15 | Precedente |
| `catalogo_dm72.json` | DM72 | c.a. | 7 | Scuola italiana |
| `catalogo_circ81_muratura.json` | Circ81 | muratura | 15 | Circolare MIT |
| `catalogo_dm87_muratura.json` | DM87 | muratura | 5 | DM specializzato |
| `catalogo_legno.json` | EN 14080 | legno | 10 | Eurocode legno |
| `catalogo_opcm3274.json` | OPCM3274 | c.a. | ~ | OPCM sismica |
| `catalogo_ntc2008.json` | NTC2008 | tutte | ~ | Precedente NTC |
| **TOTALE** | — | — | **97** | Caricati all'avvio |

---

## 9. Logica di Calcolo Automatico (TODO)

**Attualmente**: i parametri vengono letti e salvati così come sono.

**In futuro**, implementare logica di calcolo automatico:

1. **Per Calcestruzzo**: dato la classe (es. "C25/30"), calcolare automaticamente f_ck
   ```python
   if "C25" in material_id:
       f_ck_auto = 25.0  # MPa
       # Convertire in kg/cm²: 25 * 10.197 = 254.9
   ```

2. **Per Acciaio**: f_yk da diametro e classe
3. **Per Muratura**: f_k da f_mb (resistenza laterizio) e f_m (malta)
4. **Per Legno**: verifiche derivate da resistenze base (classe C, D, ecc.)

**Flag Override**: se utente spunta "Override manuale f_ck", il valore inserito manualmente non viene sovrascritto dai calcoli automatici.

---

## 10. Validazione (material_validation_logic.py)

```python
def validate(material_dict) -> dict:
    return {
        "is_complete": bool,     # tutti i campi obbligatori presenti?
        "missing": list[str],    # campi mancanti
        "warnings": list[str],   # avvisi non bloccanti
    }
```

**Validazioni per Calcestruzzo**:
- Obbligatori: material_id, descrizione, famiglia, norma_riferimento, f_ck, gamma_c
- Avvisi: f_ck < 12 MPa?, f_ck > 100 MPa? (out of range)

**Visualizzazione**: righe incomplet nella tabella evidenziate in giallo (light yellow background)

---

## 11. Esportazione (material_export_logic.py)

```python
def export(material_dict, format_str) -> str:
    if format_str == "HTML":
        return "<table>...</table>"
    elif format_str == "Markdown":
        return "| Key | Value |\n| --- | --- |\n..."
    elif format_str == "CSV":
        return "key1,key2,key3\nval1,val2,val3"
    else:
        return "key1: val1\nkey2: val2\n..."
```

---

## 12. Status Implementazione

| Componente | Status | Note |
|------------|--------|------|
| Repository caricamento | ✅ DONE | 97 materiali caricati da cataloghi JSON |
| Filtro per famiglia | ✅ DONE | Funzionante per tutte le 6 famiglia |
| Tabella dinamica | ✅ DONE | Colonne dinamiche unione di tutti i parametri |
| Frame laterale dinamico | ✅ TODO | Da testare completamente |
| Selezione automatica riga 0 | ✅ DONE | Implementata nel controller |
| CRUD (save/delete/edit) | ⚠️ PARTIAL | Save OK, delete/batch edit in sospeso |
| Validazione | ✅ BASIC | Implemented, da ampliare |
| Esportazione HTML/MD | ✅ DONE | Logica presente |
| Undo/Redo | ✅ DONE | Stack nel repository |
| Calcolo automatico parametri | ❌ TODO | Richiede revisione per ogni famiglia |
| Override manuale | ✅ DONE | Flag checkbox presente nel frame |

---

## 13. Prossimi Passi

1. ✅ Verificare visibilità della tabella e frame laterale in UI
2. ✅ Testare selezione e popolo dinamico del frame
3. ⚠️ Implementare calcoli automatici per ogni famiglia
4. ⚠️ Aggiungere validazione più robusta
5. ⚠️ Batch editing con context menu
6. ⚠️ Persistenza (save/load da file JSON)

---

## 14. Note Architetturali

- **Nessun Tkinter**: solo PySide6, come da vincoli del progetto
- **Modularità**: ogni widget è indipendente. Controller orchestra.
- **Dinamisimo**: tabella e frame si adattano ai dati senza hardcoding.
- **Audit log**: tutte le operazioni sono tracciate nel repository.
- **Reversibilità**: undo/redo implementati per tutte le operazioni CRUD.

---

**Fine Documento**
