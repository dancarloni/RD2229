Contesto
Il progetto RD2229 è un software Python per calcolo strutturale storico e moderno. La sessione precedente ha introdotto:

Materiali base RD 2229/39 con doppia notazione (moderna/storica)
material_sources.py con fonti normative e calcolo automatico valori
Editor materiali Tkinter con ComboBox fonte e gestione fonti

L'utente chiede ora di:

Aggiungere al piano la muratura con cordoli metallici (profili, piatti, configurazione reticolare in sommità, alternativi ai cordoli in CA)
Continuare il piano generale per rendere il software funzionante, con torsione, instabilità, deformazioni, fessurazione
Integrare tutte le normative in modo modulare (RD2229, DM92, DM96, NTC2018, Eurocodici, CNR-DT)

Stato Attuale del Repository
Architettura Implementata (src/)
src/
├── codes/ntc2018/          # NTC2018 code module + secondary elements (implementato)
├── core_calculus/           # Engine di calcolo: geometry, materials, verification_core,
│                              verification_engine, normative_registry (parziale)
├── fire/                    # Modulo fuoco: curves, eligibility, rc_fire_check
├── materials/               # Material model (STUB), material_repo, validation
├── methods/                 # checks_ntc2018, checks_rd2229, checks_fire_dm96
├── wind/                    # Vento: ntc2018, cnr_dt207, ec1991_1_4, service
├── report/                  # HTML/MD/PDF renderers
├── ui/qt/                   # GUI Qt6: material_editor (stub), section_manager, etc.
├── legacy/                  # GUI Tkinter legacy: historical_material_window, app, etc.
└── core/                    # Pipeline, results, geometry, section_properties
Verifiche Implementate (normative_registry.py)
VerificaRD2229NTC2018StatoFlessione semplice✅ complete✅ completeFunzionantePressoflessione⚠️ partial-Manca instabilità pilastriPressoflessione deviata✅ complete-Solo RD2229Taglio⚠️ partial✅ completeRD2229: manca formula completa Art.21Minimi armatura long.✅ complete✅ completeFunzionanteMinimi armatura taglio-✅ completeSolo NTC2018Torsione❌ non impl.❌ non impl.Da sviluppareInstabilità❌ non impl.❌ non impl.Da sviluppareFessurazione❌ non impl.❌ non impl.Da sviluppareDeformazioni❌ non impl.❌ non impl.Da sviluppare
Knowledge Base Esistente (docs/MEGAPLAN/)

KB_RD2229_1939.md, KB_NTC2018_CA.md, KB_NTC2018.md, KB_DM_1992_TA.md, KB_DM_1996_TA.md
SECONDARY_ELEMENTS_MASTER.md (spec completa)
FIRE_MASTER.md + sottodocumenti
PLAN_STRATEGIA_STRUTTURALE_ESTESA.md (vincoli architetturali)

File Chiave da Modificare/Estendere

src/core_calculus/normative_registry.py — template verifiche (aggiungere torsione, instabilità, fessurazione, deformazioni)
src/core_calculus/core/verification_core.py — funzioni calcolo base
src/methods/checks_rd2229.py — implementazioni verifiche RD2229
src/methods/checks_ntc2018.py — implementazioni verifiche NTC2018
src/materials/material_model.py — modello materiale (STUB → completo)
src/ui/qt/material_editor.py — editor materiali Qt (STUB → completo)
src/legacy/material_sources.py — fonti normative con calcolo auto


Piano Multi-Step
FASE A — Fondamenta: Modello Materiale e Editor (sessione corrente)
A1. Completare material_model.py (src/materials/material_model.py)

Estendere Material da STUB a modello completo con:

source_norm: stringa identificativa norma (RD2229, NTC2018, etc.)
gamma_c, gamma_s: coefficienti parziali (=1 per TA)
Parametri calcestruzzo: fck, fcd, sigma_c28, sigma_c, tau_c0, tau_c1, n, Ec
Parametri acciaio: fyk, fyd, sigma_sn, sigma_s, Es
Parametri muratura: fk, fvk0, tau_0, E_mur, G_mur
Metodo to_json() / from_json()


Riutilizzare pattern da src/legacy/material_sources.py (MaterialSource dataclass)
Riutilizzare src/materials/validation.py per validazione

A2. Completare editor materiali Qt (src/ui/qt/material_editor.py)

Trasformare da stub a editor funzionante con:

ComboBox fonte normativa (da material_sources)
Campi dinamici in base a material_type (concrete/steel/masonry)
Doppia notazione (moderna/storica) come già in legacy Tkinter
Pulsante "Ricarica valori da Fonte"
Gestione fonti (aggiungi/modifica/elimina)



A3. Aggiungere famiglia muratura al modello materiali

Aggiungere tipo "masonry" con parametri NTC2018 §4.5 e §11.10:

fk (resistenza caratteristica a compressione)
fvk0 (resistenza caratteristica a taglio senza σ)
fvd (resistenza di calcolo a taglio)
fd (resistenza di calcolo a compressione)
E (modulo elastico)
G (modulo di taglio)
γ_M (coefficiente parziale)
tipo_malta, tipo_blocco, classe_esecuzione



FASE B — Verifiche Mancanti: Torsione
B1. Torsione RD2229 TA — nuovo file src/methods/rd2229/torsione.py

Traduzione da VB Sub Torsione() (visual_basic/ riga 3818)
Formula: T_t = M_t / (2 × A_0 × t_ef)
Tre casi: torsione pura, T+V, M+T+V
Armatura longitudinale e trasversale per torsione
Riferimento: scienza costruzioni classica (Colonnetti, Santarella)

B2. Torsione NTC2018 SLU — nuovo in src/methods/ntc2018/torsione.py

§4.1.2.1.3.3: T_Rd = 2 × ν × α_cw × f_cd × A_k × t_ef,i × sin(θ) × cos(θ)
Interazione T+V: (V_Ed/V_Rd,max)² + (T_Ed/T_Rd,max)² ≤ 1
Armatura staffe: A_sw/s_t = T_Ed / (2×A_k×f_ywd×cot(θ))
Armatura longitudinale: A_sl = T_Ed × cot(θ) / (2×A_k×f_yd)

B3. Template normative_registry — aggiungere template torsione per entrambe le norme
FASE C — Verifiche Mancanti: Instabilità
C1. Instabilità RD2229 TA (pilastri snelli)

Metodo ω: σ_c,adm,rid = σ_c,adm × ω (coefficiente di amplificazione da tabella)
Riduzione per snellezza: λ = l₀/i_min
Tabella ω in funzione di λ (da Santarella/Giangreco)
Limitazione geometrica minima (25 cm lato minimo)

C2. Instabilità NTC2018 SLU (pilastri)

Metodo semplificato §4.1.2.1.7.2: amplificazione momento per effetti P-Δ
Snellezza limite: λ_lim = 20·A·B·C/√n (Annesso B EC2)
Metodo della curvatura nominale (§5.8.8 EC2)
Metodo della rigidezza nominale (§5.8.7 EC2)

FASE D — Verifiche Mancanti: Fessurazione (SLE)
D1. Fessurazione NTC2018 SLE — src/methods/ntc2018/fessurazione.py

§4.1.2.2.4: w_k = s_r,max × (ε_sm - ε_cm)
s_r,max = k₃×c + k₁×k₂×k₄×φ/ρ_p,eff
ε_sm - ε_cm = [σ_s - k_t×f_ct,eff/ρ_p,eff×(1+α_e×ρ_p,eff)] / E_s
Limiti w_k da tabella 4.1.IV NTC2018

D2. Fessurazione RD2229 — non prevista esplicitamente (norma storica)

Nota nel software: "Il RD 2229/39 non prevede verifica esplicita di fessurazione"
Opzionale: stima qualitativa basata su tensioni acciaio vs σ_s,adm

FASE E — Verifiche Mancanti: Deformazioni (SLE)
E1. Deformazioni NTC2018 SLE — src/methods/ntc2018/deformazioni.py

§4.1.2.2.2: freccia = integrale curvatura
Inerzia efficace (metodo Branson o EC2 §7.4.3): 1/r = ζ×(1/r)_II + (1-ζ)×(1/r)_I
ζ = 1 - β×(M_cr/M_Ed)² (distribuzione = 1 lungo termine, 0.5 corto)
Contributo viscosità: φ_eff (NTC Tab 4.1.I o EC2 §3.1.4)
Limiti: L/250 aspetto, L/500 danno

E2. Deformazioni RD2229 TA

Freccia elastica classica: f = 5qL⁴/(384EI) per carico uniforme
EI con sezione omogenizzata (già implementata in historical_ta/geometry.py)
Limite tipico: L/500 (da prassi, non da norma)

FASE F — Muratura con Cordoli Metallici
F1. Modello muratura — src/materials/masonry_model.py

Tipi di muratura: mattoni pieni, forati, blocchi cls, tufo, pietra
Tabelle NTC2018 §Tab.4.5.I÷IV per fk da tipo blocco + tipo malta
Tabelle storiche (DM 20/11/1987, Circ. 4/1981) per edifici esistenti

F2. Modello cordolo — src/elements/cordolo.py

Cordolo in CA: sezione rettangolare, armatura longitudinale e staffe
Cordolo metallico: NUOVO

Profili singoli (IPE, HEA, HEB, UPN)
Piatti saldati/bullonati (configurazione custom)
Configurazione reticolare (aste superiore/inferiore + diagonali)
Sezione composta (profilo + soletta collaborante se presente)


Verifiche cordolo metallico:

Resistenza: M_Rd, V_Rd, N_Rd
Stabilità: instabilità flesso-torsionale (LTB)
Collegamento: saldature o bulloni (domanda/capacità)
Ancoraggio alla muratura: barre filettate, piastre, resine


Normativa: NTC2018 §4.5.6.2 (cordoli), §4.2 (acciaio strutturale), EC3

F3. Sagomario profili metallici — src/data/steel_profiles/

Tabelle EN 10365 standard: IPE 80÷600, HEA 100÷1000, HEB 100÷1000, UPN 80÷400
Proprietà: A, h, b, tf, tw, Ix, Iy, Wx, Wy, Sx, Sy, ix, iy, Iw, It
Formato JSON con schema validato
Import profili custom utente (CSV/JSON)

