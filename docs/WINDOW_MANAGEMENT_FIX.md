# 🔧 Correzione Gestione Finestre - Module Selector

## 📋 Sommario Modifiche

Risolto il problema per cui la finestra principale (Module Selector) si chiudeva quando si aprivano i moduli. Ora la finestra principale **rimane sempre aperta e visibile**, mentre i moduli si aprono come finestre indipendenti.

---

## 🎯 Comportamento Finale Corretto

✅ **Module Selector** rimane sempre visibile in background  
✅ Ogni modulo (Geometry, Historical, Verification Table, Materials) apre una nuova finestra **senza** chiudere la principale  
✅ È possibile chiudere singolarmente ogni finestra di modulo  
✅ Chiudere la finestra principale chiude l'intera applicazione  
✅ **Un solo `mainloop()`** nell'applicazione (nella root principale)

---

## 📁 File Modificati

### 1. **`sections_app/ui/main_window.py`** - MainWindow
#### Cambio Principale: `tk.Tk` → `tk.Toplevel`

**PRIMA:**
```python
class MainWindow(tk.Tk):
    """Finestra principale dell'applicazione."""
    
    def __init__(self, repository, serializer, material_repository=None):
        super().__init__()  # ❌ Crea una nuova root Tk separata
```

**DOPO:**
```python
class MainWindow(tk.Toplevel):
    """Finestra del modulo Geometry - aperta come Toplevel dalla finestra principale ModuleSelector.
    
    ✅ Estende tk.Toplevel (non tk.Tk) - rimane una finestra figlia della root principale.
    ✅ Accetta la finestra parent nel costruttore.
    ✅ Un solo mainloop() nell'applicazione (nel ModuleSelector).
    """
    
    def __init__(self, master: tk.Tk, repository, serializer, material_repository=None):
        super().__init__(master=master)  # ✅ Usa master come parent
```

**Impatto:**
- MainWindow è ora una finestra figlia legata alla root principale
- Non crea più un `Tk()` indipendente
- Quando chiudi il modulo Geometry, la finestra principale rimane aperta

---

### 2. **`sections_app/ui/module_selector.py`** - Module Selector

#### Modifica: Rimozione `withdraw()` e `_on_child_close()`

**PRIMA:**
```python
def _open_geometry(self) -> None:
    logger.debug("Opening Geometry module")
    self.withdraw()  # ❌ Nasconde la finestra principale!
    win = MainWindow(self.repository, self.serializer, self.material_repository)
    win.protocol("WM_DELETE_WINDOW", self._on_child_close)

def _on_child_close(self) -> None:
    """Callback when a child window is closed: safely restore the selector window."""
    try:
        if self.winfo_exists():
            self.deiconify()  # ❌ Ripristina la finestra nascosta
    except tk.TclError:
        logger.debug("Cannot deiconify Module Selector: application already destroyed")
```

**DOPO:**
```python
def _open_geometry(self) -> None:
    """Apre il modulo Geometry come finestra Toplevel.
    
    La finestra principale ModuleSelector rimane visibile in background.
    """
    logger.debug("Opening Geometry module")
    # ✅ MainWindow è ora un Toplevel (non più un Tk indipendente)
    win = MainWindow(self, self.repository, self.serializer, self.material_repository)
    win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())

# ✅ _on_child_close() rimosso - non più necessario
```

**Applicate a:**
- `_open_geometry()`
- `_open_historical()`
- `_open_verification_table()`

**Benefici:**
- La finestra principale non viene più nascosta
- Nessun bisogno di un sistema di restore/deiconify
- Callback più semplice e diretto

---

### 3. **`tests/test_main_window_material_button.py`** - Test di MainWindow

**Cambio:** Aggiunto `master` come primo parametro in `MainWindow()` constructor

**PRIMA:**
```python
def test_editor_material_button_triggers_open_material_manager(self):
    repo = SectionRepository()
    serializer = CsvSectionSerializer()
    mw = MainWindow(repo, serializer, material_repository=None)  # ❌ Manca master
```

**DOPO:**
```python
def setUp(self):
    # Check Tkinter availability
    try:
        self.root = tk.Tk()
        self.root.withdraw()
    except tk.TclError:
        self.skipTest("Tkinter not available (headless environment)")

def test_editor_material_button_triggers_open_material_manager(self):
    repo = SectionRepository()
    serializer = CsvSectionSerializer()
    # ✅ MainWindow è ora Toplevel e richiede un master (root come parent)
    mw = MainWindow(self.root, repo, serializer, material_repository=None)
```

---

### 4. **`tests/test_module_selector_material_button.py`** - Test di Module Selector

**Aggiunto:** Controllo disponibilità Tkinter in `setUp()`

```python
def setUp(self):
    """Set up test fixtures."""
    try:
        # Try to create a root - if Tkinter is not available, skip tests
        test_root = tk.Tk()
        test_root.destroy()
    except tk.TclError:
        self.skipTest("Tkinter not available (headless environment)")
    
    self.repo = SectionRepository()
    self.serializer = CsvSectionSerializer()
    self.material_repo = MaterialRepository()
```

---

## 🏗️ Architettura Finale

