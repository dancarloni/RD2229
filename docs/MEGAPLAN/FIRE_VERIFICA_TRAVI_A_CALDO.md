
FIRE_VERIFICA_TRAVI_A_CALDO – Verifica a caldo di travi in c.a.
Status: STABILE
Ruolo: Specifica tecnica e teorica per la verifica di travi in calcestruzzo armato in caso di incendio

1. Scopo del documento
Questo documento definisce l’estensione del modulo INCENDIO alla verifica a caldo delle travi in calcestruzzo armato, in coerenza con:

FIRE_NORMATIVA_EC.md
FIRE_TEORIA_CALCOLO.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_INTEGRAZIONE_SOFTWARE.md
PLAN_CALCOLO.md
L’estensione riguarda esclusivamente la resistenza di sezione delle travi in incendio (flessione e taglio a caldo), senza introdurre analisi globali di telaio.

1. Ambito di applicazione
La verifica a caldo delle travi è ammessa per:

travi in c.a. ordinario
comportamento prevalentemente flessionale
schemi statici semplici (appoggiata, continua)
Sono esclusi:

effetti di presso‑flessione (non tipici delle travi)
analisi globale di instabilità
comportamento fragile non modellabile

1. Azioni di progetto in incendio
Le azioni di progetto sono determinate come per gli altri elementi:
\\[ M_{Ed,fi} = \\eta_{fi} \\cdot M_{Ed} \\]
\\[ V_{Ed,fi} = \\eta_{fi} \\cdot V_{Ed} \\]
con \\(\\eta_{fi}\\) definito secondo EN 1991‑1‑2.

2. Metodo di verifica ammesso
4.1 Metodo L2 – Sezione efficace (principale)
Per le travi in incendio si adotta il Metodo L2, con:

sezione ridotta per effetto termico
proprietà meccaniche degradate dei materiali
Il metodo è valido per:

R30, R60, R90, R120

1. Verifica a flessione a caldo
5.1 Ipotesi di base

deformazioni piane restano piane
contributo del calcestruzzo teso trascurato
acciaio e calcestruzzo degradati con la temperatura

5.2 Resistenza a flessione
La resistenza a flessione a caldo è valutata come:
\\[ M_{Rd,fi,t} = f\\big( A_{s,eff},\\; f_{y,\ heta},\\; z_{eff} \\big) \\]
Dove:

\\(A_{s,eff}\\) = armatura efficace residua
\\(f_{y,\ heta}\\) = resistenza dell’acciaio a caldo
\\(z_{eff}\\) = braccio interno della sezione ridotta
La verifica è:
\\[ M_{Ed,fi} \\le M_{Rd,fi,t} \\]

1. Verifica a taglio a caldo (semplificata)
6.1 Ammissibilità
Secondo EN 1992‑1‑2:

per molte classi di resistenza al fuoco non è richiesta una verifica esplicita a taglio
se richiesta, si applica una verifica semplificata

6.2 Modello semplificato

riduzione della resistenza a trazione del calcestruzzo
riduzione della capacità delle staffe
Verifica:
\\[ V_{Ed,fi} \\le V_{Rd,fi} \\]
Se la verifica non è applicabile:

restituire NOT_APPLICABLE
warning esplicito

1. Output della verifica trave
Il VerificationResultItem deve includere:
element_type = TRAVE8. Test automatici da derivare

test_fire_r60_trave_okI test devono seguire lo schema di:
FIRE_TESTS_AUTOMATICI_R60.md

1. Limiti di validità
La verifica a caldo delle travi non è valida se:

la sezione efficace è nulla
il comportamento non è flessionale
sono richieste analisi globaliIn tali casi:
esito NOT_APPLICABLE

1. Collegamenti

FIRE_TEORIA_CALCOLO.md
FIRE_ESTENSIONE_R90_R120.md
FIRE_TESTS_AUTOMATICI_R60.md
FIRE_NEXT_STEPS_ROADMAP.md

test_fire_r60_trave_not_ok
estensione dei test a R90 / R120

stato_limite = INCENDIO
check_id = FIRE_TRAVE_*
fire_class_required
fire_time_achieved
esito (OK / NOT_OK / NOT_APPLICABLE)
fire_method = L2
warning_note (taglio, spalling, limiti)
