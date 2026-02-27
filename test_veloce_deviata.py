"""Test veloce pressoflessione deviata RD 2229/39 - ASCII only."""

from dataclasses import dataclass

from src.core_calculus.contracts import CalcInput
from src.core_calculus.normative_registry import get_rd2229_templates
from src.methods.checks_rd2229 import check_pressoflessione_deviata_ta_concrete


@dataclass
class MockSection:
    width: float = 300.0
    height: float = 500.0


@dataclass
class MockMaterial:
    sigma_c28: float = 160.0
    sigma_c_adm: float = 80.0
    tau_c0: float = 9.6
    tau_c1: float = 22.4
    Ec: float = 250000.0
    n: float = 8.4
    sigma_sn: float = 3800.0
    sigma_s_adm: float = 1900.0
    Es: float = 2100000.0


# Test
print("=" * 60)
print("TEST PRESSOFLESSIONE DEVIATA RD 2229/39")
print("=" * 60)

templates = get_rd2229_templates()
template = next(t for t in templates if t.template_id == "rd2229_ta_pressoflessione_deviata_concrete")

section = MockSection(width=300.0, height=500.0)
material = MockMaterial()

calc_input = CalcInput(
    element_name="Pilastro Test",
    section=section,
    material=material,
    norm_code="RD2229",
    limit_states_enabled=["TA"],
    N=-150.0,
    Mx=35.0,
    My=25.0,
)

result = check_pressoflessione_deviata_ta_concrete(calc_input, template)

print(f"\nRisultato: {'OK' if result.ok else 'NON OK'}")
print(f"Utilizzazione: {result.utilisation:.1%}")
print("\nDettagli tecnici:")
print(f"  Sezione: {section.width/10:.0f}x{section.height/10:.0f} cm")
print(f"  N  = {calc_input.N:.1f} kN")
print(f"  Mx = {calc_input.Mx:.1f} kNm")
print(f"  My = {calc_input.My:.1f} kNm")

print("\n" + "=" * 60)
print("MESSAGGI ITALIANI COMPLETI:")
print("=" * 60)
for msg in result.messages_it:
    # Sostituisci caratteri greci con ASCII
    msg_ascii = msg.replace("σ", "sigma").replace("·", ".").replace("≤", "<=").replace("≥", ">=")
    msg_ascii = msg_ascii.replace("✓", "[OK]").replace("✗", "[X]").replace("→", "->")
    print(msg_ascii)

print("\n" + "=" * 60)
print("TEST COMPLETATO CON SUCCESSO!")
print("=" * 60)
