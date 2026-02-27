
FIRE_CASE_STUDIO_L2_VS_L3_PILASTRO_R90 – Caso studio comparativo
Status: STABILE
Ruolo: Caso studio operativo di confronto tra verifica L2 e analisi L3 FEM


1. Scopo del caso studio
Questo documento presenta un caso studio completo di confronto L2 vs L3 per la resistenza al fuoco di un pilastro in calcestruzzo armato, con classe richiesta R90.
Il caso studio ha lo scopo di:

mostrare come applicare correttamente L2 e L3 sullo stesso elemento
evidenziare differenze di risultato e di interpretazione
fornire un riferimento pratico per l’uso consapevole dell’analisi L3
⚠️ Il caso studio è didattico‑operativo e non sostituisce una relazione di progetto.


2. Descrizione dell’elemento strutturale

Tipologia: Pilastro in c.a.
Stato limite: INCENDIO
Classe di resistenza richiesta: R90
Schema statico: pilastro isolato, carico centrato
Normativa di riferimento:EN 1991‑1‑2
EN 1992‑1‑2


3. Dati geometrici e meccanici (input comune)
3.1 Geometria

Sezione: rettangolare
Dimensioni: b × h = 30 × 40 cm
Copriferro nominale: 3.0 cm
Lati esposti al fuoco: 4
3.2 Materiali

Calcestruzzo: C25/30
Acciaio di armatura: B450C
Armatura longitudinale: simmetrica
3.3 Azioni

Sforzo normale di progetto in incendio: \\(N_{Ed,fi}\\)
Combinazione in incendio conforme a EN 1991‑1‑2


4. Verifica con metodo L2 – Sezione efficace
4.1 Impostazione del metodo
Il metodo L2 applica:

riduzione della sezione resistente
degradazione delle proprietà dei materiali
verifica a presso‑flessione su sezione ridotta
Il calcolo segue lo schema di:
\\[ N_{Ed,fi} \\le N_{Rd,fi,90} \\]


4.2 Risultati L2

Profondità di sezione danneggiata: determinata da curve termiche semplificate
Sezione efficace residua: ridotta ma non nulla
Capacità resistente a 90 min: sufficiente
Esito L2: ✅ OK (R90 soddisfatta)


4.3 Commento tecnico su L2

Metodo rapido e normativamente consolidato
Approccio conservativo
Non considera:evoluzione temporale continua
instabilità numerica
redistribuzioni interne


5. Analisi con metodo L3 – FEM beam‑fiber
5.1 Motivazione dell’uso di L3
L’analisi L3 è eseguita per:

verificare l’effettivo tempo di collasso
valutare l’influenza della non linearità dei materiali
analizzare la sensibilità al II ordine


5.2 Modello L3 adottato

Modello: beam‑fiber 1D
Analisi termica: ISO 834 (STEP 1)
Analisi meccanica: non lineare (STEP 2)
Accoppiamento completo: STEP 3
Passo temporale: \\(\\Delta t = 5\\,s\\)


5.3 Risultati L3

Evoluzione progressiva della capacità resistente
Riduzione significativa oltre ~75 min
Collasso numerico/meccanico a:
\\[ t_{coll,L3} \\approx 82\\,\	ext{min} \\]
Esito L3: ❌ NOT_OK (R90 non pienamente soddisfatta)


6. Confronto diretto L2 vs L3

Aspetto	L2	L3
Tipo di analisi	Sezione efficace	FEM beam‑fiber
		
		
		
		



7. Interpretazione ingegneristica
Il confronto evidenzia che:

L2 risulta conservativo in molti casi, ma
per R90 con snellezza e copriferro ridotto può sovrastimare la resistenza
⚠️ Il risultato L3 non invalida L2, ma:

segnala una condizione limite
suggerisce attenzione progettuale
giustifica eventuali misure correttive (aumento sezione, protezione passiva)


8. Uso corretto dei risultati L3
Secondo la filosofia del modulo incendio:

L3 non sostituisce automaticamente L2
L3 è uno strumento di:verifica avanzata
comprensione dei margini
supporto decisionale
Il risultato deve essere:

accompagnato da checklist
filtrato dal Gate di rilascio L3


9. Conclusioni del caso studio

✅ L2: conforme e normativamente valido
⚠️ L3: evidenzia possibile insufficienza a R90
✅ Confronto L2/L3 eseguito correttamente e in modo difendibile
Questo caso studio mostra perché e quando l’analisi L3 è utile.


10. Collegamenti

FIRE_L3_ANALISI_COMPLETE_E_CONFRONTO_L2_L3.md
FIRE_L3_STEP1_ANALISI_TERMICA.md
FIRE_L3_STEP2_ANALISI_MECCANICA.md
FIRE_L3_STEP3_ACCOPPIAMENTO_TERMO_MECCANICO.md
FIRE_CHECKLIST_VALIDAZIONE_L3_FEM.md
FIRE_GATE_RILASCIO_L3_FEM.md
