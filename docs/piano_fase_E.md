# Fase E — Muratura Verifiche Locali

## Subfasi, checklist e storico

### E.1 Compressione + snellezza

**Stato**: COMPLETATO — commit corrente

- [x] σ ≤ f_d / γ_M con riduzione snellezza Φ
- [x] Tabella Φ da NTC2018 Tab 4.5.V (interpolazione bilineare λ×e/t)
- [x] Eccentricità e/t da momento flettente
- [x] Fattore vincolo ρ per altezza efficace

### E.2 Taglio nel piano

**Stato**: COMPLETATO — commit corrente

- [x] Criterio diagonale (Turnšek-Čačovič) — NTC2018 §7.8.2.2.1
- [x] Criterio di scorrimento (Mohr-Coulomb: fvk = fvk0 + μ·σ_n)
- [x] Pressoflessione nel piano — V_pf = (L²×t×σ₀)/(2h₀)×(1-σ₀/(0.85fd))
- [x] Verifica combinata con ordinamento per V_Rd (criterio più restrittivo)

### E.3 Fuori piano + ribaltamento (meccanismi locali)

**Stato**: COMPLETATO — commit corrente

- [x] Ribaltamento semplice (parete ruota alla base)
- [x] Ribaltamento composto (parete + cuneo sovrastante)
- [x] Flessione verticale (cerniera a metà altezza, meccanismo a 2 corpi)
- [x] Flessione orizzontale (arco a 3 cerniere tra vincoli laterali)
- [x] Cinematica lineare (§C8A.4.1): α₀, M*, e*, a₀*, verifica a terra e in quota
- [x] Cinematica non lineare (§C8A.4.2): d₀*, d*_u = 0.4·d₀*, T_s, domanda spostamento
- [x] Integrazione catene/tiranti (ForzaCatena con angolo, contributo stabilizzante)
- [x] Analisi completa tutti i meccanismi ordinati per α₀ crescente
- [x] Parametri sismici manuali (a_g, S, q, FC) + predisposizione INGV

### E.4 Spanciamento

**Stato**: COMPLETATO — commit corrente

- [x] Verifica snellezza muro λ = h_eff/t ≤ λ_max
- [x] Limiti configurabili (20 ordinario, 15 esistente, 12 sismico)

### E.5 Catene e paletti

**Stato**: COMPLETATO — commit corrente

- [x] Tipi piastre (circolare, quadrata, a paletto)
- [x] Verifica trazione catena (σ = F/A ≤ σ_s_adm)
- [x] Verifica punzonamento locale piastra (σ_p ≤ fd_mur)

### E.6 Cantonali e aperture — meccanismo ribaltamento cantonale + riduzione resistenza

**Stato**: COMPLETATO
**Priorita**: ALTA (collegamento diretto con E.3 + D.3)
**Obiettivo**: Implementare (A) il meccanismo di ribaltamento del cantonale (cuneo 3D), (B) la riduzione di resistenza dei maschi d'angolo per aperture ravvicinate.

#### E.6.A — Ribaltamento del cantonale (meccanismo 3D)

- Concetto, modellazione, riferimenti, decisioni architetturali, sub-plan dettagliato (vedi storico PIANO_LAVORO.md)

#### E.6.1 — Ribaltamento cantonale (cuneo 3D)

- [x] Analisi fonti normative e letteratura
- [x] Definizione dataclass e input 3D
- [x] Inserimento warning automatici
- [x] Funzioni di calcolo carichi agenti
- [x] Calcolo cinematica ribaltamento 3D
- [x] Gestione tipologie copertura associata
- [x] Gestione contributo cordolo D.3
- [x] Output e serializzazione risultati
- [x] Test standalone
- [x] Documentazione decisioni architetturali
- [ ] Integrazione futura in analisi_tutti_meccanismi()

#### E.6.2 — Riduzione resistenza maschi d'angolo per aperture

- [x] Funzioni aggiuntive in cantonale.py
- [x] diagnostica_apertura_angolo(parete, aperture)
- [x] coefficiente_riduzione_angolo(distanza, t, d_min)
- [x] Dataclass separata per la Diagnostica Angolo
- [x] Integrazione futura/astratta con Modello Globale
- [x] Test standalone su soglie metriche

#### E.6.3 — Spinta puntoni copertura

- [x] Integrato in E.6.1 (InputSpinta, enum TipoCopertura)

#### E.6.4 — Integrazione con cordolo reticolare D.3

- [x] Integrato in E.6.1 (ritegno_cordolo_kg)

#### E.6.5 — Test

- [x] Effetto catena/tirante sul cantonale
- [x] Effetto ritegno cordolo D.3
- [x] Diagnostica apertura-angolo: OK, WARNING, FAIL
- [x] Coefficiente riduzione: asintotico
- [ ] Flag maschio cantonale: automatico e override (spostato a completamento modello globale Fase R)
- [ ] Integrazione in analisi_tutti_meccanismi (spostato a completamento modello globale Fase R)
- [x] Retrocompatibilita': cinematica.py test esistenti (49) invariati

#### E.6.6 — Report e tabulato

- [x] Sezione "Meccanismo cantonale" nel tabulato
- [x] Sezione "Diagnostica aperture d'angolo" con warning
- [x] Passaggi calcolo tracciabili

#### Dipendenze, abilitazioni, riferimenti normativi e letteratura

- Tabelle e riferimenti come da storico PIANO_LAVORO.md

### E.7 Muratura multipiano

**Stato**: COMPLETATO — commit corrente

#### E.7.1 Carichi verticali per aree di influenza

- [x] CaricoSolaio, CaricoMaschio, _area_influenza_maschio(), distribuisci_carichi_solaio(), calcola_N_multipiano()

#### E.7.2 Combinazioni personalizzabili

- [x] CombinazioneCarico, GestoreCombinazioni, 6 combinazioni default NTC2018 §2.5.3, calcola_N_tutte(), N_Ed_max()

#### E.7.3 Verifiche compressione multipiano

- [x] Eccentricita, calcola_eccentricita(), verifica_multipiano(), RigaVerificaMaschio, RigaVerificaPiano, TabellaVerificheMultipiano

---

## Storicizzazione domande/risposte e decisioni

Tutte le domande, risposte e decisioni relative alla Fase E sono riportate qui, con riferimenti a commit e date.

---

## Note storiche/archivio (appendice)

[Eventuali note storiche, archivio, discussioni precedenti.]
