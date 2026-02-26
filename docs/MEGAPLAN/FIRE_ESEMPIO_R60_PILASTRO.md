
FIRE_ESEMPIO_R60_PILASTRO – Esempio completo di verifica
Status: STABILE
Ruolo: Caso studio di riferimento (benchmark) per verifiche di resistenza al fuoco


1. Scopo del documento
Questo documento fornisce un esempio completo e tracciabile di verifica di resistenza al fuoco per un pilastro in calcestruzzo armato, con classe richiesta R60.
Lo scopo è:

validare il CodeModule_INCENDIO
fornire un benchmark riproducibile
guidare Copilot nell’applicazione corretta di teoria e normativa


2. Dati generali del caso studio

Tipologia elemento: Pilastro in c.a.
Stato limite: INCENDIO
Classe di resistenza richiesta: R60
Norma di calcolo: EN 1991‑1‑2 + EN 1992‑1‑2
Metodo adottato: Livello 2 – Metodo della sezione efficace


3. Geometria e materiali (input sintetico)
Geometria

Sezione: rettangolare
Dimensioni nominali: da definire nel caso reale
Esposizione al fuoco: 4 lati
Materiali

Calcestruzzo: classe da definire
Acciaio: B450C (o equivalente EC)
Copriferro nominale: dato di input
⚠️ Tutti i valori numerici sono parametrici e non hardcoded.


4. Input incendio (schema conforme a PLAN_INPUT_COMUNE)

fire_required = true
fire_class_required = R60
fire_time_target = 60 min
fire_curve = ISO_834
fire_exposure_sides = 4
fire_method = L2
fire_protection_type = none




5. Costruzione delle azioni in incendio

Combinazioni di carico ottenute applicando i coefficienti \\(\\eta_{fi}\\) e \\(\\psi_{fi}\\)
Riduzione delle azioni variabili secondo EN 1991‑1‑2
Risultato:

azione di progetto in incendio \\(E_{d,fi}\\)


6. Metodo di calcolo adottato (Livello 2)
Passaggi logici

Determinazione del profilo termico nella sezione a t = 60 min
Individuazione della profondità danneggiata
Costruzione della sezione efficace ridotta
Applicazione delle proprietà meccaniche degradate:\\(f_{c,\	heta}\\)
\\(f_{y,\	heta}\\)
Verifica di equilibrio della sezione ridotta


7. Verifica di resistenza
Condizione di sicurezza:
\\[ E_{d,fi} \\le R_{d,fi,60} \\]
Esito del caso studio:

tempo di collasso stimato ≥ 60 min
classe R60 soddisfatta


8. Output atteso (VerificationResultItem)
Estratto concettuale:

check_id = FIRE_PILASTRO_R60
stato_limite = INCENDIO
fire_class_required = R60
fire_time_achieved ≥ 60
fire_method = L2
norma = EN 1991-1-2 / EN 1992-1-2
esito = OK
warning_note = none




9. Limiti di validità del caso studio

comportamento regolare della sezione
assenza di spalling esplosivo
effetti del II ordine trascurabili
In caso contrario il risultato deve essere marcato NOT_APPLICABLE.


10. Ruolo del documento nel progetto
Questo file deve essere usato come:

test di benchmark automatico
riferimento per debug del solver incendio
guida per Copilot nell’uso corretto dei moduli incendio


11. Collegamenti

FIRE_CODEMODULE_INCENDIO.md
FIRE_TEORIA_CALCOLO.md
FIRE_NORMATIVA_EC.md
FIRE_INTEGRAZIONE_SOFTWARE.md