F4. Solutore traliccio piano — src/solvers/truss_2d.py

Metodo dei nodi per tralicci isostatici (equilibrio nodale)
Input: nodi (coordinate), aste (nodo_i, nodo_j, sezione), vincoli, carichi nodali
Output: sforzo normale in ogni asta (N_Ed), reazioni vincolari
Interfaccia astratta TrussSolver predisposta per FEM futuro
Verifica aste: N_Ed vs N_Rd (trazione/compressione + instabilità Euler)
Verifica nodi: saldature o bulloni (domanda/capacità)

F5. GUI cordoli — widget Qt specifico nell'editor elementi

Scelta tipo cordolo (CA / acciaio singolo / acciaio reticolare)
Input geometrico con anteprima sezione (canvas Qt)
Selezione profilo da sagomario (ComboBox con filtro)
Configurazione reticolare: editor grafico nodi + aste
Visualizzazione sforzi nelle aste (colori: trazione/compressione)

F6. Verifiche strutturali muratura — nuova e esistente — src/methods/muratura/
Livelli di implementazione muratura per normativa
Normative considerate:

RD2229: RD 2229/1939 (solo compressione e taglio per muri portanti, tensioni ammissibili)
DM87: DM 20/11/1987 (primo geotecnico muratura moderno — Tab. resistenze, TA+SL)
Circ81: Circ. Min. LL.PP. 21/01/1981 n.21745 (istruzioni storiche per muratura esistente)
NTC2018+C7: DM 17/01/2018 §4.5 + §8.7 (muratura nuova + esistente) + Circ. 7/2019 §C4.5 + §C8.7
EC6: EN 1996-1-1 (Eurocode 6 — muratura nuova)
EC8-3: EN 1998-3 (valutazione e adeguamento sismico edifici esistenti in muratura)

VerificaRD2229DM87Circ81NTC2018+C7EC6EC8-3Compressione sempliceL2L2L2L3L2L1Pressoflessione nel pianoL1L2L2L3L2L2Taglio nel piano (a taglio + a pressoflessione)L2L2L2L3L2L2Snellezza (ribaltamento fuori piano)L2L2L2L3L2L2Flessione fuori pianoL1L1L2L3L2L2Apertura cantonali / concentrazioni stressL1L1L1L2L1L1Punzonamento locale (carichi concentrati)L1L1L1L2L2L1Spanciamento parete (instabilità)L2L2L2L3L2L1Ribaltamento globale parete fuori pianoL1L1L2L3L1L3Meccanismo di piano (taglio globale)L0L1L1L2L0L3Analisi cinematica lineare (catene)L0L0L1L3L0L3Verifica catene e paletti (calcolo)L1L1L2L3L0L2Rinforzo FRP (confinamento, flessione)L0L0L0L1L0L1Muratura senza cordoli (storica)L2L2L2L2L0L2Muratura con cordoli CAL1L1L1L3L2L2Muratura con cordoli metalliciL1L0L0L2L1L1Muratura multipiano: azioni sismicheL0L0L1L2L0L3
Struttura package muratura
src/methods/muratura/
├── __init__.py
├── modello.py              # MasonryWall dataclass: geometria + materiale + vincoli
├── azioni.py               # Azioni nel piano (N, V, M) e fuori piano (q_perp, F_perp)
├── compressione.py         # Compressione semplice TA + SLU
├── pressoflessione.py      # Pressoflessione nel piano (dominio N-M)
├── taglio.py               # Taglio per crisi a taglio e a pressoflessione (diagonal cracking)
├── snellezza.py            # Verifica snellezza λ = h_eff/t_eff + riduzione φ
├── fuori_piano.py          # Flessione fuori piano + ribaltamento (meccanismo)
├── spanciamento.py         # Instabilità per spanciamento (colonna snella)
├── punzonamento.py         # Carichi concentrati da travi/solai
├── apertura_cantonali.py   # Stress da aperture (porte/finestre): lintel, piedritti
├── catene/
│   ├── __init__.py
│   ├── calcolo_catene.py   # Forza catena = spinta muratura, verifica barra + piastra
│   ├── modello_catena.py   # Catena dataclass: φ, acciaio, L, pretensione
│   └── piastre.py          # Piastra di ancoraggio: diversi tipi e dimensioni
├── cinematica/
│   ├── __init__.py
│   ├── meccanismi.py       # Meccanismi elementari: ribaltamento semplice, flessione
│   ├── analisi_lineare.py  # Analisi cinematica lineare (NTC §C8A.4 + EC8-3)
│   └── analisi_nonlineare.py # Analisi cinematica non lineare — L1
├── multipiano/
│   ├── __init__.py
│   ├── distribuzione_azioni.py # Distribuzione azioni orizzontali per piano
│   └── indice_sicurezza.py     # ζ_E = PGA_capacità / PGA_domanda per meccanismi
└── gui/
    ├── muratura_editor.py  # Qt: editor parete (geometria, materiale, vincoli)
    ├── catene_editor.py    # Qt: input catene/paletti con tipo piastra
    └── meccanismi_widget.py # Qt: visualizzazione meccanismo e risultato
Dettaglio verifiche muratura
F6.1. Snellezza e compressione — compressione.py + snellezza.py

Snellezza: λ = h_ef / t_ef dove h_ef = ρ_n × h (fattore di vincolo), t_ef = t (o t_ef per par. doppia)
Limiti: λ ≤ 20 (NTC §4.5.6.3, elementi portanti); λ ≤ 30 (NTC §4.5.6.3, non portanti)
Compressione TA (DM87/RD2229): σ_c = N/(A_netta) ≤ σ_c,adm (da Tab. DM87 per tipo muratura)
Compressione SLU (NTC2018 §4.5.6.3): N_Ed ≤ N_Rd = Φ_i × t × f_d (dove Φ_i riduzione per snellezza ed eccentricità)
Fattore Φ_i = f(e/t, λ): da tabella NTC Tab.4.5.III o formula EC6 §6.1.2
Muratura senza cordoli: nessuna riduzione per cordolo, solo vincolo snellezza

F6.2. Taglio nel piano — taglio.py

Crisi a taglio diagonale (NTC §4.5.6.4.1):

V_Rd1 = f_vd × A_eff (resistenza a taglio diagonale)
f_vd = (f_vk0 + 0.4σ_n) / γ_M ≤ f_vk,lim/γ_M
Verifica: V_Ed ≤ V_Rd1


Crisi a pressoflessione (NTC §4.5.6.4.2):

V_Rd2 = 0.85 × (A_eff × σ_0) / h_s × (1 - σ_0 / (ψ×f_d))
dove σ_0 = N/A_eff, ψ = 1.0 (muri inflessi) o 1.5 (muri incernierati)


RD2229 TA: τ = V/(b×h) ≤ τ_amm (da tabella resistenze storiche DM87 o RD2229)
Muratura senza cordoli: lo stesso ma con h_s = altezza netta di piano (senza cordolo)

F6.3. Flessione fuori piano e ribaltamento — fuori_piano.py

Azioni fuori piano: vento (NTC §3.3), sismica (NTC §7.2.3 elem. secondari o §C8.7), pressione terreno
Modello trave verticale: parete tra impalcati come trave con carichi distribuiti e/o concentrati
Verifica flessione fuori piano SLU (NTC §4.5.6.3):

M_Ed ≤ M_Rd = f_d × t² / 6 × b (sezione rettangolare in cls semplice equivalente)


Meccanismo di ribaltamento: analisi cinematica (vedi F6.5)
Verifica snellezza per fuori piano: stessa λ di F6.1

F6.4. Spanciamento — spanciamento.py

Parete compressa con carico eccentrico: instabilità per spanciamento
Formula NTC §4.5.6.3: riduzione Φ per eccentricità + effetti II ordine
Eccentricità totale: e = e_i + e_0 + e_k (iniziale + eccentricità di calcolo + long termine)
e_k = h_ef² × (1/r) / c → curvatura da viscosità

F6.5. Calcolo catene e paletti — catene/calcolo_catene.py + catene/piastre.py

Forza di calcolo catena (analisi cinematica lineare NTC §C8A.4.1):

Meccanismo scelto → calcolo moltiplicatore α₀ → F_catena = N_mob × α₀ (forza di tiro necessaria)
Verifica pretensione minima se catena pre-tesa


Verifica barra catena (acciaio): N_catena ≤ A_s × f_yd (trazione pura)
Verifica piastra di ancoraggio:

Tipi: quadrata, rettangolare, circolare, a paletto (diversa geometria)
Verifica flessione piastra (portata mensola in 2D): M = q_loc × a²/2 ≤ M_Rd = t_p² × f_y / 4
Verifica pressione muratura sotto piastra: σ = N_catena / A_piastra ≤ σ_amm,mur (o f_d)
Verifica ancoraggio muro (pull-out da muratura): meccanismo cono o prisma di rottura


Input tipi piastre: l × h × t (mm), acciaio (S235/S275/S355), disposizione (esterna/incassata)
Muratura senza cordoli: catene spesso l'unico presidio; analisi cinematica OBBLIGATORIA
Muratura con cordoli CA: catena integrata nel cordolo (barre di ancoraggio nel getto)
Muratura con cordoli metallici: catena su profilo (saldatura o bullonatura alla flangia)

F6.6. Apertura cantonali — apertura_cantonali.py

Arco naturale sopra apertura (porte/finestre): stima carico scaricato
Verifica architrave (legno, acciaio, CA): trave semplicemente appoggiata
Concentrazione tensioni ai piedritti (cantonali): verifica localizzata
Verifica cantonale d'angolo edificio: parete d'angolo (caso più critico per sismica)
Riduzione sezione utile per aperture: calcolo A_netta, A_eff

F6.7. Punzonamento locale — punzonamento.py

Carico concentrato da trave/solaio su muratura: σ_loc = F / A_portante
Area di distribuzione: a 45° dalla trave per h_dif ≤ t/2
Verifica: σ_loc ≤ f_d,loc = β_b × f_d (NTC §4.5.6.5, fattore β_b da Tab.)
Piastra di ripartizione (se necessaria): dimensionamento e ancoraggio

