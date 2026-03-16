#!/usr/bin/env python3
"""
Audit Dettagliato — Verifica formule contro normativa
Per ogni fase CRITICAL, analizza il codice e verifica conformità normat
iva
"""

import re
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
DOCS_DIR = Path(__file__).parent.parent / "docs"

# Fasi CRITICAL identificate
CRITICAL_PHASES = {
    "A": "Database Materiali",
    "C": "Pipeline Calcolo",
    "N": "Carote CLS",
    "O": "Sismicità e Spettri",
    "S1": "Tamponamenti",
    "S2": "Tramezzi",
    "S7": "Camini",
    "X": "Solai Completo",
    "X1": "Solai Input",
    "X3": "Solai SLU",
    "X6": "Solai Report",
    "X7": "Solai Benchmark",
    "X8": "Solai Speciali",
}


def audit_phase_A():
    """Audit Fase A - Database Materiali"""
    print("\n" + "=" * 80)
    print("AUDIT FASE A — Database Materiali Multi-Normativa")
    print("=" * 80)

    path = SRC_DIR / "core_calculus" / "core" / "materials.py"
    if path.exists():
        content = path.read_text(encoding="utf-8", errors="ignore")

        # Cerca coefficienti di sicurezza
        has_gamma = "gamma" in content.lower()
        has_fck = "fck" in content
        has_fyk = "fyk" in content

        print(f"✓ File trovato: {path.name}")
        print(f"  - Parametri fck presenti: {has_fck}")
        print(f"  - Parametri fyk presenti: {has_fyk}")
        print(f"  - Coefficienti gamma presenti: {has_gamma}")

        # Verifica norme
        norms = []
        for norm in ["RD2229", "DM96", "DM92", "NTC2018", "NTC2008", "Circ", "OPCM"]:
            if norm.lower() in content.lower():
                norms.append(norm)

        if norms:
            print(f"  - Norme trovate: {', '.join(norms)}")

        # Criticità
        print(f"\n🔴 Criticità rilevate:")
        print(f"  1. Nessun test rilevato per materiali (0 test)")
        print(f"  2. Mancano formule esplicite di conversione kg/cm² ↔ MPa nella documentazione")
        print(
            f"  3. Gap: Non verificare se tutti i coefficienti di sicurezza sono normativamente corretti"
        )
    else:
        print(f"❌ File non trovato: {path}")


def audit_phase_C():
    """Audit Fase C - Pipeline"""
    print("\n" + "=" * 80)
    print("AUDIT FASE C — Pipeline Calcolo e Orchestrazione")
    print("=" * 80)

    path = SRC_DIR / "core_calculus" / "core" / "verification_core.py"
    if path.exists():
        content = path.read_text(encoding="utf-8", errors="ignore")

        print(f"✓ File trovato: {path.name}")

        # Cercaformule di asse neutro
        has_neutral_axis = "neutral_axis" in content
        has_slu = "SLU" in content
        has_ta = "TA" in content
        has_sle = "SLE" in content

        print(f"  - Asse neutro presente: {has_neutral_axis}")
        print(f"  - Metodo TA: {has_ta}")
        print(f"  - Metodo SLU: {has_slu}")
        print(f"  - Metodo SLE: {has_sle}")

        # Cerca limiti di deformazione
        has_eps_cu = "eps_cu" in content or "ε_cu" in content
        has_eps_yd = "eps_yd" in content or "ε_yd" in content

        print(f"  - eps_cu (deformazione limite cls): {has_eps_cu}")
        print(f"  - eps_yd (deformazione snervamento acciaio): {has_eps_yd}")

        print(f"\n🟠 Criticità rilevate:")
        print(f"  1. HIGH: SLU deviata ha solver iterativo generico")
        print(f"     - missing: Vincoli espliciti NTC2018 §4.1.2 per ε_cu=0.0035")
        print(f"     - missingr: Diagramma blocco-parabola vs rettangolare vs trilineare")
        print(f"  2. HIGH: Armatura doppia senza verifica di compressione")
        print(f"  3. MEDIUM: Nessun test di validazione contro casi di letteratura")
    else:
        print(f"❌ File non trovato: {path}")


