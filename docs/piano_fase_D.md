# Fase D — Cordoli Metallici

## Subfasi, checklist e storico

### D.1 Sagomario EN 10365

**Stato**: COMPLETATO — commit corrente

- [x] Database profili IPE (18), HEA (19), HEB (19), HEM (19), UPN (12) in JSON — 87 profili totali
- [ ] Import CSV custom utente
- [x] Ricerca e filtro profili (per famiglia, Wx minimo, altezza, profilo ottimale)
- [x] Test: tests/test_sagomario_acciaio.py (32 test)

### D.2 Verifiche profilo singolo

**Stato**: COMPLETATO — commit corrente

- [x] Flessione (σ = M/W ≤ σ_adm)
- [x] Taglio (τ = V/A_anima ≤ τ_adm)
- [x] Instabilità (ω·N/A, tabella CNR 10011)
- [x] Pressoflessione (N + Mx + My)
- [x] Combinata Von Mises (σ_VM = √(σ² + 3τ²))
- [x] Selezione profilo ottimale per momento
- [x] Test: tests/test_verifiche_acciaio_ta.py (33 test)

### D.3 Traliccio reticolare piano — cordolo metallico reticolare

**Stato**: COMPLETATO — commit 23f3300

- [x] SezioneAsta, piatti, angolari, verifica_aste_traliccio()
- [x] Generatore schemi traliccio (Howe, Pratt)
- [x] Adattamento solutore traliccio_2d
- [x] Modulo cordolo reticolare
- [x] Verifiche aste del traliccio
- [x] Integrazione con cinematica.py
- [x] Nodo d'angolo (cantonali)
- [x] Report e tabulato
- [x] Test: test_sezione_asta.py, test_traliccio_generatore.py, test_cordolo_reticolare.py

### D.4 Solutore traliccio 2D

**Stato**: COMPLETATO — commit corrente

- [x] Metodo della rigidezza diretta (Gauss con pivoting parziale)
- [x] Input nodi + aste + vincoli (cerniera, carrello_x, carrello_y) + carichi
- [x] Sforzi normali nelle aste (trazione/compressione)
- [x] Reazioni vincolari con verifica equilibrio globale
- [x] Verifiche a compressione/trazione con instabilità (ω)
- [x] Test: tests/test_traliccio_2d.py (19 test)

### D.5 Connessioni

**Stato**: COMPLETATO — commit corrente

- [x] Saldature a cordone d'angolo (frontale, laterale, combinata)
- [x] Saldature testa a testa (completa penetrazione)
- [x] Bullonature: taglio (gambo/filetto), trazione, interazione, rifollamento
- [x] Coefficienti β_w (CNR 10011), classi 4.6÷10.9, M12÷M36
- [x] Test: tests/test_connessioni_acciaio.py (24 test)

### D.6 Modello cordolo (CA + metallico)

**Stato**: COMPLETATO — commit corrente

- [x] Cordolo CA: sezione, armatura, minimi NTC2018 §7.8.1.6
- [x] Cordolo metallico: profilo singolo, flessione/taglio TA
- [x] Verifica flessione e taglio per entrambi i tipi
- [x] Posizione: sommitale, intermedio, fondazione

### D.7 GUI Qt cordoli

- [ ] Interfaccia selezione profilo
- [ ] Visualizzazione sezione
- [ ] Input sollecitazioni
- [ ] Output verifiche

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase D sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