F6.8. Muratura multipiano — azioni sismiche — multipiano/

Distribuzione azioni laterali (NTC §7.3.5.1 per muratura):

Metodo statico equivalente: F_i proporzionale a massa×altezza
Distribuzione ai maschi murari in funzione rigidezza (o uniforme)


Rigidezza maschio murario (NTC §4.5.5):

K_m = G × A_m / (χ × h) (taglio) + 12 × E × I_m / h³ (flessione) — combinata
χ = 1.2 per sezione rettangolare


Indice di sicurezza sismica ζ_E = PGA_c / PGA_d (NTC §8.4.1)
Calcolo PGA_c da meccanismo più sfavorevole (cinematica lineare/non lineare)

F6.9. GUI muratura — src/methods/muratura/gui/

muratura_editor.py: Qt widget — input parete (b, h, t, materiale, vincoli verticali/orizzontali)
catene_editor.py: Qt widget — tabella catene (posizione, φ, acciaio, tipo piastra, dimensioni)

Selezione tipo piastra da catalogo (quadrata/rettangolare/circolare + dimensioni custom)
Visualizzazione anteprima piastra e posizione su parete


meccanismi_widget.py: Qt widget — selezione meccanismo (da lista: ribaltamento semplice, flessione verticale, taglio piano, etc.) + visualizzazione schema + risultati α₀, ζ_E

F7. Modello a telaio equivalente — src/methods/muratura/telaio_equivalente/
Analisi globale edificio in muratura con modello a telaio equivalente semplificato (tipo POR/SAM-II).
src/methods/muratura/telaio_equivalente/
├── __init__.py
├── modello.py              # MasonryBuilding: piani, pareti, aperture → discretizzazione
├── maschio.py              # MasonryPier: elemento verticale (maschio murario)
├── fascia.py               # MasonrySpandrel: elemento orizzontale (fascia di piano)
├── nodo_rigido.py          # Nodo rigido tra maschio e fascia
├── rigidezza.py            # K_maschio (taglio+flessione), K_fascia
├── assemblaggio.py         # Assemblaggio matrice rigidezza globale piano per piano
├── distribuzione_forze.py  # Distribuzione forze sismiche ai maschi (prop. rigidezza)
├── analisi_lineare.py      # Analisi statica lineare equivalente
├── pushover.py             # Predisposizione analisi pushover (curva capacità)
└── gui/
    ├── pianta_editor.py    # Qt: editor pianta (pareti + aperture su griglia)
    └── risultati_widget.py # Qt: distribuzione forze, rapporti D/C per maschio

Discretizzazione automatica: da pianta → individuazione maschi e fasce
Rigidezza maschio (NTC §7.8.1.5.2):

K_m = 1 / (h³/(12EI) + χh/(GA)) — flessione + taglio combinati
E, G da materiale muratura (archivio centralizzato)


Resistenza maschio: V_Rd = min(V_taglio, V_pressoflessione) come da F6.2
Fasce: resistenza a flessione (con o senza cordolo/catena) + taglio
Distribuzione sismica per piano: Fb = Sd(T1) × W × λ / g (NTC §7.3.3.2)

F_i = F_b × z_i×W_i / Σ(z_j×W_j) — distribuzione lineare
Distribuzione ai maschi per rigidezza: V_i = V_piano × K_i / ΣK_j


Rapporto D/C per ogni maschio: D/C = V_Ed / V_Rd
Predisposizione pushover: curva di capacità V_base - δ_tetto (incrementale, non lineare)

FASE G — Normative Aggiuntive (modulare)
NOTA FONDAMENTALE: Per NTC2018, tutte le verifiche devono fare riferimento CONGIUNTO a:

D.M. 17/01/2018 — Norme Tecniche per le Costruzioni (NTC2018)
Circ. 21/01/2019 n. 7 C.S.LL.PP. — Istruzioni per l'applicazione dell'aggiornamento delle NTC

La Circolare fornisce chiarimenti, formule integrative, tabelle complementari e interpretazioni ufficiali.
Nei template di verifica (normative_registry.py), ogni NormReference NTC2018 deve includere
anche il riferimento al paragrafo corrispondente della Circolare (es. §C4.1.2.1.3.1).
Per ogni norma, creare sotto src/codes/<norm_id>/:

code_module.py — registrazione nel registry
parameters.json — coefficienti e tabelle
checks.py — funzioni di verifica
circular_references.json — (solo NTC2018) mapping paragrafo NTC → paragrafo Circolare

G1. DM 14/02/1992 (TA con aggiornamenti)

σ_c,adm = 60 + 0.08 × (R_ck - 150) per R_ck > 150
τ_c0 = 0.4 + 0.01 × R_ck
γ_c = 1 (metodo TA)

G2. DM 9/01/1996 (transizione TA → SL)

Metodo SL introdotto accanto a TA
Combinazioni di carico SLU/SLE
Sismica aggiornata

G3. NTC 2008 — struttura simile a NTC2018 con differenze su:

Coefficienti parziali diversi
Combinazioni di carico leggermente diverse
Classe duttilità diversa

G4. Eurocodici (EC2, EC3, EC8)

EC2: verifiche CA (fallback per NTC dove lacunosa)
EC3: acciaio strutturale (per cordoli metallici e strutture acciaio)
EC8: sismica (per confronto con NTC)

G5. CNR-DT — da PDF caricati in docs/norms/cnr_dt/

CNR-DT 200 R2/2026: rinforzo FRP
CNR-DT 207 R1/2018: azioni del vento (già parziale in src/wind/)

Struttura Package methods/ (riorganizzazione)
src/methods/
├── __init__.py
├── rd2229/
│   ├── __init__.py
│   ├── flessione.py          # (da checks_rd2229.py esistente)
│   ├── pressoflessione.py    # (da checks_rd2229.py esistente)
│   ├── taglio.py             # (da checks_rd2229.py esistente)
│   ├── torsione.py           # NUOVO
│   ├── instabilita.py        # NUOVO
│   └── minimi_armatura.py    # (da checks_rd2229.py esistente)
├── ntc2018/
│   ├── __init__.py
│   ├── flessione.py          # (da checks_ntc2018.py esistente)
│   ├── taglio.py             # (da checks_ntc2018.py esistente)
│   ├── torsione.py           # NUOVO
│   ├── instabilita.py        # NUOVO
│   ├── fessurazione.py       # NUOVO
│   ├── deformazioni.py       # NUOVO
│   ├── minimi_armatura.py    # (da checks_ntc2018.py esistente)
│   └── circular_refs.json    # Mapping NTC → Circolare 7/2019
├── dm96/
│   └── __init__.py           # Predisposizione
├── ec2/
│   └── __init__.py           # Predisposizione
├── ec3/
│   └── __init__.py           # Per cordoli metallici
└── checks_fire_dm96.py       # Esistente
FASE H — Elementi Secondari e Fuoco
H1. Elementi secondari (spec già completa in SECONDARY_ELEMENTS_MASTER.md)

Implementare src/codes/ntc2018/secondary_elements/ (già strutturato)
GUI per input elementi secondari
Calcolo Fa (forza inerziale) secondo NTC2018 §7.2.3

H2. Fuoco (parzialmente implementato)

Completare src/fire/ con metodo tabellare completo
Isoterma 500°C
Profili di temperatura REI 30÷240

FASE I — Metodo di Cross-Pozzati per Telai Piani
Riferimento architetturale: docs/MEGAPLAN/PLAN_METODO_CROSS_TELAI_PIANI.md (VINCOLO DURO)
I1. Modello strutturale astratto — src/solvers/cross_pozzati/model.py

Node: id, coordinate (x,y), vincolo (incastro/cerniera/carrello/libero)
Member: id, nodo_i, nodo_j, EI, L, tipo_estremo (incastro/cerniera)
LoadCase: id, descrizione, carichi distribuiti, concentrati, momenti
FrameModel: nodi, aste, vincoli, casi di carico
Serializzazione JSON; NESSUNA logica normativa nel modello

I2. Engine Cross-Pozzati — src/solvers/cross_pozzati/engine.py

Coefficienti di rigidezza: k = 4EI/L (incastro-incastro), 3EI/L (incastro-cerniera)
Fattori di distribuzione: d_ij = k_ij / Σk_i
Fattori di trasporto: 1/2 (standard), 0 (cerniera)
Momenti di incastro perfetto (MEP): qL²/12, Pab²/L², triangolari, etc.
Iterazione di rilassamento nodale con convergenza configurabile
Output: CrossResult (momenti finali, n_iterazioni, convergenza)

I3. Modalità didattica — src/solvers/cross_pozzati/didactic.py

Step-by-step di ogni iterazione (come testi Pozzati/Ceccoli)
Tabella distributiva per ogni nodo
Diagramma momenti step-by-step

I4. Post-processing — src/solvers/cross_pozzati/postprocess.py

Taglio: V = (M_j - M_i)/L + V_0
Momento in campata, sforzo normale
Inviluppi per combinazioni multiple
Diagrammi M, V, N per ogni asta

I5. GUI Cross-Pozzati — src/ui/qt/cross_editor.py

Editor grafico telaio: canvas Qt con nodi/aste/vincoli
Input grafico (click nodi, drag aste)
Visualizzazione diagrammi M/V/N sovrapposti
Modalità didattica: pulsante "Passo successivo"
Selezione norma per verifiche (combo NTC2018/DM96/RD2229/EC2)

I6. Bridge verso norme — src/solvers/cross_pozzati/norm_bridge.py

Converte CrossResult → input per methods/<norma>/
Genera combinazioni secondo la norma selezionata
La norma NON entra nel solutore

FASE J — FEM Strutturale per Telai Piani
J1. Solutore FEM beam 2D — src/solvers/fem/
src/solvers/fem/
├── __init__.py
├── model.py           # Nodi, elementi, vincoli, carichi
├── beam_element.py    # Matrice di rigidezza 6x6 locale (3 gdl/nodo: u,v,θ)
├── assembler.py       # Assemblaggio K globale (scipy sparse CSR)
├── solver.py          # K·u = F (scipy.linalg.solve)
├── postprocess.py     # Estrazione M, V, N da spostamenti
├── load_cases.py      # Casi di carico e combinazioni
└── validation.py      # Confronto con Cross per verifica