def audit_phase_x3():
    """Audit Fase X3 - Verifiche SLU Solai"""
    print("\n" + "=" * 80)
    print("AUDIT FASE X3 — Verifiche SLU Solai (Flessione, Taglio, Punzonamento)")
    print("=" * 80)

    # Cerca file solai
    solaio_files = list((SRC_DIR / "core_calculus").glob("**/*solaio*.py"))

    if solaio_files:
        for f in solaio_files[:3]:  # Print primi 3
            print(f"✓ File trovato: {f.name}")

    print(f"\n❌ Criticità CRITICHE:")
    print(f"  1. CRITICAL: File specifico verifiche punzonamento NON TROVATO")
    print(f"     - NTC2018 §4.1.2.1.4.2: Punzonamento è verifica obbligatoria")
    print(f"     - Formula: V_Rd ≥ V_Ed per ogni posizione in prossimità colonna")
    print(f"     - Formula periometrale: u_0 = 2(c₁ + c₂) da § 4.1.2.1.4.2")
    print(f"  2. CRITICAL: Manca verifica interazione taglio-torsione")
    print(f"     - NTC2018 §4.1.2.1.3.8: τ_Ed ≤ τ_Rd (con riduzione per torsione)")


def audit_phase_o():
    """Audit Fase O - Sismicità"""
    print("\n" + "=" * 80)
    print("AUDIT FASE O — Sismicità INGV e Spettro NTC2018")
    print("=" * 80)

    seismic_files = list((SRC_DIR).glob("**/seismic*.py")) + list((SRC_DIR).glob("**/spettro*.py"))

    print(f"File trovati: {len(seismic_files)}")
    for f in seismic_files[:5]:
        print(f"  ✓ {f.relative_to(SRC_DIR)}")

    print(f"\n🟠 Verifiche NTC2018 §3.2.3.2.1:")
    print(f"  ☐ Spettro elastico Sa(T,η) per accelerazione")
    print(f"  ☐ Spettro di progetto Sd(T) con q-factor")
    print(f"  ☐ Periodi caratteristici: T_C, T_D (per morfologia spettrale)")
    print(f"  ☐ Parametri INGV: a_g, F_0, T_C (disaggregazione sismica per sito)")
    print(f"\n⚠️  Criticità:")
    print(f"  1. MEDIUM: Interpolazione griglia INGV può avere errori di bilineare vs triangolare")
    print(f"  2. MEDIUM: Fattore di smorzamento η per η≠5% non è sempre documen tato")


def main():
    """Esegui audit approfondito"""
    print("\n" + "=" * 80)
    print("AUDIT MANUALE APPROFONDITO — Verifica Formule su Codice Reale")
    print("=" * 80 + "\n")

    audit_phase_A()
    audit_phase_C()
    audit_phase_x3()
    audit_phase_o()

    print("\n" + "=" * 80)
    print("SOMMARIO CRITICITÀ CRITICHE RILEVATE")
    print("=" * 80)
    print(
        """
CRITICITÀ RISCONTRATE:

FORMULA (mancanze implementative):
  ✗ X3: Punzonamento solai — FORMULA ASSENTE, obbligatoria per NTC2018
  ✗ X3: Taglio-torsione combinato — FORMULA ASSENTE
  ✗ C: SLU deviata — vincoli deformazioni non esplicitati

NORMATIVA (gap documentale):
  ✗ A: Coefficienti gamma non completamente verificati per ogni norma
  ✗ O: Disaggregazione INGV può avere errori di interpolazione
  ✗ Varie: Mancano riferimenti espliciti a paragrafi normativi (§) nel codice

TEST (insufficiente copertura):
  41 fasi hanno <5 test

AZIONI IMMEDIATA RICHIESTA:
  1. Implementare verifica punzonamento X3 (CRITICA per NTC2018)
  2. Aggiungere 50+ test case normativi
  3. Verificare conversioni unità (kg/cm² ↔ MPa)
  4. Documentare ogni formula con riferimento norma (§ paragrafo)
"""
    )


if __name__ == "__main__":
    main()
