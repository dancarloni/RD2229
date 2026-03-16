from src.methods.ntc2018.models import Apertura, PareteMuraria, Rinforzo
from src.methods.ntc2018.x5_core import (
    BetoncinoArmatoPlugin,
    CerchiaturaPlugin,
    IntonacoArmatoPlugin,
    ReinforcementRegistry,
    SimpleFRPPlugin,
    aggregate_opening_alpha,
    alpha_from_area_ratio,
    compute_EI_ante,
    compute_EI_post_alpha,
    compute_EI_post_with_reinforcements,
    compute_modifica_aperture,
    inertia_wall_about_horizontal_axis,
    opening_position_factor,
)


def test_inertia_and_EI():
    p = PareteMuraria(id="p1", lunghezza=400.0, altezza=300.0, spessore=30.0, E=200000.0)
    I = inertia_wall_about_horizontal_axis(p)
    assert I > 0
    EI = compute_EI_ante(p)
    assert EI == p.E * I


def test_alpha_map_and_EI_post():
    p = PareteMuraria(id="p2", lunghezza=400.0, altezza=300.0, spessore=30.0, E=200000.0)
    area_panel = p.area()
    area_ap = 0.05 * area_panel
    alpha = alpha_from_area_ratio(area_ap, area_panel)
    assert alpha == 0.05
    EI0 = compute_EI_ante(p)
    EI_post = compute_EI_post_alpha(p, alpha)
    assert EI_post == EI0 * (1.0 - alpha)


def test_frp_plugin_adds_rigidezza():
    p = PareteMuraria(id="p3", lunghezza=400.0, altezza=300.0, spessore=30.0, E=200000.0)
    r = Rinforzo(id="r1", tipo="FRP", efficacia=0.1)
    plugin = SimpleFRPPlugin()
    delta = plugin.rigidezza_aggiunta(p, r)
    assert delta == compute_EI_ante(p) * 0.1


def test_opening_position_factor_border_is_higher():
    p = PareteMuraria(id="p4", lunghezza=500.0, altezza=300.0, spessore=30.0, E=200000.0)
    a_c = Apertura(id="ac", posizione={"x": 200.0, "y": 100.0}, dimensioni={"h": 80.0, "b": 80.0})
    a_b = Apertura(id="ab", posizione={"x": 10.0, "y": 20.0}, dimensioni={"h": 80.0, "b": 80.0})
    assert opening_position_factor(a_b, p) > opening_position_factor(a_c, p)


def test_compute_EI_post_with_reinforcements():
    p = PareteMuraria(id="p5", lunghezza=500.0, altezza=300.0, spessore=30.0, E=200000.0)
    p.aperture = [
        Apertura(id="a1", posizione={"x": 100.0, "y": 80.0}, dimensioni={"h": 80.0, "b": 120.0})
    ]
    p.rinforzi = [Rinforzo(id="rf1", tipo="FRP", efficacia=0.10)]
    out = compute_EI_post_with_reinforcements(p)
    assert out["EI_ante"] > 0
    assert out["EI_post_rinforzo"] >= out["EI_post_aperture"]
    assert out["ratio_post_ante"] > 0


def test_registry_plugins_available():
    reg = ReinforcementRegistry.default()
    p = PareteMuraria(id="p6", lunghezza=500.0, altezza=300.0, spessore=30.0, E=200000.0)
    r1 = Rinforzo(id="i1", tipo="intonaco_armato")
    r2 = Rinforzo(id="b1", tipo="betoncino_armato")
    r3 = Rinforzo(id="c1", tipo="cerchiatura")
    assert reg.delta_ei(p, r1) > 0
    assert reg.delta_ei(p, r2) > 0
    assert reg.delta_ei(p, r3) > 0


def test_compute_modifica_aperture_replaces_same_id():
    old = [Apertura(id="A", posizione={"x": 10.0, "y": 10.0}, dimensioni={"h": 50.0, "b": 50.0})]
    new = [Apertura(id="A", posizione={"x": 20.0, "y": 10.0}, dimensioni={"h": 80.0, "b": 60.0})]
    merged = compute_modifica_aperture(old, new)
    assert len(merged) == 1
    assert merged[0].dimensioni["h"] == 80.0
