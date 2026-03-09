# Fase Q — Relazione di calcolo professionale

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~60 |
| **Norma/e di riferimento** | n/a (infrastruttura report) |
| **Priorità** | Media |

---

## Descrizione

Generatore di relazione di calcolo professionale completa, ottimizzata per stampa A4. Integra automaticamente tutti i moduli di calcolo (A-P) in un documento strutturato con citazioni normative puntuali, grafici, tabelle e allegati. Export multi-formato: HTML, PDF via WeasyPrint, MD, DOCX via python-docx. Ogni `SingleCheckResult` da `src/core_calculus/contracts.py` contribuisce automaticamente alla sezione di competenza grazie al campo `riferimento_normativo`.

---

## Teoria e fondamenti strutturali

### Architettura del report (pattern Composite)

Il report è un albero di nodi. Ogni nodo ha un metodo `render(formato) -> str`:

```text
RelazioneDiCalcolo
 ├── Capitolo("1. Dati generali")
 │    ├── Sezione("1.1 Geometria")
 │    │    └── BloccoTesto / BloccoTabella
 │    └── Sezione("1.2 Materiali")
 ├── Capitolo("2. Azioni")
 ├── Capitolo("3. Analisi strutturale")
 ├── Capitolo("4. Verifiche")
 │    └── Sezione per ogni tipo di verifica
 └── Capitolo("Allegati")
      └── BloccoImmagine / BloccoGrafico
```

### Template A4

- Dimensioni: 210×297 mm, margini 2.5 cm su tutti i lati
- Corpo testo: 11pt, interlinea 1.4
- Titoli: H1=14pt, H2=12pt, H3=11pt bold
- Intestazione: nome progetto, data, professionista, n. pratica
- Piè di pagina: numero pagina / totale pagine, data stampa

### Citazione normativa automatica

Ogni `SingleCheckResult` porta il campo `riferimento_normativo: str` (es. `"NTC2018 §4.1.2.1.3 Tab.4.1.IV"`). Il motore di citazione:

```text
1. Raccoglie tutti i riferimento_normativo usati nel calcolo
2. Costruisce indice normativo automatico in appendice
3. Inserisce nota a piè di formula con §/Tab/Eq del riferimento
```

### Export multi-formato

| Formato | Libreria | Note |
| --- | --- | --- |
| HTML | built-in | Base per tutti gli altri export |
| PDF | WeasyPrint (opzionale) | HTML → PDF con CSS print media |
| DOCX | python-docx (opzionale) | Conversione struttura Composite → Document |
| MD | built-in | Markdown compatibile con Pandoc |
| TXT/ASCII | built-in | Compatibile con `tabulati_calcolo.py` Fase C |

### Embedding immagini

In HTML: data-URI base64 inline (già in `grafici_html.py` Fase K). In DOCX: file temporaneo + `document.add_picture()`. In MD: path relativo a directory `allegati/`.

---

## Diagramma dipendenze subfasi

```text
Q.1 — Layout e template A4
 └── Q.2 — Integrazione pipeline calcolo
      ├── Q.3 — Citazione automatica normativa
      └── Q.4 — Generazione sezioni obbligatorie
           ├── Q.5 — Gestione immagini personalizzate
           ├── Q.6 — Export multi-formato
           ├── Q.7 — Confronto tra norme (opzionale)
           └── Q.8 — Personalizzazione sezioni
                └── Q.9 — Test su casi reali
                     └── Q.10 — Documentazione utente
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Base per sezioni calcolo, passaggi intermedi |
| SingleCheckResult | `src/core_calculus/contracts.py` | Estrazione riferimento_normativo, esito verifica |
| GraficiHTML | `src/report/grafici_html.py` | Embedding immagini matplotlib in base64 |
| GraficiSollecitazioni | `src/grafici/sollecitazioni.py` | Diagrammi M/V/N per allegati |
| MaterialRepository | `src/materials/material_repository.py` | Elenco materiali usati nel progetto |
| registro_log | `src/core/registro_log.py` | Log generazione report, warning sezioni vuote |
| aiuto_contestuale | `src/ui/qt/aiuto_contestuale.py` | Stralci normativi citati nel report |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| NTC2018 §10 | Struttura obbligatoria relazione di calcolo |
| Circ. 7/2019 §C10 | Contenuti minimi relazione strutturale |
| DPR 380/2001 art.93 | Obbligo deposito relazione calcolo |
| WeasyPrint docs | HTML→PDF con CSS print media queries |
| python-docx docs | Generazione DOCX programmatica |

---

## Struttura file/directory prevista

```text
src/report/
├── report_builder.py       # (~400 righe) builder relazione, albero Composite
├── template_a4.py          # (~200 righe) layout A4, stili CSS, intestazione/piè di pagina
├── citazioni_normative.py  # (~150 righe) raccolta e indice riferimenti normativi
├── export_pdf.py           # (~100 righe) WeasyPrint HTML→PDF, opzionale
├── export_docx.py          # (~150 righe) python-docx, struttura → Document
└── confronto_norme.py      # (~200 righe) tabella comparativa risultati multinorma

