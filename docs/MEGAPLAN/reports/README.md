# 📄 REPORTS — Template Relazioni Tecniche

Archivio dei template per la generazione di relazioni tecniche e rapporti di calcolo.

## Contenuto (7 file)

```
reports/
├── README.md (questo file)
├── RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md (Template principale)
├── RELAZIONE_RD2229_TEMPLATE.md (Template RD2229)
├── REPORT_BUILDER_NTC2018_CODE.md (Builder NTC2018)
├── REPORT_BUILDER_RD2229.md (Builder RD2229)
├── REPORT_BUILDER_RD2229_CODE.md (Codice builder)
└── APPLICATION_REPORT.md (Report applicazione)
```

## Template Principale

### RELAZIONE_DI_CALCOLO_NTC2018_TEMPLATE_OPERATIVO.md

Struttura standard relazione NTC2018:

```
1. Frontespizio
2. Sommario esecutivo
3. Dati progetto e input
4. Ipotesi e metodo di calcolo
5. Materiali
6. Geometria e sezioni
7. Azioni
8. Combinazioni di carico
9. Verifiche SLU
   - Flessione
   - Taglio
   - Torsione
10. Verifiche SLE
    - Fessurazione
    - Deformazioni
11. Analisi sismica (se applicable)
12. Conclusioni
13. Allegati (disegni, file input)
```

## Builder Automatico

**REPORT_BUILDER_*.md** contiene:
- Classi Python per generare HTML/PDF
- Tabelle formattate con risultati calcolo
- Tracciamento passaggi intermedi
- Firma digitale (metadata)

## Output Generati

```
project/
└── reports/
    ├── RELAZIONE_20260329_Elemento01.pdf
    ├── RELAZIONE_20260329_Elemento01.html
    └── Allegati/
        ├── Input.json
        └── Risultati.csv
```

## Stato Implementazione

- ✅ Template NTC2018 definito
- 🟨 Builder in fase di integrazione
- 🟨 Firma digitale da implementare

**Ultimo aggiornamento**: 2026-03-29
