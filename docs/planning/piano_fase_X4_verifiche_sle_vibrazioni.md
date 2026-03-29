# Fase X4 - Verifiche SLE e Vibrazioni

## Stato e metadati

| Campo | Valore |
| --- | --- |
| Stato | COMPLETATO |
| Commit | - |
| Data | 2026-03-15 |
| Dipendenza master | docs/piano_fase_X.md |
| Test pianificati | ~100 |
| Test implementati/validati | 37 (unit + benchmark) |
| Ambito | Freccia, tensioni/fessurazione SLE, frequenze e comfort |

---

## Scopo del modulo

Implementare verifiche in esercizio per solai con approccio tracciabile, output dettagliato in stile X3 e warning codificati.

---

## Dipendenze reali del repo

- src/codes/params/NTC2018.json
- src/core/registro_log.py
- src/core/combinations/ntc2018_combinations.py
- src/codes/ntc2018/code_module.py

---

## Fonti normative principali

- NTC2018 §4.1.2.2.4: criteri di deformabilita in esercizio
- NTC2018 §4.1.2.2.5: limiti tensionali SLE
- NTC2018 §C7.10.5: criteri di comfort vibrazionale
- NTC2018 §11.2.10.7: viscosita/effetti differiti
- EN 1992-1-1 §7.4.1: deformazioni
- EN 1992-1-1 §7.3.4: apertura fessure (Eq. 7.8)
- EN ISO 10137 §7.1, §C.2.1: frequenza e accelerazione per comfort

---

## Audit pre-implementazione (all-green)

Correzioni applicate rispetto al piano iniziale:

1. Corretto riferimento deformabilita: da NTC2018 §7.2.6 a NTC2018 §4.1.2.2.4.
2. Corretto mapping tensioni/fessurazione: tensioni -> §4.1.2.2.5, fessurazione -> §4.1.2.2.4.
3. Corretto modello accelerazione: `a_peak = F/(xi*m*L)`, `a_RMS = a_peak/sqrt(2)`.
4. Verificata coerenza dimensionale su formule freccia, tensioni e f1.

---

## Tabella sintetica verifiche, formule e riferimenti

| Verifica | Formula principale | Riferimento normativo | Fallback | Note |
| --- | --- | --- | --- | --- |
| Deformabilita (X4.1) | `q_l = q_s*i/10^4`; `f_ist = k*q_l*L^4/(E*I)`; `f_tot = f_ist*(1+phi)` | NTC2018 §4.1.2.2.4; EN 1992-1-1 §7.4.1; NTC2018 §11.2.10.7 | `f~L^2/(k*h)` (predim.) | Supporto multi-schema vincoli |
| Tensioni SLE (X4.2) | `x_n = nAs/b *[-1+sqrt(1+2bd/(nAs))]`; `I_fess`; `sigma_c = M*x_n/I_fess`; `sigma_s = n*M*(d-x_n)/I_fess` | NTC2018 §4.1.2.2.5; EN 1992-1-1 §7.1 | `sigma=M/W` | limiti rara/QP + acciaio |
| Fessurazione (X4.2) | `w_k = s_r,max*(eps_sm-eps_cm)` | EN 1992-1-1 §7.3.4 Eq.(7.8); NTC2018 §4.1.2.2.4 | - | limiti `w_lim_mm` da NTC2018.json |
| Vibrazioni (X4.3) | `f1 = lambda^2/(2*pi*L^2)*sqrt(EI/m)`; `a_RMS = F/(xi*m*L*sqrt(2))` | NTC2018 §C7.10.5; EN ISO 10137 | `f1~18/sqrt(delta_cm)` | soglie differenziate per destinazione |

---

## Warning code del modulo

- X4-DEF-001, X4-DEF-002, X4-DEF-003, X4-DEF-004, X4-DEF-FALL-001
- X4-SLE-001, X4-SLE-002, X4-SLE-003, X4-SLE-004, X4-SLE-FALL-001
- X4-VIB-001, X4-VIB-002, X4-VIB-003, X4-VIB-004, X4-VIB-FALL-001

Tutti i warning sono registrati anche su `registro_log` con `registro.avviso(...)`.

---

## Decisioni Q&A recepite

- Sviluppo parallelo dei sotto-moduli.
- Output dettagliato (steps, warnings, details, trace, norm_references).
- Fallback sempre disponibile, ma esplicito e tracciato con warning dedicato.
- Parametri estesi e configurabili con default normativi.
- Inclusa fessurazione `w_k` in X4.2.
- Inclusa viscosita `phi` in X4.1 (freccia lungo termine).
- Soglie vibrazioni differenziate: residenziale 4 Hz, uffici 4 Hz, palestre 5 Hz, passerelle 8 Hz.
- Dual-mode unita recepito: output storico + conversioni utili (cm/mm, kgf/cm2/MPa).
- Multi-schema vincoli recepito: appoggio-appoggio, incastro-incastro, incastro-appoggio.

---

## Implementazione eseguita

File creati:
- src/methods/ntc2018/checks_x4.py
- tests/codes/test_x4_sle_checks.py
- tests/codes/test_x4_sle_benchmark.py

File modificati:
- src/codes/ntc2018/code_module.py
- src/codes/params/NTC2018.json

Check implementati:
- x4_sle_deformabilita
- x4_sle_tensioni
- x4_sle_vibrazioni

---

## Quick reference testabile

| Test | Input | Output atteso |
| --- | --- | --- |
| X4-T01 | q_s, i, L, E, I | f_ist/f_tot/f_lim + UC_f |
| X4-T02 | M_rara, M_qp, b, d, As, fck, E | sigma_c rara/QP, sigma_s |
| X4-T03 | input X4-T02 + copriferro, diametro, classe | w_k e confronto con w_lim |
| X4-T04 | L, EI, m, xi, destinazione | f1 + soglia categoria |
| X4-T05 | F_ped, m, L, xi | a_RMS e confronto con 0.5 m/s2 |
| X4-T06 | input incompleto + fallback | warning *-FALL-001 |

---

## Stato avanzamento sub-fasi

- [x] X4.1 - Deformabilita
- [x] X4.2 - Tensioni SLE + fessurazione
- [x] X4.3 - Vibrazioni
- [x] X4.4 - Test e benchmark

---

## Esito test X4

- tests/codes/test_x4_sle_checks.py -> 22 pass / 0 fail
- tests/codes/test_x4_sle_benchmark.py -> 15 pass / 0 fail
- Totale validato su X4 (mirato): 37 pass / 0 fail

---

## Diagramma dipendenze subfasi

```text
X4.1 ---> X4.2 ---> X4.4
  |         |
  +-------> X4.3 ---> X4.4
```

---

## Rischi normativi residui

- Modello vibrazionale semplificato monomodale: per casi complessi resta necessaria analisi FEM dinamica.
- Fessurazione implementata in forma operativa semplificata: per casi specialistici usare analisi dettagliata di distribuzione armature.
- Le soglie comfort possono richiedere affinamento in base a capitolato del committente.

---

## Cronologia e decisioni

- 2026-03-15: creato modulo X4 da split master Fase X.
- 2026-03-15: completato audit tecnico-normativo pre-codifica e corretto il piano.
- 2026-03-15: completata implementazione X4 con cablaggio su CodeModule e parametri NTC2018.
- 2026-03-15: completata validazione mirata X4 con 37/37 test verdi.
