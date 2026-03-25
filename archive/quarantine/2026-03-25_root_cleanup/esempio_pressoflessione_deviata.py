"""
Esempio di utilizzo delle verifiche di pressoflessione deviata RD 2229/39.

Dimostra come utilizzare i nuovi check per N-Mx-My con sovrapposizione elastica.
"""

from dataclasses import dataclass

from src.core_calculus.contracts import CalcInput
from src.core_calculus.normative_registry import get_rd2229_templates
from src.methods.rd2229.checks import (
    check_pressoflessione_deviata_ta_concrete,
    check_pressoflessione_deviata_ta_steel,
)

# ==============================================================================
# MOCK OBJECTS (per test senza dipendenze esterne)
# ==============================================================================


@dataclass
class MockSection:
    """Sezione rettangolare mock."""

    width: float = 300.0  # mm
    height: float = 500.0  # mm


@dataclass
class MockMaterial:
    """Materiale RD2229 R160 / FeB38k mock."""

    # Concrete R160
    sigma_c28: float = 160.0
    sigma_c_adm: float = 80.0
    tau_c0: float = 9.6
    tau_c1: float = 22.4
    Ec: float = 250000.0
    n: float = 8.4

    # Steel FeB38k
    sigma_sn: float = 3800.0
    sigma_s_adm: float = 1900.0
    Es: float = 2100000.0


# ==============================================================================
# ESEMPI DI UTILIZZO
# ==============================================================================


def esempio_1_verifica_concrete_ok():
    """Esempio 1: Verifica calcestruzzo - caso OK."""
    print("=" * 80)
    print("ESEMPIO 1: Verifica Calcestruzzo - Caso OK")
    print("=" * 80)

    # Recupera template dal registry
    templates = get_rd2229_templates()
    template = next(
        t for t in templates if t.template_id == "rd2229_ta_pressoflessione_deviata_concrete"
    )

    # Prepara input
    section = MockSection(width=300.0, height=500.0)  # 30x50 cm
    material = MockMaterial()  # R160 (σ_c,adm = 80 kg/cm²)

    calc_input = CalcInput(
        element_name="Pilastro P1 - Biassiale",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-150.0,  # kN - compressione
        Mx=35.0,  # kNm
        My=25.0,  # kNm
        lc="LC2",
        fc=1.20,
    )

    # Esegui verifica
    result = check_pressoflessione_deviata_ta_concrete(calc_input, template)

    # Mostra risultati
    print(f"\n{'[OK] VERIFICA SUPERATA' if result.ok else '[NON OK] VERIFICA NON SUPERATA'}")
    print(f"Utilizzazione: {result.utilisation:.1%}\n")

    print("Dettagli:")
    print(f"  σ_c,max = {result.details['sigma_c_max_kg_cm2']:.2f} kg/cm²")
    print(f"  σ_c,adm = {result.details['sigma_c_adm_kg_cm2']:.2f} kg/cm²")
    print(f"  Wx = {result.details['Wx_cm3']:.1f} cm³")
    print(f"  Wy = {result.details['Wy_cm3']:.1f} cm³")

    print("\nMessaggi completi:")
    for msg in result.messages_it:
        print(msg)

    return result


def esempio_2_verifica_sezione_snella():
    """Esempio 2: Verifica con riduzione per sezione snella (b < 25 cm)."""
    print("\n\n" + "=" * 80)
    print("ESEMPIO 2: Sezione Snella - Riduzione σ_c,adm")
    print("=" * 80)

    templates = get_rd2229_templates()
    template = next(
        t for t in templates if t.template_id == "rd2229_ta_pressoflessione_deviata_concrete"
    )

    # Sezione snella: b = 20 cm < 25 cm
    section = MockSection(width=200.0, height=400.0)  # 20x40 cm
    material = MockMaterial()

    calc_input = CalcInput(
        element_name="Pilastro P2 - Snello",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-120.0,
        Mx=30.0,
        My=20.0,
    )

    result = check_pressoflessione_deviata_ta_concrete(calc_input, template)

    print(f"\n{'[OK] VERIFICA SUPERATA' if result.ok else '[NON OK] VERIFICA NON SUPERATA'}")
    print(f"Utilizzazione: {result.utilisation:.1%}\n")

    if result.details.get("reduction_applied"):
        print("[!] RIDUZIONE PER SEZIONE SNELLA APPLICATA:")
        print(f"  A_min = {result.details['A_min_cm']:.1f} cm < 25 cm")
        print(f"  Fattore riduzione = {result.details['reduction_factor']:.3f}")
        print(f"  σ_c,adm base = {result.details['sigma_c_adm_base_kg_cm2']:.1f} kg/cm²")
        print(f"  σ_c,adm ridotta = {result.details['sigma_c_adm_kg_cm2']:.1f} kg/cm²")

    return result


