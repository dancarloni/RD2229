from gui.section_gui import plot_section
from core.geometry import RectangularSection

s = RectangularSection(width=20.0, height=30.0)
fig, ax = plot_section(s, title='Test Rect', show=False)
print('OK', hasattr(fig, 'canvas'))