Matrice rigidezza locale: EA/L (assiale) + 12EI/L³, 6EI/L², 4EI/L (flessionale)
Rotazione locale→globale con matrice T
Vincoli: eliminazione gdl, penalizzazione, rilascio cerniera
Carichi distribuiti → forze nodali equivalenti

J2. Validazione FEM vs Cross — src/solvers/fem/validation.py

Test su telai canonici (portale, 2 campate, multipiano)
Errore atteso < 0.1% rispetto a Cross

J3. Interfaccia astratta solutore — src/solvers/base.py
pythonclass StructuralSolver(ABC):
    def solve(self, model, load_cases) -> AnalysisResult: ...
    def get_internal_forces(self, member_id, x) -> InternalForces: ...
```
- CrossPozzatiSolver e FEMSolver implementano la stessa interfaccia
- Scelta solutore dalla GUI; norme consumano risultati indifferentemente

### FASE K — FEM Sismico (predisposizione)

> Implementazione futura. Ora si predispongono solo interfacce e modelli dati.

**K1. Analisi modale** — `src/solvers/fem/modal.py`
- Matrice di massa M (consistente o concentrata)
- Autovalori: (K - ω²M)·φ = 0 → periodi T_i, forme modali φ_i
- Massa partecipante per modo; min modi fino a 85% massa (NTC2018 §7.3.3.1)

**K2. Analisi statica equivalente**
- F_i = F_h × (z_i×W_i) / Σ(z_j×W_j)
- F_h = S_d(T_1) × W × λ / g
- Spettro da NTC2018 (già in src/codes/ntc2018/)

**K3. Analisi dinamica lineare**
- Spettro di risposta: S_a(T_i) per ogni modo
- Combinazione modale: SRSS o CQC

### FASE L — Telai 3D (predisposizione futura)

> Solo modello dati e interfacce.

**L1. Modello 3D** — `src/solvers/fem/model_3d.py`
- Nodo 3D: 6 gdl (u, v, w, θx, θy, θz)
- Elemento beam 3D: matrice 12×12 (torsione GJ/L + flessione biassiale EIy, EIz)
- Diaframmi rigidi di piano

**L2. GUI 3D**
- Visualizzazione 3D (matplotlib 3D o vispy)
- Rotazione/zoom, selezione elementi, deformata 3D

### FASE M — Report e Relazione di Calcolo

**M1. Template relazione di calcolo** — `src/report/`
- Struttura standard relazione tecnica italiana:
  1. Premessa e normativa di riferimento
  2. Descrizione dell'opera
  3. Materiali (con fonte normativa e parametri)
  4. Azioni e combinazioni di carico
  5. Modello di calcolo (Cross/FEM, ipotesi)
  6. Verifiche di resistenza (SLU o TA) con dettaglio per sezione
  7. Verifiche di esercizio (SLE: fessurazione, deformazioni)
  8. Verifiche particolari (fuoco, sismica, elementi secondari)
  9. Conclusioni
- Citazione normativa automatica: ogni verifica genera automaticamente il riferimento
  (es. "Verifica eseguita ai sensi del §4.1.2.1.3.1 D.M. 17/01/2018 e §C4.1.2.1.3.1 Circ. 7/2019")
- Già esistenti renderer HTML/MD/PDF in `src/report/`; estendere con template strutturato

**M2. Export PDF professionale**
- Layout pagina A4 con intestazione/piè di pagina configurabili
- Logo studio tecnico, dati committente, data, n. pratica
- Tabelle risultati formattate
- Diagrammi M/V/N integrati
- Indice automatico
- Numerazione equazioni
- Libreria: reportlab o weasyprint (da verificare dipendenze)

**M3. Export dati e interoperabilità**
- Export JSON strutturato (per import in altri software)
- Export CSV tabellare (per Excel)
- Export DXF sezioni (per CAD)
- Export SVG diagrammi (per documenti)

### FASE N — Edifici Esistenti e Vulnerabilità

**N1. Livelli di conoscenza** — `src/codes/ntc2018/existing_buildings/`
- NTC2018 §8.5.4 + Circ. §C8.5.4:
  - LC1 (limitata): indagini limitate, FC = 1.35
  - LC2 (adeguata): indagini estese, FC = 1.20
  - LC3 (accurata): indagini esaustive, FC = 1.00
- Già predisposto in `src/core_calculus/lc_fc_adjustments.py`
- GUI per selezione LC e calcolo automatico FC

**N2. Materiali edifici esistenti**
- Resistenze medie → caratteristiche: f_cm / FC
- Tabelle NTC2018 §C8.5.1 per calcestruzzo/acciaio storici
- Tabelle Circ. §C8A.2 per muratura esistente (resistenze da prove)
- Fattori di riduzione per degrado

**N3. Verifiche sismiche edifici esistenti**
- Indice di sicurezza sismica: ζ_E = PGA_capacità / PGA_domanda
- Livelli di intervento:
  - Adeguamento: ζ_E ≥ 1.0 (NTC §8.4.1)
  - Miglioramento: ζ_E ≥ 0.6 per classe III, ≥ 0.1 incremento (NTC §8.4.2)
  - Riparazione locale: singoli elementi (NTC §8.4.3)

**N4. Meccanismi locali muratura** (predisposizione)
- Ribaltamento semplice (parete fuori piano)
- Flessione verticale fuori piano
- Flessione orizzontale
- Meccanismo di piano (taglio)
- Analisi cinematica lineare e non lineare (NTC §C8A.4)

**N5. Interventi di rinforzo** (predisposizione)
- FRP (CNR-DT 200): confinamento pilastri, rinforzo a flessione/taglio
- Incamiciatura in CA
- Cordoli metallici (collegamento con FASE F)
- Tiranti e catene

### FASE O — Testing e Validazione

**O1. Benchmark con manuali classici**
- Cercare online tabelle/esempi numerici Santarella e Giangreco
- Implementare test con valori noti da letteratura tecnica italiana
- Predisporre OCR per scansioni future (vedi FASE P)
- Confronto con soluzioni analitiche per casi semplici

**O2. Suite test per ogni norma**
```
tests/
├── test_rd2229/
│   ├── test_flessione.py       # Confronto con Santarella
│   ├── test_taglio.py
│   ├── test_torsione.py
│   └── test_instabilita.py
├── test_ntc2018/
│   ├── test_flessione_slu.py
│   ├── test_taglio_slu.py
│   ├── test_fessurazione.py
│   ├── test_deformazioni.py
│   └── test_torsione_slu.py
├── test_solvers/
│   ├── test_cross_pozzati.py   # Telai canonici
│   ├── test_fem_beam.py        # Confronto con Cross
│   └── test_truss_2d.py        # Tralicci
└── test_integration/
    ├── test_material_flow.py   # Materiale → verifica → report
    └── test_gui_e2e.py         # Test end-to-end Qt
