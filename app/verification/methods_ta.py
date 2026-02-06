from __future__ import annotations
from typing import Optional
import math
import logging

from app.domain.models import VerificationInput, VerificationOutput
from app.domain.sections import get_section_geometry
from app.domain.materials import get_concrete_properties, get_steel_properties

logger = logging.getLogger(__name__)

MPA_TO_KGCM2 = 10.197


def compute_ta_verification(
    _input: VerificationInput,
    section_repository: Optional[object] = None,
    material_repository: Optional[object] = None,
) -> VerificationOutput:
    try:
        N = _input.N
        primary_m = _input.Mx if abs(_input.Mx) >= abs(_input.My) else _input.My
        M_kgm = primary_m
        M = M_kgm * 100
        T = _input.Ty

        n = _input.n_homog if _input.n_homog > 0 else 15.0

        As_sup = _input.As_sup
        As_inf = _input.As_inf
        d_sup = _input.d_sup
        d_inf = _input.d_inf

        _fck_mpa, _fck_kgcm2, sigma_ca = get_concrete_properties(_input, material_repository)
        _fyk_mpa, _fyk_kgcm2, sigma_fa = get_steel_properties(_input, material_repository)

        B, H = get_section_geometry(_input, section_repository, unit="cm")

        if d_sup <= 0:
            d_sup = 4.0
        if d_inf <= 0:
            d_inf = 4.0

        d = H - d_inf

        if abs(N) < 0.01:
            e = 1e10
            is_fless_semplice = True
        else:
            e = abs(M / N) if N != 0 else 0
            is_fless_semplice = False

        rho_inf = As_inf / (B * d) if d > 0 and B > 0 else 0.001
        rho_sup = As_sup / (B * d) if d > 0 and B > 0 else 0.0

        term1 = n * rho_inf
        term2 = math.sqrt((n * rho_inf) ** 2 + 2 * n * rho_inf) if term1 >= 0 else 0.1
        x_over_d = term2 - term1 if term2 > term1 else 0.3

        x = x_over_d * d

        if x < 0.05 * H:
            x = 0.05 * H
        if x > 0.95 * H:
            x = 0.95 * H

        y_baric = x / 3

        if x > 0 and d > x / 3:
            J_sez_reag = B * x ** 3 / 12 + B * x * (y_baric) ** 2
            sigma_c_max = (M * x) / J_sez_reag if J_sez_reag > 0 else 0.0
            if x > 0:
                sigma_s = n * sigma_c_max * (d - x) / x
            else:
                sigma_s = 0.0
        else:
            sigma_c_max = 0.0
            sigma_s = 0.0

        sigma_c_min = 0.0

        coeff_util_cls = sigma_c_max / sigma_ca if sigma_ca > 0 else 0.0
        coeff_util_acc = sigma_s / sigma_fa if sigma_fa > 0 else 0.0
        coeff_sicurezza = max(coeff_util_cls, coeff_util_acc)

        if coeff_util_cls <= 1.0 and coeff_util_acc <= 1.0:
            esito = "VERIFICATO"
        else:
            esito = "NON VERIFICATO"

        messaggi = [
            "=== VERIFICA A TENSIONI AMMISSIBILI (TA) - RD 2229/1939 ===",
            "",
            "DATI INPUT:",
            f"  Sezione: {_input.section_id or 'rettangolare B×H'}",
            f"  Dimensioni: B = {B:.1f} cm, H = {H:.1f} cm, d = {d:.1f} cm",
            f"  Armatura inferiore As = {As_inf:.2f} cm²",
            f"  Armatura superiore As' = {As_sup:.2f} cm²",
            f"  Coefficiente omogeneizzazione n = {n:.1f}",
            f"  Sollecitazioni: N = {N:.0f} kg, Mx = {_input.Mx:.2f} kg·m, My = {_input.My:.2f} kg·m, Mz = {_input.Mz:.2f} kg·m",
            "",
            "TENSIONI AMMISSIBILI:",
            f"  Calcestruzzo σ_ca = {sigma_ca:.1f} Kg/cm²",
            f"  Acciaio σ_fa = {sigma_fa:.0f} Kg/cm²",
            "",
            "RISULTATI CALCOLO:",
            f"  Posizione asse neutro x = {x:.2f} cm (da lembo compresso)",
            f"  Rapporto x/d = {x/d:.3f}",
            f"  Tensione cls max σ_c = {sigma_c_max:.2f} Kg/cm²",
            f"  Tensione acciaio σ_s = {sigma_s:.0f} Kg/cm²",
            "",
            "VERIFICHE:",
            f"  Cls: σ_c / σ_ca = {sigma_c_max:.1f} / {sigma_ca:.1f} = {coeff_util_cls:.3f} {'✓' if coeff_util_cls <= 1.0 else '✗'}",
            f"  Acc: σ_s / σ_fa = {sigma_s:.0f} / {sigma_fa:.0f} = {coeff_util_acc:.3f} {'✓' if coeff_util_acc <= 1.0 else '✗'}",
            "",
            f"ESITO: {esito} (coeff. utilizzo max = {coeff_sicurezza:.3f})",
        ]

        return VerificationOutput(
            sigma_c_max=sigma_c_max,
            sigma_c_min=sigma_c_min,
            sigma_s_max=sigma_s,
            asse_neutro=x,
            deformazioni=f"x/d = {x/d:.3f}, ρ_inf = {rho_inf * 100:.2f}%",
            coeff_sicurezza=coeff_sicurezza,
            esito=esito,
            messaggi=messaggi,
        )

    except Exception as e:
        logger.exception("Errore in compute_ta_verification: %s", e)
        return VerificationOutput(
            sigma_c_max=0.0,
            sigma_c_min=0.0,
            sigma_s_max=0.0,
            asse_neutro=0.0,
            deformazioni="",
            coeff_sicurezza=0.0,
            esito="ERRORE",
            messaggi=[f"Errore durante il calcolo TA: {e}"],
        )