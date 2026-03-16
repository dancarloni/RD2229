from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from .models import Apertura, PareteMuraria, Rinforzo


def inertia_wall_about_horizontal_axis(p: PareteMuraria) -> float:
    """Moment of inertia for rectangular wall cross-section about horizontal axis.

    Uses I = b*h^3/12 where b = spessore (cm), h = altezza (cm).
    Units: cm^4 (multiplied by E [kgf/cm^2] gives kgf*cm^2 as EI proxy used internally).
    """
    b = p.spessore
    h = p.altezza
    return (b * (h**3)) / 12.0


def compute_EI_ante(p: PareteMuraria) -> float:
    I = inertia_wall_about_horizontal_axis(p)
    return p.E * I


def alpha_from_area_ratio(area_ap: float, area_panel: float) -> float:
    """Baseline mapping from area ratio to alpha_ap (conservativa di partenza).

    - <10% -> 0.05
    - 10-25% -> 0.20
    - 25-50% -> 0.40
    - >50% -> 0.80
    """
    if area_panel <= 0:
        return 0.0
    r = area_ap / area_panel
    if r < 0.10:
        return 0.05
    if r < 0.25:
        return 0.20
    if r < 0.50:
        return 0.40
    return 0.80


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def opening_position_factor(apertura: Apertura, parete: PareteMuraria) -> float:
    """Factor >= 1 based on opening critical position in the wall panel."""
    dims = apertura.normalized_dimensions()
    b = max(dims["b"], 0.0)
    h = max(dims["h"], 0.0)
    x = float(apertura.posizione.get("x", 0.0))
    y = float(apertura.posizione.get("y", 0.0))

    left = x
    right = max(parete.lunghezza - (x + b), 0.0)
    top = max(parete.altezza - (y + h), 0.0)

    side_ratio = min(left, right) / parete.lunghezza if parete.lunghezza > 0 else 1.0
    top_ratio = top / parete.altezza if parete.altezza > 0 else 1.0

    side_factor = 1.25 if side_ratio < 0.12 else 1.0
    top_factor = 1.20 if top_ratio < 0.15 else 1.0
    return side_factor * top_factor


def aggregate_opening_alpha(
    parete: PareteMuraria, aperture: Optional[Iterable[Apertura]] = None
) -> float:
    """Global alpha from active openings, weighted by area and position."""
    a_list = list(aperture) if aperture is not None else parete.aperture_attive()
    area_panel = parete.area()
    if area_panel <= 0.0 or not a_list:
        return 0.0

    weighted_alpha = 0.0
    for a in a_list:
        if not a.is_attiva():
            continue
        a_area = a.area()
        base = alpha_from_area_ratio(a_area, area_panel)
        pos_f = opening_position_factor(a, parete)
        weighted_alpha += base * (a_area / area_panel) * pos_f * 4.0

    return _clamp(weighted_alpha, 0.0, 0.95)


def compute_EI_post_alpha(p: PareteMuraria, alpha_ap: float) -> float:
    """Compute post-intervention EI applying simple reduction factor alpha_ap.

    This is a placeholder; norm-driven methods (aree equivalenti / telaio equivalente)
    will replace this with more accurate estimations.
    """
    EI0 = compute_EI_ante(p)
    return EI0 * (1.0 - float(alpha_ap))


def compute_EI_post_openings(
    parete: PareteMuraria,
    aperture: Optional[Iterable[Apertura]] = None,
) -> Dict[str, float]:
    """Compute EI post openings and return detailed factors."""
    a_list = list(aperture) if aperture is not None else parete.aperture_attive()
    area_panel = parete.area()
    area_open = sum(a.area() for a in a_list if a.is_attiva())
    alpha = aggregate_opening_alpha(parete, a_list)
    EI0 = compute_EI_ante(parete)
    EI_post = compute_EI_post_alpha(parete, alpha)
    return {
        "EI_ante": EI0,
        "EI_post_aperture": EI_post,
        "alpha_ap": alpha,
        "rapporto_aperture": (area_open / area_panel) if area_panel > 0 else 0.0,
    }


