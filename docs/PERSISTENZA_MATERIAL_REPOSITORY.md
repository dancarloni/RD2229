# Persistenza MaterialRepository

## Descrizione

Il `MaterialRepository` ora supporta la **persistenza automatica** su file JSON, proprio come il `SectionRepository`. Tutti i materiali creati, modificati o eliminati vengono salvati automaticamente in un file locale e ripristinati al successivo avvio del programma.

## Caratteristiche

✅ **Salvataggio automatico**: Ad ogni operazione (`add()`, `update()`, `delete()`, `clear()`), il repository salva tutti i materiali su file JSON.

✅ **Caricamento automatico**: All'inizializzazione, il repository carica tutti i materiali dal file JSON se esiste.

✅ **Persistenza completa**: Tutte le proprietà dei materiali vengono salvate e ripristinate.

✅ **Compatibilità completa**: Il codice esistente continua a funzionare senza modifiche (il parametro `json_file` è opzionale).

✅ **Gestione degli errori**: Se il file JSON non esiste, il repository parte vuoto. Se il file è corrotto, registra un errore ma continua a funzionare.

## Utilizzo

### Uso predefinito (file "materials.json" nella cartella corrente)

```python
from core_models.materials import Material, MaterialRepository

# Crea/carica repository (usa "materials.json" per default)
repo = MaterialRepository()

# Aggiungi un materiale (salva automaticamente)
material = Material(name="C25/30", type="concrete", properties={"fck": 25})
repo.add(material)

# Modifica un materiale (salva automaticamente)
material_modified = Material(
    id=material.id,
    name="C25/30",
    type="concrete",
    properties={"fck": 25, "gamma_c": 1.5}
)
repo.update(material.id, material_modified)

# Elimina un materiale (salva automaticamente)
repo.delete(material.id)

# Trova materiale per nome
found = repo.find_by_name("C25/30")

# Trova materiale per ID
found_by_id = repo.find_by_id(material.id)

# Ottieni tutti i materiali
all_materials = repo.get_all()
```

### Uso con percorso personalizzato

```python
# Specifica una directory personalizzata
repo = MaterialRepository(json_file="/path/to/my_materials.json")
```

### Uso con directory relativa

```python
# Nella directory dell'applicazione
repo = MaterialRepository(json_file="data/materials.json")
```

## Struttura JSON salvato

Il file JSON contiene un array di materiali con tutte le loro proprietà:

```json
[
  {
    "id": "70bd9464-...",
    "name": "C25/30",
    "type": "concrete",
    "properties": {
      "fck": 25,
      "gamma_c": 1.5,
      "fcd": 16.7,
      "fctm": 2.6,
      "Ec": 31000
    }
  },
  {
    "id": "a1234567-...",
    "name": "B500B",
    "type": "steel",
    "properties": {
      "fyk": 500,
      "gamma_s": 1.15,
      "Es": 200000
    }
  },
  ...
]
```

## Modifiche al Codice

### File modificato: `core_models/materials.py`

**Aggiunte:**
- Import: `json`, `logging`, `os`
- Attributo di classe `DEFAULT_JSON_FILE = "materials.json"`
- Attributo di istanza `_json_file`
- Metodo `to_dict()` nella classe `Material`
- Metodo statico `from_dict()` nella classe `Material`
- Metodo `load_from_file()`
- Metodo `save_to_file()`
- Metodo `find_by_id()`
- Metodo `update()`
- Metodo `delete()`
- Metodo `clear()`

**Modificato:**
- `__init__()`: Aggiunto caricamento automatico da file JSON
- `add()`: Aggiunto salvataggio automatico
- Tutti i metodi di modifica salvano automaticamente

### API

#### `__init__(json_file: str = "materials.json")`

Inizializza il repository e carica i materiali dal file JSON se esiste.

#### `load_from_file() -> None`

Carica tutti i materiali dal file JSON.

#### `save_to_file() -> None`

Salva tutti i materiali nel file JSON.

