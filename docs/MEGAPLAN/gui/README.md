# 🎨 GUI — Interfaccia Utente

Documentazione dell'interfaccia grafica Qt/PySide6 per il software RD2229.

## Contenuto (9 file)

```
gui/
├── README.md (questo file)
├── GUI_MAIN_PY_NAVIGAZIONE.md (Navigazione principale)
├── GUI_SELEZIONE_NORMATIVA.md (Selezione norma)
├── GUI_SELEZIONE_VERIFICHE_RISULTATI.md (Selezione verifiche)
├── GUI_RISULTATI_VIEW_CODICE.md (Visualizzazione risultati)
├── GUI_SEZIONI_MATERIALI_VIEW_CODICE.md (Sezioni/materiali)
├── GUI_SOLLECITAZIONI_VIEW_CODICE.md (Carichi/sollecitazioni)
├── GUI_VERIFICATION_ENGINE_BINDING.md (Binding motore)
├── GUI_RESULTS_TO_RELAZIONE_BINDING.md (Report binding)
└── GUI_VERIFICATION_SUPPORT.md (Funzioni di supporto)
```

## Architettura GUI

**Stack**: PySide6 / Qt 6 (moderno, cross-platform)

### Widget Principali
- **MainWindow**: Navigazione centrale
- **NormativeSelector**: Selezione norma/standard
- **VerificationPanel**: Selezione verifiche
- **ResultsView**: Tabulati e report
- **SectionGeometryWidget**: Disegno sezioni
- **MaterialsWidget**: Gestione materiali
- **LoadsWidget**: Combinazioni di carico

### Binding Engine
- Connessione Qt Signals/Slots ↔ `src/core/pipeline.py`
- Validator real-time su input
- Progress reporting

### Report Output
- Generazione HTML/PDF
- Tabulati di calcolo con passaggi intermedi
- Esportazione dati

## Stato

- ✅ Widget base implementati
- 🟨 Binding completo in corso
- 🟨 Tematizzazione colori/stili da completare

**Ultimo aggiornamento**: 2026-03-29
