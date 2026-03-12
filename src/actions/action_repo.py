"""Infrastruttura per la gestione delle AZIONI DI VERIFICA.

Una "azione di verifica" (VerificationAction) è un oggetto che incapsula
una singola REGOLA DI VERIFICA strutturale. Il repository raccoglie tutte
le azioni disponibili e le collega a normative specifiche.

Azioni implementate:
- FlexureCheck: flessione semplice (NTC2018 SLU + RD2229 TA)
- ShearCheck: taglio (NTC2018 SLU + RD2229 TA)
- PressFlexureCheck: pressoflessione (NTC2018 SLU + RD2229 TA)
- TorsionCheck: torsione (NTC2018 SLU)
- SLEStressCheck: tensioni in esercizio (NTC2018 SLE)
- SLECrackingCheck: fessurazione (NTC2018 SLE)
"""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


# ===========================================================================
# Interfaccia base
# ===========================================================================


class VerificationAction:
    """Interfaccia base per una singola azione di verifica.

    Ogni azione implementa:
    - action_id: identificatore univoco
    - description: descrizione della verifica
    - norms: norme supportate
    - run(element, normative, settings) -> dict con risultato
    """

    action_id: str = "undefined"
    description: str = "Verification Action (base)."
    norms: list[str] = []

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        raise NotImplementedError("Azione di verifica non implementata.")


# ===========================================================================
# Repository
# ===========================================================================

ACTION_REPOSITORY: dict[str, VerificationAction] = {}


def register_action(action: VerificationAction) -> None:
    """Registra una azione di verifica nel repository."""
    if action.action_id in ACTION_REPOSITORY:
        logger.debug("Sovrascrittura azione '%s'.", action.action_id)
    ACTION_REPOSITORY[action.action_id] = action


def get_action(action_id: str) -> VerificationAction | None:
    """Recupera una azione di verifica registrata."""
    action = ACTION_REPOSITORY.get(action_id)
    if action is None:
        logger.warning("Azione '%s' non trovata nel repository.", action_id)
    return action


def list_actions() -> list[str]:
    """Restituisce la lista di tutte le azioni disponibili."""
    return list(ACTION_REPOSITORY.keys())


def list_actions_for_norm(norm_code: str) -> list[VerificationAction]:
    """Restituisce le azioni applicabili a una specifica norma."""
    return [a for a in ACTION_REPOSITORY.values() if norm_code in a.norms]


# ===========================================================================
# Funzioni di utilità per le formule
# ===========================================================================


def _get_float(obj: Any, key: str, default: float = 0.0) -> float:
    """Estrae un float da un oggetto (dict o attributo)."""
    if isinstance(obj, dict):
        return float(obj.get(key, default))
    return float(getattr(obj, key, default))


def _material_param(normative: dict, key: str, default: float = 0.0) -> float:
    """Estrae un parametro dal contesto normativo."""
    mat = normative.get("material", {})
    if isinstance(mat, dict):
        return float(mat.get(key, default))
    return float(getattr(mat, key, default))


# ===========================================================================
# FlexureCheck — Verifica flessione semplice
# ===========================================================================


