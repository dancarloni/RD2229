# Fase W — Pipeline OCR per manuali tecnici storici

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ⬜ TODO |
| **Commit** | — |
| **Data prevista** | — |
| **Test pianificati** | ~40 |
| **Norma/e di riferimento** | n/a (infrastruttura OCR) |
| **Priorità** | Bassa |

---

## Descrizione

Pipeline OCR per estrazione automatica di tabelle e formule da manuali tecnici storici: Santarella "Il Cemento Armato", Giangreco "Teoria e Tecnica delle Costruzioni", Pozzati "Teoria e Tecnica delle Strutture". L'obiettivo è rendere disponibile il contenuto tabulare dei libri di testo come dati strutturati JSON, direttamente importabili negli archivi esistenti del progetto (cataloghi materiali, tabelle coefficienti, formule). La pipeline è progettata per funzionare su scansioni di qualità variabile (300-600 DPI).

---

## Teoria e fondamenti strutturali

### Architettura pipeline OCR

```text
PDF/Immagine scansionata
    └── Preprocessing (OpenCV)
         ├── Deskew (correzione inclinazione)
         ├── Denoise (riduzione rumore)
         └── Binarizzazione (Otsu threshold)
              └── Rilevamento tabelle
                   ├── Linee orizzontali/verticali (morfologia OpenCV)
                   └── Hough transform per tabelle senza bordi
                        └── OCR celle (Tesseract 5 / PaddleOCR)
                             └── Strutturazione JSON
                                  └── Validazione automatica
```

### Strumenti OCR disponibili

| Strumento | Tipo | Forza | Debolezza |
| --- | --- | --- | --- |
| Tesseract 5 | Open source | Configurabile, multilingua | Scarso su layout complessi |
| PaddleOCR | Open source (deep learning) | Ottimo su testi inclinati e rumorosi | Pesante (modelli GPU) |
| pdfplumber | Python (PDF layer) | Perfetto per PDF nativi (non scansioni) | Inutile su scansioni |
| tabula-py | Python (wrapper tabula-java) | Buono per tabelle PDF nativi | Solo PDF nativi |
| camelot | Python | Tabelle con linee visibili | Richiede Ghostscript |

### Tabelle target prioritarie

| Manuale | Tabella | Utilizzo nel progetto |
| --- | --- | --- |
| Santarella Vol.1 | Tabelle MIP (momenti incastro, portante) | Fase L (Cross-Pozzati) |
| Santarella Vol.2 | Carichi fissi solai, scale | Fase V |
| Pozzati Vol.2 | Fattori distribuzione Cross iterativo | Fase L |
| Pozzati Vol.3 | Coefficienti α lastra bidirezionale | Fase V |
| CNR 10011 | Tabelle ω (coefficienti instabilità acciaio) | Fase S (EC3) |
| NTC 1996 (Circolare) | Tabelle Φ riduzione snellezza muratura | Fase E/R |

### Riconoscimento formule matematiche

```text
Immagine formula
    └── Preprocessing: normalizzazione, padding
         └── Modello: LaTeX-OCR (open source) o MathPix API
              └── Output: stringa LaTeX → validazione simboli
                   └── Conversione: LaTeX → Python expression (sympy)
```

### Validazione automatica

Confronto valore estratto con valore noto (già implementato nel codice):

```text
errore_relativo = |valore_estratto - valore_atteso| / valore_atteso
soglia_accettazione = 1%    (per valori numerici)
soglia_accettazione = 5%    (per coefficienti empirici)
```

Se errore > soglia: flaggare per revisione manuale.

---

## Diagramma dipendenze subfasi