```

**O3. Validazione incrociata**
- Ogni solutore (Cross, FEM) deve produrre risultati coerenti entro 0.1%
- Confronto con VB originale per verifiche RD2229
- Test regressione per evitare rotture con nuove feature

**O4. CI/CD** (predisposizione)
- GitHub Actions per pytest automatico
- Lint (flake8/ruff) + type check (mypy)
- Coverage minima per moduli di calcolo

### FASE P — OCR Manuali Tecnici Storici

**P1. Pipeline OCR per scansioni** — `src/tools/ocr_pipeline.py`
- Input: immagini scannerizzate (PNG/JPG/TIFF) di pagine di manuali
- OCR testo: Tesseract (pytesseract) per testo italiano
- OCR matematico: per formule → LaTeX o mathML
  - Opzioni: Mathpix API, pix2tex (open source), o Nougat (Meta)
- OCR grafici/tabelle: estrazione dati da tabelle scannerizzate
  - Opzione: img2table o camelot per tabelle
- Output: file Markdown strutturato con formule e tabelle

**P2. Integrazione con Knowledge Base**
- Le formule estratte alimentano docs/MEGAPLAN/KB_*.md
- I valori numerici estratti alimentano parameters.json delle norme
- Tracciabilità: ogni formula ha riferimento a pagina/manuale di origine

**P3. Strumenti necessari** (da installare quando servono)
- `pytesseract` + `tesseract-ocr` (apt) per OCR base
- `pix2tex` o `nougat` per OCR matematico
- `Pillow` per preprocessing immagini
- Opzionale: `camelot-py` per tabelle PDF

### FASE R — Sezioni: Creazione e Calcolo Parametri Statici (da implementare subito)

Il modulo sezioni esiste già con buona copertura. Codice esistente da riusare:
- `src/core_calculus/core/geometry.py` — 10 tipi sezione (Rectangular, Circular, T, L, I, Pi, Hollow, etc.)
- `src/core_calculus/core/geometry_model.py` — SectionGeometry (polygon), SectionProperties, CoreData, EllipseData
- `src/core_calculus/section_calculations.py` — calcolo proprietà canonico (area, centroid, inerzia, nocciolo, ellisse)
- `src/legacy/sections_app/` — GUI Tkinter legacy per gestione sezioni

**R1. Completare calcolo parametri statici** (verificare cosa manca)
- Area, perimetro, baricentro (x_c, y_c) ✅ già implementato
- Momenti di inerzia (Ix, Iy, Ixy) ✅ già implementato
- Assi principali di inerzia (rotazione α) — verificare
- Raggi giratori (ix, iy) — verificare
- Moduli di resistenza (Wx, Wy) — verificare
- Nocciolo centrale di inerzia — ✅ CoreData presente
- Ellisse centrale di inerzia — ✅ EllipseData presente
- Momento statico (Sx, Sy) per taglio — verificare
- Sezione omogenizzata con armature (per CA)

**R2. GUI Qt per sezioni** — `src/ui/qt/section_editor.py`
- Creare nuovo editor Qt (legacy Tkinter è obsoleto)
- Canvas disegno sezione in scala con:
  - Contorno sezione con quote
  - Baricentro (punto)
  - Assi principali di inerzia (linee)
  - Raggi giratori (cerchi)
  - Nocciolo centrale (poligono ombreggiato)
  - Ellisse centrale (ellisse tratteggiata)
  - Armature (cerchi colorati con diametro)
- Pannello proprietà: tabella con tutti i parametri statici
- Input: selezione tipo sezione + dimensioni, oppure poligono custom
- Supporto sezione con aperture (holes)

**R3. Sezione omogenizzata** — per verifiche CA
- Input: sezione geometrica + armature (posizione, area, n)
- Calcolo area omogenizzata: A_om = A_cls + (n-1)×ΣA_si
- Baricentro omogenizzato
- Inerzia omogenizzata: I_om
- Già parziale in `historical_ta/geometry.py`; centralizzare

### FASE S — Pressoflessione Retta e Deviata (da implementare subito)

**S1. Pressoflessione retta NTC2018 SLU** — `src/methods/ntc2018/pressoflessione.py`
- Diagramma di interazione N-M (dominio di rottura)
- Calcolo asse neutro per N + M assegnati
- Stress block rettangolare (λ=0.8, η=1.0 per f_ck ≤ 50 MPa)
- Sezione semplicemente e doppiamente armata
- Output: N_Rd, M_Rd, x/d, utilizzazione
- Diagramma N-M con punto di lavoro sovrapposto

**S2. Pressoflessione deviata NTC2018 SLU** — `src/methods/ntc2018/pressoflessione_deviata.py`
- Formula semplificata (contorno di Bresler): (M_Edx/M_Rdx)^α + (M_Edy/M_Rdy)^α ≤ 1
- α funzione di N_Ed/N_Rd (da 1.0 a 2.0)
- Metodo rigoroso: ricerca asse neutro inclinato (Newton-Raphson)
- Dominio 3D (N, Mx, My) — visualizzazione

**S3. Pressoflessione retta RD2229 TA** — completare `src/methods/rd2229/pressoflessione.py`
- Già parziale nel normative_registry
- Aggiungere instabilità pilastri snelli (λ > 15)
- Riduzione σ_c,adm per snellezza (Art. 16)
- Sezione parzializzata vs interamente compressa

**S4. Pressoflessione deviata RD2229 TA** — già ✅ complete nel registry
- Verificare e integrare con nuova struttura package

### FASE T — Elementi Senza Armatura a Taglio (da implementare subito)

**T1. Taglio senza armatura NTC2018** — `src/methods/ntc2018/taglio.py` (estensione)
- V_Rd,c = [C_Rd,c × k × (100 × ρ_l × f_ck)^(1/3) + k₁ × σ_cp] × b_w × d
- Con: k = 1 + √(200/d) ≤ 2.0, C_Rd,c = 0.18/γ_c
- Minimo: V_Rd,c ≥ (v_min + k₁×σ_cp) × b_w × d
- §4.1.2.1.3.1 NTC + §C4.1.2.1.3.1 Circolare
- Già template parziale in `src/codes/ntc2018/checks_vrdc.py` — RIUSARE

**T2. Taglio senza armatura RD2229 TA** — estensione `src/methods/rd2229/taglio.py`
- τ = V / (b × d) ≤ τ_c0 (tensione ammissibile senza staffe)
- Se τ > τ_c0: armatura necessaria
- Se τ > τ_c1: sezione insufficiente

**T3. Elementi non armati (calcestruzzo semplice)** — `src/methods/ntc2018/cls_non_armato.py`
- NTC2018 §4.1.12: strutture in calcestruzzo non armato
- Resistenza a compressione: N_Rd = f_cd × A_c × (1 - 2×e/h)
- Eccentricità massima: e ≤ 0.45×h (§4.1.12.1.1)
- Resistenza a taglio: V_Rd = f_ctd × b × h / γ
- Nessuna armatura → no fessurazione, no duttilità
- Warning esplicito nella GUI: "Elemento in cls non armato - verificare requisiti §4.1.12"

### FASE U — Grafici Sollecitazioni, Inviluppi, Spostamenti (da implementare subito)

**U1. Modulo grafici** — `src/plotting/`
```
src/plotting/
├── __init__.py
├── diagrams.py        # Diagrammi M, V, N lungo l'asta
├── envelopes.py       # Inviluppi di sollecitazione
├── deformed.py        # Deformata e spostamenti
├── interaction.py     # Diagrammi di interazione N-M, N-Mx-My
├── section_plot.py    # Disegno sezione con proprietà
└── qt_widgets.py      # Widget Qt per embedding in GUI
```

**U2. Diagrammi sollecitazioni** — `src/plotting/diagrams.py`
- Diagramma momento flettente M(x) lungo l'asta
- Diagramma taglio V(x)
- Diagramma sforzo normale N(x)
- Scala automatica, quote, valori caratteristici
- Segno convenzionale configurabile (teso sotto/sopra)
- Colori personalizzabili per tipo di sollecitazione
- Backend: matplotlib per export + Qt canvas per GUI interattiva

**U3. Inviluppi** — `src/plotting/envelopes.py`
- Inviluppo per combinazioni multiple: M_max(x), M_min(x), V_max(x), V_min(x)
- Aree colorate tra inviluppo superiore e inferiore
- Combinazione critica evidenziata per ogni sezione
- Tabella riassuntiva valori massimi/minimi per sezione

**U4. Deformata e spostamenti** — `src/plotting/deformed.py`
- Deformata elastica dell'asta/telaio
- Scala di amplificazione configurabile
- Spostamenti nodali in tabella
- Rotazioni nodali
- Freccia massima evidenziata con quota

**U5. Diagrammi di interazione** — `src/plotting/interaction.py`
- Dominio N-M per sezione CA (SLU)
- Curva di interazione con punto di lavoro (N_Ed, M_Ed)
- Dominio 3D N-Mx-My (proiezioni 2D)
- Dominio T-V (interazione torsione-taglio)

**U6. Widget Qt** — `src/plotting/qt_widgets.py`
- Widget Qt per embedding matplotlib in finestre
- Zoom, pan, export PNG/SVG/PDF
- Toolbar con strumenti di misura
- Sincronizzazione tra grafici (hover su uno evidenzia sugli altri)

### FASE V — Solai

**V1. Solaio in laterocemento** — `src/elements/solai/laterocemento.py`
- Tipi: travetti prefabbricati, gettati in opera, precompressi
- Geometria: interasse, altezza blocco, cappa, larghezza nervatura
- Sezione resistente: T equivalente (NTC2018 §4.1.9)
- Verifiche:
  - Flessione SLU (campata + appoggio)
  - Taglio SLU (verifica V_Rd,c senza staffe + con staffe nei travetti)
  - Fessurazione SLE (apertura fessure w_k)
  - Deformazioni SLE (freccia, L/250 aspetto, L/500 danno)
- Carichi: peso proprio (da tabelle produttori), permanenti, accidentali
- Tabelle di predimensionamento: altezza minima h ≥ L/25 (solaio ordinario)

**V2. Solaio alveolare precompresso** — `src/elements/solai/alveolare.py`
- Geometria da catalogo produttore (spessori 12÷50 cm)
- Precompressione: fili aderenti, tensione iniziale σ_pi
- Verifiche:
  - SLU: M_Rd con armatura pretesa
  - SLE tensioni: σ_c ≤ 0.6×f_ck (combinazione rara), σ_c ≤ 0.45×f_ck (quasi-permanente)
  - SLE fessurazione: classe 2 (assenza decompressione) o classe 3 (w_k)
  - Taglio: V_Rd,c con contributo precompressione
- Ancoraggio testata: zona di diffusione precompressione

**V3. Solaio misto acciaio-cls** — `src/elements/solai/misto.py`
- Lamiera grecata + getto collaborante
- Connessione: pioli Nelson (NTC §4.3.4.3, EC4)
- Verifiche: flessione (sezione mista), taglio longitudinale, fuoco
- Fasi: fase 1 (solo lamiera), fase 2 (mista collaborante)

**V4. GUI solai** — `src/ui/qt/solaio_editor.py`
- Selezione tipo solaio (laterocemento, alveolare, misto)
- Input geometrico con anteprima sezione
- Tabella carichi con calcolo peso proprio automatico
- Risultati: verifiche + diagrammi M/V + freccia

### FASE W — Scale

**W1. Rampa scala** — `src/elements/scale/rampa.py`
- Geometria: luce, alzata, pedata, spessore, inclinazione
- Modello: soletta inclinata semplicemente appoggiata o incastrata
- Carico: peso proprio (soletta + gradini) + accidentale (Cat. C1: 4.0 kN/m²)
- Peso gradini: γ_cls × (alzata/2) × pedata / pedata
- Verifiche:
  - Flessione SLU
  - Taglio (generalmente verificato per spessori ordinari)
  - Deformazioni SLE
  - Armatura minima

**W2. Pianerottolo** — `src/elements/scale/pianerottolo.py`
- Soletta piana con carichi da rampe convergenti
- Verifica a flessione per carichi concentrati da rampe
- Continuità con rampe (momenti negativi all'attacco)

**W3. Trave a ginocchio** — `src/elements/scale/trave_ginocchio.py`
- Trave inclinata di bordo scala
- Pressoflessione (N + M da geometria inclinata)
- Torsione (carico eccentrico dalla soletta)

### FASE X — Fondazioni e Geotecnica

#### Livelli di implementazione per normativa

**Notazione livelli:**
- **L0** = NON APPLICABILE (la norma non tratta questo aspetto)
- **L1** = PREDISPOSIZIONE (modello dati + interfaccia, TODO espliciti, nessuna formula)
- **L2** = PARZIALE (formula base implementata, casi speciali TODO)
- **L3** = COMPLETO (implementazione completa citabile in relazione di calcolo)

**Normative considerate:**
- **RD2229**: Regio Decreto 2229/1939 (tensioni ammissibili, solo σ_amm terreno)
- **DM88**: DM 11/03/1988 — primo geotecnico moderno italiano (superato)
- **DM96**: DM 16/01/1996 (aggiornamento fondazioni, ancora TA)
- **NTC2018+C7**: DM 17/01/2018 Cap.6 + Circ. 7/2019 Cap.C6 (GEO/STR/HYD/UPL)
- **EC7**: EN 1997-1:2004 (Eurocode 7 — geotechnical design)
- **EC8-5**: EN 1998-5:2004 (fondazioni sotto azione sismica)

#### Matrice copertura geotecnica

| Verifica | RD2229 | DM88 | DM96 | NTC2018+C7 | EC7 | EC8-5 |
|----------|--------|------|------|-----------|-----|-------|
| Capacità portante fond. superficiali | L2 | L2 | L2 | L3 | L2 | L1 |
| Cedimenti (elastici + consolidazione) | L1 | L2 | L2 | L2 | L2 | L0 |
| Plinto su terreno: pressioni | L2 | L2 | L2 | L3 | L2 | L1 |
| Trave rovescia su suolo Winkler | L1 | L1 | L1 | L2 | L1 | L0 |
| Platea su suolo elastico | L1 | L1 | L1 | L1 | L1 | L0 |
| Pali: capacità portante assiale | L0 | L1 | L1 | L2 | L2 | L1 |
| Pali: capacità portante laterale | L0 | L0 | L0 | L1 | L1 | L1 |
| Gruppo pali: efficienza | L0 | L0 | L0 | L1 | L1 | L0 |
| Muro di sostegno: spinta attiva/passiva | L1 | L2 | L2 | L2 | L2 | L1 |
| Muro di sostegno: ribaltamento/scorrimento | L1 | L2 | L2 | L3 | L2 | L1 |
| Muro di sostegno: portanza base | L1 | L2 | L2 | L3 | L2 | L1 |
| Paratia (verifica globale) | L0 | L0 | L0 | L1 | L1 | L0 |
| Stabilità pendii (Bishop, Fellenius) | L0 | L0 | L0 | L1 | L1 | L1 |
| Tiranti al suolo | L0 | L0 | L0 | L1 | L1 | L0 |
| Liquefazione (NTC §7.11.3.4.2) | L0 | L0 | L0 | L2 | L0 | L2 |
| Fondazioni sismiche (GFOS) | L0 | L0 | L0 | L2 | L0 | L2 |

#### Struttura package geotecnica
```
src/geotecnica/
├── __init__.py
├── models/
│   ├── terreno.py          # SoilLayer, SoilProfile, SoilParams
│   ├── fondazione.py       # FoundationGeometry, FoundationResult
│   └── muro_sostegno.py    # RetainingWallGeometry, EarthPressureResult
├── portanza/
│   ├── __init__.py
│   ├── terzaghi.py         # Formula Terzaghi (DM88/DM96)
│   ├── hansen.py           # Formula Hansen / Meyerhof (NTC2018+EC7)
│   ├── ntc2018.py          # NTC2018 §6.4 + Circ. C6.4
│   └── ec7.py              # EN1997 Annex D
├── cedimenti/
│   ├── __init__.py
│   ├── elastici.py         # Cedimento elastico (formula Boussinesq)
│   └── consolidazione.py   # Cedimento consolidazione (Terzaghi 1D) — L1
├── pali/
│   ├── __init__.py
│   ├── portanza_assiale.py # Q_b + Q_s (metodi α, β, λ)
│   └── portanza_laterale.py # Metodo Broms — L1
├── muri_sostegno/
│   ├── __init__.py
│   ├── spinte.py           # Rankine, Coulomb, Mononobe-Okabe (sismico)
│   ├── verifica_ntc.py     # Ribaltamento, scorrimento, portanza NTC2018
│   └── verifica_ec7.py     # DA1/DA2/DA3 approcci di calcolo
├── liquefazione/
│   ├── __init__.py
│   └── ntc2018.py          # NTC §7.11.3.4.2 — metodo semplificato CRR/CSR
├── sismica/
│   ├── __init__.py
│   └── ec8_5.py            # EN1998-5: amplificazione, GFOS — L1/L2
└── gui/
    └── geotecnica_widget.py # Qt widget per input terreno e risultati