class FlexureCheck(VerificationAction):
    """Verifica flessionale — NTC2018 SLU e RD2229 TA.

    NTC2018 SLU §4.1.2:
        M_Rd = As × f_yd × (d - 0.4·x)
        dove x = As × f_yd / (0.8 × b × f_cd)
        Verifica: M_Ed ≤ M_Rd

    RD2229 TA:
        σ_c = M / W ≤ σ_c_adm
        σ_s = n × M × y_s / J ≤ σ_s_adm
    """

    action_id = "flexure_check"
    description = "Verifica a flessione (NTC2018 SLU / RD2229 TA)."
    norms = ["NTC2018", "DM96", "RD2229"]

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        norm = normative.get("norm_code", "NTC2018")

        b = _get_float(element, "width_cm", _get_float(element, "b", 30.0))
        h = _get_float(element, "height_cm", _get_float(element, "h", 50.0))
        d = _get_float(element, "d", h - 4.0)
        As = _get_float(element, "As", 0.0)
        M_Ed = abs(_get_float(element, "Mx", _get_float(element, "M_Ed", 0.0)))

        partials: dict[str, Any] = {"b_cm": b, "h_cm": h, "d_cm": d, "As_cm2": As}

        if norm == "RD2229":
            return self._run_ta(b, h, d, As, M_Ed, normative, partials)
        return self._run_slu(b, h, d, As, M_Ed, normative, partials)

    def _run_slu(
        self,
        b: float,
        h: float,
        d: float,
        As: float,
        M_Ed: float,
        normative: dict,
        partials: dict,
    ) -> dict[str, Any]:
        f_cd = _material_param(normative, "f_cd", 141.7)  # kg/cm²
        f_yd = _material_param(normative, "f_yd", 3904.0)

        if As <= 0 or d <= 0 or b <= 0:
            return {
                "action_id": self.action_id,
                "ok": False,
                "messages": ["Dati geometrici o di armatura insufficienti."],
                "partials": partials,
            }

        # Profondità asse neutro
        x = As * f_yd / (0.8 * b * f_cd)
        # Momento resistente
        M_Rd = As * f_yd * (d - 0.4 * x) / 100.0  # kg·m

        utilization = M_Ed / M_Rd if M_Rd > 0 else float("inf")
        ok = utilization <= 1.0

        partials.update(
            {
                "f_cd": round(f_cd, 1),
                "f_yd": round(f_yd, 1),
                "x_cm": round(x, 2),
                "M_Rd_kgm": round(M_Rd, 1),
                "M_Ed_kgm": round(M_Ed, 1),
                "utilization": round(utilization, 3),
            }
        )

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"M_Ed = {M_Ed:.1f} kg·m, M_Rd = {M_Rd:.1f} kg·m, "
                f"utilizzazione = {utilization:.3f}",
            ],
            "partials": partials,
        }

    def _run_ta(
        self,
        b: float,
        h: float,
        d: float,
        As: float,
        M_Ed: float,
        normative: dict,
        partials: dict,
    ) -> dict[str, Any]:
        sigma_c_adm = _material_param(normative, "sigma_c_adm", 60.0)
        sigma_s_adm = _material_param(normative, "sigma_s_adm", 1400.0)
        n = _material_param(normative, "n_omogenizzazione", 10.0)

        W = b * h**2 / 6.0  # cm³
        J = b * h**3 / 12.0  # cm⁴
        y_s = d - h / 2.0

        sigma_c = M_Ed * 100.0 / W if W > 0 else float("inf")
        sigma_s = n * M_Ed * 100.0 * abs(y_s) / J if J > 0 else float("inf")

        ok_c = sigma_c <= sigma_c_adm
        ok_s = sigma_s <= sigma_s_adm
        ok = ok_c and ok_s

        partials.update(
            {
                "sigma_c": round(sigma_c, 1),
                "sigma_c_adm": round(sigma_c_adm, 1),
                "sigma_s": round(sigma_s, 1),
                "sigma_s_adm": round(sigma_s_adm, 1),
                "n": n,
                "W_cm3": round(W, 1),
                "J_cm4": round(J, 1),
            }
        )

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"σ_c = {sigma_c:.1f} ≤ {sigma_c_adm:.1f} kg/cm²: {'OK' if ok_c else 'NON VERIFICATO'}",
                f"σ_s = {sigma_s:.1f} ≤ {sigma_s_adm:.1f} kg/cm²: {'OK' if ok_s else 'NON VERIFICATO'}",
            ],
            "partials": partials,
        }


# ===========================================================================
# ShearCheck — Verifica taglio
# ===========================================================================


