# Fase Q — Report relazione di calcolo professionale

## Subfasi dettagliate e checklist

- [ ] Q.1 — Definizione layout e template A4 (HTML/MD base, struttura sezioni, stili, placeholder immagini)
- [ ] Q.2 — Integrazione pipeline di calcolo (estrazione automatica risultati, materiali, riferimenti)
- [ ] Q.3 — Citazione automatica norma/articolo/paragrafo/tabella per ogni materiale e verifica
- [ ] Q.4 — Generazione sezioni obbligatorie (sommario, materiali, verifiche, allegati, grafici)
- [ ] Q.5 — Gestione immagini personalizzate (upload/incolla, posizionamento, esportazione)
- [ ] Q.6 — Esportazione multi-formato (HTML, MD, PDF, TXT/ASCII, docx)
- [ ] Q.7 — Confronto tra norme (attivabile su richiesta, con tabella comparativa risultati)
- [ ] Q.8 — Personalizzazione sezioni report (inclusione/esclusione sezioni, ordinamento)
- [ ] Q.9 — Test di generazione report su casi reali (copertura casi d’uso, validazione output)
- [ ] Q.10 — Documentazione e istruzioni utente (come generare, personalizzare, esportare il report)

## Vincoli e note operative

- Ogni sub-fase deve essere tracciata in questo file con domande, risposte e decisioni.
- Il layout deve essere ottimizzato per stampa A4 e compatibile con esportazione PDF/docx.
- Le citazioni normative devono essere puntuali e verificabili.
- L’integrazione con la pipeline di calcolo deve essere automatica e retrocompatibile.
- Le immagini devono poter essere incollate o caricate dall’utente e posizionate liberamente.
- Il confronto tra norme deve essere opzionale e attivabile dall’utente.
- Tutti i formati di output devono essere testati e validati.
- Ogni modifica o deroga va storicizzata.

## Dipendenze e integrazioni

- Dipende da: modulo report_builder.py, export.py, pipeline.py, materiali, verifiche, GUI (upload immagini), moduli di esportazione (HTML, MD, PDF, docx), tabelle normative.
- Deve integrarsi con: pipeline di calcolo, archivi materiali, moduli verifica, GUI, sistema di storicizzazione domande/risposte.
- Tutte le funzioni devono essere retrocompatibili con i report e i dati già generati.
- Il layout A4 deve essere testato sia su HTML che su MD; l’esportazione PDF/docx deve essere validata su almeno due casi reali.
- Immagini e allegati devono essere referenziabili sia nel report che nella storicizzazione delle attività (es: “immagine X caricata in Q.5, commit Y”).

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase Q sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