```text
W.1 — Setup pipeline OCR (pdf2image, pytesseract, OpenCV)
 └── W.2 — Estrazione tabelle Santarella (MIP, carichi fissi)
      └── W.3 — Estrazione tabelle Giangreco (travi continue, distribuzione)
           └── W.4 — Estrazione tabelle Pozzati (Cross, coefficienti α lastra)
                └── W.5 — Strutturazione dati JSON (schema archivi esistenti)
                     └── W.6 — Validazione (confronto con valori già implementati)
                          └── W.7 — Integrazione (import automatico in archivi)
```

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| Archivi materiali JSON | `data/materials/` | Schema di riferimento per dati estratti |
| Fase L (Cross-Pozzati) | `src/methods/rd2229/telaio/` | Validazione coefficienti Cross estratti |
| Fase V (solai) | `src/solai/` | Validazione coefficienti α lastra bidirezionale |
| registro_log | `src/core/registro_log.py` | Log pipeline: pagine elaborate, errori OCR |
| pdf2image | dipendenza opzionale | PDF → immagini PNG ad alta risoluzione |
| pytesseract | dipendenza opzionale | Wrapper Python per Tesseract 5 |
| opencv-python | dipendenza opzionale | Preprocessing: deskew, denoise, binarizzazione |
| tabula-py | dipendenza opzionale | Estrazione tabelle da PDF nativi (non scansioni) |

---

## Riferimenti normativi e bibliografici

| Riferimento | Utilizzo |
| --- | --- |
| Santarella L. — Il Cemento Armato Vol.1 e Vol.2 (1968) | Fonte primaria tabelle MIP, carichi, scale |
| Giangreco E. — Teoria e Tecnica delle Costruzioni Vol.1-3 (1983) | Travi continue, coefficienti distribuzione |
| Pozzati P. — Teoria e Tecnica delle Strutture Vol.1-3 (1980) | Cross iterativo, lastre bidirezionali |
| CNR 10011/1988 | Tabelle ω instabilità acciaio |
| Smith R. et al. — An Overview of the Tesseract OCR Engine (2007) | Riferimento Tesseract |
| PaddleOCR documentation (Baidu 2020) | Riferimento PaddleOCR deep learning |
| LaTeX-OCR — Lukas Blecher (2021) | Riconoscimento formule matematiche open source |

---

## Struttura file/directory prevista

```text
src/ocr/
├── __init__.py              # Export pubblico pipeline OCR
├── pipeline.py              # (~200 righe) orchestrazione: input → JSON output
├── preprocessing.py         # (~150 righe) OpenCV: deskew, denoise, binarizzazione, resize
├── tabelle.py               # (~200 righe) rilevamento tabelle, estrazione celle, strutturazione
├── formule.py               # (~150 righe) riconoscimento formule LaTeX-OCR, conversione sympy
└── validazione.py           # (~100 righe) confronto con valori noti, flag per revisione

data/ocr/
├── santarella/              # Pagine PDF scansionate (non nel repo — gitignored)
│   ├── vol1_cap3.pdf
│   └── vol2_cap6.pdf
├── giangreco/               # Pagine PDF scansionate
└── pozzati/                 # Pagine PDF scansionate

data/ocr/estratti/
├── santarella_mip.json      # Tabelle MIP estratte e validate
├── pozzati_cross.json       # Coefficienti Cross estratti
└── pozzati_lastra.json      # Coefficienti α lastra bidirezionale

tests/
├── test_preprocessing.py    # (~10 test) deskew, denoise su immagini campione
├── test_tabelle.py          # (~15 test) estrazione tabelle da immagini di test
├── test_formule.py          # (~10 test) LaTeX-OCR su formule campione
└── test_validazione.py      # (~10 test) confronto estratto vs atteso, flag errori
```

---

## Subfasi pianificate

### W.1 — Setup pipeline OCR

**Stato**: TODO

- [ ] Aggiungere dipendenze opzionali in `requirements-ocr.txt` separato (non in requirements.txt principale)
- [ ] Implementare check disponibilità: `try: import pytesseract` con fallback graceful
- [ ] Installazione Tesseract 5 binario su Windows/Linux con istruzioni nel README OCR
- [ ] Test su pagina campione (immagine sintetica con tabella nota): verifica pipeline end-to-end
- [ ] Benchmark qualità OCR: Tesseract vs PaddleOCR su campione 5 pagine
- [ ] Log: tempo elaborazione per pagina, tasso errore caratteri (CER)