class ShearCheck(VerificationAction):
    """Verifica a taglio — NTC2018 SLU e RD2229 TA.

    NTC2018 SLU §4.1.2.3:
        V_Rd,s = A_sw/s × 0.9·d × f_yd × (cotα + cotθ) × sinα
        Verifica: V_Ed ≤ V_Rd,s

    RD2229 TA:
        τ = V / (b × d) ≤ τ_c1_adm (con staffe)
    """

    action_id = "shear_check"
    description = "Verifica a taglio (NTC2018 SLU / RD2229 TA)."
    norms = ["NTC2018", "DM96", "RD2229"]

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        norm = normative.get("norm_code", "NTC2018")

        b = _get_float(element, "width_cm", _get_float(element, "b", 30.0))
        h = _get_float(element, "height_cm", _get_float(element, "h", 50.0))
        d = _get_float(element, "d", h - 4.0)
        V_Ed = abs(_get_float(element, "Tx", _get_float(element, "V_Ed", 0.0)))

        diam_st = _get_float(element, "staffe_diametro", 8.0)
        n_bracci = _get_float(element, "staffe_num_bracci", 2.0)
        passo = _get_float(element, "staffe_passo", 20.0)
        A_sw = n_bracci * math.pi * (diam_st / 10.0) ** 2 / 4.0

        partials: dict[str, Any] = {
            "b_cm": b,
            "d_cm": d,
            "V_Ed_kg": round(V_Ed, 1),
            "diam_st_mm": diam_st,
            "n_bracci": n_bracci,
            "passo_cm": passo,
            "A_sw_cm2": round(A_sw, 3),
        }

        if norm == "RD2229":
            return self._run_ta(b, d, V_Ed, normative, partials)
        return self._run_slu(b, d, A_sw, passo, V_Ed, normative, partials)

    def _run_slu(
        self,
        b: float,
        d: float,
        A_sw: float,
        passo: float,
        V_Ed: float,
        normative: dict,
        partials: dict,
    ) -> dict[str, Any]:
        f_yd = _material_param(normative, "f_yd", 3904.0)

        if passo <= 0 or d <= 0:
            return {
                "action_id": self.action_id,
                "ok": False,
                "messages": ["Passo staffe o altezza utile non validi."],
                "partials": partials,
            }

        cot_theta = 2.5
        V_Rd_s = (A_sw / passo) * 0.9 * d * f_yd * cot_theta

        utilization = V_Ed / V_Rd_s if V_Rd_s > 0 else float("inf")
        ok = utilization <= 1.0

        partials.update(
            {
                "f_yd": round(f_yd, 1),
                "V_Rd_s_kg": round(V_Rd_s, 1),
                "utilization": round(utilization, 3),
            }
        )

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"V_Ed = {V_Ed:.1f} kg, V_Rd,s = {V_Rd_s:.1f} kg, "
                f"utilizzazione = {utilization:.3f}",
            ],
            "partials": partials,
        }

    def _run_ta(
        self,
        b: float,
        d: float,
        V_Ed: float,
        normative: dict,
        partials: dict,
    ) -> dict[str, Any]:
        tau_c1_adm = _material_param(normative, "tau_c1_adm", 14.0)

        tau = V_Ed / (b * d) if b * d > 0 else float("inf")
        ok = tau <= tau_c1_adm

        partials.update(
            {
                "tau_kg_cm2": round(tau, 2),
                "tau_c1_adm": round(tau_c1_adm, 1),
            }
        )

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"τ = {tau:.2f} ≤ {tau_c1_adm:.1f} kg/cm²: {'OK' if ok else 'NON VERIFICATO'}",
            ],
            "partials": partials,
        }


# ===========================================================================
# PressFlexureCheck — Pressoflessione
# ===========================================================================


