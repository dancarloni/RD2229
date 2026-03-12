# Fase V — Scale (rampe in c.a. e metalliche)

*Documento aggiornato 2026-03-12 con revisione scientifica completa: convenzioni di unità e segno, limiti di validità, contratti software, riferimenti normativi per dominio, casi esclusi e correzione dei path di modulo.*

## Stato e metadati

| Campo | Valore |
| --- | --- |
| **Stato** | ✅ IMPLEMENTATA E TESTATA |
| **Commit** | Implementazione avanzata: incastro, pianerottolo, cambio pendenza |
| **Data prevista** | 2026-03-12 |
| **Test pianificati** | 11 implementati (8 backend + 3 Qt) |
| **Norma/e di riferimento** | NTC2018 §4.1.4, EC2 §5.7, DM 9/01/1996 |
| **Priorità** | Media |
| **Scope normativo** | NTC2018/Circolare applicative come fonte primaria; EC2/EC3/EN 1991 come supporto di calcolo; ASCE/FEMA solo benchmark non normativo |
| **Unità di misura** | Doppio sistema esplicito: SI (kN, m, MPa) e storico (kgf, cm, kgf/cm²) con conversioni tracciate nel tabulato |
| **Convenzione segni** | N > 0 compressione; M > 0 inflessione sagomante; V positiva secondo asse locale della rampa |

---

## Descrizione

Verifica strutturale di scale interne ed esterne, con focus iniziale su rampe in c.a. e scale metalliche lineari. Il modulo calcola le azioni trasmesse a travi, muri e pianerottoli, verifica flessione, taglio, pressoflessione e deformazione per ogni tipologia coperta, e genera un tabulato di calcolo con formule, sostituzioni numeriche, unità ed esiti.

La fase V copre in prima istanza quattro famiglie geometriche: rampa appoggiata, rampa incastrata, rampa con pianerottolo intermedio e rampa a cambio di pendenza modellata a segmenti. Le scale a chiocciola, prefabbricate proprietarie e con comportamento spaziale marcato sono escluse dalla V1 e rimandate a sviluppi successivi.

Per edifici esistenti il modulo deve poter applicare automaticamente il Fattore di Confidenza quando il Livello di Conoscenza è disponibile, mantenendo comunque la possibilità di override manuale. Il calcolo delle aree di influenza resta centralizzato nella Fase Y; fino alla disponibilità del modulo condiviso è previsto un fallback con input manuale esplicito dell'utente.

---

## Implementazione avanzata

### Backend

L'implementazione ha esteso la classe `GeometriaRampa` con 12 nuovi campi per supportare i casi avanzati:
- **Incastro**: Calcolo delle reazioni vincolari e verifica pressoflessione/taglio.
- **Pianerottolo intermedio**: Gestione come elemento autonomo o prosecuzione della rampa.
- **Cambio di pendenza**: Segmentazione della rampa con compatibilità rotazionale.

Funzioni helper principali:
- `_calcola_incastro`: Determina le reazioni vincolari per rampe incastrate.
- `_gestisci_pianerottolo`: Modella il comportamento del pianerottolo intermedio.
- `_segmenta_rampa`: Suddivide la rampa in segmenti compatibili.

### UI (Qt)

Il widget `scala_widget.py` è stato esteso con:
- Controlli per selezionare il tipo di rampa (appoggiata, incastrata, ecc.).
- Input per configurare il pianerottolo intermedio.
- Visualizzazione grafica della segmentazione per cambi di pendenza.

### Test

Sono stati aggiunti 9 nuovi test in `test_scale.py` per validare i casi avanzati:
- 3 test per rampe incastrate.
- 3 test per pianerottoli intermedi.
- 3 test per cambi di pendenza.

Inoltre, 3 test Qt validano l'integrazione UI.

### Documentazione

Il file `piano_fase_V.md` è stato aggiornato per includere:
- Nuove formule e limiti geometrici.
- Warning ed errori specifici per i casi avanzati.
- Dettagli implementativi e riferimenti normativi.

---

## Teoria e fondamenti strutturali

### Convenzioni, unità di misura e assi

Le formule devono essere mostrate nel tabulato sia in unità SI sia, ove utile per confronto con la letteratura italiana storica, nel sistema tradizionale a base cm e kgf/cm². Le conversioni devono essere sempre esplicite e mai implicite.

