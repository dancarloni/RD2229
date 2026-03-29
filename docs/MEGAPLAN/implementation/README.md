# ⚙️ IMPLEMENTATION — Step Implementativi

Documentazione dei passaggi implementativi dettagliati per il software RD2229.

## Contenuto (15 file)

```
implementation/
├── README.md (questo file)
├── IMPLEMENTAZIONE_*.md (6 file — workflow NTC2018)
├── INTEGRAZIONE_*.md (1 file — integrazione moduli)
├── STEP2*.md (2 file — step 2 integrazione)
├── END_STEP2*.md (2 file — conclusione step 2)
├── FASE2_*.md (1 file — baseline congelata)
├── CodeModule_CONTRACT.md (Contratto I/O moduli)
├── PROMPT_UNICO_POST_IMPLEMENTAZIONE_AUDIT.md (Audit)
└── MANIFEST_APPLICAZIONE.md (Manifest applicazione)
```

## Step Principali

| File | Descrizione | Status |
|------|-------------|--------|
| IMPLEMENTAZIONE_GUI_NTC2018_ARCHIVI_E_VERIFICHE | GUI archivi e verifiche | ✅ |
| IMPLEMENTAZIONE_GUI_NTC2018_WORKFLOW | Workflow UI | ✅ |
| IMPLEMENTAZIONE_NTC2018_STEP2_SLE_CA_CAP4 | SLE calcestruzzo | ✅ |
| IMPLEMENTAZIONE_NTC2018_STEP3_MOTORE_COMBINAZIONI | Motore combinazioni | ✅ |
| IMPLEMENTAZIONE_NTC2018_STEP4_ZETA_E_ESISTENTI_CAP7 | Edifici esistenti | 🟨 |
| IMPLEMENTAZIONE_NTC2018_STEP5_GERARCHIA_E_CAPACITÀ_CAP7 | Gerarchia e capacità | 🟨 |
| IMPLEMENTAZIONE_NTC2018_VERIFICHE_CAP4_CAP7 | Verifiche SLU/SLE | 🟨 |

## Architettura I/O Standard

Tutti i moduli devono conformarsi a:
```python
@dataclass
class CalcInput:
    """Input standardizzato per qualsiasi calcolo"""
    progetto: Project
    elemento: Element
    norma: str  # "DM96", "NTC2018", etc.
    combinazione: str  # "SLU", "SLE"
    materiali: dict

@dataclass
class CalcResult:
    """Output standardizzato"""
    verificato: bool
    rapporto_verifica: float  # ≤ 1 = OK
    passaggi_calcolo: list[str]
    to_dict() -> dict
```

Vedi **CodeModule_CONTRACT.md** per dettagli.

## Milestone Recenti

- ✅ Fase 2 baseline congelata (2026-03-26)
- ✅ Step 2 integrazione completato
- 🟨 Step 3-5 in sviluppo

**Ultimo aggiornamento**: 2026-03-29