class PressFlexureCheck(VerificationAction):
    """Verifica a pressoflessione — NTC2018 SLU e RD2229 TA.

    NTC2018 SLU:
        Diagramma di interazione N-M semplificato.
        N_Ed / N_Rd + M_Ed / M_Rd ≤ 1.0

    RD2229 TA:
        σ_c = N/A + M/W ≤ σ_c_adm
    """

    action_id = "press_flexure_check"
    description = "Verifica a pressoflessione (NTC2018 SLU / RD2229 TA)."
    norms = ["NTC2018", "DM96", "RD2229"]

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        norm = normative.get("norm_code", "NTC2018")

        b = _get_float(element, "width_cm", _get_float(element, "b", 30.0))
        h = _get_float(element, "height_cm", _get_float(element, "h", 50.0))
        d = _get_float(element, "d", h - 4.0)
        As = _get_float(element, "As", 0.0)
        N_Ed = _get_float(element, "N", _get_float(element, "N_Ed", 0.0))
        M_Ed = abs(_get_float(element, "Mx", _get_float(element, "M_Ed", 0.0)))

        partials: dict[str, Any] = {
            "b_cm": b,
            "h_cm": h,
            "d_cm": d,
            "N_Ed_kg": round(N_Ed, 1),
            "M_Ed_kgm": round(M_Ed, 1),
        }

        if norm == "RD2229":
            return self._run_ta(b, h, N_Ed, M_Ed, normative, partials)
        return self._run_slu(b, h, d, As, N_Ed, M_Ed, normative, partials)

    def _run_slu(
        self,
        b: float,
        h: float,
        d: float,
        As: float,
        N_Ed: float,
        M_Ed: float,
        normative: dict,
        partials: dict,
    ) -> dict[str, Any]:
        f_cd = _material_param(normative, "f_cd", 141.7)
        f_yd = _material_param(normative, "f_yd", 3904.0)

        N_Rd = 0.8 * b * h * f_cd + As * f_yd if As > 0 else 0.8 * b * h * f_cd
        if As > 0 and d > 0:
            x = As * f_yd / (0.8 * b * f_cd)
            M_Rd = As * f_yd * (d - 0.4 * x) / 100.0
        else:
            M_Rd = 0.0

        ratio_N = abs(N_Ed) / N_Rd if N_Rd > 0 else 0.0
        ratio_M = M_Ed / M_Rd if M_Rd > 0 else 0.0
        utilization = ratio_N + ratio_M
        ok = utilization <= 1.0

        partials.update(
            {
                "N_Rd_kg": round(N_Rd, 1),
                "M_Rd_kgm": round(M_Rd, 1),
                "ratio_N": round(ratio_N, 3),
                "ratio_M": round(ratio_M, 3),
                "utilization": round(utilization, 3),
            }
        )

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"N/N_Rd + M/M_Rd = {ratio_N:.3f} + {ratio_M:.3f} = "
                f"{utilization:.3f} {'≤' if ok else '>'} 1.0",
            ],
            "partials": partials,
        }

    def _run_ta(
        self,
        b: float,
        h: float,
        N_Ed: float,
        M_Ed: float,
        normative: dict,
        partials: dict,
    ) -> dict[str, Any]:
        sigma_c_adm = _material_param(normative, "sigma_c_adm", 60.0)

        A = b * h
        W = b * h**2 / 6.0

        sigma_N = N_Ed / A if A > 0 else 0.0
        sigma_M = M_Ed * 100.0 / W if W > 0 else 0.0
        sigma_max = sigma_N + sigma_M

        ok = sigma_max <= sigma_c_adm

        partials.update(
            {
                "sigma_N": round(sigma_N, 2),
                "sigma_M": round(sigma_M, 2),
                "sigma_max": round(sigma_max, 2),
                "sigma_c_adm": round(sigma_c_adm, 1),
            }
        )

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"σ = N/A + M/W = {sigma_N:.2f} + {sigma_M:.2f} = {sigma_max:.2f} "
                f"≤ {sigma_c_adm:.1f} kg/cm²: {'OK' if ok else 'NON VERIFICATO'}",
            ],
            "partials": partials,
        }