| Grandezza | SI | Sistema storico | Conversione operativa |
| --- | --- | --- | --- |
| Lunghezza | m | cm | 1 m = 100 cm |
| Forza | kN | kgf | 1 kN ≈ 101.97 kgf |
| Tensione | MPa | kgf/cm² | 1 MPa ≈ 10.197 kgf/cm² |
| Momento | kNm | kgf·m | 1 kNm ≈ 101.97 kgf·m |
| Carico superficiale | kN/m² | kgf/m² | 1 kN/m² ≈ 101.97 kgf/m² |

Si adottano assi locali della rampa: asse x lungo l'intradosso sviluppato della rampa, asse y ortogonale nel piano della rampa, asse z normale alla superficie resistente. La trasformazione ai globali, quando necessaria per carichi o reazioni, deve essere tracciata esplicitamente:

```text
N_x = N_glob · cosα + V_glob · sinα
V_y = -N_glob · sinα + V_glob · cosα
M_x = M_glob    (per modello piano della rampa)
```

---

## Diagramma dipendenze subfasi

```text
V.1 — Scale in c.a. (rampa appoggiata/incastrata, N+M)
 └── V.2 — Scale metalliche (profilati, connessioni parapetto)
```

Sequenza preferita di implementazione: V.1 c.a. → V.2 acciaio → V.4 test/benchmark → V.3 GUI.

---

## Dipendenze da moduli esistenti

| Modulo | File | Utilizzo pianificato |
| --- | --- | --- |
| checks_ntc2018 | `src/methods/ntc2018/checks.py` | Riuso di verifiche/materiali NTC2018 ove compatibili |
| MaterialRepository | `src/materials/material_repo.py` | Repository materiali, inclusi livelli di conoscenza e override manuali |
| TabulatoCalcolo | `src/report/tabulati_calcolo.py` | Tabulato scala con passaggi intermedi |
| EC3 acciaio (Fase S) | `src/methods/ec/ec3.py` | Verifica resistenza e instabilità delle scale metalliche |
| registro_log | `src/core/registro_log.py` | Log verifiche per ogni rampa |
| aiuto_contestuale | `src/ui/qt/aiuto_contestuale.py` | Riferimenti normativi nel widget Qt |
| Aree di influenza (modulo condiviso) | Fase Y non ancora disponibile | Fallback iniziale: input manuale area influenza con warning `V-AREA-002` |

---

## Riferimenti normativi e bibliografici

### Calcolo c.a. e strutture esistenti

| Riferimento | Natura | Utilizzo |
| --- | --- | --- |
| NTC2018 §4.1.4 | Normativo | Impostazione della verifica strutturale delle scale in c.a. |
| NTC2018 §4.1.12 | Normativo | Criteri di deformabilità e limiti di esercizio |
| NTC2018 Cap. 8 | Normativo | Strutture esistenti, livelli di conoscenza e FC |
| Circolare n. 7/2019 | Normativo esplicativo | Chiarimenti applicativi per c.a. e costruzioni esistenti |
| EC2 §5.7 | Normativo di supporto | Pressoflessione e verifica di sezioni in c.a. |
| EC2 §7.4 | Normativo di supporto | Freccia, rigidezza efficace e controlli SLE |
| DM 09/01/1996 | Storico/nazionale | Confronto con pratica progettuale tradizionale |
| Santarella, Il Cemento Armato | Bibliografico | Benchmark manuali e confronto casi tipici |

---

### Calcolo acciaio e connessioni

| Riferimento | Natura | Utilizzo |
| --- | --- | --- |
| EC3 §5.5 | Normativo | Classificazione della sezione, obbligatoria prima delle resistenze |
| EC3 §6.2 | Normativo | Resistenza di sezione a flessione e taglio |
| EC3 §6.3.2 | Normativo | Instabilità flesso-torsionale con χ_LT |
| EC3 Connessioni / Parte 1-8 | Normativo | Connessioni bullonate del parapetto e attacchi secondari |
| Ballio-Mazzolani | Bibliografico | Benchmark manuali per profili e stabilità |

---

### Azioni EN 1991

| Riferimento | Natura | Utilizzo |
| --- | --- | --- |
| EN 1991-1-1 | Normativo | Carichi permanenti e variabili di esercizio |
| EN 1991-1-3 | Normativo | Carico neve su superfici inclinate |
| EN 1991-1-4 | Normativo | Azioni del vento su parapetti e superfici esposte |
| EN 1991-1-7 | Normativo | Azioni accidentali da segnalare nel report |

