# Verification Table — Scorciatoie di tastiera e comportamento di inserimento

Questo documento descrive il comportamento di navigazione e inserimento dati nella `Verification Table` (implementata con `ttk.Treeview`) e spiega le convenzioni usate.

⚠️ Nota: le seguenti descrizioni assumono che l'utente stia utilizzando l'editor cella (Entry) che viene posizionato sopra la cella attiva.

## Comportamenti principali

- TAB
  - Se non sei nell'ultima colonna: salva il valore corrente e sposta il cursore alla colonna successiva nella stessa riga.
  - Se sei nell'ultima colonna della riga:
    - se esiste una riga successiva → il cursore va alla prima colonna della riga successiva;
    - se la riga successiva non esiste → viene creata automaticamente una nuova riga copiando **tutti** i valori della riga corrente e il cursore va alla prima colonna della nuova riga.

- SHIFT+TAB
  - Comporta il comportamento inverso: applica eventuali suggerimenti attivi, salva il valore e sposta alla colonna precedente; se si trova nella prima colonna, si sposta all'ultima colonna della riga precedente (o rimane sulla riga corrente se non esiste precedente).

- INVIO (Return)
  - Per impostazione predefinita sposta il cursore **di riga** mantenendo la stessa colonna (comodo per inserire valori colonna per colonna). Se non esiste la riga successiva, viene creata una nuova riga copiando la corrente.

- FRECCIA GIÙ
  - Salva il valore corrente e sposta il cursore alla stessa colonna della riga successiva. Se la riga successiva non esiste, viene creata copiando la corrente.

- HOME / END (quando il Treeview ha il focus)
  - `Home`: apre l'editor sulla prima colonna della riga corrente.
  - `End`: apre l'editor sull'ultima colonna della riga corrente.

## Copia automatica di riga

- Quando viene creata una nuova riga automaticamente (TAB dalla ultima colonna, INVIO oltre l'ultima riga, o freccia giù oltre l'ultima riga), la nuova riga viene popolata copiando i valori di tutte le colonne dalla riga precedente.
- Questo permette inserimenti rapidi: modifica solo i campi che cambiano e TAB/INVIO per creare e proseguire.

## Suggerimenti (autocomplete)

- Alcune colonne (es. materiali, sezioni) dispongono di suggerimenti testuali.
- Quando i suggerimenti sono visibili e l'utente preme `Enter` nella listbox, il suggerimento selezionato viene applicato e l'edit viene committato.
- Quando si preme `Tab` o `Shift+Tab` con suggerimenti aperti, il sistema applica automaticamente il suggerimento corrente e poi esegue la navigazione (commit + spostamento).

## Note per sviluppatori

- La funzione che crea una riga copiando la precedente è `VerificationTableApp.add_row_from_previous(previous_item_id)`.
- Lo stato corrente della cella è tracciato in `current_item_id` e `current_column_index`.
- La logica di avanzamento centralizzata è in `_commit_and_move(delta_col, delta_row)` — qui avviene la creazione della nuova riga quando necessario.

---

## Esempi rapidi di utilizzo (snippet)

Di seguito alcuni snippet pratici da usare in codice per sfruttare le nuove API della Verification Table.

- Creare una nuova riga copiando la riga selezionata (programmatico):

```python
# supponendo `app` sia istanza di VerificationTableApp e che ci sia almeno una riga
selected = app.tree.focus()  # item_id della riga corrente
if not selected:
    selected = list(app.tree.get_children())[0]
new_item = app.add_row_from_previous(selected)
# ora `new_item` è l'item_id della nuova riga copiata
```

- Avviare l'editing programmaticamente su una cella specifica:

```python
# apre l'editor sulla colonna 'N' della prima riga
first = list(app.tree.get_children())[0]
app._start_edit(first, 'N')
```

- Usare `add_row_from_previous` in un flusso personalizzato (es. import parziale):

```python
# integrazione: dopo aver importato una riga, creare la successiva pre-popolata
last = list(app.tree.get_children())[-1]
app.add_row_from_previous(last)
```

- Sostituire `Entry` con una `ttk.Combobox` per colonne con valori fissi (es. materiali):

```python
# esempio concettuale: durante _start_edit, per colonne specifiche creare Combobox
if col in {'mat_concrete', 'mat_steel', 'stirrups_mat'}:
    cb = ttk.Combobox(self.tree, values=self.material_names)
    cb.place(x=x, y=y, width=width, height=height)
    cb.set(value)
    cb.focus_set()
    # bind degli stessi eventi di navigazione su cb come su Entry
```

> Nota: i metodi usati internamente come `_start_edit` e `_commit_and_move` sono progettati per essere riusati; se preferisci, posso estrarre una piccola API pubblica attorno a questi comportamenti.

Se vuoi, procedo con:
1. estrarre helper pubblici per usare `Combobox` senza duplicazione di codice, oppure
2. aggiungere esempi più dettagliati nei test (ad es. test che verificano che Combobox sia usata e che i valori vengano commitati), oppure
3. aprire una PR con tutte le modifiche e la documentazione aggiornata.

Dimmi quale opzione preferisci (rispondi: “1”, “2” o “3”).