from src.methods.ntc2018.models import Apertura, PareteMuraria, Rinforzo


def test_parete_serialization():
    p = PareteMuraria(id="p1", lunghezza=400.0, altezza=300.0, spessore=30.0)
    d = p.to_dict()
    assert d["id"] == "p1"
    assert d["lunghezza"] == 400.0


def test_apertura_area():
    a = Apertura(id="a1", dimensioni={"h": 100.0, "b": 80.0})
    assert a.area() == 8000.0


def test_rinforzo_fields():
    r = Rinforzo(id="r1", tipo="FRP", efficacia=0.25)
    assert r.tipo == "FRP"
    assert r.efficacia == 0.25
