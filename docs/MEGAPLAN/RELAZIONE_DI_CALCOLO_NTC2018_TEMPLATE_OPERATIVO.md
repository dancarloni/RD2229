
RELAZIONE DI CALCOLO – NTC 2018 (Template Operativo)
Status: DOCUMENTO OPERATIVO – GENERAZIONE AUTOMATICA DA SOFTWARE
Questo file definisce la relazione di calcolo standard generata dal software, coerente e vincolante con tutti gli STEP di implementazione NTC2018 completati (CAP_4 e CAP_7).
La relazione è norma‑driven, tracciabile, difendibile e ricostruibile: ogni valore deriva da oggetti software (LoadCombination, VerificationResult, ZetaECalculator, GerarchiaResistenzeVerifier).


0. Riferimenti normativi e documentali

D.M. 17/01/2018 – Norme Tecniche per le Costruzioni (NTC2018)
Circolare 21/01/2019 n. 7
KB_NTC2018.md
KB_NTC2018_AZIONI.md
KB_NTC2018_ANALISI.md
KB_NTC2018_CA.md
KB_NTC2018_SISMICA.md
KB_NTC2018_ESISTENTI.md
IMPLEMENTAZIONE_NTC2018_STEP1_CORE.md
IMPLEMENTAZIONE_NTC2018_STEP2_SLE_CA_CAP4.md
IMPLEMENTAZIONE_NTC2018_STEP3_MOTORE_COMBINAZIONI.md
IMPLEMENTAZIONE_NTC2018_STEP4_ZETA_E_ESISTENTI_CAP7.md
IMPLEMENTAZIONE_NTC2018_STEP5_GERARCHIA_E_CAPACITÀ_CAP7.md


1. Dati generali dell’opera

Oggetto: ____
Ubicazione: _
Committente: ___
Progettista: ___
Normativa di riferimento: NTC2018
Tipologia: ☐ Nuova costruzione ☐ Edificio esistente


2. Inquadramento normativo
La presente relazione è redatta ai sensi delle NTC2018 e distingue esplicitamente:

CAPITOLO 4 – verifiche statiche (SLU / SLE)
CAPITOLO 7 – verifiche sismiche (capacità, gerarchia)
CAPITOLO 8 – costruzioni esistenti (ζE, LC, FC)
È vietata qualsiasi commistione tra CAP_4 e CAP_7 non dichiarata.


3. Modello strutturale e analisi
3.1 Schema strutturale

Tipologia: telaio / setti / misto
Materiali: c.a. / acciaio / altro
Ipotesi di vincolo e continuità
3.2 Metodo di analisi

☐ Analisi lineare elastica
☐ Analisi modale
☐ Analisi non lineare (se applicabile)
Riferimento: KB_NTC2018_ANALISI.md


4. Azioni e combinazioni di carico
Le azioni e le combinazioni sono generate dal Motore Combinazioni NTC2018.
4.1 Azioni elementari

Azione	Tipo	Valore
G1	Permanente strutturale	
G2	Permanente non strutturale	
Q	Variabile	
E	Sismica	

4.2 Combinazioni utilizzate
Per ciascuna combinazione:

Nome
Stato limite
Capitolo NTC
Riferimento normativo
(derivato da LoadCombination)


5. Verifiche – CAPITOLO 4 (SLU / SLE)
5.1 Verifiche SLU – c.a.
Per ciascun elemento:

Sollecitazione di progetto (Ed)
Resistenza di progetto (Rd)
Rapporto Ed/Rd
Esito
(derivato da VerificationResult con capitolo_ntc = CAP_4)
5.2 Verifiche SLE – c.a.

Limitazione delle tensioni
Controllo della fessurazione
Verifica delle deformazioni
Riferimento: NTC2018 §4.1.4


6. Verifiche sismiche – CAPITOLO 7
6.1 Parametri sismici

Zona sismica
Categoria di sottosuolo
Classe d’uso
Spettro di progetto
Riferimento: KB_NTC2018_SISMICA.md
6.2 Gerarchia delle resistenze

Elementi dissipativi
Elementi non dissipativi
Verifica di sovraresistenza
Esito: ☐ OK ☐ NON OK
(derivato da GerarchiaResistenzeVerifier)
6.3 Capacità sismica Rd

Metodo di determinazione
Valore Rd


7. Edifici esistenti – CAPITOLO 8
7.1 Livello di conoscenza

☐ LC1 ☐ LC2 ☐ LC3
Fattore di confidenza FC = ___
7.2 Indice di sicurezza ζE

Domanda sismica Ed = ___
Capacità sismica Rd = ___
FC = ___
ζE = Rd / (Ed · FC) = ____
Classificazione:

☐ Intervento locale
☐ Miglioramento sismico
☐ Adeguamento sismico
(derivato da ZetaECalculator)


8. Esiti finali

Ambito	Capitolo	Esito
Statico SLU	CAP_4	☐ OK ☐ NO
Statico SLE	CAP_4	☐ OK ☐ NO
Sismico	CAP_7	☐ OK ☐ NO
ζE	CAP_8	☐ OK ☐ NO



9. Dichiarazioni
La presente relazione è coerente con le NTC2018, è integralmente ricostruibile dai dati di calcolo e difendibile in sede tecnica e legale.


10. Allegati

Output di calcolo
Tabulati verifiche
Diagrammi sollecitazioni
Report automatici del software


Questo template è vincolante per la generazione della relazione di calcolo NTC2018 dal software.