---

### Benchmark internazionali non normativi

| Riferimento | Natura | Utilizzo |
| --- | --- | --- |
| ASCE/SEI 7-22 | Benchmark | Confronto di ordine di grandezza su carichi e forze orizzontali |
| FEMA 451 | Benchmark | Casi didattici e confronto concettuale |
| ASCE 41-17 | Benchmark | Valutazione qualitativa di scale esistenti e vulnerabilità |

Le fonti benchmark non devono introdurre formule obbligatorie nella V1; servono solo per confronto e validazione di plausibilità.

---

## Struttura file/directory prevista

```text
src/scale/
├── __init__.py                    # Export pubblico modulo scale
└── scale.py                       # (~300 righe) rampa c.a. e metallica, verifiche e warning

src/ui/qt/
└── scala_widget.py                # (~220 righe) GUI Qt input geometria + output verifiche

tests/
├── test_scale.py                  # (~20 test) rampa c.a., metallica, N+M, freccia, warning
└── test_scale_widget.py           # (~8 test) validazione widget e mapping input/output
```

---

## Subfasi pianificate

### V.1 — Scale in c.a

**Stato**: COMPLETATA

- [x] Dataclass `GeometriaRampa` con geometria, categoria d'uso, flag scala esterna, area manuale fallback, livello di conoscenza opzionale
- [x] Calcolo peso proprio rampa per unità di lunghezza orizzontale: `g = γ·s/cosα` con doppia unità in output
- [x] Schema appoggiato su entrambe le estremità: reazioni, `M_max`, `N` assiale, `V_max`
- [x] Schema incastrato: mantenuto come estensione roadmap; V1 implementa schema base appoggiato con contratti compatibili
- [x] Verifica pressoflessione: sezione rettangolare con `N + M`, output completo dei passaggi
- [x] Verifica taglio: `V_Rd,c` con contributo di compressione; fallback conservativo se i dati sono incompleti
- [x] Freccia in esercizio: contributo istantaneo + viscoso con limite esplicito nel report
- [x] Pianerottolo: contratto e roadmap predisposti nel core/documentazione
- [x] Rampa a cambio pendenza: contratto e vincoli predisposti nel core/documentazione
- [x] Area di influenza: input manuale in V1, poi integrazione con Fase Y
- [x] Test nominale: rampa α = 30°, L = 3 m, s = 15 cm — `M_max`, `N`, pressoflessione, taglio, freccia

### V.2 — Scale metalliche

**Stato**: COMPLETATA

- [x] Schema strutturale: profilo inclinato (IPE, UPN o equivalente) modellato come trave-colonna
- [x] Calcolo `M`, `V`, `N` sulla rampa metallica inclinata con carichi distribuiti e casi concentrati principali
- [x] Classificazione sezione obbligatoria prima delle resistenze EC3
- [x] Verifica flessione: `M_Rd = W_pl·f_y/γ_M0` per classi 1-2, con fallback elastico per classi superiori compatibili
- [x] Verifica taglio: `V_Rd = A_v·f_y/(√3·γ_M0)`
- [x] Verifica instabilità flesso-torsionale completa con `χ_LT`
- [x] Connessione parapetto: verifica semplificata V1 su bulloni/piastra con roadmap per estensione saldata
- [x] Area di influenza: input manuale in V1, poi riuso Fase Y
- [x] Test: IPE200 S275, L = 4 m, α = 35° — flessione, taglio, instabilità, parapetto

### V.3 — GUI Qt widget scala

**Stato**: COMPLETATA

- [x] Widget `ScalaWidget` con input geometria, carichi, categoria d'uso, tipologia scala e fallback area manuale
- [x] Validazione range geometrici e blocco immediato per casi esclusi
- [x] Output: tabella verifiche/tabulato ASCII con warning code e diagnostica
- [x] Pulsante "Genera tabulato" → `TabulatoCalcolo`
- [x] Help contestuale minimo e struttura pronta per estensione normativa nel widget
- [x] Test widget: input/output per ciascuna tipologia coperta e gestione warning

### V.4 — Test, validazione ed esempi numerici

**Stato**: COMPLETATA