#### `add(mat: Material) -> None`

Aggiunge un materiale e salva automaticamente.

#### `update(material_id: str, updated_material: Material) -> None`

Aggiorna un materiale e salva automaticamente.

#### `delete(material_id: str) -> None`

Elimina un materiale e salva automaticamente.

#### `clear() -> None`

Elimina tutti i materiali e salva automaticamente.

#### `find_by_name(name: str) -> Optional[Material]`

Cerca un materiale per nome.

#### `find_by_id(material_id: str) -> Optional[Material]`

Cerca un materiale per ID.

#### `get_all() -> List[Material]`

Ottiene tutti i materiali.

## Comportamento

### All'avvio del programma
1. Se `materials.json` non esiste → Repository vuoto
2. Se `materials.json` esiste → Carica automaticamente tutti i materiali

### Ad ogni operazione
- `add()` → Salva automaticamente
- `update()` → Salva automaticamente
- `delete()` → Salva automaticamente
- `clear()` → Salva automaticamente (file vuoto)

### Nessuna perdita di dati
- Se il programma si arresta → I materiali rimangono nel JSON
- Se il programma si riavvia → I materiali vengono ripristinati automaticamente

## Logging

Il repository registra tutte le operazioni di persistenza a livello DEBUG:

```
DEBUG: Materiale aggiunto: uuid (C25/30)
DEBUG: Materiale aggiornato: uuid (C25/30)
DEBUG: Materiale eliminato: uuid (C25/30)
DEBUG: Salvati 3 materiali in materials.json
INFO: Caricati 3 materiali da materials.json
```

## Compatibilità

✅ **Completamente retro-compatibile**: Il codice esistente continua a funzionare.

```python
# Codice vecchio (continua a funzionare)
repo = MaterialRepository()  # Usa default "materials.json"

# Codice nuovo (opzionale)
repo = MaterialRepository(json_file="my_custom_materials.json")
```

## Test

### Test Unitari
- ✅ `test_material_persistence_basic()` - Creazione, salvataggio, caricamento
- ✅ `test_material_persistence_update_delete()` - Modifica e eliminazione
- ✅ `test_empty_repository()` - Repository vuoto
- ✅ `test_find_by_id()` - Ricerca per ID

**Esecuzione**:
```bash
python test_material_persistence.py
```

### Demo Pratica
```bash
python demo_material_persistence.py
```

## Differenze rispetto a SectionRepository

Il `MaterialRepository` segue lo stesso pattern del `SectionRepository`, ma con alcune differenze:

| Aspetto | SectionRepository | MaterialRepository |
|---------|-------------------|-------------------|
| File default | `sections.json` | `materials.json` |
| Classe principale | `Section` | `Material` |
| Identificazione univoca | UUID | UUID |
| Chiave logica | `logical_key()` | Nome (non esplicitamente) |
| Metodi CRUD | add, update, delete | add, update, delete |
| Ricerca | find_by_id, get_all | find_by_id, find_by_name, get_all |
| Serializzazione | to_dict() | to_dict() + from_dict() |

## Note di Implementazione

- **UUID**: Ogni materiale mantiene il suo UUID originale nel file JSON
- **Proprietà**: Le proprietà sono salvate come dizionario e ripristinate completamente
- **Non-modificato**: Il modello `Material` è stato leggermente esteso con metodi di serializzazione
- **Transazione**: Ogni operazione di salvataggio è atomica (scrive tutto o nulla)
- **Directory**: La directory viene creata automaticamente se non esiste

## Prossimi Passi (Opzionali)

- [ ] Aggiungere crittografia al file JSON
- [ ] Implementare backup automatico
- [ ] Aggiungere versioning del file JSON
- [ ] Aggiungere validazione schema JSON
- [ ] Implementare sincronizzazione con database

## Conclusione

La persistenza del `MaterialRepository` è stata implementata seguendo lo stesso pattern del `SectionRepository`, garantendo coerenza e facilità di manutenzione in tutto il progetto.
