## Scopo

Istruzioni rapide per agenti AI che devono lavorare sul codice RD2229: cosa sapere per essere produttivi subito, dove guardare e quali comandi eseguire.

## Big picture (architettura)

- **Core di calcolo**: la logica principale è in [src/core_calculus](src/core_calculus) (es. [src/core_calculus/verification_engine.py](src/core_calculus/verification_engine.py)).
- **Compatibilità/adapter**: il package `core/` contiene shim che importano da `src` (es. [core/verification_engine.py](core/verification_engine.py)).
- **Moduli di calcolo**: i calcoli sono organizzati in `calculations/<elemento>` (pattern: un file per sottoargomento, vedi struttura in [README.md](README.md)).
- **Verifiche**: la logica delle verifiche storiche è in [verifications](verifications) e nel core ([src/core_calculus/core](src/core_calculus/core)).
- **Dati storici**: tabelle e coefficienti sono centralizzati in [data](data) e caricati tramite `config/*_loader.py`.

## Convenzioni e pattern specifici

- **Unità storiche**: molte routine usano `Kg/cm²` (vedi `README.md`), attenzione alle conversioni.
- **Codici di calcolo**: valori stringa come `"TA"`, `"SLU"`, `"SLE"` selezionano comportamenti/dati diversi.
- **Plugin di configurazione**: i loader in `config/` (`calculation_codes_loader.py`, `historical_materials_loader.py`) possono essere assenti — il core usa fallback e cache (`lru_cache`).
- **Interfaccia engine**: usare `create_verification_engine(calculation_code)` o `VerificationEngine` in [src/core_calculus/core/verification_engine.py](src/core_calculus/core/verification_engine.py).
- **Struttura dei moduli**: nuovi moduli devono seguire `calculations/<elemento>/<nome>.py` e restituire risultati e passaggi intermedi (OK/NON OK + steps).

## Flussi di sviluppo e comandi utili

- Ambiente e dipendenze:

  ```bash
  python -m venv .venv
  # PowerShell
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```

- Pre-commit e linting:

  ```bash
  pip install pre-commit
  pre-commit install
  pre-commit run --all-files
  ```

- Test:

  ```bash
  pytest -q
  ```

- Eseguire demo / GUI (usa `PYTHONPATH` verso `src`):

  ```powershell
  $env:PYTHONPATH='c:\workspaces\RD2229\RD2229\src'; python scripts/run_verification_demo.py
  ```

  (Alternativamente `python scripts/run_verification_demo.py` se `src` è installato nel path.)

## Dove guardare per comprendere i cambiamenti

- Calcolo e orchestrazione: [src/core_calculus/core/verification_engine.py](src/core_calculus/core/verification_engine.py)
- Implementazioni dei metodi: [src/core_calculus/verification_engine.py](src/core_calculus/verification_engine.py) e `calculations/` per i moduli specifici
- Loader/config: [config/calculation_codes_loader.py](config/calculation_codes_loader.py) e [config/historical_materials_loader.py](config/historical_materials_loader.py)
- Dati persistenti: [data/](data) e file di esempio in root (`materials.json`, `materials_backup.json`)

## Come proporre una modifica concreta (pattern)

1. Aggiungi il modulo sotto `calculations/<elemento>/` seguendo il nome `sottoargomento.py`.
2. Esponi funzioni pulite che prendono input semplici (dict/typed dataclasses) e restituiscono un risultato + passaggi intermedi.
3. Aggiungi test unitari in `tests/` che verificano sia valori finali sia step intermedi.
4. Se servono dati nuovi, aggiungi JSON in `data/` e aggiorna gli loader in `config/`.

## Esempio minimo: usare l'engine in uno script

```python
from src.core_calculus.core.verification_engine import create_verification_engine

engine = create_verification_engine('TA')
inputs = {'width': 30.0, 'height': 50.0, 'Mx': 0.0, 'My': 0.0, 'N': 0.0}
# costruire gli oggetti SectionGeometry/Material/LoadCase usando i factory nel core
# poi chiamare engine.perform_verification(...)
```

## Note finali e limiti

- Documenta ogni formula/assunzione direttamente nel file di calcolo: i controlli storici devono poter mostrare i passaggi.
- Evitare di cambiare le unità globali senza aggiornare conversioni e test.

Se vuoi, applico questo file al repository e posso iterare sulla versione dopo il tuo feedback.