# ===========================================================================
# TorsionCheck
# ===========================================================================


class TorsionCheck(VerificationAction):
    """Verifica a torsione — NTC2018 SLU §4.1.2.4.

    T_Rd,max = 2 × ν × f_cd × A_k × t_ef (con θ=45°)
    Verifica: T_Ed ≤ T_Rd,max
    """

    action_id = "torsion_check"
    description = "Verifica a torsione (NTC2018 SLU)."
    norms = ["NTC2018", "DM96"]

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        b = _get_float(element, "width_cm", _get_float(element, "b", 30.0))
        h = _get_float(element, "height_cm", _get_float(element, "h", 50.0))
        T_Ed = abs(_get_float(element, "Mz", _get_float(element, "T_Ed", 0.0)))
        f_cd = _material_param(normative, "f_cd", 141.7)

        t_ef = min(b, h) / 6.0
        A_k = max((b - t_ef) * (h - t_ef), 1.0)

        nu = 0.5
        T_Rd_max = 2.0 * nu * f_cd * A_k * t_ef / 100.0

        utilization = T_Ed / T_Rd_max if T_Rd_max > 0 else float("inf")
        ok = utilization <= 1.0

        partials = {
            "b_cm": b,
            "h_cm": h,
            "t_ef_cm": round(t_ef, 2),
            "A_k_cm2": round(A_k, 1),
            "T_Ed_kgm": round(T_Ed, 1),
            "T_Rd_max_kgm": round(T_Rd_max, 1),
            "utilization": round(utilization, 3),
        }

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"T_Ed = {T_Ed:.1f} kg·m, T_Rd,max = {T_Rd_max:.1f} kg·m, "
                f"utilizzazione = {utilization:.3f}",
            ],
            "partials": partials,
        }


# ===========================================================================
# SLEStressCheck — Tensioni in esercizio
# ===========================================================================


class SLEStressCheck(VerificationAction):
    """Verifica tensioni in esercizio — NTC2018 SLE §4.1.2.5.

    σ_c ≤ 0.60 × f_ck (combinazione caratteristica)
    σ_s ≤ 0.80 × f_yk
    """

    action_id = "sle_stress_check"
    description = "Verifica tensioni in esercizio (NTC2018 SLE)."
    norms = ["NTC2018"]

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        b = _get_float(element, "width_cm", _get_float(element, "b", 30.0))
        h = _get_float(element, "height_cm", _get_float(element, "h", 50.0))
        d = _get_float(element, "d", h - 4.0)
        As = _get_float(element, "As", 0.0)
        M_sle = abs(_get_float(element, "M_sle", _get_float(element, "Mx", 0.0)))

        f_ck = _material_param(normative, "f_ck", 254.9)
        f_yk = _material_param(normative, "f_yk", 4589.0)
        E_c = _material_param(normative, "E_cm", 300000.0)
        E_s = _material_param(normative, "E_s", 2100000.0)
        n_ae = E_s / E_c if E_c > 0 else 15.0

        if As > 0 and b > 0 and d > 0:
            delta = (n_ae * As) ** 2 + 2 * b * n_ae * As * d
            x_n = (-n_ae * As + math.sqrt(max(delta, 0))) / b
            J_r = b * x_n**3 / 3.0 + n_ae * As * (d - x_n) ** 2
        else:
            x_n = h / 2.0
            J_r = b * h**3 / 12.0

        sigma_c = M_sle * 100.0 * x_n / J_r if J_r > 0 else 0.0
        sigma_s = n_ae * M_sle * 100.0 * (d - x_n) / J_r if J_r > 0 else 0.0

        lim_c = 0.60 * f_ck
        lim_s = 0.80 * f_yk

        ok_c = sigma_c <= lim_c
        ok_s = sigma_s <= lim_s
        ok = ok_c and ok_s

        partials = {
            "x_n_cm": round(x_n, 2),
            "J_r_cm4": round(J_r, 1),
            "sigma_c": round(sigma_c, 1),
            "lim_c": round(lim_c, 1),
            "sigma_s": round(sigma_s, 1),
            "lim_s": round(lim_s, 1),
            "n_ae": round(n_ae, 2),
        }

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"σ_c = {sigma_c:.1f} ≤ {lim_c:.1f} kg/cm²: {'OK' if ok_c else 'NON VERIFICATO'}",
                f"σ_s = {sigma_s:.1f} ≤ {lim_s:.1f} kg/cm²: {'OK' if ok_s else 'NON VERIFICATO'}",
            ],
            "partials": partials,
        }


