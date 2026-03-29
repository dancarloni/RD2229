# 📚 NORMS — Knowledge Base Normative

Archivio della knowledge base relativa a tutte le normative strutturali coperte dal software RD2229.

## Norme Coperte

| Norma | Periodo | File | Status |
|-------|---------|------|--------|
| **RD 2229/1939** | 1939 | KB_RD2229_1939.md | ✅ |
| **DM 14/02/1992** | 1992 | KB_DM_1992_TA.md | ✅ |
| **DM 09/01/1996** | 1996 | KB_DM_1996_TA.md | ✅ |
| **NTC 2008** | 2008 | Vedi norms/ | 🟨 |
| **NTC 2018 + C.7/2019** | 2018 | KB_NTC2018*.md | 🟨 |

## Struttura

```
norms/
├── README.md (questo file)
├── KB_RD2229_1939.md (Regio Decreto storico)
├── KB_DM_1992_TA.md (Decreto 1992)
├── KB_DM_1996_TA.md (Decreto 1996)
├── KB_NTC2018.md (Circolare 252/2019)
├── KB_NTC2018_ANALISI.md (Analisi delle azioni)
├── KB_NTC2018_AZIONI.md (Combinazioni di carico)
├── KB_NTC2018_CA.md (Calcestruzzo armato)
├── KB_NTC2018_ESISTENTI.md (Edifici esistenti)
├── KB_NTC2018_SISMICA.md (Analisi sismica)
└── VERIFICHE_RD2229.md (Verifiche storiche)
```

## Capitoli Principali

### RD 2229/1939
- Calcestruzzo semplice e armato
- Tensioni ammissibili (TA)
- Acciaio ordinario

### DM 1992/1996
- Evoluzioni da RD2229
- Coefficienti di sicurezza parziali
- Combinazioni di carico

### NTC 2018
- **Cap. 2**: Requisiti di sicurezza
- **Cap. 4**: Azioni
- **Cap. 7**: Criteri di verifica SLU/SLE
- **Cap. 11**: Analisi sismica
- **Cap. 12**: Edifici esistenti

## Uso

Referenziare i file KB_* da:
- `src/methods/<norma>/checks.py` (per formule normative)
- `docs/implementation/_theory/` (per derivazioni dettagliate)
- Test suite (per validazione vs norma)

**Ultimo aggiornamento**: 2026-03-29
