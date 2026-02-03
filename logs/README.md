# Sistema di Logging per GUI Materials Manager

## Descrizione
Il sistema di logging registra tutte le operazioni eseguite tramite la GUI per la gestione dei materiali. I log vengono salvati in `logs/gui_operations.log` con timestamp, livello e messaggio.

## Operazioni loggate
- **Avvio/Chiusura applicazione**: Registra quando la GUI viene aperta e chiusa.
- **Aggiunta materiale**: Nome del materiale aggiunto.
- **Modifica materiale**: Nome originale e nuovo nome (se rinominato).
- **Cancellazione materiale**: Nome del materiale cancellato.
- **Aggiornamento lista**: Numero di materiali trovati.
- **Applicazione filtri**: Quando vengono applicati filtri.
- **Pulizia filtri**: Quando vengono rimossi i filtri.
- **Ordinamento**: Colonna per cui è stato ordinato.
- **Visualizzazione dettagli**: Nome del materiale selezionato.
- **Errori**: Eccezioni durante le operazioni.

## Formato log
```
YYYY-MM-DD HH:MM:SS - LEVEL - Messaggio
```

Esempi:
- `2023-10-01 12:00:00 - INFO - Avvio applicazione GUI Materials Manager`
- `2023-10-01 12:01:00 - INFO - Materiale aggiunto: Calcestruzzo120`
- `2023-10-01 12:02:00 - ERROR - Errore nell'aggiunta del materiale Calcestruzzo120: Materiale già esistente`

## Utilizzo
I log possono essere utilizzati per:
- Tracciare le modifiche ai materiali.
- Debuggare problemi nell'applicazione.
- Audit delle operazioni utente.

Il file di log viene creato automaticamente nella directory `logs/` alla prima esecuzione.