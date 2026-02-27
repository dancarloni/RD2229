
VERIFICHE RD 2229/1939 – Tensioni Ammissibili
Status: FILE OPERATIVO – CORE DI VERIFICA (VINCOLANTE)
Questo documento definisce in modo formale e implementabile le verifiche strutturali secondo il R.D. 16/11/1939 n. 2229, da integrare nel motore di verifica già sviluppato.
Le verifiche RD2229:

sono a tensioni ammissibili;
sono deterministiche;
sono a freddo (assenza di sismica moderna);
non utilizzano concetti di SLU/SLE, capacità o fattori q.


1. Ambito normativo
Normativa di riferimento:

R.D. 2229/1939 – Norme per l’esecuzione delle opere in conglomerato cementizio semplice ed armato
Regolamenti applicativi storici e prassi consolidata
Campo di applicazione:

strutture in cemento armato;
verifiche di elementi singoli (travi, pilastri, solette);
analisi elastica lineare.


2. Principi fondamentali del metodo
Secondo il RD 2229:

le sollecitazioni sono calcolate elasticamente;
le verifiche avvengono confrontando le tensioni agenti con le tensioni ammissibili;
il materiale non è spinto a comportamento plastico;
non esiste gerarchia delle resistenze.
Formalmente:

σ_calcolo ≤ σ_ammissibile




3. Tipologie di verifiche previste
Per ciascun elemento strutturale devono essere eseguite le seguenti verifiche.
3.1 Pressoflessione semplice e composta
Verifica delle tensioni nel calcestruzzo e nell’acciaio dovute a:

sforzo normale N;
momenti flettenti Mx, My.
Criterio:

σ_c ≤ σ_c,amm
σ_s ≤ σ_s,amm




3.2 Flessione semplice (travi)
Verifica delle tensioni di flessione nel conglomerato e nelle armature longitudinali.
Criterio:

σ_max ≤ σ_amm




3.3 Taglio
Verifica delle tensioni tangenziali medie:

τ ≤ τ_amm


La presenza di armatura a taglio consente un incremento della tensione ammissibile secondo le regole storiche.


3.4 Compressione semplice (pilastri)
Verifica della tensione media di compressione:

σ = N / A ≤ σ_c,amm




3.5 Trazione semplice (eccezionale)
Ammessa solo se giustificata (tiranti, catene):

σ_s ≤ σ_s,amm




4. Tensioni ammissibili
Le tensioni ammissibili sono funzione di:

classe del calcestruzzo (storica);
tipo di acciaio;
coefficienti di sicurezza impliciti della normativa.
Nel software:

le tensioni ammissibili NON sono hardcoded;
sono recuperate dall’archivio materiali storico;
sono completamente parametriche.


5. Dati di input richiesti
Per ogni verifica RD2229 sono richiesti:

geometria completa della sezione;
proprietà meccaniche del materiale;
sollecitazioni elastiche:N
Mx, My
Tx (se presente)


6. Modello dati – Verifica RD2229

from dataclasses import dataclass
from ntc_capitolo import NTCCapitol

@dataclass
class VerificaRD2229:
    nome: str
    sigma_calcolo: float
    sigma_ammissibile: float
    esito: bool
    riferimento_normativo: str = "R.D. 2229/1939"
    capitolo_ntc: NTCCapitol = NTCCapitol.RD2229




7. Integrazione con VerificationEngine
Le verifiche RD2229:

sono istanze di VerificationResult;
vengono gestite dal VerificationEngine unico;
sono instradate tramite VerificationFactoryRD2229.
Nessuna modifica al motore centrale è necessaria.


8. Risultati e classificazione
Ogni verifica restituisce:

tensione calcolata;
tensione ammissibile;
rapporto σ/σ_amm;
esito:✅ OK
❌ NON OK
I risultati:

sono mostrati in RisultatiView;
confluiscono nella Relazione di Calcolo RD2229.


9. Esclusioni esplicite
Il metodo RD2229 non include:

verifiche sismiche;
stati limite;
progettazione in capacità;
fattori di comportamento;
ζE.
Qualsiasi tentativo di utilizzo improprio deve essere bloccato dalla GUI.


10. Stato finale
✅ Verifiche RD2229 formalizzate ✅ Coerenti con l’architettura multi‑normativa ✅ Integrabili nel core esistente ✅ Pronte per VERIFICATION_FACTORY_RD2229


Questo file è vincolante per l’implementazione delle verifiche strutturali secondo il R.D. 2229/1939.