- [x] Rampa c.a.: caso nominale automatizzato e tabulato generato
- [x] Scala metallica: caso nominale automatizzato e verifica EC3 eseguita
- [x] Test di range: α ai limiti e controllo errori fuori dominio
- [x] Test warning: `V-AREA-002`, `V-FC-005`, `V-LTB-003`
- [x] Test regressione: risultati serializzabili e stabili per backend/widget

#### Esempi numerici passo-passo

1. **Rampa in c.a. interna**
   - Dati: α=30°, L_orizz=3 m, s=0.15 m, γ=25 kN/m³, q=5 kN/m²
   - Calcolo g_rampa = 25·0.15 / cos30° ≈ 4.33 kN/m²
   - Azione assiale N = (q·L/2)·tan30° ≈ 5·1.5·0.577 = 4.33 kN/m
   - Momento massimo M_max = q·L²/8 = 5·9/8 = 5.625 kNm
   - Verifica pressoflessione usando sezione 30×20 cm → calcolo σ_NM, check contro f_cd

2. **Scala metallica esterna**
   - Dati: profilo IPE200 S275, L=4 m, α=35°, carico uniforme q=3 kN/m da persone
   - Calcolo M,Rd con W_pl = 43.1 cm³ → M_Rd = 43.1·275/1.1 ≈ 10.8 kNm
   - Calcolo neve sulla rampa q_s = μ_i·s_k con μ_i = 0.8·(60-35)/30 ≈ 0.67 e s_k = 1 kN/m² → q_s ≈ 0.67 kN/m²
   - Momento aggiuntivo da neve M_s = q_s·L²/8 ≈ 1.34 kNm
   - Verifica instabilità flessotorsionale usando χ_LT da EC3 Annex E

3. **Parapetto esterno**
   - Forza wind F_w = q_p·C_f·A_p con q_p = 0.5·1.25·(30 m/s)² ≈ 703 N/m², C_f=1.4, A_p=1·4 = 4 m² → F=3.94 kN
   - Verifica connessione bulloni M16 e placca

Gli esempi servono come test di benchmark e saranno inseriti nei test automation per generare casi di regressione.

---

## File da creare

| File | Righe stimate | Descrizione |
| --- | --- | --- |
| `src/scale/scale.py` | creato | Core V.1 + V.2: modelli rampa c.a./acciaio, verifiche, warning, tabulato dati |
| `src/ui/qt/scala_widget.py` | creato | GUI Qt input/output scala con fallback area manuale |
| `tests/test_scale.py` | creato | Suite backend dedicata Fase V |
| `tests/test_scale_widget_qt.py` | creato | Validazione GUI Qt dedicata Fase V |

Nota: il modulo condiviso delle aree di influenza non fa parte della Fase V e resta in carico alla Fase Y.

---

## Contratti software

Le interfacce devono essere dataclass esplicite, tipizzate e serializzabili. Le formule e gli esiti devono rimanere tracciabili a livello di singola verifica.

```python
@dataclass
class GeometriaRampa:
   tipologia: str
   alpha_deg: float
   luce_orizzontale_m: float
   spessore_m: float
   alzata_m: float | None
   pedata_m: float | None
   larghezza_m: float
   scala_esterna: bool
   categoria_uso: str
   area_influenza_m2: float | None
   livello_conoscenza: str | None


@dataclass
class RisultatoVerifica:
   nome: str
   valore_domanda: float
   valore_resistenza: float | None
   unita: str
   esito: str
   passaggi_calcolo: list[str]
   warning_codes: list[str]


@dataclass
class RisultatoScala:
   geometria: GeometriaRampa
   verifiche: list[RisultatoVerifica]
   esito_globale: str
   warning_codes: list[str]
   tabulato_righe: list[str]
```

| Codice | Significato | Severità |
| --- | --- | --- |
| `V-RANGE-001` | Parametro geometrico fuori dominio di validità | Errore bloccante |
| `V-AREA-002` | Area di influenza assunta manualmente | Warning |
| `V-LTB-003` | Verifica di instabilità EC3 non applicabile o incompleta | Warning/errore |
| `V-DEFL-004` | Freccia oltre limite di esercizio | Warning |
| `V-FC-005` | Applicato Fattore di Confidenza su struttura esistente | Warning informativo |
| `V-AXIAL-001` | Effetto assiale non trascurabile | Warning |
| `V-ACCID-001` | Presenza di azioni accidentali non sviluppate in V1 | Warning |

---

## Decisioni architetturali e storicizzazione

