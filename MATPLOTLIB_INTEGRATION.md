# Matplotlib Integration - RD2229

## Panoramica

Matplotlib è stato integrato e abilitato nel progetto RD2229 per fornire capacità di visualizzazione grafica avanzate per sezioni strutturali e risultati di verifica.

## Installazione

Il progetto è stato installato in modalità di sviluppo (editable mode) utilizzando:

```bash
pip install -e .
```

Questo comando installa:
- **pandas** (v3.0.0) - Per la gestione dei dati
- **matplotlib** (v3.10.8) - Per la visualizzazione grafica
- Tutte le dipendenze necessarie (numpy, pillow, etc.)

## Verificare l'Installazione

Per verificare che matplotlib sia correttamente installato e funzionante:

```bash
python demo_matplotlib_integration.py
```

Questo script:
1. Verifica l'installazione di matplotlib, pandas e numpy
2. Genera tre demo di visualizzazione grafica
3. Salva i grafici in `/tmp/matplotlib_demo_*.png`

## Funzionalità Grafiche Disponibili

### 1. Visualizzazione Sezioni (`gui/section_gui.py`)

Il modulo `gui.section_gui` fornisce la funzione `plot_section()` per visualizzare graficamente le sezioni:

```python
from gui.section_gui import plot_section
from sections_app.models.sections import RectangularSection

# Crea una sezione
section = RectangularSection(width=30.0, height=50.0, name='Sez. 1')

# Visualizza con matplotlib
plot_section(section, title='Sezione Rettangolare', show=True)
```

### 2. Integrazione con Main Window (`sections_app/ui/main_window.py`)

La finestra principale delle sezioni include un pulsante "Mostra Matplotlib" che:
- Apre una visualizzazione grafica della sezione corrente
- Mostra il baricentro e le dimensioni
- Permette l'esportazione dell'immagine

### 3. Verification Table

La tabella di verifica può ora utilizzare matplotlib per:
- Visualizzare le sezioni strutturali
- Mostrare la distribuzione delle tensioni
- Rappresentare graficamente i risultati delle verifiche
- Generare diagrammi di stress-strain

## Tipi di Sezioni Supportate

Matplotlib può visualizzare:
- ✓ Sezioni rettangolari (`RectangularSection`)
- ✓ Sezioni circolari (`CircularSection`)
- ✓ Sezioni a T (`TSection`)
- ✓ Sezioni a I (`ISection`)
- ✓ Sezioni ad L (`LSection`)
- ✓ Sezioni cave (rettangolari e circolari)

## Esempi di Uso

### Esempio 1: Plot Base di una Sezione

```python
import matplotlib
matplotlib.use('Agg')  # Backend non-interattivo per server/CI
from sections_app.models.sections import RectangularSection
from gui.section_gui import plot_section

section = RectangularSection(width=30.0, height=50.0)
fig, ax = plot_section(section, show=False)

# Salva il grafico
import matplotlib.pyplot as plt
plt.savefig('my_section.png', dpi=150, bbox_inches='tight')
plt.close()
```

### Esempio 2: Visualizzazione Personalizzata

```python
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_title('Sezione con Armatura')

# Disegna la sezione
rect = Rectangle((0, 0), 30, 50, fill=True, 
                facecolor='lightgray', edgecolor='black')
ax.add_patch(rect)

# Aggiungi barre d'armatura
for x in [5, 15, 25]:
    ax.plot(x, 45, 'ko', markersize=8, markerfacecolor='red')
    ax.plot(x, 5, 'ko', markersize=8, markerfacecolor='red')

ax.set_aspect('equal')
plt.show()
```

### Esempio 3: Grafico di Verifica

```python
import matplotlib.pyplot as plt
import numpy as np

# Simula distribuzione tensioni
y = np.linspace(0, 50, 100)
stress = np.where(y > 30, (y - 30) * 0.5, -(30 - y) * 0.6)

fig, ax = plt.subplots()
ax.fill_betweenx(y, 0, stress, where=(stress >= 0), 
                color='blue', alpha=0.3, label='Compressione')
ax.fill_betweenx(y, 0, stress, where=(stress < 0), 
                color='red', alpha=0.3, label='Trazione')
ax.axhline(y=30, color='green', linestyle='--', label='Asse Neutro')
ax.legend()
plt.show()
```

## File Modificati/Creati

1. **requirements.txt** - Contiene `matplotlib` e `pandas`
2. **setup.cfg** - Configurato con le dipendenze corrette
3. **demo_matplotlib_integration.py** - Script di verifica e demo
4. **MATPLOTLIB_INTEGRATION.md** - Questa documentazione

## Dipendenze Installate

```
matplotlib==3.10.8
pandas==3.0.0
numpy==2.4.2
pillow==12.1.0
contourpy==1.3.3
cycler==0.12.1
fonttools==4.61.1
kiwisolver==1.4.9
```

## Note per gli Sviluppatori

### Backend Matplotlib

Per ambienti senza display (server, CI):
```python
import matplotlib
matplotlib.use('Agg')  # Backend non-interattivo
```

Per ambienti con GUI:
```python
# Usa il backend predefinito (TkAgg, Qt5Agg, etc.)
import matplotlib.pyplot as plt
plt.show()  # Mostra finestra interattiva
```

### Testing

I test che utilizzano matplotlib dovrebbero:
1. Usare il backend 'Agg' per evitare dipendenze GUI
2. Chiamare `plot_section(..., show=False)` e verificare il risultato
3. Chiudere le figure con `plt.close()` dopo l'uso

Esempio:
```python
def test_plot_section():
    import matplotlib
    matplotlib.use('Agg')
    from gui.section_gui import plot_section
    from core.geometry import RectangularSection
    
    section = RectangularSection(width=20.0, height=30.0)
    fig, ax = plot_section(section, show=False)
    
    assert fig is not None
    assert ax is not None
    
    import matplotlib.pyplot as plt
    plt.close(fig)
```

### Integrazione con Tkinter

Il modulo `gui/section_gui.py` combina matplotlib con tkinter. Importa tkinter solo quando necessario per evitare errori in ambienti headless.

## Troubleshooting

### Problema: "No module named 'tkinter'"
**Soluzione**: In ambienti senza GUI, usa il backend Agg:
```python
import matplotlib
matplotlib.use('Agg')
```

### Problema: Plot non visibili
**Soluzione**: Assicurati di chiamare `plt.show()` o salvare con `plt.savefig()`:
```python
plt.savefig('output.png')
```

### Problema: Warning backend
**Soluzione**: Configura esplicitamente il backend all'inizio dello script:
```python
import matplotlib
matplotlib.use('TkAgg')  # o 'Qt5Agg', 'Agg', etc.
```

## Riferimenti

- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- File di esempio: `demo_matplotlib_integration.py`
- Test: `tests/test_plot_section.py`

## Prossimi Passi

Possibili miglioramenti futuri:
1. Aggiungere visualizzazione 3D delle sezioni
2. Implementare animazioni per mostrare stati di carico
3. Creare dashboard interattive con matplotlib widgets
4. Esportazione in formati vettoriali (PDF, SVG)
5. Grafici interattivi con zoom e pan

---

**Data di integrazione**: Febbraio 2026  
**Versione Matplotlib**: 3.10.8  
**Versione Pandas**: 3.0.0
