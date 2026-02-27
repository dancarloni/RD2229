from src.codes.ntc2018 import spectrum_paste_service as svc


def test_parse_decimal_point():
    raw = "Operatività 0.5 0.25 0.3 0.4"
    rows, msgs, qual = svc.parse_edilus_ms_table(raw)
    # only one of four labels supplied -> missing others yields WARNING
    assert qual == "WARNING"
    assert len(rows) == 1
    assert abs(rows[0].tr_years - 0.5) < 1e-6


def test_parse_decimal_comma():
    raw = "Danno 1,0 0,1 0,2 0,3"
    rows, msgs, qual = svc.parse_edilus_ms_table(raw)
    # one row only -> quality WARNING due to missing labels
    assert qual == "WARNING"
    assert len(rows) == 1
    assert abs(rows[0].ag_g - 0.1) < 1e-6


def test_missing_rows_warning():
    raw = "Operatività 0.5 0.25 0.3 0.4\n"  # only one of four labels present
    rows, msgs, qual = svc.parse_edilus_ms_table(raw)
    assert len(rows) == 1
    assert qual == "WARNING"
    assert any("mancante" in m for m in msgs)


def test_invalid_token_error():
    raw = "Salvaguardia Vita 0.5 A B C"
    rows, msgs, qual = svc.parse_edilus_ms_table(raw)
    assert len(rows) == 0
    assert qual == "ERROR"
    assert any("manca valori" in m for m in msgs)
