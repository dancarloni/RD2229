def test_shim_import():
    import verification_table

    # Basic smoke assertions: names exist and run_demo is callable
    assert hasattr(verification_table, "VerificationTableApp")
    assert hasattr(verification_table, "VerificationTableWindow")
    assert callable(getattr(verification_table, "run_demo"))
    assert hasattr(verification_table, "COLUMNS")