class ReinforcementPluginBase:
    """Base class for reinforcement plugins.

    Plugins must implement `rigidezza_aggiunta(parete, rinforzo)` returning delta_EI (float).
    """

    def rigidezza_aggiunta(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float:
        raise NotImplementedError()


class SimpleFRPPlugin(ReinforcementPluginBase):
    """Example simple FRP plugin: increases EI by a fraction of EI_local.

    Uses `rinforzo.efficacia` as fraction of EI added to the local portion.
    """

    def rigidezza_aggiunta(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float:
        EI0 = compute_EI_ante(parete)
        eff = rinforzo.efficacia or 0.0
        return EI0 * float(eff)


class IntonacoArmatoPlugin(ReinforcementPluginBase):
    def rigidezza_aggiunta(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float:
        EI0 = compute_EI_ante(parete)
        eff = rinforzo.efficacia if rinforzo.efficacia is not None else 0.08
        return EI0 * float(eff)


class BetoncinoArmatoPlugin(ReinforcementPluginBase):
    def rigidezza_aggiunta(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float:
        EI0 = compute_EI_ante(parete)
        eff = rinforzo.efficacia if rinforzo.efficacia is not None else 0.12
        return EI0 * float(eff)


class CerchiaturaPlugin(ReinforcementPluginBase):
    def rigidezza_aggiunta(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float:
        EI0 = compute_EI_ante(parete)
        eff = rinforzo.efficacia if rinforzo.efficacia is not None else 0.15
        return EI0 * float(eff)


@dataclass
class ReinforcementRegistry:
    plugins: Dict[str, ReinforcementPluginBase]

    @classmethod
    def default(cls) -> "ReinforcementRegistry":
        return cls(
            plugins={
                "FRP": SimpleFRPPlugin(),
                "intonaco_armato": IntonacoArmatoPlugin(),
                "betoncino_armato": BetoncinoArmatoPlugin(),
                "cerchiatura": CerchiaturaPlugin(),
                "inserto_metallico": CerchiaturaPlugin(),
            }
        )

    def register(self, rinforzo_tipo: str, plugin: ReinforcementPluginBase) -> None:
        self.plugins[rinforzo_tipo] = plugin

    def delta_ei(self, parete: PareteMuraria, rinforzo: Rinforzo) -> float:
        plugin = self.plugins.get(rinforzo.tipo)
        if plugin is None:
            return 0.0
        return max(plugin.rigidezza_aggiunta(parete, rinforzo), 0.0)


def compute_EI_post_with_reinforcements(
    parete: PareteMuraria,
    aperture: Optional[Iterable[Apertura]] = None,
    rinforzi: Optional[Iterable[Rinforzo]] = None,
    registry: Optional[ReinforcementRegistry] = None,
) -> Dict[str, float]:
    """Evaluate EI before/after openings and after reinforcements."""
    base = compute_EI_post_openings(parete, aperture)
    regs = registry or ReinforcementRegistry.default()
    r_list = list(rinforzi) if rinforzi is not None else parete.rinforzi

    delta_tot = 0.0
    for r in r_list:
        delta_tot += regs.delta_ei(parete, r)

    EI_post = base["EI_post_aperture"] + delta_tot
    EI_ante = base["EI_ante"]
    ratio_post_ante = EI_post / EI_ante if EI_ante > 0 else 0.0

    return {
        "EI_ante": EI_ante,
        "EI_post_aperture": base["EI_post_aperture"],
        "EI_post_rinforzo": EI_post,
        "delta_EI_rinforzi": delta_tot,
        "alpha_ap": base["alpha_ap"],
        "rapporto_aperture": base["rapporto_aperture"],
        "ratio_post_ante": ratio_post_ante,
    }


def compute_modifica_aperture(
    aperture_esistenti: Iterable[Apertura],
    aperture_modificate: Iterable[Apertura],
) -> list[Apertura]:
    """Merge openings by id: modified openings replace existing ones."""
    merged = {a.id: a for a in aperture_esistenti}
    for a in aperture_modificate:
        merged[a.id] = a
    return list(merged.values())