### W.2 — Estrazione tabelle Santarella

**Stato**: TODO

- [ ] Scansionare/acquisire pagine rilevanti Santarella Vol.1 (tabelle MIP §3.x) e Vol.2 (carichi solai §6.x)
- [ ] Preprocessing specifico per Santarella: font tipografico anni '60 — calibrazione Tesseract
- [ ] Rilevamento tabelle con bordi: morfologia OpenCV (erode + dilate per linee orizzontali/verticali)
- [ ] Estrazione celle e parsing numerico (punti decimali, segni ±)
- [ ] Strutturazione JSON: `{"fonte": "Santarella Vol.1 Tab.3.x", "tipo": "MIP", "valori": [...]}`
- [ ] Validazione: confronto con tabella MIP già implementata in Fase L
- [ ] Test: pagina campione — verifica 10 valori estratti vs valori attesi

### W.3 — Estrazione tabelle Giangreco

**Stato**: TODO

- [ ] Acquisire pagine Giangreco rilevanti (travi continue, coefficienti distribuzione momenti)
- [ ] Preprocessing: Giangreco ha layout a 2 colonne — segmentazione colonne prima di OCR
- [ ] Estrazione tabelle con intestazioni multiriga
- [ ] Strutturazione JSON con metadati: capitolo, pagina, tipo tabella
- [ ] Validazione: confronto con formule analitiche note (trave continua a 2 campate)
- [ ] Test: tabella coefficienti trave a 3 campate — verifica valori

### W.4 — Estrazione tabelle Pozzati

**Stato**: TODO

- [ ] Acquisire pagine Pozzati Vol.2 (Cross iterativo) e Vol.3 (lastre bidirezionali)
- [ ] Tabelle Cross: coefficienti di ripartizione momenti (strutturati come matrice indicizzata per α = I/l)
- [ ] Tabelle lastra bidirezionale: α_x, α_y per β = L_x/L_y e condizioni di vincolo
- [ ] Strutturazione JSON compatibile con `src/solai/gettato_in_opera.py` (Fase V)
- [ ] Validazione: confronto α_x estratto con valore implementato in Fase V (se disponibile)
- [ ] Test: riga tabella α per β=1.5 (lastra quadrata) — verifica simmetria α_x = α_y

### W.5 — Strutturazione dati JSON

**Stato**: TODO

- [ ] Definire schema JSON comune per tutti i tipi di dati estratti
- [ ] Campi obbligatori: `fonte`, `norma_o_manuale`, `pagina`, `tipo`, `data_estrazione`, `validato`, `valori`
- [ ] Funzione `esporta_json(tabella_strutturata) -> dict` con schema validato
- [ ] Funzione `importa_in_archivio(json_estratto, archivio_target)` per integrazione
- [ ] Gestione conflitti: valore già presente nell'archivio → confronto, non sovrascrivere
- [ ] Test: 3 tipi di tabella → verifica schema JSON valido

### W.6 — Validazione automatica

**Stato**: TODO

- [ ] Raccolta "valori noti" da codice esistente (fasi A-V) come golden dataset
- [ ] Per ogni valore estratto: calcolo errore relativo vs valore noto (se disponibile)
- [ ] Soglie: < 1% accettato automaticamente; 1-5% flaggato per revisione; > 5% scartato
- [ ] Report validazione: tabella con valore estratto, valore atteso, errore%, esito
- [ ] Integrazione con registro_log: log errori sistematici (possibile calibrazione OCR)
- [ ] Test: golden dataset 20 valori — verifica classificazione automatica

### W.7 — Integrazione negli archivi esistenti

**Stato**: TODO

