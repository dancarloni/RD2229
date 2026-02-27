
FIRE_L3_STEP4_MODELLI_2D_PARETI – Apertura linea 2D (pareti portanti)
Status: IN AVVIO
Ruolo: Nuovo STEP per estensione del solver FEM L3 a modelli 2D di pareti portanti in c.a.


1. Scopo dello STEP 4
Questo documento apre formalmente la linea 2D (pareti portanti) come nuovo STEP del modulo L3 FEM al fuoco, estendendo quanto sviluppato per elementi 1D (beam‑fiber) a modelli bidimensionali di pareti.
Lo STEP 4 ha lo scopo di:

introdurre la modellazione 2D di pareti in c.a. in incendio
gestire meccanismi locali non catturabili in 1D
preparare l’evoluzione verso solver FEM interno avanzato


2. Perché aprire la linea 2D (pareti)
La modellazione 1D risulta insufficiente per:

pareti portanti soggette a gradiente termico bidimensionale
distribuzioni non uniformi delle tensioni
meccanismi locali di schiacciamento o instabilità
Le pareti sono spesso elementi critici in incendio e richiedono:

modellazione continua della sezione
valutazione locale del danno


3. Ambito dello STEP 4 (iniziale e controllato)
In questa prima fase 2D si implementa solo:

parete rettangolare in c.a.
modello 2D di sezione (non ancora parete estesa in altezza)
analisi termo‑meccanica piano‑sforzi / piano‑deformazioni
incendio ISO 834
Sono esclusi in questo STEP:

instabilità globale di parete
analisi 3D
comportamento fuori piano


4. Architettura FEM 2D
4.1 Tipo di modello

elementi 2D solidi (quad / tri)
mesh regolare iniziale
nodi con:temperatura
spostamenti


4.2 Relazione con il solver L3 1D
Il solver 2D:

riusa:modulo termico L3
leggi costitutive non lineari
sostituisce:integrazione beam‑fiber
curvatura 1D


5. Analisi termica 2D (STEP 4.1)
5.1 Obiettivo
Calcolare il campo di temperatura 2D nella sezione della parete:
\\[ T(x,y,t) \\]


5.2 Semplificazione iniziale
Nella prima iterazione:

temperatura imposta per strati
dipendenza da distanza dalla superficie esposta
nessuna diffusione avanzata
Questo consente:

continuità con ISO 834
stabilità numerica


6. Analisi meccanica 2D (STEP 4.2)
6.1 Stato di sforzo

piano‑sforzi per pareti snelle
piano‑deformazioni per pareti tozze
La scelta è un parametro esplicito.


6.2 Leggi costitutive

calcestruzzo: non lineare compressivo a caldo
acciaio: bilineare a caldo
perfetta aderenza acciaio‑cls (prima iterazione)


7. Accoppiamento termo‑meccanico 2D
Schema concettuale:

aggiornamento campo termico
aggiornamento proprietà materiali elemento‑per‑elemento
risoluzione equilibrio 2D
verifica collasso locale


8. Criteri di collasso per pareti
Il collasso della parete è dichiarato quando:

perdita di convergenza globale
schiacciamento locale esteso
formazione di meccanismo fragile
Il tempo di collasso è:
\\[ t_{coll,2D} \\]


9. Output dello STEP 4
Il solver 2D deve produrre:

VerificationResultItem (fire_method = L3)
campo di temperatura finale
mappa delle zone danneggiate
tempo di collasso


10. Test minimi obbligatori
Prima di avanzare allo STEP successivo:

☐ test termico 2D elementare
☐ test meccanico 2D a freddo
☐ confronto qualitativo 1D vs 2D


11. Gate di avanzamento linea 2D
La linea 2D può avanzare solo se:

i test minimi sono superati
la checklist L3 è soddisfatta
il Gate L3 consente l’estensione


12. Evoluzione futura (STEP successivi)
Dalla linea 2D si potrà evolvere verso:

pareti estese in altezza (2.5D)
accoppiamento globale
modelli 3D


13. Collegamenti

FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md
FIRE_L3_COSTITUTIVE_NONLINEARI.md
FIRE_L3_ANALISI_COMPLETE_E_CONFRONTO_L2_L3.md
FIRE_GATE_RILASCIO_L3_FEM.md
