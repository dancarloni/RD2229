Normative source: EN 1992‑1‑1 §6.2 (Eurocode 2).
Formula (EC2, verbatim reference — compute using NA where required):
v_rd,c = [C_Rd,c · k · (100 · ρ_l · f_ck)^(1/3) + k1 · σ_cp] · b_w · d
with definitions: k = 1 + sqrt(200/d) ≤ 2.0; ρ_l = A_sl/(b_w·d); k1 = 0.15; C_Rd,c = 0.18/γ_c; v_min = ν_min · b_w · d (see EC2).
Applicability rules: return NOT_APPLICABLE when input outside EC2 bounds (d too small, ρ_l below minimum, etc.).
Tests: include the five golden inputs listed in Test fixtures.
TODOs: confirm γ_c from Italian NA and paste exact EC2 clause.

Fonte normativa: EN 1992‑1‑1 §6.2 (Eurocode 2). NTC2018 rimanda a EC2 per espressioni dettagliate.
Formula (EC2 — riferimento):
v_rd,c = [C_Rd,c · k · (100 · ρ_l · f_ck)^(1/3) + k1 · σ_cp] · b_w · d
con: k = 1 + sqrt(200/d) (≤ 2.0), ρ_l = A_sl/(b_w·d), k1 = 0.15, C_Rd,c = 0.18/γ_c; v_min = ν_min·b_w·d (ν_min = 0.035·k^(3/2)·√f_ck).
Applicabilità: restituisce NOT_APPLICABLE per d o ρ_l fuori dai limiti EC2; segnala se sezione non‑rettangolare o condizioni di bordo non standard.
Output richiesti: status (OK/NOT_OK/NOT_APPLICABLE), utilisation (V_Ed/V_Rd,c), V_Rd,c [kN], v_min [kN], norm_references[], messages[].
Esempi (golden fixtures — da usare nei test):

Case A (PASS): b=300 mm, d=450 mm, f_ck=30 MPa, ρ_l=0.015, σ_cp=0 MPa, V_Ed=60 kN → V_Rd,c ≈ 96.0 kN (assunzione γ_c=1.5) → status = OK.
Case B (FAIL): same geometry, V_Ed=200 kN → status = NOT_OK.
Case C (NOT_APPLICABLE): d < normative_min (es. d=80 mm) → status = NOT_APPLICABLE.
Case D (axial effect): σ_cp=+3 MPa → V_Rd,c increases (es. ≈ 156.8 kN with γ_c=1.5) → rivedere utilisation.
TODO (normativo): incollare testo originale EN1992‑1‑1 §6.2 e confermare γ_c e parametri dalla National Annex italiana.
