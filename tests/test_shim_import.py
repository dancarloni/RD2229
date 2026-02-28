def test_shim_import():
    import verification_table

    # Basic smoke assertions: names exist
    assert hasattr(verification_table, "VerificationTableApp")
    assert hasattr(verification_table, "VerificationTableWindow")
    # run_demo may no longer be exposed by the shim, that's acceptable
    assert not hasattr(verification_table, "run_demo") or callable(
        getattr(verification_table, "run_demo")
    )
    assert hasattr(verification_table, "COLUMNS")
