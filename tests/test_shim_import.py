def test_shim_import():
    import verification_table

    # Basic smoke assertions: names exist
    assert hasattr(verification_table, "VerificationTableApp")
    assert hasattr(verification_table, "VerificationTableWindow")
    # ``run_demo`` may or may not be present; if it exists it should be
    # callable.  avoid calling ``getattr`` without a default because the shim
    # can raise an AttributeError when the legacy module is loaded and doesn't
    # provide the name.
    if hasattr(verification_table, "run_demo"):
        assert callable(verification_table.run_demo)
    assert hasattr(verification_table, "COLUMNS")