- [ ] Import automatico tabelle validate in `data/ocr/estratti/`
- [ ] Funzione `aggiorna_archivio(sorgente_json, archivio_json)` con merge selettivo
- [ ] Versioning dati: ogni aggiornamento archivio registrato con hash sorgente OCR
- [ ] CLI semplice: `python -m src.ocr.pipeline --input pagina.pdf --output estratto.json`
- [ ] Test: import tabella MIP estratta → verifica disponibilità in Fase L

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/ocr/__init__.py` | 15 | Export pubblico pipeline OCR |
| `src/ocr/pipeline.py` | 200 | Orchestrazione end-to-end: input → JSON |
| `src/ocr/preprocessing.py` | 150 | OpenCV: deskew, denoise, binarizzazione |
| `src/ocr/tabelle.py` | 200 | Rilevamento tabelle, estrazione celle |
| `src/ocr/formule.py` | 150 | LaTeX-OCR, conversione sympy |
| `src/ocr/validazione.py` | 100 | Confronto con valori noti, flag errori |
| `requirements-ocr.txt` | 15 | Dipendenze opzionali OCR separate |
| `tests/test_preprocessing.py` | 10 test | Deskew, denoise su immagini campione |
| `tests/test_tabelle.py` | 15 test | Estrazione tabelle da immagini di test |
| `tests/test_formule.py` | 10 test | LaTeX-OCR su formule campione |
| `tests/test_validazione.py` | 10 test | Confronto estratto vs atteso |

---

## Decisioni architetturali aperte

| Decisione aperta | Opzioni |
| --- | --- |
| Motore OCR principale | A) Tesseract 5 (leggero, open source, già consolidato) / B) PaddleOCR (più preciso, pesante) / C) Configurabile a runtime |
| Riconoscimento formule | A) LaTeX-OCR open source (sufficiente per formule strutturali) / B) MathPix API (più accurato, a pagamento) |
| Gestione scansioni protette da copyright | A) Solo pagine specifiche acquisite dall'utente / B) Nessun file scansionato nel repo (solo estratti JSON validati) |
| Formato dati estratti | A) JSON (coerente con archivi esistenti) / B) SQLite (più efficiente per grandi volumi) |
| Integrazione con requisiti principali | A) `requirements-ocr.txt` separato (evita dipendenze pesanti per chi non usa OCR) / B) Gruppo extras in `pyproject.toml` |

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Qualità scansioni variabile | Libri anni '60-'80: font usurati, pagine ingiallite, righe storte | Preprocessing aggressivo (deskew, denoise, contrast stretching) |
| Tabelle senza bordi visibili | Alcune tabelle in Pozzati usano solo spazi per allineamento | Rilevamento colonne da allineamento verticale testo |
| Font tipografico storico | Caratteri specifici anni '60 non riconosciuti da Tesseract standard | Training custom Tesseract su font campione (tessdata custom) |
| Formule con simboli greci e indici | Tesseract non gestisce bene σ, τ, γ, pedici/apici | LaTeX-OCR per formule; Tesseract solo per testo e numeri |
| Copyright manuali tecnici | I libri citati sono protetti da copyright | Non includere scansioni nel repo; solo estratti JSON come opera derivata di dati |
| Dipendenze di sistema | pdf2image richiede Poppler; pytesseract richiede Tesseract installato | Istruzioni di installazione esplicite; graceful degradation se assenti |

---

## Note di pianificazione

- La Fase W ha la priorità più bassa perché il suo valore dipende dalla disponibilità delle scansioni, che l'utente deve procurarsi autonomamente (copyright).
- I file PDF/immagini scansionati non devono essere inclusi nel repository git (`.gitignore` per `data/ocr/santarella/`, etc.); solo gli estratti JSON validati possono essere committati.
- La pipeline deve essere robusta al fallimento parziale: se una pagina non viene estratta correttamente, il sistema continua con le successive e registra l'errore nel log.
- Il valore principale della Fase W è la validazione automatica (W.6): anche senza OCR automatico, lo stesso framework può essere usato per validare dati inseriti manualmente.
- Considerare di avviare W.1 (setup) e W.6 (validazione) come infrastruttura utile indipendentemente dall'OCR vero e proprio.

## Storicizzazione

Nessuna sessione ancora — fase non avviata.