```
┌─────────────────────────────────────────────┐
│   ModuleSelector (tk.Tk)                    │
│   • Finestra root principale                │
│   • Esegue mainloop() unico dell'app        │
│   • Rimane visibile quando moduli aperti    │
└─────────────────────────────────────────────┘
        │       │        │         │
        │       │        │         │
    ┌───▼──┐ ┌──▼──┐ ┌───▼─┐ ┌────▼────┐
    │ Geom │ │Hist │ │Verif│ │Materials│
    │(Top) │ │(Top)│ │(Top)│ │ (Top)   │
    │      │ │     │ │     │ │         │
    └──────┘ └─────┘ └─────┘ └─────────┘
   (Toplevel) (Toplevel) (Toplevel) (Toplevel)
    Finestre figlie - indipendenti tra loro
    Chiudere uno non chiude gli altri
```

---

## ✅ Test e Validazione

**Risultati Test:**
```
53 passed, 1 skipped, 1 warning, 9 subtests passed in 8.42s
```

**Commit:** `9e7b211 - Fix: window management - keep Module Selector open when opening modules`

**Git Push:** ✅ Sincronizzato con `origin/main`

---

## 🚀 Comportamento in Pratica

### Scenario 1: Aprire Geometry
1. Clicca "Open Geometry" nel Module Selector
2. ✅ **Module Selector rimane visibile** in background
3. Una nuova finestra "Gestione Proprietà Sezioni" si apre
4. ✅ Puoi continuare a usare il Module Selector mentre Geometry è aperto

### Scenario 2: Aprire Multiple Moduli
1. Apri Geometry → finestra Geometry aperta
2. Clicca "Open Materials" → finestra Materials aperta
3. ✅ Geometry, Materials **e** Module Selector sono **tutti visibili**
4. Puoi passare tra le finestre liberamente

### Scenario 3: Chiudere un Modulo
1. Chiudi la finestra Geometry (pulsante X o Esc)
2. ✅ Module Selector **rimane aperta**
3. ✅ Materials (se aperta) **rimane aperta**
4. Solo Geometry viene chiusa

### Scenario 4: Chiudere l'Applicazione
1. Chiudi la finestra Module Selector (pulsante X)
2. ✅ L'intera applicazione termina (chiude tutti i moduli aperti)

---

## 💡 Punti Chiave Tecnici

| Aspetto | Prima | Dopo |
|---------|-------|------|
| **Root principale** | `tk.Tk()` (ModuleSelector) | `tk.Tk()` (ModuleSelector) |
| **Modulo Geometry** | `tk.Tk()` (indipendente) | `tk.Toplevel()` (figlia) |
| **Modulo Historical** | `tk.Toplevel()` | `tk.Toplevel()` ✅ |
| **Modulo Verification Table** | `tk.Toplevel()` | `tk.Toplevel()` ✅ |
| **Modulo Materials** | `tk.Toplevel()` | `tk.Toplevel()` ✅ |
| **mainloop()** | Multiple (uno per ogni Tk) | **Unico** (solo ModuleSelector) |
| **Visibilità Main** | ❌ Nascosta quando modulo aperto | ✅ **Sempre visibile** |
| **Gestione chiusura** | Complessa (withdraw/deiconify) | **Semplice** (destroy singoli) |

---

## 📝 Commenti nel Codice

Nel file `main_window.py`, la classe MainWindow ha ora commenti espliciti:

```python
class MainWindow(tk.Toplevel):
    """Finestra del modulo Geometry - aperta come Toplevel dalla finestra principale ModuleSelector.
    
    ✅ Estende tk.Toplevel (non tk.Tk) - rimane una finestra figlia della root principale.
    ✅ Accetta la finestra parent nel costruttore.
    ✅ Un solo mainloop() nell'applicazione (nel ModuleSelector).
    """
```

Nel `module_selector.py`:

```python
def _open_geometry(self) -> None:
    """Apre il modulo Geometry come finestra Toplevel.
    
    La finestra principale ModuleSelector rimane visibile in background.
    """
```

---

## 🎓 Lezione Appresa

**Problema:** Usando `tk.Tk()` in MainWindow veniva creata una **root window indipendente**, che non poteva coesistere correttamente con la root di ModuleSelector. L'unica soluzione era nascondere la principale.

**Soluzione:** Convertire MainWindow a `tk.Toplevel()` la rende una **finestra figlia** della root principale, mantenendo la gerarchia corretta e permettendo la coesistenza di multiple finestre.

**Regola d'Oro Tkinter:** 
> In un'applicazione Tkinter, ci deve essere **una sola `tk.Tk()`** (la root), e tutti gli altri top-level dovrebbero essere **`tk.Toplevel()`** (figlie della root).

---

## ✨ Risultato Finale

L'applicazione ora ha un comportamento **intuitivo e professionale**:
- La finestra di selezione moduli rimane sempre visibile come "hub" centrale
- Ogni modulo apre in una finestra indipendente ma gestita dalla root
- L'utente ha il controllo totale su quali finestre tenere aperte
- Chiudere la principale chiude l'intera applicazione
- Chiudere un modulo non influenza gli altri

🎉 **Problema risolto!**
