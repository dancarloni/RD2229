# D.3 — Traliccio Reticolare Piano (Cordolo Metallico Reticolare)
# Contesto completo per implementazione futura

## Concetto chiave

Il traliccio e' disposto ORIZZONTALMENTE IN PIANTA sulla sommita' del muro.
Entrambi i correnti e le diagonali sono nello spessore della muratura.
Il cordolo si oppone ai meccanismi fuori piano (ribaltamento, spanciamento,
cuneo d'angolo) con la rigidezza nel piano di maggiore inerzia.

NON e' un traliccio verticale. Il piano XY del solutore viene reinterpretato
come piano orizzontale: X = lungo il muro, Y = spessore muro (trasversale).

## Decisioni Q&A complete (3 round, 35 domande)

### Geometria e disposizione
- Profondita' traliccio: configurabile dall'utente, default = spessore muro
- Sviluppo in pianta: singolo muro rettilineo OPPURE anello chiuso perimetrale
- Angoli (se anello): nodo rigido saldato OPPURE piastra d'angolo bullonata
- Altezza sezione trasversale verticale: calcolata dal profilo, non rilevante
  (per piatti saldati e' pochi mm = somma spessori piatti)
- Il traliccio e' continuamente connesso alla sommita' del muro (intimamente
  collaborante). Muro e traliccio hanno rigidezze diverse ma spostamento
  unico congruente ed equilibrato.

### Modello strutturale e carichi
- F da cinematica.py (automatico), distribuita proporzionalmente al modo di
  collasso OPPURE calcolata come discreta ai nodi, a scelta dell'utente
- Il traliccio e' caricato sempre nella direzione di maggiore rigidezza
- Schema statico: tutte le configurazioni supportate (appoggiato, continuo,
  anello chiuso)
- Solo forze orizzontali nel piano del traliccio (no carichi gravitazionali)
- Combinazioni: tutte le norme supportate + custom utente (attivabili/disattivabili)
- Verifiche: SLU + SLE + fatica ciclica sismica (TODO placeholder, metodo da definire)

### Collegamento traliccio-muro
- Tipo: barre inghisate / tasselli chimici / connettori, tutti selezionabili
- Rigidezza: configurabile (cerniera / incastro parziale)
- Corrente caricato: entrambi, in funzione della direzione del sisma
- Grado di collaborazione: configurabile (vincolo cinematico puro /
  azione composta / intermedio)

### Integrazione con cinematica.py
- Il cordolo diventa vincolo in sommita' nel modello cinematico (DEFAULT)
- Flusso: cinematica -> F -> traliccio -> K -> cinematica ricalcola alpha_0 (TODO futuro)
- Tutti i meccanismi fuori piano attivi di default, disattivabili singolarmente
- Nodo d'angolo: verifica equilibrio locale + modello globale ad anello

### Dimensionamento
- Verifica: dato schema + profili -> esito
- Dimensionamento inverso: dato schema -> profili minimi per alpha_0 target + rigidezza
- L'utente puo' fissare lo schema e il software propone i profili minimi,
  OPPURE il software propone entrambi (schema + profili)

### Output e verifiche
- Output completo: rigidezza/resistenza (input per cinematica) + verifica aste +
  connessioni nodi + collegamento muro + tabulato integrato e standalone
- Normativa acciaio: selezionabile (NTC2018 SLU / TA storica)
- Instabilita': entrambi i piani (orizzontale e verticale), selezionabile
- Uso standalone: SI, anche senza contesto muratura

### Solutore e vincoli
- Piano XY reinterpretato come orizzontale (stesse coordinate, nessun flag)
- Vincoli: appoggi fissi estremi + molle distribuite lungo corrente (configurabili)
- Unita': selezionabile tramite unita_misura.py
- Persistenza: miglior giudizio (suggerito: dentro struttura dati edificio)
- Report: integrato + standalone esportabile

### Priorita' implementativa (consigliata)
1. D.3.1 Generatore schemi (Warren/Pratt + pre-dimensionamento + anteprima)
2. D.3.2 Adattamento solutore (molle, carichi distribuiti, rigidezza globale)
3. D.3.3 Modulo cordolo reticolare (dataclass, integrazione F da cinematica)
4. D.3.4 Verifiche aste (compressione, trazione, instabilita', connessioni)
5. D.3.5 Integrazione cinematica (ritegno sommitale, ricalcolo alpha_0)
6. D.3.6 Nodo d'angolo (cantonali)
7. D.3.7 Report e tabulato
8. D.3.8 Test
9. D.3.9 Tool disegno grafico avanzato (FASE FUTURA, non in D.3)

## File da creare

| File | Tipo | Contenuto |
|------|------|-----------|
| `src/steel/traliccio_generatore.py` | NUOVO | genera_warren(), genera_pratt(), suggerimento profili, anteprima matplotlib, validazione geometrica |
| `src/elements/cordolo_reticolare.py` | NUOVO | CordoloReticolare dataclass, da_cinematica(), verifica/dimensiona, enums |

## File da modificare

| File | Modifica |
|------|----------|
| `src/steel/traliccio_2d.py` | Aggiungere: molle distribuite ai nodi, carico distribuito su corrente (forze nodali equivalenti), output rigidezza globale K. NON toccare algoritmo core Gauss. |
| `src/methods/muratura/cinematica.py` | Aggiungere parametro opzionale `ritegno_sommitale` (forza H o rigidezza K) alle funzioni di meccanismo. Aggiungere RIBALTAMENTO_CANTONALE a TipoMeccanismo enum. |
| `src/report/tabulati_calcolo.py` | Sezione dedicata cordolo reticolare |

## File esistenti da riusare (NON modificare se non necessario)

| File | Cosa riusare |
|------|-------------|
| `src/steel/traliccio_2d.py` (~330 righe) | Solutore rigidezza diretta, Gauss con pivoting |
| `src/steel/connessioni.py` (~380 righe) | Saldature + bulloni per verifiche nodi |
| `src/steel/verifiche_ta.py` (~410 righe) | Verifiche asta singola (flessione, taglio, instabilita', Von Mises). ATTENZIONE: accetta solo ProfiloAcciaio da sagomario, potrebbe servire adapter per piatti/angolari. |
| `src/steel/sagomario.py` (~188 righe) | 87 profili standard (IPE, HEA, HEB, HEM, UPN) |
| `src/methods/muratura/cinematica.py` (~654 righe) | 4 meccanismi + analisi completa, ForzaCatena, ParametriSismici |
| `src/elements/cordolo.py` (~350 righe) | CordoloMetallico con input manuale (A, Wx, h). Enum METALLICO_RETICOLARE dichiarato ma NON implementato. |
| `src/core/unita_misura.py` | Sistema unita' selezionabile |

## Interfacce chiave tra moduli

### cinematica.py -> cordolo_reticolare.py
- `RisultatoMeccanismo` contiene `alpha_0`, `passaggi_calcolo`
- La forza F per il traliccio si ricava dall'equilibrio del meccanismo
- `ForzaCatena(F, angolo)` gia' usata per catene/tiranti, riutilizzabile
  come pattern per il ritegno del cordolo

### traliccio_2d.py -> cordolo_reticolare.py
- Input: nodi (id, x, y), aste (id, nodo_i, nodo_j, A, E), vincoli, carichi
- Output: spostamenti nodali, sforzi normali nelle aste, reazioni vincolari
- Da aggiungere: molle (nodo, kx, ky), carichi distribuiti, K_globale

### connessioni.py -> verifiche nodi traliccio
- `verifica_saldatura_angolo(a, L, F, sigma_adm, beta_w)` -> esito
- `verifica_bullone_taglio(classe, diametro, n_piani, F)` -> esito
- `verifica_rifollamento(d, t, fu, F)` -> esito

### verifiche_ta.py -> verifiche aste traliccio
- `verifica_instabilita(profilo, N, L0, sigma_adm)` -> esito con omega
- NOTA: accetta ProfiloAcciaio (da sagomario). Per piatti e angolari serve
  creare un adapter o estendere l'input per accettare A, I, r direttamente.

## Note tecniche importanti

1. Il solutore traliccio_2d e' gia' generico nel piano XY. Non serve flag
   per distinguere orientamento verticale/orizzontale.

2. CordoloReticolare e' classe SEPARATA da CordoloMetallico (D.6).
   Non eredita, ma puo' condividere l'enum TipoCordolo.

3. La fatica ciclica sismica e' un TODO placeholder. Non implementare
   ora, solo predisporre il campo nel risultato.

4. Il flusso iterativo cinematica <-> traliccio (bidirezionale) e' un
   TODO futuro. Per ora: cinematica -> F -> traliccio (unidirezionale).

5. Per il carico distribuito su corrente: convertire in forze nodali
   equivalenti (meta' del carico su ciascun nodo adiacente, per carico
   uniforme). Per carico proporzionale al modo: distribuzione non uniforme.
