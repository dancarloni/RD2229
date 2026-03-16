from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StopCriteria:
    stop_on_capacity: bool = True
    stop_on_drift: bool = True
    stop_on_ductility: bool = True

    def at_least_one_enabled(self) -> bool:
        return self.stop_on_capacity or self.stop_on_drift or self.stop_on_ductility


@dataclass(frozen=True)
class PushoverSettings:
    methods: tuple[str, ...] = ("bilineare", "trilineare", "numerico")
    drift_y: float = 0.002
    drift_u: float = 0.010
    ductility_max: float = 5.0
    ductility_min: float = 1.8
    drift_limit: float = 0.005
    post_yield_stiffness_ratio: float = 0.10
    n_steps_numerical: int = 20
    tau_base_kgf_cm2: float = 6.0
    strength_gain_coeff: float = 0.35
    stop_criteria: StopCriteria = StopCriteria()


@dataclass(frozen=True)
class PerformanceLevel:
    name: str
    drift_limit: float
    demand_factor: float


def build_seismic_combinations(
    gk_kgf: float,
    qk_kgf: float,
    ag_over_g: float,
    q_factor: float,
    levels: tuple[PerformanceLevel, ...],
) -> dict[str, Any]:
    """Build simplified seismic demands per performance level.

    The formulation is intentionally conservative and transparent:
    Fh = (Gk + 0.3*Qk) * (ag/g) * q * demand_factor
    """
    base_mass_proxy = max(gk_kgf + (0.3 * max(qk_kgf, 0.0)), 0.0)
    base_coeff = max(ag_over_g, 0.0) * max(q_factor, 0.1)
    out: dict[str, Any] = {}
    for lvl in levels:
        demand = base_mass_proxy * base_coeff * max(lvl.demand_factor, 0.0)
        out[lvl.name] = {
            "drift_limit": round(lvl.drift_limit, 6),
            "demand_factor": round(lvl.demand_factor, 6),
            "demand_kgf": round(demand, 6),
        }
    return {
        "base_mass_proxy_kgf": round(base_mass_proxy, 6),
        "base_coeff": round(base_coeff, 6),
        "levels": out,
    }


def evaluate_performance_levels(
    pushover_result: dict[str, Any],
    combinations: dict[str, Any],
) -> dict[str, Any]:
    levels = combinations.get("levels", {})
    methods = pushover_result.get("results", {})
    out: dict[str, Any] = {}
    for lvl_name, lvl_data in levels.items():
        drift_limit = float(lvl_data.get("drift_limit", 0.0))
        demand = float(lvl_data.get("demand_kgf", 0.0))
        method_eval: dict[str, Any] = {}
        for method_name, result in methods.items():
            fu = float(result.get("Fu_kgf", 0.0))
            drift_u = float(result.get("drift_u", 0.0))
            cap_ratio = fu / max(demand, 1e-9)
            drift_ok = drift_u <= drift_limit if drift_limit > 0.0 else True
            method_eval[method_name] = {
                "capacity_ratio": round(cap_ratio, 6),
                "drift_u": round(drift_u, 6),
                "drift_limit": round(drift_limit, 6),
                "capacity_ok": cap_ratio >= 1.0,
                "drift_ok": drift_ok,
                "ok": (cap_ratio >= 1.0) and drift_ok,
            }
        out[lvl_name] = method_eval
    return out


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def _trapz(points: list[tuple[float, float]]) -> float:
    if len(points) < 2:
        return 0.0
    area = 0.0
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        area += ((y0 + y1) * 0.5) * (x1 - x0)
    return area


def _capacity_proxy(
    lunghezza_cm: float,
    spessore_cm: float,
    alpha_ap: float,
    ratio_delta_ei: float,
    settings: PushoverSettings,
) -> float:
    area_res_cm2 = max(lunghezza_cm * spessore_cm, 0.0)
    base = settings.tau_base_kgf_cm2 * area_res_cm2
    reduction = 1.0 - (0.8 * _clamp(alpha_ap, 0.0, 0.95))
    increase = 1.0 + max(ratio_delta_ei, 0.0) * settings.strength_gain_coeff
    return max(base * reduction * increase, 0.0)


def _initial_stiffness(ei_kgf_cm2: float, h_cm: float) -> float:
    denom = max(h_cm**3, 1e-9)
    return max(ei_kgf_cm2 / denom, 1e-9)


def _build_bilinear(
    stiffness: float,
    capacity: float,
    h_cm: float,
    settings: PushoverSettings,
) -> dict[str, Any]:
    dy = max(settings.drift_y * h_cm, 1e-6)
    fy = min(stiffness * dy, 0.85 * capacity)
    du = max(settings.drift_u * h_cm, settings.ductility_max * dy)
    fu = max(capacity, fy)
    points = [(0.0, 0.0), (dy, fy), (du, fu)]
    return {
        "method": "bilineare",
        "curve": [{"u_cm": round(u, 6), "F_kgf": round(f, 6)} for u, f in points],
        "K0_kgf_cm": round(fy / dy, 6),
        "Fy_kgf": round(fy, 6),
        "Fu_kgf": round(fu, 6),
        "dy_cm": round(dy, 6),
        "du_cm": round(du, 6),
        "mu": round(du / dy, 6),
        "energia_kgf_cm": round(_trapz(points), 6),
        "drift_u": round(du / max(h_cm, 1e-9), 6),
    }


