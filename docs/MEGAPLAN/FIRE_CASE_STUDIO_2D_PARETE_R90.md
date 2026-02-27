
FIRE_CASE_STUDIO_2D_PARETE_R90 – Caso studio completo L2 vs L3 2D (parete in c.a.)
Status: STABILE
Ambito: Prototipale – uso tecnico‑didattico e di validazione interna
Ruolo: Caso studio ufficiale per la linea L3 2D (pareti) del modulo INCENDIO


1. Scopo del caso studio
Il presente documento sviluppa ex novo un caso studio completo di verifica al fuoco R90 di una parete portante in calcestruzzo armato, con confronto strutturato tra:

Metodo L2 (approccio semplificato normativo – sezione efficace)
Metodo L3 2D (analisi FEM termo‑meccanica avanzata)
Il caso studio ha i seguenti obiettivi:

dimostrare come impostare correttamente una verifica L3 2D a caldo
confrontare L2 vs L3 senza forzature né abusi del metodo avanzato
evidenziare meccanismi locali tipici delle pareti non intercettabili in 1D
⚠️ Il caso studio non ha valore certificativo ed è finalizzato a sviluppo, validazione e formazione.


2. Descrizione dell’elemento strutturale

Tipologia: Parete portante in c.a.
Stato limite: INCENDIO
Classe di resistenza richiesta: R90
Funzione strutturale: elemento verticale portante continuo
Normativa di riferimento:EN 1991‑1‑2
EN 1992‑1‑2


3. Dati geometrici e meccanici (input comuni)
3.1 Geometria della parete

Spessore parete: 25 cm
Larghezza di calcolo: 1.00 m (striscia unitaria)
Altezza considerata: unitaria (analisi di sezione 2D)
Copriferro nominale: 3.0 cm
Superfici esposte al fuoco: 1 lato


3.2 Materiali

Calcestruzzo: C25/30
Acciaio di armatura: B450C
Armatura verticale: distribuita, aderente
Le proprietà a caldo sono valutate secondo EN 1992‑1‑2.


3.3 Azioni in incendio

Sforzo normale di progetto in incendio: \\(N_{Ed,fi}\\)
Combinazione delle azioni: incendio accidentale (EN 1991‑1‑2)
Azioni orizzontali: trascurate (caso studio base)


4. Verifica con metodo L2 – Approccio semplificato
4.1 Impostazione del metodo L2
Il metodo L2 applicato alla parete prevede:

determinazione della profondità di calcestruzzo danneggiato
definizione della sezione efficace residua
verifica a presso‑compressione su sezione ridotta
Schema di verifica:
\\[ N_{Ed,fi} \\le N_{Rd,fi,90} \\]


4.2 Risultati della verifica L2

Spessore efficace residuo: sufficiente
Capacità resistente a 90 min: maggiore della domanda
Esito L2: ✅ OK – Classe R90 soddisfatta


4.3 Limiti intrinseci del metodo L2 per le pareti

analisi monodimensionale della sezione
temperatura media su strati
assenza di informazione su:gradienti termici locali
concentrazioni di deformazione
meccanismi di collasso localizzati
Il metodo è normativamente corretto, ma strutturalmente semplificato.


5. Analisi con metodo L3 2D a caldo
5.1 Motivazione dell’uso di L3 2D
L’analisi L3 2D è eseguita per:

valutare il gradiente termico bidimensionale reale
intercettare meccanismi locali di schiacciamento
determinare il tempo effettivo di collasso della parete


5.2 Modello FEM 2D adottato

Tipo di modello: solido 2D (quad)
Stato di sforzo: piano‑deformazioni
Analisi termica: STEP 4.1 – Analisi termica 2D5.3 Risultati dell’analisi L3 2D
Dall’analisi termo‑meccanica emergono:

campo termico fortemente non uniforme
elevate deformazioni lato esposto al fuoco
innesco di schiacciamento localizzato del calcestruzzoTempo di collasso individuato:
\\[ t_{coll,2D} \\approx 78\\,\	ext{min} \\]
Esito L3 2D: ❌ NOT_OK – Classe R90 non soddisfatta


6. Confronto diretto L2 vs L3 2D

Aspetto	L2	L3 2D
Tipo di modello	Sezione efficace	FEM 2D
		
		
		
		



7. Interpretazione ingegneristica
Il confronto mostra che:

il metodo L2 è globalmente conservativo, ma
non intercetta meccanismi locali tipici delle paretiL’analisi L3 2D evidenzia:
perdita anticipata di capacità portante
collasso locale prima del raggiungimento di R90⚠️ Questo risultato non invalida L2, ma segnala:
una condizione limite critica
la necessità di valutare:aumento di spessore
protezioni passive
riduzione delle sollecitazioni


8. Uso corretto dei risultati L3 2D
Secondo la filosofia del modulo INCENDIO:

L3 2D non sostituisce automaticamente L2
è uno strumento di:analisi avanzata
supporto progettuale
comprensione dei margini di sicurezzaOgni risultato L3 deve essere:
accompagnato da checklist di validazione
filtrato dal Gate di rilascio L3
documentato in modo trasparente


9. Conclusioni del caso studio

✅ L2: verifica conforme e normativamente valida
⚠️ L3 2D: evidenzia collasso anticipato
✅ Confronto L2 vs L3 2D eseguito in modo corretto, prudente e difendibileIl caso studio dimostra perché la linea 2D è indispensabile per le pareti portanti in incendio.


10. Collegamenti

FIRE_L3_STEP4_1_ANALISI_TERMICA_2D_CODICE.md
FIRE_L3_STEP4_2_ANALISI_MECCANICA_2D_FREDDO.md
FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO.md
FIRE_L3_COSTITUTIVE_NONLINEARI.md
FIRE_GATE_RILASCIO_L3_FEM.md



Analisi meccanica:validata a freddo (STEP 4.2)
accoppiata a caldo (STEP 4.3)
Leggi costitutive: non lineari termo‑dipendenti
Passo temporale: \\(\\Delta t = 5\\,s\\)