Dettaglio implementazioni
X1. Plinto isolato — src/elements/fondazioni/plinto.py

Tipi: tozzo (rigido, l/h ≤ 1), snello (flessibile, l/h > 1), a bicchiere (prefabbricato)
Pressioni sul terreno: distribuzione trapezoidale/triangolare/uniforme

Caso centrico: σ = N/A
Caso eccentrico (1 asse): σ = N/A ± M/W = N/A ± 6Ne/(BL²)
Caso bieccenrico: formula bilineare


Capacità portante (NTC2018+C7 §6.4.2, L3):

Qult = c'×Nc×Fc + γ×Df×Nq×Fq + 0.5×γ×B×Nγ×Fγ (Hansen/Meyerhof)
Fattori forma Fc, Fq, Fγ (per piante rettangolari, quadrate, circolari)
Fattori inclinazione per forze orizzontali
Combinazioni GEO: A1+M1+R1 / A2+M2+R1 / A2+M2+R2


Capacità portante TA (RD2229, L2): σ_amm = σ_lim / CS_terreno (CS = 3 di norma)
Verifiche strutturali plinto (CA o cls semplice):

Punzonamento: v_Ed ≤ v_Rd,c (NTC §4.1.2.1.3.4, L3)
Flessione: momento su sezione di riferimento (x = faccia pilastro)
Taglio a una via (travi e mensoloni)
Armatura minima


Collegamento pilastro-plinto: calcolo lunghezza ancoraggio barre

X2. Trave rovescia — src/elements/fondazioni/trave_rovescia.py

Trave continua su suolo elastico (modello Winkler, L2)
Coefficiente di sottofondo k_s: input utente o correlazioni (SPT, PLT)
Soluzione analitica (travi infinite/semi-infinite su suolo elastico)
Pressioni di contatto: distribuzione reazione suolo
Verifiche strutturali: flessione, taglio, fessurazione, deformazioni
Predisposizione per soluzione FEM (FASE J)

X3. Platea — src/elements/fondazioni/platea.py (L1)

Modello dati + interfaccia; calcolo richiede FEM 2D (piastre su suolo)
Predisposizione per collegamento con FASE J (FEM beam 2D → FEM piastra)
Verifiche strutturali elementari: punzonamento pilastri, flessione media

X4. Pali — src/elements/fondazioni/pali.py

Portanza assiale (NTC2018 §6.4.3, L2):

Q_b = q_b × A_b (base): correlazioni SPT, CPT, o da prove di carico
Q_s = Σ(q_si × A_si) (attrito laterale): metodi α (argilla), β (sabbia)
Verifica GEO: R_c,k ≥ F_c,d / ξ_i (fattori di correlazione da Tab.6.4.I NTC)


Portanza laterale (L1): predisposizione metodo Broms, p-y curves
Gruppo pali (L1): efficienza η_G, distribuzione carichi da corda
Palo sismico (EC8-5 §5, L1): verifica curvatura, lunghezza libera

X5. Muro di sostegno — src/geotecnica/muri_sostegno/

Tipi: gravità, a mensola (CA), a contrafforti, gabbioni
Spinte terra (L2):

