"""Test Fase R.1: livelli conoscenza e fattori confidenza."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.core.registro_log import registro
from src.esistenti.livelli_conoscenza import (
    LivelloConoscenza,
    MaterialeConFC,
    applica_fc_a_resistenza,
    risolvi_fc,
)


@dataclass
class MockMaterial:
    f_ck: float = 25.0
    f_yk: float = 450.0


def _count_log_entries() -> int:
    return len(registro.ottieni_voci(modulo="esistenti.livelli_conoscenza"))


def test_risolvi_fc_default_per_livello() -> None:
    assert risolvi_fc(LivelloConoscenza.LC1) == pytest.approx(1.35)
    assert risolvi_fc(LivelloConoscenza.LC2) == pytest.approx(1.20)
    assert risolvi_fc(LivelloConoscenza.LC3) == pytest.approx(1.00)


def test_risolvi_fc_supporta_input_stringa() -> None:
    assert risolvi_fc("LC2") == pytest.approx(1.20)


def test_risolvi_fc_override_valido() -> None:
    assert risolvi_fc("LC2", fc_override=1.10) == pytest.approx(1.10)


@pytest.mark.parametrize("fc_bad", [0.9, 1.8])
def test_risolvi_fc_override_fuori_range(fc_bad: float) -> None:
    with pytest.raises(ValueError, match="FC fuori range"):
        risolvi_fc("LC2", fc_override=fc_bad)


def test_applica_fc_a_resistenza_formula_base() -> None:
    f_d_eff = applica_fc_a_resistenza(180.0, "LC2")
    assert f_d_eff == pytest.approx(150.0)


def test_applica_fc_a_resistenza_usa_override() -> None:
    f_d_eff = applica_fc_a_resistenza(180.0, "LC2", fc_override=1.10)
    assert f_d_eff == pytest.approx(180.0 / 1.10)


def test_materiale_con_fc_da_materiale() -> None:
    materiale = MockMaterial(f_ck=30.0, f_yk=450.0)

    adattato = MaterialeConFC.da_materiale(
        materiale=materiale,
        livello_conoscenza=LivelloConoscenza.LC2,
    )

    assert adattato.livello_conoscenza is LivelloConoscenza.LC2
    assert adattato.fc_usato == pytest.approx(1.20)
    assert adattato.proprieta.f_ck_adjusted == pytest.approx(25.0)
    assert adattato.proprieta.f_yk_adjusted == pytest.approx(375.0)


def test_lc1_genera_warning_nel_registro() -> None:
    before = _count_log_entries()
    _ = risolvi_fc("LC1")
    after = _count_log_entries()
    assert after >= before + 1


def test_override_fc_genera_warning_nel_registro() -> None:
    before = _count_log_entries()
    _ = risolvi_fc("LC2", fc_override=1.10)
    after = _count_log_entries()
    assert after >= before + 1


def test_livello_non_valido() -> None:
    with pytest.raises(ValueError, match="Livello di conoscenza non valido"):
        risolvi_fc("LC9")
