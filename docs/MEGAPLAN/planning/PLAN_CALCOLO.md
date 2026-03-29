
PLAN – CODICE DI CALCOLO
Status: STABILE Ambito: Architettura del calcolo Vincolo: Nessun codice operativo
Scopo
Definire cosa viene calcolato, con quale norma, con quali limiti di validità, garantendo modularità, tracciabilità normativa e retro‑compatibilità.
Interfaccia normativa

Ogni norma è esposta tramite CodeModule.
Il motore di verifica è norma‑agnostico.
Norme supportate

NTC2018 (core)
RD2229/39, DM92, DM96 (legacy tramite adapter/shim)
Eurocodici (EC2/EC3/EC8): solo fallback documentato
Moduli NTC2018 (priorità)

Calcestruzzo armato: SLU/SLE
Taglio con e senza armatura trasversale (V_Rd,c)
Sismica globale
Elementi secondari / non strutturali (§7.2)
Regole progettuali

Priorità normativa: NTC → EC → NOT_APPLICABLE
Ogni check restituisce: esito, utilisation, campo di validità, riferimenti normativi
Nessuna formula in GUI
Deliverable

Elenco check per norma
Mappa NTC → EC (fallback)
Criteri di esclusione/applicabilità
