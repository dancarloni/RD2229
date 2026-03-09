# Fase I — Sezioni parametri statici completi

## Subfasi, checklist e storico

### I.1 Rapporto di omogeneizzazione n per norma

**Stato**: COMPLETATO — commit 3bed1a7

- [x] n per RD2229, DM92, DM96, NTC2008, NTC2018, EC2
- [x] Opzioni selezionabili, default e override utente
- [x] Test: test_sezione_omogenizzata.py (91 test)

### I.2 Sezione omogeneizzata integra + fessurata

**Stato**: COMPLETATO

- [x] calcola_sezione_omogenizzata(), calcola_asse_neutro_fessurato()
- [x] Tutti i tipi di sezione

### I.3 Parametri torsionali

**Stato**: COMPLETATO

- [x] J_t, C_w, x_s, y_s implementati
- [x] Test: test_section_torsion.py (27 test)

### I.4 Sezione composta acciaio-cls

**Stato**: COMPLETATO

- [x] IPE_TABLE, calcola_sezione_composta(), calcola_tensioni_sle_composita()

### I.5 Disegno sezione c.a

**Stato**: COMPLETATO

- [x] disegna_sezione(), crea_figura_sezione_sle(), salva_figura()
- [x] Widget Qt: sezione_canvas.py

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase I sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