Rankine: K_a = tan²(45 - φ'/2), K_p = tan²(45 + φ'/2)
Coulomb: con attrito muro-terra (δ = 2/3 φ')
Mononobe-Okabe (sismica, L1)


Verifiche stabilità (NTC2018 §6.5, L3):

Ribaltamento: ΣM_stab / ΣM_rib ≥ R_rib (approccio TA) / M_stab,d ≥ M_rib,d (GEO)
Scorrimento: H_d ≤ R_h,d = V_d × tan(δ_d) + c_d × A
Portanza base fondazione: metodo Hansen


Verifiche strutturali mensola (L2): flessione, taglio, armatura minima

X6. Geotecnica sismica — src/geotecnica/sismica/

Liquefazione (NTC2018 §7.11.3.4.2, L2):

CRR = f(SPT_N₁,₆₀) — curva di resistenza da standard
CSR = 0.65 × (a_g/g) × (σ_v0/σ'_v0) × r_d
FS_liq = CRR × MSF / CSR; se FS_liq < 1 → potenziale liquefazione
Categorie di suolo A÷F: amplificazione sismica locale


Amplificazione sismica locale (NTC §3.2.2, L2):

Categorizzazione suolo: Vs30 da prove geofisiche
Fattori S_S, S_T (stratigraphic + topographic amplification)


Fondazioni sotto sisma (EC8-5, L1):

Verifica capacità portante con azione sismica: q_Rd,seis ≤ q_Rd,stat × (1 - F_seis/N)
Predisposizione modello dati per GFOS (Global Foundation Overstrength factor)



X7. Cedimenti — src/geotecnica/cedimenti/

Cedimento elastico (L2): s_e = q × B × (1-ν²)/E_s × I_f (fattore di forma)
Cedimento di consolidazione (L1): s_c = H × C_c/(1+e₀) × log(σ'_v0+Δσ/σ'_v0)
Limiti di cedimento: NTC §6.4.1 (tabella indicativa)
Cedimento differenziale: calcolo tra punti fondali diversi

X8. GUI geotecnica — src/geotecnica/gui/geotecnica_widget.py

Widget Qt per profilo stratigrafico (tabella strati: z, γ, φ', c', E_s, ν)
Calcolo Vs30 da velocità onde S per strato
Visualizzazione grafica profilo (canvas Qt: colori per tipo suolo)
Esportazione relazione geotecnica (sezione dedicata nel report)

FASE X-BIS — Resistenza Calcestruzzo in Sito (Carote)
Modulo dedicato: src/existing_buildings/concrete_cores/
Calcolo della resistenza del calcestruzzo in sito a partire dalle prove su carote estratte da elementi strutturali esistenti, secondo molteplici formulazioni presenti in letteratura.
X-BIS.1. Modello dati carota — core_sample.py
python@dataclass
class CoreSample:
    id: str
    elemento_origine: str       # elemento strutturale di provenienza
    diametro_mm: float          # φ carota (tipico: 75, 94, 100, 150 mm)
    altezza_mm: float           # altezza campione (L/D ratio)
    direzione_estrazione: str   # orizzontale/verticale (rispetto al getto)
    presenza_armatura: bool     # barra inclusa nel campione → correzione
    stato_saturazione: str      # secco / saturo / naturale
    f_carota_lab_MPa: float     # resistenza da prova in laboratorio (input)
    data_prova: str
    laboratorio: str
    note: str
```

**X-BIS.2. Formulazioni di conversione** — `conversion_formulas.py`
Dalla resistenza della carota (f_core) alla resistenza in sito (f_is) e al cilindrico f_c:

| Formulazione | Riferimento | Livello |
|--------------|-------------|---------|
| British Standard BS 1881 Part 120 | Fattore L/D + direzione | L3 |
| ACI 214.4R-10 | Fattore forma + umidità | L3 |
| Concrete Society TR11 | Conversione con fattori multipli | L3 |
| RILEM (1979) | Fattore L/D specifico | L3 |
| Masi (2005) | Ricerca italiana su carote esistenti | L2 |
| Fiore et al. (2008) | Correzione per calcestruzzo storico | L2 |
| NTC2018 + Circ. 7/2019 §C8.5.3 | Procedura normativa per LC1/LC2/LC3 | L3 |
| EN 13791:2019 | Standard europeo carote | L2 |
| Formula utente custom | Inserimento manuale formula | L2 |

- **Fattori di correzione** applicati a ciascuna formulazione:
  - L/D ratio (slenderness): correzione se L/D ≠ 2.0 (tipico 1.0÷2.0)
  - Direzione estrazione: orizz. vs vert. (differenza ~5÷8%)
  - Presenza armatura: riduzione 5÷15% se barra presente
  - Stato umidità: secco vs saturo (~10÷15%)
  - Diametro carota: correlazione a cilindri standard 150×300
  - Danno da estrazione (drilling damage): fattore riduttivo ~0.92÷0.98
- **Output per ogni formulazione**:
  - f_is (resistenza in sito)
  - f_ck,is (caratteristica stimata)
  - E_cm (modulo elastico): da correlazione (es. EC2 §3.1.3: E_cm = 22×(f_cm/10)^0.3 GPa)
  - f_ctm (trazione media): da f_cm
  - Tutti i parametri meccanici derivati del calcestruzzo

**X-BIS.3. Analisi statistica carote** — `statistics.py`
- Campione di N carote → media, dev.std, CoV
- Stima f_ck,is secondo:
  - NTC2018 Circ. §C8.5.3: in funzione del Livello di Conoscenza (LC1/LC2/LC3) e FC
  - EN 13791 Metodo A (≥15 carote) e Metodo B (3÷14 carote)
- Outlier detection (test Grubbs o Chauvenet)
- Classificazione calcestruzzo esistente (stima classe originale probabile)

**X-BIS.4. GUI carote** — `src/ui/qt/concrete_cores_widget.py`
- **Tabella input**: elenco carote con tutti i campi (ComboBox per direzione/saturazione/diametro standard + sempre input manuale possibile)
- **Dropdown formulazione**: selezione da catalogo formulazioni (BS, ACI, RILEM, NTC...) + possibilità di selezionarne multiple per confronto
- **Tabella risultati**: griglia comparativa (formulazione × parametro) per ogni carota
- **Statistiche**: media, dev.std, f_ck_is per ogni formulazione
- **Grafico**: istogramma resistenze + curva gaussiana stima; scatter f_core vs f_is per formulazione
- **Import da Excel**: possibilità di importare file Excel con dati carote (utente fornirà template)
- **Export relazione**: sezione dedicata nel report con tabella risultati e citazione normativa

**X-BIS.5. Archivio centralizzato** — integrazione con `src/materials/`
- I risultati (f_ck_is, E_cm, f_ctm) vengono registrati nell'archivio materiali come `ConcreteInSitu`
- Utilizzabili direttamente come materiale per le verifiche di edifici esistenti (FASE N)
- Nessuna duplicazione: lo stesso archivio materiali serve tutto il software

### FASE Y — Sismica Dettagliata

**Y0. Parametri sismici di sito** — `src/codes/ntc2018/seismic/parametri_sito.py`

Calcolo parametri sismici in funzione di: **posizione geografica**, **classe d'uso**, **vita utile**.

- **Vita di riferimento** VR (NTC2018 §2.4.3):
  - Vita nominale VN: 10 anni (provvisorie), 25 (agricole), 50 (ordinarie), 100 (strategiche)
  - Coefficiente CU per classe d'uso: CU=0.7 (CI), CU=1.0 (CII), CU=1.5 (CIII), CU=2.0 (CIV)
  - VR = VN × CU ≥ 35 anni
- **Periodi di ritorno TR** per stati limite (NTC2018 Tab.3.2.I):
  - SLO (operatività): PVR = 81% → TR_SLO = -VR / ln(1-0.81)
  - SLD (danno): PVR = 63% → TR_SLD
  - SLV (salvaguardia vita): PVR = 10% → TR_SLV
  - SLC (collasso): PVR = 5% → TR_SLC
- **Parametri spettrali ag, F0, Tc*** da griglia NTC2018 (Annesso A):
  - **Griglia NTC2018** pubblica: 10751 punti, file hazard.npy / zone.npy (INGV)
  - Interpolazione bilineare per lat/lon non coincidente con nodi
  - Input 1 — **Griglia integrata**: inserisci lat/lon → calcolo automatico da griglia INGV
  - Input 2 — **Import da Edilus mappe sismiche**: incolla/importa i valori ag, F0, Tc* già calcolati da Edilus (evita ridondanza calcolo)
  - Input 3 — **Manuale**: inserisci direttamente ag, F0, Tc* per ogni TR
- **Spettro elastico** Se(T) — NTC2018 §3.2.3.2:
  - TC = CC × TC*, TB = TC/3, TD = max(4×ag/g + 1.6, 2.0)
  - CC: coefficiente da categoria suolo (Tab.3.2.V)
  - Plateau: Se = ag × S × F0 (per TB ≤ T ≤ TC)
- **Spettro di progetto** Sd(T) = Se(T) / q (ridotto per comportamento non lineare)
- **GUI parametri sismici** — `src/ui/qt/seismic_params_widget.py`:
  - Mappa interattiva Italia (matplotlib) con click per selezione sito
  - ComboBox classe d'uso (CI÷CIV) + input VN
  - Tabella riepilogativa ag/F0/Tc* per tutti i TR
  - Bottone "Importa da Edilus" (incolla testo formattato Edilus → parsing automatico)
  - Visualizzazione spettri Se(T) per i 4 stati limite sovrapposti su grafico

**Y1. Fattore di comportamento q** — `src/codes/ntc2018/seismic/`
- NTC2018 §7.3.1: q = q_0 × K_R
- q_0 da tipo strutturale e classe di duttilità (CD"A", CD"B")
  - Telai: q_0 = 3.0α_u/α_1 (CD"A"), 4.5α_u/α_1 (CD"B")
  - Pareti: q_0 = 3.0 (CD"A"), 4.0α_u/α_1 (CD"B")
  - Miste: q_0 medio
- K_R: regolarità in altezza (1.0 regolare, 0.8 irregolare)
- Tabella §7.4.1 con tutti i valori

**Y2. Duttilità e dettagli costruttivi** — `src/codes/ntc2018/seismic/ductility.py`
- Classe di duttilità alta (CD"A") e bassa (CD"B")
- Requisiti geometrici zone critiche:
  - Travi: h_cr = h_trave, l_cr = h_trave (§7.4.4.1.1)
  - Pilastri: l_cr = max(h_pil, L/6, 45cm) (§7.4.4.2.1)
- Armatura zone critiche:
  - Staffe: passo ≤ min(h/4, 175mm, 6φ_long) in CD"A"
  - Confinamento: ω_wd ≥ 0.08 (CD"A"), ≥ 0.12 con N alto
- Gerarchia delle resistenze:
  - Pilastro forte / trave debole: ΣM_Rd,col ≥ 1.3 × ΣM_Rd,beam (§7.4.4.2.1)
  - Taglio da gerarchia: V_Ed = (M_Rd,i + M_Rd,j) / l_cl × γ_Rd (§7.4.4.1.2.2)

**Y3. Nodi trave-pilastro** — `src/codes/ntc2018/seismic/joints.py`
- Verifica nodo confinato: V_jh ≤ η × f_cd × b_j × h_jc (§7.4.4.3.1)
- Nodo non confinato: V_jh ≤ 0.3 × η × f_cd × b_j × h_jc
- Armatura nel nodo: staffe orizzontali ≥ armatura pilastro sopra
- Ancoraggio barre trave nel nodo

**Y4. Pareti sismiche** — `src/codes/ntc2018/seismic/walls.py`
- Pareti duttili: zone critiche alla base (NTC §7.4.4.5)
- Armatura minima: ρ_h ≥ 0.2%, ρ_v ≥ 0.3%
- Elementi di bordo confinati
- Taglio: V_Rd ≥ V_Ed da gerarchia
- Limitazione sforzo normale: ν_d ≤ 0.40 (CD"A")

**Y5. Spettro e azioni sismiche** (parzialmente in src/codes/ntc2018/)
- Spettro elastico S_e(T) — verificare implementazione
- Spettro di progetto S_d(T) = S_e(T) / q
- Combinazione sismica: E + G₁ + G₂ + ψ₂×Q
- Effetti torsionali accidentali: e_a = ±0.05×L

### FASE Z — Sviluppi Futuri Ulteriori (solo pianificazione)

- Analisi pushover (non lineare statica)
- Analisi time-history (non lineare dinamica)
- FEM 2D/3D solido per analisi termica fuoco (L3 avanzato)
- Precompressione (post-teso e pre-teso)
- Strutture prefabbricate (collegamenti, tolleranze)
- Ponti (carichi mobili, treni di carico NTC/EC1)
- Strutture in legno (NTC §4.4, EC5, CNR-DT 206)
- Strutture in acciaio complete (NTC §4.2, EC3)
- Geotecnica avanzata (stabilità pendii, muri di sostegno, terre armate)

---

## Principi Architetturali Fondamentali

1. **Modularità estrema**: ogni modulo/routine di calcolo deve essere autonomo e sostituibile senza intaccare il resto del software. Mai refactoring completi per modificare un singolo modulo.
2. **Zero duplicazione funzioni**: nessuna funzione duplicata tra schede/widget diversi. Se due moduli necessitano della stessa logica → funzione condivisa in modulo comune (`src/core/`, `src/materials/`, etc.).
3. **Archivi centralizzati e condivisi**: materiali, impostazioni, coefficienti, normative → UNA sola sorgente (repository/database). Mai frammentazione degli archivi. Tutti i moduli attingono dallo stesso archivio.
4. **Dropdown da archivio + input manuale**: ogni parametro recuperabile da tabelle/archivi → ComboBox/dropdown per selezionare da catalogo. MA deve SEMPRE essere possibile inserire manualmente qualsiasi parametro (override utente).
5. **Interfacce stabili**: ogni modulo espone interfacce (ABC/Protocol) stabili. Implementazioni interne possono cambiare liberamente senza impatto sugli altri moduli.
6. **Single Responsibility**: ciascuna scheda GUI ha una funzione ben definita, senza sovrapposizioni con altre schede.
7. **Config-driven**: tutti i coefficienti e parametri normativi vengono da file `.jsoncode` o YAML, mai hardcoded nel codice.

---

## Decisioni Utente Confermate

- **Cordoli metallici**: tutti e subito (profili singoli + piatti + reticolari 2D); predisporre per 3D futuro
- **Tralicci**: piani con saldatura E bullonatura da subito; 3D pianificato per futuro
- **Priorità sessione**: entrambi in parallelo (editor materiali + verifiche mancanti)
- **CNR-DT PDF**: installare poppler-utils per leggerli direttamente
- **Approccio generale**: rendere funzionante, rigore tecnico, chiarezza su implementato vs non implementato
- **Torsione**: partire da VB + ricerca online formule TA storiche; predisporre interfacce per PDF/scansioni futuri; VIETATE allucinazioni
- **Sagomario**: tabelle EN 10365 standard + possibilità di importare profili custom dell'utente
- **Muratura**: tabelle COMPLETE NTC2018 (Tab.4.5.I÷IV) + tabelle storiche DM 20/11/1987 e Circ. 4/1981
- **SLE**: input manuale M_Ed come default + opzione calcolo automatico da modulo combinazioni esistente
- **GUI**: SOLO Qt (PySide6/PyQt6). Legacy Tkinter è DEPRECATO e OBSOLETO — non toccare
- **Struttura file**: Package per norma (methods/rd2229/torsione.py, methods/ntc2018/fessurazione.py)
- **Solutore traliccio**: solutore semplice metodo nodi + predisposizione interfaccia FEM futuro
- **Circolare n. 7/2019**: OBBLIGATORIA insieme a NTC2018 — tutte le verifiche NTC2018 devono citare anche la Circolare applicativa (Circ. 21/01/2019 n. 7 C.S.LL.PP.) come riferimento normativo complementare. Utente caricherà PDF + io leggo con poppler-utils
- **Migrazione methods/**: sposta subito checks_rd2229.py e checks_ntc2018.py nei nuovi package, aggiorna tutti gli import. Pulizia totale, nessun redirect
- **Cross-Pozzati carichi**: statici fissi implementati + interfaccia predisposta per carichi mobili futuri
- **FEM libreria**: scipy + numpy per algebra lineare e matrici sparse
- **Report**: relazione di calcolo professionale con citazione normativa automatica
- **Edifici esistenti**: LC1/LC2/LC3 con FC, meccanismi locali muratura, indice ζ_E
- **OCR manuali**: predisporre pipeline per scansioni Santarella/Giangreco con OCR matematico
- **Fonti Santarella/Giangreco**: cerco io online; utente fornirà scansioni in futuro
- **File VB futuri (da utente)**: l'utente fornirà file Visual Basic come base per: modello FEM, calcolo lastre, calcolo piastre, stabilità dei pendii, apertura fuori piano nella muratura. Quando consegnati: convertire in Python con massima modularità, mantenendo logica VB come riferimento
- **Muratura**: verifiche locali (F6.1÷F6.9) incluse catene, paletti, piastre di dimensioni diverse, punzonamento, cantonali, ribaltamento, spanciamento. Muratura senza cordoli (storica) pianificata. Multipiano con distribuzione sismica.
- **Geotecnica**: modulo completo src/geotecnica/ con matrice implementazione per normativa (RD2229, DM88, DM96, NTC2018+C7, EC7, EC8-5). Liquefazione, muri di sostegno, pali, cedimenti — livelli L0÷L3 definiti.
- **Carote calcestruzzo in sito (FASE X-BIS)**: implementare subito le formulazioni note dalla letteratura (BS 1881, ACI 214.4R, RILEM, Masi, NTC2018+C7, EN 13791). Utente fornirà file Excel con ulteriori formulazioni e fonti in futuro. GUI con tabella comparativa, import Excel, export relazione.
- **Parametri sismici (FASE Y0)**: griglia INGV integrata nel repository (~10751 punti, file JSON) per calcolo autonomo da lat/lon + bottone import da Edilus come alternativa. Classe d'uso (CI÷CIV), vita utile VN, spettri elastici e di progetto per SLO/SLD/SLV/SLC.
- **Muratura globale**: verifiche locali complete + modello a telaio equivalente semplificato (maschi + fasce come bielle). Predisposizione analisi pushover.
- **Architettura modulare**: archivi centralizzati (materiali, normative, coefficienti), dropdown da catalogo + sempre input manuale, zero duplicazione funzioni tra moduli, ogni modulo sostituibile indipendentemente.

## Priorità di Implementazione per Sessione Corrente

Lavoro in parallelo su più fronti. Fasi marcate "DA SUBITO":

**Fronte 1 — Fondamenta:**
1. Installare poppler-utils per leggere PDF CNR-DT
2. A1: Completare material_model.py (concrete/steel/masonry)
3. A2: Completare editor materiali Qt
4. R1-R3: Sezioni — completare parametri statici + GUI Qt + omogenizzata

**Fronte 2 — Verifiche Resistenza:**
1. S1-S4: Pressoflessione retta e deviata (NTC2018 SLU + RD2229 TA)
2. B1-B2: Torsione (RD2229 + NTC2018)
3. C1-C2: Instabilità (RD2229 + NTC2018)
4. T1-T3: Taglio senza armatura + CLS non armato

**Fronte 3 — Verifiche Esercizio:**
1. D1: Fessurazione NTC2018 SLE
2. E1-E2: Deformazioni NTC2018 + RD2229

**Fronte 4 — Grafici e Visualizzazione:**
1. U1-U6: Diagrammi M/V/N, inviluppi, deformata, interazione N-M

**Fronte 5 — Muratura e Cordoli:**
1. F1: Modello muratura + tabelle NTC + storiche
2. F2-F4: Cordoli metallici + sagomario + solutore traliccio
3. F5: GUI cordoli

## Strategia Documentazione e Tracciamento Avanzamenti

### File di tracciamento (creati durante implementazione)
```
docs/PROGRESS/
├── STATUS.md                    # Stato globale: cosa è FATTO vs cosa è DA FARE
├── FASE_A_materials.md          # Avanzamento FASE A — completato/in corso/TODO
├── FASE_B_torsione.md           # Avanzamento FASE B
├── FASE_F_muratura.md           # Avanzamento FASE F (incl. F6 verifiche)
├── FASE_X_geotecnica.md         # Avanzamento FASE X
├── FASE_X_BIS_carote.md         # Avanzamento FASE X-BIS
├── FASE_Y_sismica.md            # Avanzamento FASE Y
├── ... (uno per FASE)
└── ARCHITECTURE_DECISIONS.md    # Decisioni architetturali prese durante implementazione
STATUS.md — aggiornato ad ogni sessione con:

Tabella globale: FASE | Stato (✅/⚠️/❌) | % completamento | Ultima modifica | Note
Lista file modificati nell'ultima sessione
TODO immediati per la prossima sessione
Blocchi/dipendenze irrisolte

FASE_*.md — per ogni fase:

Checklist dettagliata sottotask con stato (☐/☑)
File creati/modificati con path esatto
Formule implementate con riferimento normativo (articolo, comma, tabella)
Test scritti e risultati
Punti aperti e decisioni pendenti

Requisiti GUI: riferimenti normativi e formule nel calcolo
Ogni widget/scheda di calcolo deve mostrare:

Riferimento normativo: articolo, comma, tabella della norma usata (es. "NTC2018 §4.1.2.1.3.2 + Circ.7 §C4.1.2.1.3.2")
Formula utilizzata: formula LaTeX o Unicode nel widget, con simboli spiegati
Passaggi di calcolo: dettaglio intermedi (N_Ed → A_s,calc → A_s,min → A_s,eff) visibili in area espandibile
Tooltip informativi: su ogni campo, tooltip con significato e unità di misura
Esportazione: tutti i passaggi riportati nella relazione di calcolo automatica

Ottimizzazione implementazione per sessioni
Principio: sessioni lunghe e ragionate, minima necessità operativa.

Batch per affinità: implementare insieme moduli correlati (es. tutte le verifiche muratura in una sessione)
Prima i modelli dati, poi la logica, poi la GUI: in quest'ordine — mai saltare fasi
Riuso codice esistente: prima di scrivere, verificare se esiste già funzionalità simile → riusare
Test inline: scrivere test unitari contestualmente al modulo, non in sessione separata
Nessun refactoring retroattivo: componenti completate NON si toccano più (salvo bug). Se serve modifica: creare nuova versione, non alterare l'esistente.
Documentazione contestuale: ogni file .py deve avere docstring con:

Riferimento normativo (articolo, tabella)
Formula principale usata
Unità di misura (kg/cm² default, MPa solo se esplicitamente richiesto)
Limitazioni note



Verifica

pytest tests/ — tutti i test esistenti devono passare
Verificare che material_model.py sia deserializzabile da JSON
Verificare che editor Qt si apra senza errori (se PySide6/PyQt6 disponibile)
Confronto valori calcolati con tabelle Santarella per RD2229
Leggere PDF CNR-DT dopo installazione poppler-utils
