from __future__ import annotations

import logging
import math

from app.domain.materials import get_concrete_properties, get_steel_properties
from app.domain.models import VerificationInput, VerificationOutput
from app.domain.sections import get_section_geometry

logger = logging.getLogger(__name__)


def compute_sle_verification(
    _input: VerificationInput,
    section_repository: object | None = None,
    material_repository: object | None = None,
) -> VerificationOutput:
    try:
        primary_m = _input.Mx if abs(_input.Mx) >= abs(_input.My) else _input.My
        M_kgm = primary_m
        M = M_kgm * 100

        n = _input.n_homog if _input.n_homog > 0 else 15.0

        As_inf = _input.As_inf
        d_inf = _input.d_inf if _input.d_inf > 0 else 4.0

        B, H = get_section_geometry(_input, section_repository, unit="cm")
        d = H - d_inf

        fck_kgcm2 = get_concrete_properties(_input, material_repository)[1]
        fyk_kgcm2 = get_steel_properties(_input, material_repository)[1]

        sigma_c_lim = 0.6 * fck_kgcm2
        sigma_s_lim = 0.8 * fyk_kgcm2

        rho = As_inf / (B * d) if d > 0 and B > 0 else 0.001

        term = n * rho
        x_over_d = math.sqrt(term**2 + 2 * term) - term if term > 0 else 0.3
        x = x_over_d * d

        if x < 0.05 * H:
            x = 0.05 * H
        if x > 0.95 * H:
            x = 0.95 * H

        I_fess = B * x**3 / 3 + n * As_inf * (d - x) ** 2

        if I_fess > 0:
            sigma_c = M * x / I_fess
        else:
            sigma_c = 0.0

        if x > 0 and I_fess > 0:
            sigma_s = n * M * (d - x) / I_fess
        else:
            sigma_s = 0.0

        coeff_util_cls = sigma_c / sigma_c_lim if sigma_c_lim > 0 else 0.0
        coeff_util_acc = sigma_s / sigma_s_lim if sigma_s_lim > 0 else 0.0
        coeff_sicurezza = max(coeff_util_cls, coeff_util_acc)

        tensioni_ok = (sigma_c <= sigma_c_lim) and (sigma_s <= sigma_s_lim)

        if As_inf > 0:
            phi_eq = 12.0
            rho_eff = As_inf / (B * 2.5 * d_inf)
            sr_max = 3.4 * 4.0 + 0.425 * phi_eq / rho_eff if rho_eff > 0 else 300.0
            eps_sm = max(sigma_s / (n * 200000), 0.6 * sigma_s / 200000)
            wk = sr_max * eps_sm / 1000
        else:
            wk = 0.0

        wk_lim = 0.3
        fessure_ok = wk <= wk_lim

        if tensioni_ok and fessure_ok:
            esito = "VERIFICATO"
        else:
            esito = "NON VERIFICATO"

        messaggi = [
            "=== VERIFICA STATO LIMITE DI ESERCIZIO (SLE) - NTC2018 ===",
            "",
            "DATI INPUT:",
            f"  Sezione: {_input.section_id or 'rettangolare B×H'}",
            f"  Dimensioni: B = {B:.1f} cm, H = {H:.1f} cm, d = {d:.1f} cm",
            f"  Armatura inferiore As = {As_inf:.2f} cm²",
            f"  Coeff. omogeneizzazione n = {n:.1f}",
            f"  Sollecitazioni: Mx = {_input.Mx:.2f} kg·m, My = {_input.My:.2f} kg·m,"
            f" Mz = {_input.Mz:.2f} kg·m",
            "",
            "LIMITI TENSIONI SLE:",
            f"  Cls σ_c,lim = 0.6·fck = {sigma_c_lim:.1f} Kg/cm²",
            f"  Acc σ_s,lim = 0.8·fyk = {sigma_s_lim:.0f} Kg/cm²",
            "",
            "RISULTATI CALCOLO (stadio II - fessurato):",
            f"  Posizione asse neutro x = {x:.2f} cm (x/d = {x/d:.3f})",
            f"  Tensione cls σ_c = {sigma_c:.2f} Kg/cm² "
            f"{'✓' if sigma_c <= sigma_c_lim else '✗'}",
            f"  Tensione acciaio σ_s = {sigma_s:.0f} Kg/cm² "
            f"{'✓' if sigma_s <= sigma_s_lim else '✗'}",
            "",
            "VERIFICA FESSURAZIONE:",
            f"  Apertura fessure wk = {wk:.3f} mm",
            f"  Limite wk,lim = {wk_lim:.2f} mm {'✓' if wk <= wk_lim else '✗'}",
            "",
            f"ESITO: {esito} (coeff. utilizzo max = {coeff_sicurezza:.3f})",
        ]

        return VerificationOutput(
            sigma_c_max=sigma_c,
            sigma_c_min=0.0,
            sigma_s_max=sigma_s,
            asse_neutro=x,
            deformazioni=f"wk = {wk:.3f} mm, x/d = {x/d:.3f}",
            coeff_sicurezza=coeff_sicurezza,
            esito=esito,
            messaggi=messaggi,
        )

    except Exception as e:
        logger.exception("Errore in compute_sle_verification: %s", e)
        return VerificationOutput(
            sigma_c_max=0.0,
            sigma_c_min=0.0,
            sigma_s_max=0.0,
            asse_neutro=0.0,
            deformazioni="",
            coeff_sicurezza=0.0,
            esito="ERRORE",
            messaggi=[f"Errore durante il calcolo SLE: {e}"],
        )
