# GUI INTEGRATION RULES

> Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md` — LOCKED

## Regole fondamentali (non negoziabili)

1. **GUI → Application Services only**: la GUI chiama solo Application Services o ViewModel. Mai direttamente Engine, Repository o Config.
2. **No file storage in GUI**: la GUI non apre, legge o scrive file di progetto direttamente.
3. **No calcoli in GUI**: nessuna formula o logica normativa in widget, dialog o view.
4. **No import Engine in GUI**: i moduli `src/rd2229/mvp/engine.py`, `src/core_calculus/`, `src/fire/` non devono essere importati da widget.
5. **ViewModel come unico ponte**: i viewmodel sono l'unico punto di contatto tra GUI e dominio.

## Pattern consentiti

- GUI emette segnali/eventi → ViewModel interpreta → chiama Application Service
- Application Service chiama Engine → ritorna risultato → ViewModel aggiorna stato → GUI riflette
- GUI visualizza `VerificationResult.status` senza logica business

## Anti-pattern vietati

```python
# VIETATO: import diretto di Engine in widget
from src.rd2229.mvp.engine import PlaceholderVerificationEngine  # NON FARE

# VIETATO: apertura DB in GUI
import sqlite3; conn = sqlite3.connect("project.db")  # NON FARE

# VIETATO: calcoli in GUI
def on_button_click(self):
    result = 1.2 * axial / capacity  # NON FARE
```

## Pattern consentiti (esempi)

```python
# CORRETTO: GUI chiama viewmodel/service
class VerificationView(QWidget):
    def run_verification(self):
        self.viewmodel.run_check(self.input_widget.get_request())
```

## Regole per modulo incendio

- Il modulo `src/fire/` non deve essere importato direttamente dalla GUI.
- La GUI visualizza risultati fire tramite lo stesso contratto `VerificationResult`.
- Separazione: fire e strutturale sono due Application Services distinti.

## Test GUI

- I test GUI usano `pytest.mark.gui` e sono esclusi da CI standard.
- Ogni flusso GUI testabile headless va testato via ViewModel senza widget reali.
