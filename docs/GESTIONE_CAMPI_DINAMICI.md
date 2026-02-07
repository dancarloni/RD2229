# 📐 Guida: Gestione Dinamica dei Campi di Input per Sezioni

## 🎯 Problema Risolto

L'applicazione ora aggiorna **dinamicamente** i campi di input quando si seleziona una diversa tipologia di sezione nella ComboBox.

## ✅ Cosa È Stato Implementato

### 1. **Configurazione Tipologie di Sezione** (`SECTION_DEFINITIONS`)

Il dizionario `SECTION_DEFINITIONS` in `main_window.py` contiene tutte le configurazioni delle tipologie di sezione supportate:

```python
SECTION_DEFINITIONS = {
    "Rettangolare": {
        "class": RectangularSection,
        "fields": [
            ("width", "Larghezza b (cm)"),
            ("height", "Altezza h (cm)"),
        ],
        "tooltip": "Sezione rettangolare piena con base b e altezza h",
        "field_tooltips": {
            "width": "Larghezza della base della sezione (cm, 1 decimale)",
            "height": "Altezza totale della sezione (cm, 1 decimale)",
        },
    },
    # ... altre tipologie
}
```

**Componenti di ogni tipologia:**
- `"class"`: Classe del modello (es. `RectangularSection`)
- `"fields"`: Lista di tuple `(nome_campo, label_visualizzata)`
- `"tooltip"`: Descrizione generale della sezione (opzionale)
- `"field_tooltips"`: Dizionario con tooltip per ogni campo (opzionale)

### 2. **Handler per Cambio Tipologia** (`_on_section_change`)

Quando l'utente seleziona una diversa tipologia nella ComboBox:

```python
def _on_section_change(self, _event=None) -> None:
    """Handler per cambio tipologia sezione - ricostruisce campi input dinamicamente."""
    tipo_selezionato = self.section_var.get()
    logger.debug(f"Cambio tipologia sezione: {tipo_selezionato}")
    
    # Ricostruisce i campi di input per la nuova tipologia
    self._create_inputs()
    
    # Se era in modalità editing, resetta (la tipologia è cambiata)
    if self.editing_section_id is not None:
        self.editing_section_id = None
        self._update_editing_mode_label()
    
    # Pulisce eventuali calcoli precedenti
    self.current_section = None
    self.output_text.delete("1.0", tk.END)
    self.canvas.delete("all")
```

**Funzionalità:**
- Richiama `_create_inputs()` per ricostruire i campi
- Resetta la modalità editing se attiva
- Pulisce output e grafica precedenti
- Logga il cambio per debugging

### 3. **Ricostruzione Dinamica dei Campi** (`_create_inputs`)

Metodo che ricostruisce completamente i widget nel frame "Dati geometrici":

```python
def _create_inputs(self) -> None:
    # 1. Pulisce il frame dai widget precedenti
    for widget in self.inputs_frame.winfo_children():
        widget.destroy()
    self.inputs.clear()

    # 2. Recupera la definizione della tipologia selezionata
    tipo_sezione = self.section_var.get()
    definition = SECTION_DEFINITIONS[tipo_sezione]
    field_tooltips = definition.get("field_tooltips", {})
    
    # 3. Crea i campi di input dinamicamente
    for row, (field, label_text) in enumerate(definition["fields"]):
        # Label del parametro
        lbl = tk.Label(self.inputs_frame, text=label_text, anchor="w")
        lbl.grid(row=row, column=0, sticky="w", padx=4, pady=4)
        
        # Entry con validazione float a 1 decimale
        vcmd = (self.register(self._validate_float_input), '%P')
        entry = tk.Entry(
            self.inputs_frame,
            width=18,
            validate="key",
            validatecommand=vcmd
        )
        entry.grid(row=row, column=1, padx=4, pady=4, sticky="ew")
        
        # Memorizza l'entry
        self.inputs[field] = entry
        
        # Aggiunge tooltip se disponibile
        if field in field_tooltips:
            self._create_tooltip(entry, field_tooltips[field])
```