def _build_trilinear(
    stiffness: float,
    capacity: float,
    h_cm: float,
    settings: PushoverSettings,
) -> dict[str, Any]:
    dy = max(settings.drift_y * h_cm, 1e-6)
    fy = min(stiffness * dy, 0.80 * capacity)
    dcr = 0.45 * dy
    fcr = min(stiffness * dcr, 0.45 * fy)
    du = max(settings.drift_u * h_cm, settings.ductility_max * dy)
    fu = max(capacity, fy)
    dp = 0.70 * du
    fp = min(fu, fy + (du - dy) * stiffness * settings.post_yield_stiffness_ratio)
    points = [(0.0, 0.0), (dcr, fcr), (dy, fy), (dp, fp), (du, fu)]
    return {
        "method": "trilineare",
        "curve": [{"u_cm": round(u, 6), "F_kgf": round(f, 6)} for u, f in points],
        "K0_kgf_cm": round(fcr / max(dcr, 1e-9), 6),
        "Fy_kgf": round(fy, 6),
        "Fu_kgf": round(fu, 6),
        "dy_cm": round(dy, 6),
        "du_cm": round(du, 6),
        "mu": round(du / dy, 6),
        "energia_kgf_cm": round(_trapz(points), 6),
        "drift_u": round(du / max(h_cm, 1e-9), 6),
    }


def _build_numerical(
    stiffness: float,
    capacity: float,
    h_cm: float,
    settings: PushoverSettings,
) -> dict[str, Any]:
    dy = max(settings.drift_y * h_cm, 1e-6)
    du = max(settings.drift_u * h_cm, settings.ductility_max * dy)
    n_steps = int(_clamp(float(settings.n_steps_numerical), 5.0, 200.0))
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    for i in range(1, n_steps + 1):
        u = (du / n_steps) * i
        if u <= dy:
            force = stiffness * u
        else:
            hardening = stiffness * settings.post_yield_stiffness_ratio * (u - dy)
            force = min((stiffness * dy) + hardening, capacity)
        points.append((u, max(force, 0.0)))

    fy = stiffness * dy
    fu = max(f for _, f in points)
    return {
        "method": "numerico",
        "curve": [{"u_cm": round(u, 6), "F_kgf": round(f, 6)} for u, f in points],
        "K0_kgf_cm": round(stiffness, 6),
        "Fy_kgf": round(fy, 6),
        "Fu_kgf": round(fu, 6),
        "dy_cm": round(dy, 6),
        "du_cm": round(du, 6),
        "mu": round(du / dy, 6),
        "energia_kgf_cm": round(_trapz(points), 6),
        "drift_u": round(du / max(h_cm, 1e-9), 6),
    }


def _evaluate_stop_flags(
    result: dict[str, Any],
    settings: PushoverSettings,
) -> dict[str, bool]:
    flags = {
        "capacity_reached": result["Fu_kgf"] >= result["Fy_kgf"],
        "drift_limit_reached": result["drift_u"] >= settings.drift_limit,
        "ductility_limit_reached": result["mu"] >= settings.ductility_max,
    }
    return flags


def run_pushover_methods(
    *,
    ei_kgf_cm2: float,
    h_cm: float,
    lunghezza_cm: float,
    spessore_cm: float,
    alpha_ap: float,
    ratio_delta_ei: float,
    settings: PushoverSettings,
) -> dict[str, Any]:
    methods = tuple(dict.fromkeys(settings.methods))
    stiffness = _initial_stiffness(ei_kgf_cm2, h_cm)
    capacity = _capacity_proxy(
        lunghezza_cm=lunghezza_cm,
        spessore_cm=spessore_cm,
        alpha_ap=alpha_ap,
        ratio_delta_ei=ratio_delta_ei,
        settings=settings,
    )

    builders = {
        "bilineare": _build_bilinear,
        "trilineare": _build_trilinear,
        "numerico": _build_numerical,
    }

    outputs: dict[str, Any] = {}
    for name in methods:
        builder = builders.get(name)
        if builder is None:
            continue
        result = builder(stiffness, capacity, h_cm, settings)
        result["stop_flags"] = _evaluate_stop_flags(result, settings)
        outputs[name] = result

    return {
        "stiffness_kgf_cm": round(stiffness, 6),
        "capacity_kgf": round(capacity, 6),
        "results": outputs,
    }


def compare_ante_post(
    ante: dict[str, Any],
    post: dict[str, Any],
) -> dict[str, Any]:
    by_method: dict[str, Any] = {}
    methods = set(ante.get("results", {}).keys()) & set(post.get("results", {}).keys())
    for method in methods:
        a = ante["results"][method]
        p = post["results"][method]
        k_ratio = p["K0_kgf_cm"] / max(a["K0_kgf_cm"], 1e-9)
        fu_ratio = p["Fu_kgf"] / max(a["Fu_kgf"], 1e-9)
        mu_ratio = p["mu"] / max(a["mu"], 1e-9)
        en_ratio = p["energia_kgf_cm"] / max(a["energia_kgf_cm"], 1e-9)
        by_method[method] = {
            "ratio_K0": round(k_ratio, 6),
            "ratio_Fu": round(fu_ratio, 6),
            "ratio_mu": round(mu_ratio, 6),
            "ratio_energia": round(en_ratio, 6),
        }
    return {"by_method": by_method}
