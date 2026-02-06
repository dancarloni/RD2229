from __future__ import annotations

import logging
from typing import Optional

from app.domain.materials import get_concrete_properties, get_steel_properties
from app.domain.models import VerificationInput, VerificationOutput
from app.domain.sections import get_section_geometry

logger = logging.getLogger(__name__)
MPA_TO_KGCM2 = 10.197


def compute_slu_verification(
    _input: VerificationInput,
    section_repository: Optional[object] = None,
    material_repository: Optional[object] = None,
) -> VerificationOutput:
    try:
        N_kg = _input.N
        primary_m = _input.Mx if abs(_input.Mx) >= abs(_input.My) else _input.My
        M_kgm = primary_m

        M = M_kgm * 9806.65

        As_sup = _input.As_sup * 100
        As_inf = _input.As_inf * 100
        d_sup_cm = _input.d_sup if _input.d_sup > 0 else 4.0
        d_inf_cm = _input.d_inf if _input.d_inf > 0 else 4.0

        B, H = get_section_geometry(_input, section_repository, unit="mm")
        d = H - d_inf_cm * 10

        fck, *_ = get_concrete_properties(_input, material_repository)
        fyk, *_ = get_steel_properties(_input, material_repository)

        gamma_c = 1.5
        gamma_s = 1.15

        fcd = 0.85 * fck / gamma_c
        fyd = fyk / gamma_s

        eps_cu = 0.0035
        x = 0.3 * d

        Ac_compr = B * 0.8 * x
        Rc = Ac_compr * fcd

        Rc_sup = As_sup * fyd if x > d_sup_cm * 10 else 0.0

        z = d - 0.4 * x
        Mrd = Rc * z + Rc_sup * (d - d_sup_cm * 10)

        coeff_sicurezza = abs(M) / Mrd if Mrd > 0 else 999.0

        if coeff_sicurezza <= 1.0:
            esito = "VERIFICATO"
        else:
            esito = "NON VERIFICATO"

        fcd_kgcm2 = fcd * MPA_TO_KGCM2
        fyd_kgcm2 = fyd * MPA_TO_KGCM2

        sigma_c_max = fcd if coeff_sicurezza >= 1.0 else fcd * coeff_sicurezza
        sigma_s_max = fyd if As_inf > 0 else 0.0

        sigma_c_max_kgcm2 = sigma_c_max * MPA_TO_KGCM2
        sigma_s_max_kgcm2 = sigma_s_max * MPA_TO_KGCM2

        messaggi = [
            "=== VERIFICA STATO LIMITE ULTIMO (SLU) - NTC2018 ===",
            "",
            "DATI INPUT:",
            f"  Sezione: {_input.section_id or 'rettangolare B×H'}",
            f"  Dimensioni: B = {B/10:.1f} cm, H = {H/10:.1f} cm, d = {d/10:.1f} cm",
            f"  Armatura inferiore As = {As_inf/100:.2f} cm²",
            f"  Armatura superiore As' = {As_sup/100:.2f} cm²",
            f"  Sollecitazioni: N = {N_kg:.0f} kg",
            f"    Mx = {_input.Mx:.2f} kg·m, My = {_input.My:.2f} kg·m, Mz = {_input.Mz:.2f} kg·m",
            "",
            "RESISTENZE MATERIALI:",
            f"  Calcestruzzo fck = {fck:.0f} MPa → fcd = {fcd:.1f} MPa ({fcd_kgcm2:.1f} Kg/cm²)",
            f"  Acciaio fyk = {fyk:.0f} MPa → fyd = {fyd:.0f} MPa ({fyd_kgcm2:.0f} Kg/cm²)",
            "",
            "RISULTATI CALCOLO:",
            f"  Posizione asse neutro x = {x/10:.2f} cm",
            f"  Rapporto x/d = {x/d:.3f}",
            f"  Momento resistente M_Rd = {Mrd/9806.65:.2f} kg·m",
            f"  Momento agente M_Ed = {M_kgm:.2f} kg·m",
            "",
            "VERIFICA:",
            f"  M_Ed / M_Rd = {coeff_sicurezza:.3f} "
            f"{('✓' if coeff_sicurezza <= 1.0 else '✗')}",
            "",
            f"ESITO: {esito}",
        ]

        return VerificationOutput(
            sigma_c_max=sigma_c_max_kgcm2,
            sigma_c_min=0.0,
            sigma_s_max=sigma_s_max_kgcm2,
            asse_neutro=x / 10,
            deformazioni=f"ε_cu = {eps_cu*1000:.2f}‰, x/d = {x/d:.3f}",
            coeff_sicurezza=coeff_sicurezza,
            esito=esito,
            messaggi=messaggi,
        )

    except Exception as e:
        logger.exception("Errore in compute_slu_verification: %s", e)
        return VerificationOutput(
            sigma_c_max=0.0,
            sigma_c_min=0.0,
            sigma_s_max=0.0,
            asse_neutro=0.0,
            deformazioni="",
            coeff_sicurezza=0.0,
            esito="ERRORE",
            messaggi=[f"Errore durante il calcolo SLU: {e}"],
        )