**Logica:**
1. Distrugge tutti i widget esistenti
2. Legge la definizione dalla tipologia corrente
3. Crea dinamicamente Label + Entry per ogni campo
4. Configura validazione per float a 1 decimale
5. Aggiunge tooltip informativi

### 4. **Validazione Input Numerico** (`_validate_float_input`)

Valida in tempo reale l'input dell'utente:

```python
def _validate_float_input(self, value: str) -> bool:
    """
    Valida input numerico: accetta solo float con massimo 1 cifra decimale.
    """
    if value == "":
        return True
    
    try:
        float(value)
        
        # Controlla il numero di cifre decimali
        if '.' in value:
            parts = value.split('.')
            # Massimo 1 cifra decimale
            if len(parts) == 2 and len(parts[1]) <= 1:
                return True
            else:
                return False
        else:
            return True
    except ValueError:
        return False
```

**Funzionalità:**
- Accetta solo numeri
- Massimo 1 cifra decimale (es. `25.5` ✅, `25.55` ❌)
- Validazione in tempo reale durante la digitazione

### 5. **Sistema di Tooltip** (`_create_tooltip`)

Mostra suggerimenti al passaggio del mouse:

```python
def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
    """Crea un tooltip che appare al passaggio del mouse su un widget."""
    def on_enter(event):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(
            tooltip,
            text=text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            justify="left",
            padx=4,
            pady=2
        )
        label.pack()
        widget._tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, '_tooltip'):
            widget._tooltip.destroy()
            del widget._tooltip
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
```

## 📋 Esempio Pratico: Campi Visualizzati per Ogni Tipologia

### **Sezione Rettangolare**
```
┌─────────────────────────────────┐
│ Larghezza b (cm)  [_________]   │  ← Tooltip: "Larghezza della base..."
│ Altezza h (cm)    [_________]   │  ← Tooltip: "Altezza totale..."
└─────────────────────────────────┘
```

### **Sezione Circolare**
```
┌─────────────────────────────────┐
│ Diametro D (cm)   [_________]   │  ← Tooltip: "Diametro del cerchio..."
└─────────────────────────────────┘
```

### **Sezione a T**
```
┌─────────────────────────────────┐
│ Larghezza ala bf (cm)    [____] │  ← Tooltip: "Larghezza dell'ala..."
│ Spessore ala hf (cm)     [____] │  ← Tooltip: "Spessore dell'ala..."
│ Spessore anima bw (cm)   [____] │  ← Tooltip: "Spessore dell'anima..."
│ Altezza anima hw (cm)    [____] │  ← Tooltip: "Altezza dell'anima..."
└─────────────────────────────────┘
```

## 🔧 Come Aggiungere una Nuova Tipologia di Sezione

### Step 1: Creare il Modello
In `src/rd2229/sections_app/models/sections.py`:

```python
@dataclass
class ISection(Section):
    """Sezione a doppia T (I)."""
    
    flange_width: float = 0.0
    flange_thickness: float = 0.0
    web_height: float = 0.0
    web_thickness: float = 0.0
    
    def __init__(self, name: str, flange_width: float, 
                 flange_thickness: float, web_height: float, 
                 web_thickness: float, note: str = ""):
        super().__init__(name=name, section_type="I_SECTION", note=note)
        self.flange_width = flange_width
        self.flange_thickness = flange_thickness
        self.web_height = web_height
        self.web_thickness = web_thickness
    
    def _compute(self) -> SectionProperties:
        # Implementare calcolo delle proprietà
        ...
```

### Step 2: Aggiungere a SECTION_DEFINITIONS
In `src/rd2229/sections_app/ui/main_window.py`:

