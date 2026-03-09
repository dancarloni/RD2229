"""Integrazione carote con LC/FC e archivio materiali.

Due flussi:
1. Standalone: applica_fc_a_risultato() -> AdjustedMaterialProperties
2. Integrato: registra_materiale_in_situ() -> Material registrato nel repo
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.codes.carote.analysis import CoreAnalysisResult
from src.core_calculus.lc_fc_adjustments import (
    AdjustedMaterialProperties,
    apply_lc_fc_adjustments,
    get_typical_fc_for_lc,
)

if TYPE_CHECKING:
    pass

# MPa -> kg/cm²
_MPA_TO_KG_CM2 = 1.0 / 0.0980665


class _MaterialProxy:
    """Proxy duck-typed per apply_lc_fc_adjustments.

    apply_lc_fc_adjustments richiede un oggetto con f_ck e f_yk > 0.
    Per calcestruzzo puro, f_yk e' nominale (450 MPa) — il valore
    adjusted di f_yk non ha significato fisico ed e' da ignorare.
    """

    def __init__(self, f_ck_mpa: float, f_yk_mpa: float = 450.0) -> None:
        self.f_ck = f_ck_mpa
        self.f_yk = f_yk_mpa


def applica_fc_a_risultato(
    analysis: CoreAnalysisResult,
    lc: str = "LC2",
    fc: float | None = None,
    formulation: str = "NTC2018",
) -> AdjustedMaterialProperties:
    """Applica fattore di confidenza FC al risultato dell'analisi.

    Args:
        analysis: risultato analisi carote
        lc: livello di conoscenza (LC1, LC2, LC3)
        fc: fattore di confidenza (None = automatico da LC)
        formulation: formulazione di riferimento per f_ck,is

    Returns:
        AdjustedMaterialProperties con f_ck adjusted
    """
    if fc is None:
        fc = get_typical_fc_for_lc(lc)

    derived = analysis.derived.get(formulation)
    if derived is None:
        raise ValueError(
            f"Formulazione '{formulation}' non presente nei risultati. "
            f"Disponibili: {list(analysis.derived.keys())}"
        )

    f_ck_is = derived.f_ck_is_mpa
    proxy = _MaterialProxy(f_ck_mpa=f_ck_is)
    return apply_lc_fc_adjustments(proxy, lc=lc, fc=fc)


def registra_materiale_in_situ(
    analysis: CoreAnalysisResult,
    repo: Any,
    material_id: str = "",
    norma: str = "NTC2018",
    lc: str = "LC2",
    formulation: str = "NTC2018",
) -> Any:
    """Registra un materiale calcestruzzo in situ nel repository.

    Crea un Material(famiglia="calcestruzzo") con i parametri derivati
    dall'analisi carote e lo salva nel repo.

    Args:
        analysis: risultato analisi carote
        repo: MaterialRepository
        material_id: ID materiale (auto-generato se vuoto)
        norma: norma di riferimento
        lc: livello di conoscenza
        formulation: formulazione per f_ck,is

    Returns:
        Material registrato
    """
    from src.materials.material_model import Material

    derived = analysis.derived.get(formulation)
    if derived is None:
        raise ValueError(
            f"Formulazione '{formulation}' non presente nei risultati. "
            f"Disponibili: {list(analysis.derived.keys())}"
        )

    stats = analysis.statistics.get(formulation)
    n_samples = len(analysis.samples)

    # Conversione MPa -> kg/cm²
    f_ck_kgcm2 = derived.f_ck_is_mpa * _MPA_TO_KG_CM2
    E_kgcm2 = derived.E_cm_mpa * _MPA_TO_KG_CM2

    if not material_id:
        material_id = f"CLS_INSITU_{derived.classification}_{lc}"

    nota = (
        f"Calcestruzzo in situ da {n_samples} carote. "
        f"Formulazione: {formulation}, LC: {lc}. "
        f"f_ck,is = {derived.f_ck_is_mpa:.1f} MPa, "
        f"classe {derived.classification}."
    )
    if stats:
        nota += f" Media = {stats.summary.mean:.1f} MPa, CoV = {stats.summary.cov:.3f}."

    mat = Material(
        material_id=material_id,
        descrizione=f"Cls in situ {derived.classification} — {formulation} {lc}",
        famiglia="calcestruzzo",
        norma_riferimento=norma,
        f_ck=f_ck_kgcm2,
        E=E_kgcm2,
        sigma_c_adm=derived.sigma_c_adm_kgcm2,
        note=nota,
    )

    repo.add(mat)
    return mat