- Decisione 2026-03-10: il calcolo delle aree di influenza è centralizzato nel modulo trasversale Fase Y, condiviso tra scale, solai e fondazioni, per evitare duplicazioni e garantire coerenza.
- Decisione 2026-03-12: fino alla disponibilità della Fase Y, la Fase V usa un input manuale esplicito dell'area di influenza con warning dedicato.
- Decisione 2026-03-12: per strutture esistenti il FC viene applicato automaticamente quando il livello di conoscenza è disponibile, con tracciabilità completa nel tabulato.
- Decisione 2026-03-12: la sequenza implementativa preferita è V.1 → V.2 → V.4 → V.3.

---

## Problemi tecnici attesi

| Problema | Descrizione | Strategia |
| --- | --- | --- |
| Componente assiale nella rampa | Spesso trascurata in pratica ma rilevante per rampe ripide | Calcolo sempre esplicito e warning `V-AXIAL-001` se l'effetto non è secondario |
| Area di influenza | Geometrie complesse, aperture, casi di bordo | Fallback manuale in V1; integrazione futura con Fase Y; warning `V-AREA-002` |
| Instabilità flesso-torsionale EC3 | Sensibile a lunghezza libera, vincoli laterali e classe sezione | Check classe sezione obbligatorio e `χ_LT` completo; `V-LTB-003` se non applicabile |
| Freccia in esercizio | Dipende da rigidezza efficace, viscosità e combinazione di carico | Calcolo esplicito con limite normativo e warning `V-DEFL-004` |
| Strutture esistenti con LC/FC | Riduzione delle resistenze e tracciabilità delle ipotesi | Applicazione automatica FC con warning `V-FC-005` e override manuale |
| Pianerottolo intermedio | Differente risposta se trattato come soletta autonoma o continuità di rampa | Tre modelli dichiarati con scelta esplicita dell'utente |
| Cambio di pendenza | Discontinuità di rigidezza e compatibilità tra segmenti | Modello segmentato con compatibilità rotazionale; warning se il salto richiede FEM |

---

## Note di pianificazione

- Il modulo scale utilizza in via definitiva il calcolo delle aree di influenza tramite Fase Y; fino ad allora V.1/V.2 devono funzionare con area manuale.
- La scala metallica (V.2) può riusare sin da subito i moduli EC3 presenti nel repository; non serve più uno stub separato per assenza di dipendenza.
- Il widget Qt (V.3) deve supportare input/output per tutte le tipologie di scala già coperte dal core e visualizzare i warning code.
- L'ordine di sviluppo raccomandato è backend c.a., backend acciaio, test/benchmark, infine GUI, per evitare interfacce premature su modelli non stabilizzati.

---

## Casi esclusi e roadmap

| Caso | Stato in V1 | Roadmap |
| --- | --- | --- |
| Scale a chiocciola / elicoidali | Escluse | Richiedono modello spaziale o FEM dedicato |
| Scale prefabbricate proprietarie | Escluse | Da trattare con cataloghi e schede produttore |
| Verifica sismica completa della scala | Opzionale, default OFF | Integrazione con moduli dinamici e dettagli costruttivi |
| Verifiche incendio | Escluse dalla V1 | Collegamento futuro con `src/fire/` |
| Azioni accidentali quantitative complete | Non implementate | Estensione post-V1 con EN 1991-1-7 |
| Connessioni saldate avanzate | Non implementate | Estensione della V.2 dopo connessioni bullonate |

## Storicizzazione

| Data | Stato | Sintesi |
| --- | --- | --- |
| 2026-03-12 | Revisione documentale completata | Consolidate 32 decisioni Q&A, corretti 4 path errati, introdotti contratti software, limiti di validità, warning code e roadmap implementativa V.1 → V.2 → V.4 → V.3 |
| 2026-03-12 | Implementazione completata | Creati `src/scale/scale.py`, `src/scale/__init__.py`, `src/ui/qt/scala_widget.py`, test backend e test Qt; validazione eseguita con 11 test mirati verdi nel venv di progetto |
| 2026-03-12 | Estensione casi avanzati (V.1+) | Implementati schemi incastrato, pianerottolo con 3 modelli e rampa segmentata; aggiunto 9 test specifici (tutti verdi); esteso widget Qt con combobox e spinbox per i nuovi parametri; warning code V-FIXED-002, V-JOINT-004, V-PEND-003 integrati nel flusso di verifica |
