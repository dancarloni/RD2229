def test_plot_section_smoke():
    # import RectangularSection from wherever it's available; skip if not
    try:
        from core.geometry import RectangularSection
    except ImportError:
        try:
            from src.core.geometry import RectangularSection
        except ImportError:
            import pytest

            pytest.skip("core.geometry not importable")

    from gui.section_gui import plot_section

    s = RectangularSection(width=20.0, height=30.0)
    fig_ax = plot_section(s, title="test", show=False)
    assert isinstance(fig_ax, tuple) and len(fig_ax) == 2