src/ui/qt/
└── report_widget.py        # (~400 righe) GUI Qt: selezione sezioni, preview, export

tests/
├── test_report_builder.py  # (~25 test) costruzione albero, render HTML/MD
├── test_citazioni.py       # (~15 test) raccolta riferimenti, indice
└── test_export.py          # (~20 test) export HTML, MD; mock per PDF/DOCX
```

---

## Subfasi pianificate

### Q.1 — Layout e template A4

**Stato**: TODO

- [ ] Definire classe `TemplateA4` con parametri margini, font, colori
- [ ] Implementare CSS per stampa A4 (`@media print`, `@page`)
- [ ] Intestazione con: nome progetto, committente, professionista, data, n. pratica
- [ ] Piè di pagina con numero pagina e data stampa
- [ ] Stile tabelle: bordi, ombreggiatura righe alternate, header grassetto
- [ ] Stile blocchi formula: box grigio chiaro, font monospace
- [ ] Placeholder immagini: riquadro con dimensione e didascalia
- [ ] Test: render HTML pagina singola con tutti gli elementi

### Q.2 — Integrazione pipeline calcolo

**Stato**: TODO

- [ ] Definire interfaccia `FornitoreSezione` (protocollo) che ogni modulo di calcolo implementa
- [ ] Implementare `PipelineReport` che raccoglie sezioni da tutti i moduli registrati
- [ ] Registrazione automatica moduli via decoratore `@contribuisce_report`
- [ ] Ordinamento sezioni per capitolo/numero
- [ ] Gestione sezioni vuote (nessun calcolo eseguito per quel modulo)
- [ ] Test: pipeline con 3 moduli mock, verifica ordine e contenuto sezioni

### Q.3 — Citazione automatica normativa

**Stato**: TODO

- [ ] Raccolta di tutti i `riferimento_normativo` dai `SingleCheckResult`
- [ ] Deduplicazione e ordinamento (norma, §, tabella)
- [ ] Generazione indice normativo in appendice con tutte le citazioni usate
- [ ] Inserimento nota a piè di formula nel corpo del report
- [ ] Formato citazione standard: `[NTC2018 §4.1.2.1.3]`
- [ ] Test: 5 verifiche con riferimenti sovrapposti — verifica indice deduplicato

### Q.4 — Generazione sezioni obbligatorie

**Stato**: TODO

- [ ] Sommario automatico con numeri di pagina (HTML: ancora, PDF: generato da WeasyPrint)
- [ ] Capitolo 1: dati generali (descrizione opera, normativa applicata, metodo di analisi)
- [ ] Capitolo 2: materiali (tabella da MaterialRepository, con riferimento normativo)
- [ ] Capitolo 3: azioni (carichi, combinazioni NTC2018)
- [ ] Capitolo 4: analisi strutturale (risultati FEM o Cross-Pozzati)
- [ ] Capitolo 5: verifiche (una sezione per ogni tipo: flessione, taglio, torsione, SLE, ...)
- [ ] Allegati: grafici, tabelle dettagliate, estratti normativi
- [ ] Test: report completo con dati minimi — verifica struttura e lunghezza

### Q.5 — Gestione immagini personalizzate

**Stato**: TODO

- [ ] Widget Qt per upload immagine (file dialog, incolla da clipboard)
- [ ] Posizionamento immagine nel report: prima/dopo sezione, inline
- [ ] Didascalia immagine editabile
- [ ] Embedding base64 in HTML per portabilità
- [ ] Export file separato per DOCX (directory `allegati/`)
- [ ] Test: upload immagine PNG, verifica embedding HTML e path DOCX

### Q.6 — Esportazione multi-formato

**Stato**: TODO

- [ ] Export HTML: file self-contained con CSS e immagini inline
- [ ] Export MD: Markdown puro, immagini come path relativo
- [ ] Export TXT/ASCII: compatibile con tabulati Fase C (80 colonne)
- [ ] Export PDF: WeasyPrint (dipendenza opzionale — graceful degradation se assente)
- [ ] Export DOCX: python-docx (dipendenza opzionale)
- [ ] Test: export HTML e MD su report con 3 capitoli; mock per PDF/DOCX

### Q.7 — Confronto tra norme (opzionale)

**Stato**: TODO

- [ ] Tabella comparativa: stessa sezione verificata con NTC2018, NTC2008, DM96, RD2229
- [ ] Colonne: norma, M_Rd, V_Rd, N_Rd, esito, note
- [ ] Attivabile da flag `confronto_multinorma=True` in `PipelineReport`
- [ ] Evidenziare differenze significative (> 10%) con colore
- [ ] Test: sezione rettangolare 30×50 — confronto valori tra norme

### Q.8 — Personalizzazione sezioni report

**Stato**: TODO

- [ ] GUI Qt: checklist sezioni da includere/escludere
- [ ] Riordinamento sezioni tramite drag-and-drop
- [ ] Salvataggio profilo report (JSON) per riuso su progetti simili
- [ ] Sezioni custom: testo libero, immagine, tabella dati utente
- [ ] Test: report con 2 sezioni escluse — verifica sommario aggiornato

### Q.9 — Test su casi reali

**Stato**: TODO

- [ ] Report completo per trave in c.a. (flessione + taglio + SLE NTC2018)
- [ ] Report completo per pilastro (pressoflessione, lunghezza libera)
- [ ] Report completo per telaio piano (analisi + verifiche tutti gli elementi)
- [ ] Verifica dimensioni file output (HTML < 5MB, PDF < 10MB per 50 pagine)
- [ ] Verifica correttezza riferimenti normativi (campionamento manuale 10%)
- [ ] Test regressione: report generato = report atteso (hash o diff strutturale)

### Q.10 — Documentazione utente

**Stato**: TODO

- [ ] Help contestuale Qt su ogni campo del report_widget
- [ ] Guida "Come generare la relazione di calcolo" (testo in-app)
- [ ] Guida "Personalizzazione e export" (testo in-app)
- [ ] Esempi di report pre-compilati per casi tipici
- [ ] Log errori di generazione con suggerimenti correzione

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/report/report_builder.py` | 400 | Builder relazione, albero Composite, render |
| `src/report/template_a4.py` | 200 | Layout A4, CSS print, intestazione/piè pagina |
| `src/report/citazioni_normative.py` | 150 | Raccolta, deduplicazione, indice riferimenti |
| `src/report/export_pdf.py` | 100 | WeasyPrint HTML→PDF (opzionale) |
| `src/report/export_docx.py` | 150 | python-docx Composite→Document (opzionale) |
| `src/report/confronto_norme.py` | 200 | Tabella comparativa multinorma |
| `src/ui/qt/report_widget.py` | 400 | GUI Qt generazione report |
| `tests/test_report_builder.py` | 25 test | Albero, render HTML/MD |
| `tests/test_citazioni.py` | 15 test | Raccolta riferimenti, indice |
| `tests/test_export.py` | 20 test | Export HTML/MD, mock PDF/DOCX |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Pattern contribuzione moduli al report | A) Decoratore `@contribuisce_report` / B) Registrazione esplicita in `PipelineReport` |
| Dipendenze PDF/DOCX opzionali | A) Warning se assenti, export disabilitato / B) Errore esplicito con istruzioni installazione |
| Formato citazione normativa | A) Nota a piè di formula `[NTC2018 §4.1.2.1.3]` / B) Superscript con rimando a indice |
| Confronto multinorma: quando attivarlo? | A) Flag esplicito utente / B) Sempre presente ma sezione collassabile in HTML |
| Numerazione pagine in HTML | A) CSS counter (solo print) / B) Script JS per anteprima browser |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| WeasyPrint su Windows | Dipendenze native (Cairo, Pango) difficili su Windows | Documentare installazione, graceful degradation |
| Sincronizzazione moduli calcolo | Ogni modulo deve implementare `FornitoreSezione` | Protocollo Python (structural subtyping) senza ereditarietà |
| Dimensione file HTML | Immagini base64 inline aumentano dimensione | Limite immagini per sezione, compressione PNG |
| Retrocompatibilità tabulati C | `TabulatoCalcolo` (Fase C) usa ASCII — deve restare utilizzabile | Report builder come livello sopra, non sostituto |

---

## Note di pianificazione

- La Fase Q dipende logicamente dal completamento di almeno A-J per avere dati reali da mostrare.
- Il pattern Composite consente di aggiungere nuovi tipi di blocco (es. BloccoFormula, BloccoGrafico3D) senza modificare il builder.
- La sezione confronto multinorma (Q.7) richiede che le norme DM96, RD2229, NTC2018 restituiscano tutte `SingleCheckResult` con la stessa struttura.
- La GUI `report_widget.py` deve essere integrata nella finestra principale Qt come pannello laterale o tab separato.

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
