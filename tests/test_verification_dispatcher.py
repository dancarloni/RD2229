from verification_table import VerificationInput, VerificationOutput, compute_verification_result


def test_dispatcher_uses_engine_result(monkeypatch):
    inp = VerificationInput()

    sentinel = VerificationOutput(
        sigma_c_max=1.0,
        sigma_c_min=0.0,
        sigma_s_max=0.0,
        asse_neutro=0.0,
    )

    monkeypatch.setattr("verification_table._compute_with_engine", lambda *_: sentinel)

    out = compute_verification_result(inp, None, None)
    assert out is sentinel


def test_dispatcher_falls_back_when_engine_none(monkeypatch):
    inp = VerificationInput(verification_method="TA")

    monkeypatch.setattr("verification_table._compute_with_engine", lambda *_: None)

    # ensure compute_ta_verification is invoked by checking for a valid VerificationOutput
    out = compute_verification_result(inp, None, None)
    assert isinstance(out, VerificationOutput)
    # TA implementation returns esito in {'VERIFICATO','NON VERIFICATO'} or 'ERRORE'
    assert out.esito in ("VERIFICATO", "NON VERIFICATO", "ERRORE")
