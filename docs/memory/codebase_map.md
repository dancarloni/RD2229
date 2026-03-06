# Mappa Codebase — Moduli Chiave e Interfacce
# Per orientamento rapido durante implementazione

## Muratura — src/methods/muratura/

### cinematica.py (~654 righe)
- TipoMeccanismo enum: RIBALTAMENTO_SEMPLICE, RIBALTAMENTO_COMPOSTO,
  FLESSIONE_VERTICALE, FLESSIONE_ORIZZONTALE
  (TODO: aggiungere RIBALTAMENTO_CANTONALE per E.6)
- PosizioneParete enum: A_TERRA, IN_QUOTA
- PareteMuraria dataclass (riga 52): h, t, L, gamma, N_sommita
- ForzaCatena dataclass (riga ~100): F, angolo (gradi)
- ParametriSismici dataclass: a_g, S, q, FC, z_quota, H_edificio
- RisultatoMeccanismo dataclass: tipo, alpha_0, passaggi_calcolo, ...
- ribaltamento_semplice() righe ~170-230
- ribaltamento_composto() righe 235-283: CUNEO 2D su singola parete
  (template per cantonale, ma cantonale e' 3D con 2 pareti)
- flessione_verticale() righe ~290-380
- flessione_orizzontale() righe ~390-460
- cinematica_lineare() righe ~470-530: alpha_0 -> a_0* -> verifica
- cinematica_non_lineare() righe ~530-600: d_0* -> d*_u -> T_s
- analisi_tutti_meccanismi() righe 620-654: lista ordinata per alpha_0
  Parametri: parete, sismica, catene, cuneo_h, cuneo_angolo
  (TODO: aggiungere ritegno_sommitale, meccanismi_attivi)

### modello_edificio.py (~300 righe)
- Gerarchia: Edificio -> Piano -> Parete -> Apertura
- TipoApertura enum (riga 29): PORTA, FINESTRA
- Apertura dataclass (riga 150): x_offset, z_offset, larghezza, altezza
  Proprieta': x_fine, z_fine
- Parete dataclass (riga 195): nome, x_ini, y_ini, x_fin, y_fin,
  spessore, altezza_interpiano, materiale, aperture: list[Apertura]
  Proprieta': lunghezza, angolo, direzione_principale
  Metodi: aperture_ordinate(), to_dict()
- MaterialeMuratura dataclass: fm, tau_0, fvk0, gamma_M, FC,
  Proprieta' derivate: fd, tau_0d, fvk0d

### discretizzazione.py (~350 righe)
- Maschio dataclass (riga 67): id, L, h, t, x_baricentro, y_baricentro,
  materiale, N, vincolo, drift_limite
  (TODO E.6: aggiungere is_cantonale: bool = False, fattore_riduzione_angolo: float = 1.0)
- Fascia dataclass (riga 148): id, L, h, t, ha_cordolo, e_biella,
  id_maschio_sx, id_maschio_dx
- discretizza_parete() (riga 262): ordina aperture, crea maschi tra aperture,
  crea fasce sopra/sotto aperture. Ritorna (maschi, fasce, passaggi).
  Maschi creati come zone tra bordi aperture (righe 324-373).
  (TODO E.6: assegnare is_cantonale ai maschi estremi)

### verifiche.py (~400 righe)
- Compressione con snellezza (righe 181-245)
- Taglio nel piano: Turnsek-Cacovic + scorrimento + pressoflessione (308-479)
- Spanciamento (516-550)
- (TODO E.6: applicare k_riduzione ai maschi con is_cantonale e apertura vicina)

### rigidezza.py (~350 righe)
- rigidezza_maschio(): Timoshenko (flessione + taglio)
- CentroRigidezzaPiano: x_CR, y_CR, K_x, K_y, K_theta
- assembla_matrice_piano(): 3x3 condensata
- distribuisci_forza_piano(): 3 GDL/piano

### resistenza.py (~280 righe)
- ResistenzaMaschio: V_Rd, curva bilineare, forza_per_spostamento()
- calcola_resistenza_maschio(): integra 3 criteri da verifiche.py

### por_analisi.py (~380 righe)
- pushover_piano(), pushover_multipiano()
- bilinearizza_curva(), analisi_por_completa()

## Acciaio — src/steel/

### traliccio_2d.py (~330 righe)
- Solutore rigidezza diretta per tralicci piani
- Input: nodi (id, x, y), aste (id, ni, nj, A, E), vincoli, carichi nodali
- Vincoli: cerniera, carrello_x, carrello_y
- Gauss con pivoting parziale
- Output: spostamenti, sforzi normali, reazioni vincolari
- Verifiche: compressione con omega, trazione
- (TODO D.3: aggiungere molle, carichi distribuiti, K_globale)

### verifiche_ta.py (~410 righe)
- Input: ProfiloAcciaio (da sagomario) — SOLO profili standard
- verifica_flessione(), verifica_taglio(), verifica_instabilita()
- verifica_pressoflessione(), verifica_von_mises()
- profilo_ottimale_per_momento()
- (NOTA D.3: per piatti/angolari serve adapter o input generico A,I,r)

### connessioni.py (~380 righe)
- Saldature: angolo (frontale, laterale, combinata), testa a testa
- Bulloni: taglio, trazione, interazione, rifollamento
- Coefficienti beta_w (CNR 10011), classi 4.6-10.9, M12-M36

### sagomario.py (~188 righe)
- 87 profili: IPE(18), HEA(19), HEB(19), HEM(19), UPN(12)
- Ricerca per famiglia, Wx minimo, altezza, profilo ottimale

## Elementi — src/elements/

### cordolo.py (~350 righe)
- CordoloCA: sezione, armatura, minimi NTC2018
- CordoloMetallico: profilo singolo, A, Wx, h (input manuale)
  nome_profilo e' solo decorativo, non collegato a sagomario
- TipoCordolo enum: CA, METALLICO_PROFILO, METALLICO_RETICOLARE
  METALLICO_RETICOLARE dichiarato ma NON implementato
- (TODO D.3: CordoloReticolare in file separato cordolo_reticolare.py)

## Materiali — src/materials/

### material_model.py (~804 righe)
- Material dataclass: norma_riferimento (str), parametri derivati
- (TODO A.2: aggiungere source_refs: list[dict])

### material_repo.py
- CRUD per cataloghi JSON, load_sources() generico list[dict]
- (TODO A.2: tipizzare con MaterialSource)

## Report — src/report/

### tabulati_calcolo.py
- Generazione ASCII/HTML per relazioni di calcolo
- (TODO D.3, E.6: aggiungere sezioni cordolo reticolare e cantonale)

## Core — src/core/

### unita_misura.py
- Sistema unita' selezionabile (cm/kg vs m/kN vs mm/N)

### registro_log.py
- Log centralizzato con listener GUI

## Codes — src/codes/

### ntc2018/secondary_elements/
- ta_models.py: stima T_a (4 modelli) + S_a floor
- drift_models.py: stima drift Metodo B + USER + GLOBAL
- checks.py: SLU forza inerziale, SLE drift

### dm96/secondary_elements/
- checks.py: F_h = C*beta*W, drift h/300

### rd2229/secondary_elements/
- checks.py: stabilita' TA (omega*N/A)

## Legacy — src/legacy/ (da eliminare progressivamente)

### material_sources.py (~330 righe)
- MaterialSource, CalculationMethod, MaterialSourceLibrary
- (TODO A.2: migrare dati, poi ELIMINARE)