# ===========================================================================
# SLECrackingCheck — Verifica fessurazione
# ===========================================================================


class SLECrackingCheck(VerificationAction):
    """Verifica fessurazione — NTC2018 SLE §4.1.2.5.2.

    w_k = s_r,max × (ε_sm - ε_cm)
    Verifica: w_k ≤ w_lim (tipicamente 0.3 mm o 0.4 mm)
    """

    action_id = "sle_cracking_check"
    description = "Verifica fessurazione (NTC2018 SLE)."
    norms = ["NTC2018"]

    def run(
        self, element: Any, normative: dict[str, Any], settings: dict[str, Any]
    ) -> dict[str, Any]:
        b = _get_float(element, "width_cm", 30.0)
        h = _get_float(element, "height_cm", 50.0)
        d = _get_float(element, "d", h - 4.0)
        As = _get_float(element, "As", 0.0)
        M_sle = abs(_get_float(element, "M_sle", _get_float(element, "Mx", 0.0)))
        copriferro = _get_float(element, "cover_cm", 3.0)
        diam_barre = _get_float(element, "diam_barre_mm", 16.0) / 10.0

        f_ctm = _material_param(normative, "f_ctm", 25.0)
        E_s = _material_param(normative, "E_s", 2100000.0)
        E_c = _material_param(normative, "E_cm", 300000.0)
        n_ae = E_s / E_c if E_c > 0 else 15.0
        w_lim = float(settings.get("w_lim_mm", 0.3))

        z = 0.9 * d
        sigma_s = M_sle * 100.0 / (As * z) if As * z > 0 else 0.0

        h_c_eff = min(2.5 * (h - d), h / 2.0)
        rho_p = As / (b * h_c_eff) if b * h_c_eff > 0 else 0.01
        k1 = 0.8
        k2 = 0.5
        s_r_max_cm = 3.4 * copriferro + 0.425 * k1 * k2 * diam_barre / max(rho_p, 0.001)

        kt = 0.6
        eps_term1 = (
            (sigma_s - kt * f_ctm / max(rho_p, 0.001) * (1 + n_ae * rho_p)) / E_s
            if E_s > 0
            else 0.0
        )
        eps_term2 = 0.6 * sigma_s / E_s if E_s > 0 else 0.0
        eps_diff = max(eps_term1, eps_term2)

        w_k_cm = s_r_max_cm * eps_diff
        w_k_mm = w_k_cm * 10.0

        ok = w_k_mm <= w_lim

        partials = {
            "sigma_s": round(sigma_s, 1),
            "s_r_max_cm": round(s_r_max_cm, 2),
            "w_k_mm": round(w_k_mm, 3),
            "w_lim_mm": w_lim,
        }

        return {
            "action_id": self.action_id,
            "ok": ok,
            "messages": [
                f"w_k = {w_k_mm:.3f} mm ≤ {w_lim:.1f} mm: {'OK' if ok else 'NON VERIFICATO'}",
            ],
            "partials": partials,
        }


# ===========================================================================
# Registrazione automatica
# ===========================================================================

register_action(FlexureCheck())
register_action(ShearCheck())
register_action(PressFlexureCheck())
register_action(TorsionCheck())
register_action(SLEStressCheck())
register_action(SLECrackingCheck())
