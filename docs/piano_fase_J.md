# Fase J — Pressoflessione deviata multinorma

## Subfasi, checklist e storico

### J.1 Refactoring BarraArmatura

**Stato**: COMPLETATO — commit 73482f0

- [x] Aggiunta coordinata x, retrocompatibilità

### J.2 Tipi e sezione omogenizzata biassiale

**Stato**: COMPLETATO

- [x] PressoflessSpec, PressoflessResult, DominioNMy
- [x] calcola_omogenizzata_biassiale(), crea_armatura_rettangolare()

### J.3 Verifica TA calcestruzzo

**Stato**: COMPLETATO

- [x] Sovrapposizione elastica, Bresler TA, alpha selezionabile
- [x] Norme: RD2229, DM92, DM96

### J.4 Verifica SLU (NTC2018/NTC2008/EC2)

**Stato**: COMPLETATO

- [x] Wrapper checks_ntc2018, conversione unità
- [x] Norme: NTC2018, NTC2008, EC2

### J.5 Dominio 3D N-Mx-My

**Stato**: COMPLETATO

- [x] calcola_dominio_3d(), disegna_dominio_3d(), disegna_dominio_2d_mxmy(), disegna_dominio_2d_nm()

### J.6 Instabilità biassiale

**Stato**: COMPLETATO

- [x] amplifica_momenti_biassiale(), riuso omega_ca()

### J.7 Dispatcher multinorma

**Stato**: COMPLETATO

- [x] calcola_pressoflessione_deviata(), routing TA/SLU, amplificazione integrata

### J.8 Widget Qt

**Stato**: COMPLETATO

- [x] dominio_canvas.py, 3 viste, slider interattivi

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase J sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
