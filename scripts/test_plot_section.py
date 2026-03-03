from core.geometry import RectangularSection
from gui.section_gui import plot_section

s = RectangularSection(width=20.0, height=30.0)
fig, ax = plot_section(s, title="Test Rect", show=False)
print("OK", hasattr(fig, "canvas"))
