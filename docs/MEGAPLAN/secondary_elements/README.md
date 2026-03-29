# 🏗️ SECONDARY_ELEMENTS — Elementi Secondari

Documentazione per gli elementi secondari secondo NTC 2018.

## Elementi Coperti

| Elemento | Norma | File | Status |
|----------|-------|------|--------|
| Tramezzi | NTC2018 Cap. 7.8.1 | SECONDARY_ELEMENTS_*.md | 🟨 |
| Impianti | NTC2018 Cap. 7.8.2 | SECONDARY_ELEMENTS_*.md | 🟨 |
| Facciate | NTC2018 Cap. 7.8.3 | Incluso | 🟨 |
| Balconate | NTC2018 Cap. 7.8.4 | Incluso | 🟨 |
| Parapetti | NTC2018 Cap. 7.8.5 | Incluso | 🟨 |

## Contenuto (6 file)

```
secondary_elements/
├── README.md (questo file)
├── SECONDARY_ELEMENTS_AUTOMATION.md (Automazione calcolo)
├── SECONDARY_ELEMENTS_MASTER.md (Entry point principale)
├── SPEC_SecondaryElementSpec.md (Specifica tecnica)
├── SPEC_RC_SLE_Cracking.md (Fessurazione SLE)
├── SPEC_RC_SLU_VRDc_NoStirrups.md (Taglio senza staffe)
└── CONFIG_NTC2018_SECONDARY_ELEMENTS_SPEC.md (Configurazione)
```

## Verifiche Implementate

### SLU (Stato Limite Ultimo)
- ✅ Flessione
- ✅ Taglio (senza staffe)
- 🟨 Torsione

### SLE (Stato Limite di Esercizio)
- ✅ Fessurazione (w_k)
- 🟨 Deformazioni
- 🟨 Vibrazioni

## Procedure

1. **Selezione elemento** → Scegliere tipo secondario
2. **Geometria** → Definire sezione e materiale
3. **Azioni** → Carichi da norma  (vedi Cap. 3.1.3)
4. **Verifiche** → Eseguire SLU/SLE
5. **Report** → Generare relazione di calcolo

## Relazione con Elementi Primari

- Elementi secondari hanno **vincoli statici specifici** (appoggio su elemento primario)
- Verifiche SLU **semplificate** rispetto elementi strutturali
- Azioni estratte da **tabella normativa** (NTC 2018, Cap. 7.8)

**Ultimo aggiornamento**: 2026-03-29
