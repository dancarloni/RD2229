# Persistenza SectionRepository

## Descrizione

Il `SectionRepository` ora supporta la **persistenza automatica** su file JSON. Tutte le sezioni create, modificate o eliminate vengono salvate automaticamente in un file locale e ripristinate al successivo avvio del programma.

## Caratteristiche

✅ **Salvataggio automatico**: Ad ogni operazione (`add_section()`, `update_section()`, `delete_section()`, `clear()`), il repository salva tutte le sezioni su file JSON.

✅ **Caricamento automatico**: All'inizializzazione, il repository carica tutte le sezioni dal file JSON se esiste.

✅ **Persistenza completa**: Tutte le proprietà geometriche e calcolate vengono salvate e ripristinate.

✅ **Compatibilità completa**: Il codice esistente continua a funzionare senza modifiche (il parametro `json_file` è opzionale).

✅ **Gestione degli errori**: Se il file JSON non esiste, il repository parte vuoto. Se il file è corrotto, registra un errore ma continua a funzionare.

## Utilizzo

### Uso predefinito (file "sections.json" nella cartella corrente)

```python
from sections_app.services.repository import SectionRepository

# Crea/carica repository (usa "sections.json" per default)
repo = SectionRepository()

# Aggiungi una sezione (salva automaticamente)
section = RectangularSection(name="Rettangolare 20x30", width=20, height=30)
repo.add_section(section)

# Modifica una sezione (salva automaticamente)
section_modified = RectangularSection(name="Rettangolare 25x35", width=25, height=35)
repo.update_section(section.id, section_modified)

# Elimina una sezione (salva automaticamente)
repo.delete_section(section.id)
```

### Uso con percorso personalizzato

```python
# Specifica una directory personalizzata
repo = SectionRepository(json_file="/path/to/my_sections.json")
```

### Uso con directory relativa

```python
# Nella directory dell'applicazione
repo = SectionRepository(json_file="data/sections.json")
```

## Struttura JSON salvato

Il file JSON contiene un array di sezioni con tutte le loro proprietà:

```json
[
  {
    "id": "72c95436-d5f7-4423-b804-d3799a1960cb",
    "name": "Rettangolare 20x30",
    "section_type": "RECTANGULAR",
    "width": 20.0,
    "height": 30.0,
    "rotation_angle_deg": 0.0,
    "area": 600.0,
    "x_G": 10.0,
    "y_G": 15.0,
    "Ix": 45000.0,
    "Iy": 20000.0,
    "Ixy": 0.0,
    "Qx": 7500.0,
    "Qy": 3333.3333333333335,
    "rx": 8.660254037844387,
    "ry": 5.773502691896257,
    "core_x": 0.0,
    "core_y": 0.0,
    "ellipse_a": 8.660254037844387,
    "ellipse_b": 5.773502691896257,
    "note": "Test"
  },
  ...
]
```

## API

### `__init__(json_file: str = "sections.json")`

Inizializza il repository e carica le sezioni dal file JSON se esiste.

**Parametri**:
- `json_file` (str, opzionale): Percorso del file JSON. Default: `"sections.json"`

### `load_from_file() -> None`

Carica tutte le sezioni dal file JSON.

**Comportamento**:
- Se il file non esiste, il repository rimane vuoto
- Se il file esiste, carica tutte le sezioni
- Registra errori a livello DEBUG/WARNING

### `save_to_file() -> None`

Salva tutte le sezioni nel file JSON.

**Comportamento**:
- Crea il file se non esiste
- Crea la directory se non esiste
- Sovrascrive il file se esiste
- Formatta il JSON con indentazione (2 spazi)

### `add_section(section: Section) -> bool`

Aggiunge una sezione al repository e salva automaticamente.

### `update_section(section_id: str, updated_section: Section) -> None`

Aggiorna una sezione al repository e salva automaticamente.

### `delete_section(section_id: str) -> None`

Elimina una sezione dal repository e salva automaticamente.

### `clear() -> None`

Elimina tutte le sezioni dal repository e salva automaticamente.

## Logging

Il repository registra tutte le operazioni di persistenza:

```
DEBUG: Caricata sezione 72c95436-d5f7-4423-b804-d3799a1960cb (Rettangolare 20x30)
DEBUG: Caricate 3 sezioni da sections.json
DEBUG: Salvate 3 sezioni in sections.json
```

## Compatibilità

✅ **Completamente retro-compatibile**: Il codice esistente continua a funzionare.

```python
# Codice vecchio (continua a funzionare)
repo = SectionRepository()  # Usa default "sections.json"

# Codice nuovo (opzionale)
repo = SectionRepository(json_file="my_custom_sections.json")
```

## Comportamento dei metodi

| Metodo | Salva | Dettagli |
|--------|-------|----------|
| `add_section()` | ✅ Sì | Salva se sezione non è duplicata |
| `update_section()` | ✅ Sì | Salva se update ha successo |
| `delete_section()` | ✅ Sì | Salva se sezione era presente |
| `clear()` | ✅ Sì | Salva file vuoto |
| `load_from_file()` | ❌ No | Solo lettura |
| `get_all_sections()` | ❌ No | Solo lettura |
| `find_by_id()` | ❌ No | Solo lettura |

## Gestione degli errori

### File JSON non esiste
- ✅ **Comportamento**: Repository inizia vuoto, salva il primo file JSON automaticamente

### File JSON corrotto
- ✅ **Comportamento**: Registra errore, repository rimane vuoto, prossimo salvataggio sovrascrive il file corrotto

### Directory non esiste
- ✅ **Comportamento**: Viene creata automaticamente durante il salvataggio

### Permessi insufficienti
- ⚠️ **Comportamento**: Registra errore, operazione continua in memoria (ma non persiste)

## Esempi

### Applicazione GUI

```python
from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from sections_app.ui.main_window import MainWindow

# Repository con persistenza automatica
repo = SectionRepository(json_file="data/sections.json")
serializer = CsvSectionSerializer()

# La GUI userà automaticamente il repository persistente
main_window = MainWindow(repo, serializer)
```

### Demo

```python
# Crea repository con 3 sezioni
repo = SectionRepository(json_file="demo.json")

rect = RectangularSection(name="Rect", width=20, height=30)
circ = CircularSection(name="Circle", diameter=25)
t_section = TSection(name="T", flange_width=40, flange_thickness=5, 
                     web_thickness=8, web_height=25)

for section in [rect, circ, t_section]:
    repo.add_section(section)

# Tutte le sezioni sono ora salvate in "demo.json"
print(f"Salvate {len(repo.get_all_sections())} sezioni")

# Carica in nuovo repository
repo2 = SectionRepository(json_file="demo.json")
print(f"Caricate {len(repo2.get_all_sections())} sezioni da disco")
```

## Note di implementazione

- **UUID**: Ogni sezione mantiene il suo UUID originale nel file JSON
- **Rotazione**: L'angolo di rotazione è salvato e ripristinato correttamente
- **Proprietà calcolate**: Tutte le proprietà geometriche sono salvate e ripristinate
- **Non-modificato**: I modelli Section non sono stati modificati
- **Transazione**: Ogni operazione di salvataggio è atomica (scrive tutto o nulla)
