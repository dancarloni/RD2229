def test_plot_section_smoke():
    from gui.section_gui import plot_section
    from core.geometry import RectangularSection

    s = RectangularSection(width=20.0, height=30.0)
    fig_ax = plot_section(s, title='test', show=False)
    assert isinstance(fig_ax, tuple) and len(fig_ax) == 2