```python
SECTION_DEFINITIONS = {
    # ... definizioni esistenti
    "A I (doppia T)": {
        "class": ISection,
        "fields": [
            ("flange_width", "Larghezza ali bf (cm)"),
            ("flange_thickness", "Spessore ali hf (cm)"),
            ("web_height", "Altezza anima hw (cm)"),
            ("web_thickness", "Spessore anima bw (cm)"),
        ],
        "tooltip": "Sezione a doppia T (I) con due ali simmetriche",
        "field_tooltips": {
            "flange_width": "Larghezza delle ali superiore e inferiore (cm, 1 decimale)",
            "flange_thickness": "Spessore delle ali (cm, 1 decimale)",
            "web_height": "Altezza dell'anima centrale (cm, 1 decimale)",
            "web_thickness": "Spessore dell'anima (cm, 1 decimale)",
        },
    },
}
```

### Step 3: Implementare il Disegno (Opzionale)
In `main_window.py`, nel metodo `_draw_section`:

```python
def _draw_section(self, section: Section) -> None:
    # ... codice esistente
    elif isinstance(section, ISection):
        self._draw_i_section(section, transform)
    # ...

def _draw_i_section(self, section: ISection, transform) -> None:
    """Disegna sezione a I sul canvas."""
    # Implementare logica di disegno
    ...
```

### Step 4: Testare
1. Avviare l'applicazione
2. Selezionare la nuova tipologia dalla ComboBox
3. Verificare che i campi si aggiornino correttamente
4. Inserire valori di test e calcolare le proprietà

## 📏 Vincoli e Convenzioni

### Unità di Misura
- **Tutte le dimensioni sono in cm** (centimetri)
- **Formato numerico**: float con **massimo 1 cifra decimale**
  - ✅ Validi: `25`, `30.5`, `100.0`
  - ❌ Non validi: `25.55`, `30.125`

### Validazione Input
- La validazione avviene **in tempo reale** durante la digitazione
- Solo numeri positivi (la validazione del segno positivo avviene al momento del calcolo)
- La funzione `_validate_float_input` impedisce l'inserimento di valori non conformi

### Tooltip
- Ogni campo può avere un tooltip esplicativo
- I tooltip appaiono al passaggio del mouse
- Sfondo giallo chiaro (`#ffffe0`) per visibilità

## 🐛 Troubleshooting

### Problema: I campi non si aggiornano al cambio tipologia
**Soluzione**: Verificare che:
1. Il binding `<<ComboboxSelected>>` sia presente
2. `_on_section_change` chiami effettivamente `_create_inputs()`
3. Non ci siano eccezioni nel log

### Problema: La validazione non funziona
**Soluzione**: Verificare che:
1. `validatecommand` sia correttamente configurato nell'Entry
2. Il metodo `_validate_float_input` sia registrato con `self.register()`
3. Il parametro `validate="key"` sia presente

### Problema: I tooltip non appaiono
**Soluzione**: Verificare che:
1. `_create_tooltip` sia chiamato per ogni widget
2. Il testo del tooltip sia presente in `field_tooltips`
3. Gli eventi `<Enter>` e `<Leave>` siano correttamente bindati

## 📚 Documentazione Correlata

- **Modelli sezioni**: `src/rd2229/sections_app/models/sections.py`
- **Repository**: `src/rd2229/sections_app/services/repository.py`
- **Calcoli geometrici**: Implementati nei metodi `_compute()` di ogni classe Section
- **Test automatizzati**: `tests/test_sections_random_demo.py`

## 🎨 Estensibilità

Il sistema è progettato per essere facilmente estendibile:

1. **Nuove tipologie**: Aggiungere voci a `SECTION_DEFINITIONS`
2. **Nuovi campi**: Aggiungere tuple in `"fields"`
3. **Validazioni custom**: Estendere `_validate_float_input` o creare nuovi validatori
4. **Tooltip personalizzati**: Aggiungere voci in `"field_tooltips"`

L'architettura separa chiaramente:
- **Modello** (dati e calcoli) → `sections.py`
- **Vista** (interfaccia grafica) → `main_window.py`
- **Configurazione** (definizioni tipologie) → `SECTION_DEFINITIONS`

Questo consente modifiche indipendenti a ciascun layer senza impatti sugli altri.
