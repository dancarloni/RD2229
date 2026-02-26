
FIRE_CHECKLIST_TECNICO_LEGALE – Verifiche di resistenza al fuoco
Status: STABILE
Ruolo: Checklist tecnico‑legale e di validazione per verifiche incendio


1. Scopo del documento
Questa checklist definisce tutti i controlli minimi obbligatori affinché una verifica di resistenza al fuoco:

sia corretta dal punto di vista normativo
sia difendibile dal punto di vista tecnico‑legale
sia riproducibile e verificabile nel tempo
La checklist è applicabile a:

calcoli manuali
software di calcolo
relazioni tecniche
contenziosi e verifiche peritali


2. Checklist normativa (obbligatoria)
2.1 Inquadramento normativo

☐ Incendio qualificato come azione eccezionale
☐ Riferimento esplicito a NTC 2018 (o norma vigente)
☐ Riferimento a DM / Codice di Prevenzione Incendi applicabile
☐ Esplicitazione del campo di applicazione (nuovo / esistente)


2.2 Prestazioni richieste

☐ Classe di resistenza al fuoco richiesta (R30 / R60 / R90 / …)
☐ Motivazione della classe R (destinazione d’uso, livello di prestazione)
☐ Esplicitazione di eventuali deroghe o soluzioni alternative


2.3 Modelli normativi di calcolo

☐ Richiamo a EN 1991‑1‑2 (azioni in incendio)
☐ Richiamo a EN 1992‑1‑2 (resistenza di sezione)
☐ Versione normativa esplicitamente indicata


3. Checklist tecnica di input
3.1 Dati geometrici

☐ Geometria della sezione chiaramente definita
☐ Numero di lati esposti al fuoco dichiarato
☐ Copriferro nominale indicato


3.2 Dati dei materiali

☐ Classe del calcestruzzo dichiarata
☐ Tipo di acciaio di armatura dichiarato
☐ Proprietà a caldo derivate da norma (non stimate)


3.3 Dati incendio

☐ Curva di incendio adottata (ISO 834 / parametrica)
☐ Tempo di esposizione richiesto
☐ Eventuali protezioni passive dichiarate


4. Checklist del metodo di calcolo

☐ Metodo dichiarato (L1 / L2 / L3)
☐ Metodo ammesso per il caso specifico
☐ Ipotesi di calcolo esplicitate
☐ Limiti di validità dichiarati


5. Checklist di verifica strutturale

☐ Azioni di progetto in incendio correttamente ridotte
☐ Verifica esplicita della condizione:
\\[ E_{d,fi} \\le R_{d,fi,t} \\]

☐ Tempo di collasso stimato o verificato


6. Checklist di output e risultati

☐ Esito chiaro (OK / NOT_OK / NOT_APPLICABLE)
☐ Classe R richiesta vs classe R raggiunta
☐ Metodo e norma sempre riportati
☐ Avvertenze tecniche evidenziate


7. Checklist di tracciabilità e riproducibilità

☐ Input completamente riportati o allegati
☐ Versione del software o metodo indicata
☐ Parametri normativi non hardcoded
☐ Risultato riproducibile a parità di input


8. Checklist software (se applicabile)

☐ Separazione netta input / calcolo / output
☐ Nessuna logica normativa nella GUI
☐ Output conforme a VerificationResultItem9. Red flags (attenzione)
La verifica non è difendibile se:

⛔ Classe R non motivata
⛔ Metodo non dichiarato
⛔ Curve materiali non normative
⛔ Risultato senza limiti di validità
⛔ Parametri impliciti o nascosti


10. Uso della checklist
Questa checklist deve essere:

allegata alla relazione incendio
utilizzata come controllo finale
applicata in fase di validazione software


11. Collegamenti

FIRE_MASTER.md
FIRE_NORMATIVA_NTC.md
FIRE_NORMATIVA_EC.md
FIRE_TEORIA_CALCOLO.md
FIRE_CODEMODULE_INCENDIO.md
FIRE_ESEMPIO_R60_PILASTRO.md



☐ Log del calcolo disponibile
