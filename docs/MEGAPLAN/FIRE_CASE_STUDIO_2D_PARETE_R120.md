
FIRE_CASE_STUDIO_2D_PARETE_R120 – Estensione del caso studio L3 2D (parete in c.a.)
Status: STABILE
Ambito: Prototipale – validazione avanzata e supporto progettuale
Ruolo: Estensione a R120 del caso studio ufficiale L3 2D per pareti portanti in c.a.


1. Scopo dell’estensione a R120
Il presente documento estende formalmente e operativamente il caso studio:

FIRE_CASE_STUDIO_2D_PARETE_R90.mdalla classe di resistenza al fuoco R120, mantenendo:
stessa geometria di base
stesso modello FEM 2D
stesso impianto metodologico L2 vs L3
L’obiettivo è:

verificare la robustezza del modello L3 2D su durate elevate
valutare l’evoluzione dei meccanismi locali oltre R90
fornire un riferimento per R120 in ambito prestazionale
⚠️ Anche questo caso studio è non certificativo.


2. Dati di base (immutati rispetto a R90)
2.1 Geometria

Spessore parete: 25 cm
Larghezza di calcolo: 1.00 m
Altezza considerata: unitaria (sezione 2D)
Copriferro nominale: 3.0 cm
Superfici esposte al fuoco: 1 lato


2.2 Materiali

Calcestruzzo: C25/30
Acciaio di armatura: B450C
Leggi costitutive: non lineari termo‑dipendenti


2.3 Azioni in incendio

Sforzo normale di progetto in incendio: \\(N_{Ed,fi}\\)
Combinazione incendio accidentale (EN 1991‑1‑2)
Azioni orizzontali: trascurate


3. Verifica con metodo L2 – Estensione a R120
3.1 Impostazione
Il metodo L2 viene applicato per la durata R120, mediante:

incremento della profondità di calcestruzzo danneggiato
riduzione della sezione efficace
verifica a presso‑compressione su sezione residua
Schema di verifica:
\\[ N_{Ed,fi} \\le N_{Rd,fi,120} \\]


3.2 Esito della verifica L2 (R120)

Spessore efficace residuo: fortemente ridotto
Capacità resistente a 120 min: al limite / insufficiente
Esito L2 (R120): ⚠️ AL LIMITE / NOT_OK


3.3 Commento sul metodo L2 a R120
Per durate elevate:

il metodo L2 diventa estremamente conservativo
la sensibilità a copriferro e spessore cresce fortemente
l’informazione locale rimane assente


4. Analisi con metodo L3 2D a caldo – R120
4.1 Modello FEM adottato

Tipo di modello: solido FEM 2D (quad)
Stato di sforzo: piano‑deformazioni
Analisi termica: STEP 4.1 – Analisi termica 2D4.2 Evoluzione termo‑meccanica fino a 120 min
L’analisi evidenzia:

propagazione profonda del fronte termico
drastica riduzione delle proprietà meccaniche
estensione delle zone di schiacciamento
perdita progressiva di rigidezza globale


4.3 Tempo di collasso individuato
Il collasso della parete avviene a:
\\[ t_{coll,2D}^{R120} \\approx 96\\,\	ext{min} \\]
con meccanismo di:

schiacciamento diffuso del calcestruzzo lato esposto
perdita di equilibrio globaleEsito L3 2D (R120): ❌ NOT_OK – Classe R120 non soddisfatta


5. Confronto R90 vs R120 (L3 2D)

Classe	Tempo di collasso L3 2D	Esito
R90	≈ 78 min	NOT_OK
		

Il passaggio a R120 non comporta un incremento lineare del tempo di resistenza.


6. Confronto L2 vs L3 2D – R120

Aspetto	L2 R120	L3 2D R120
Tipo di modello	Sezione efficace	FEM 2D
		
		
		



7. Interpretazione ingegneristica
L’estensione a R120 mostra che:

i meccanismi locali governano il collasso
l’aumento della durata di incendio accentua le differenze L2 vs L3
l’analisi L3 2D diventa indispensabile per R ≥ 120Possibili strategie progettuali:
aumento dello spessore
incremento del copriferro
protezione passiva aggiuntiva


8. Implicazioni per benchmark e relazione di calcolo
Questo caso studio consente di:

definire un benchmark automatico R120
riutilizzare la relazione di calcolo tipo senza modifiche strutturali
supportare decisioni progettuali su R elevate


9. Conclusioni

✅ R90: già non soddisfatta secondo L3 2D
❌ R120: non soddisfatta con margine ridotto
✅ L3 2D conferma la necessità di approccio prestazionale


10. Collegamenti

FIRE_CASE_STUDIO_2D_PARETE_R90.md
FIRE_BENCHMARK_2D_R90_AUTOMATICO.md
FIRE_RELAZIONE_CALCOLO_TIPO_L3_2D_PARETI.md
FIRE_L3_STEP4_3_ACCOPPIAMENTO_TERMO_MECCANICO_2D_CALDO.md
FIRE_GATE_RILASCIO_L3_FEM.md



Analisi meccanica:validata a freddo (STEP 4.2)
accoppiata a caldo (STEP 4.3)
Passo temporale: \\(\\Delta t = 5\\,s\\)