def esempio_3_verifica_steel_senza_moduli():
    """Esempio 3: Verifica acciaio SENZA moduli W_sx/W_sy (PARTIAL)."""
    print("\n\n" + "=" * 80)
    print("ESEMPIO 3: Verifica Acciaio - Senza Moduli (PARTIAL)")
    print("=" * 80)

    templates = get_rd2229_templates()
    template = next(
        t for t in templates if t.template_id == "rd2229_ta_pressoflessione_deviata_steel"
    )

    section = MockSection(width=300.0, height=500.0)
    material = MockMaterial()

    # NO extra dict → mancano W_sx_cm3, W_sy_cm3
    calc_input = CalcInput(
        element_name="Pilastro P3 - Acciaio",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-150.0,
        Mx=40.0,
        My=30.0,
    )

    result = check_pressoflessione_deviata_ta_steel(calc_input, template)

    print(f"\n{'[OK]' if result.ok else '[DATI MANCANTI]'}")
    print(f"Motivo: {result.details.get('partial_reason', 'N/A')}\n")

    print("Messaggi:")
    for msg in result.messages_it:
        print(msg)

    return result


def esempio_4_verifica_steel_con_moduli():
    """Esempio 4: Verifica acciaio CON moduli W_sx/W_sy (COMPLETA)."""
    print("\n\n" + "=" * 80)
    print("ESEMPIO 4: Verifica Acciaio - Con Moduli (COMPLETA)")
    print("=" * 80)

    templates = get_rd2229_templates()
    template = next(
        t for t in templates if t.template_id == "rd2229_ta_pressoflessione_deviata_steel"
    )

    section = MockSection(width=300.0, height=500.0)
    material = MockMaterial()  # FeB38k: σ_s,adm = 1900 kg/cm²

    # Fornire W_sx, W_sy in extra
    calc_input = CalcInput(
        element_name="Pilastro P4 - Acciaio Completo",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=40.0,
        My=30.0,
        extra={
            "W_sx_cm3": 500.0,  # cm³ - esempio
            "W_sy_cm3": 320.0,  # cm³ - esempio
        },
    )

    result = check_pressoflessione_deviata_ta_steel(calc_input, template)

    print(f"\n{'[OK] VERIFICA SUPERATA' if result.ok else '[NON OK] VERIFICA NON SUPERATA'}")
    print(f"Utilizzazione: {result.utilisation:.1%}\n")

    print("Dettagli:")
    print(f"  σ_s,max = {result.details['sigma_s_max_kg_cm2']:.2f} kg/cm²")
    print(f"  σ_s,adm = {result.details['sigma_s_adm_kg_cm2']:.2f} kg/cm²")
    print(f"  W_sx = {result.details['W_sx_cm3']:.1f} cm³")
    print(f"  W_sy = {result.details['W_sy_cm3']:.1f} cm³")

    return result


# ==============================================================================
# MAIN
# ==============================================================================


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print(" " * 15 + "ESEMPI PRESSOFLESSIONE DEVIATA RD 2229/39")
    print(" " * 20 + "Sovrapposizione Elastica N-Mx-My")
    print("=" * 80)

    # Esegui tutti gli esempi
    esempio_1_verifica_concrete_ok()
    esempio_2_verifica_sezione_snella()
    esempio_3_verifica_steel_senza_moduli()
    esempio_4_verifica_steel_con_moduli()

    print("\n\n" + "=" * 80)
    print("TUTTI GLI ESEMPI COMPLETATI")
    print("=" * 80)
    print("\nPer integrare nel tuo workflow:")
    print("  1. Usa get_rd2229_templates() per recuperare i template")
    print("  2. Prepara CalcInput con section, material, N, Mx, My")
    print("  3. Chiama check_pressoflessione_deviata_ta_concrete/steel")
    print("  4. Leggi result.ok, result.utilisation, result.messages_it")
    print("\nDocumentazione: src/methods/checks_rd2229.py linee 1083-1437")
    print()
