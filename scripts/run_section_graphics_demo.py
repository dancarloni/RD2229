"""Small demo script to show `SectionGraphicsController` usage.

Run with:
    python scripts/run_section_graphics_demo.py

If tkinter is unavailable the script exits with a message.
"""

try:
    import tkinter as tk
except Exception:
    print("Tkinter not available in this environment — demo skipped")
    raise SystemExit(0)

from apps.sections.section_graphics import SectionGraphicsController
from src.core_calculus.core.geometry_model import SectionGeometry
from src.core_calculus.section_calculations import compute_section_properties_from_geometry


def make_examples():
    examples = []
    examples.append(("Rect", SectionGeometry.from_rectangle(10.0, 20.0, name="rect")))
    outer = SectionGeometry.from_rectangle(12.0, 8.0, name="outer")
    hole = SectionGeometry.from_rectangle(4.0, 2.0, name="hole")
    outer.holes = [hole.exterior]
    examples.append(("With hole", outer))
    return examples


def main():
    root = tk.Tk()
    root.title("Section Graphics Demo")
    canvas = tk.Canvas(root, width=900, height=600, bg="white")
    canvas.pack(fill="both", expand=True)

    controller = SectionGraphicsController(canvas)
    examples = make_examples()

    current = 0

    def draw_current():
        canvas.delete("all")
        name, geom = examples[current]
        props = compute_section_properties_from_geometry(geom)
        controller.draw_all(geom, props)
        root.title(f"Section Graphics Demo — {name}")

    def next_example():
        nonlocal current
        current = (current + 1) % len(examples)
        draw_current()

    btn = tk.Button(root, text="Next Example", command=next_example)
    btn.pack(side="bottom")

    draw_current()
    root.mainloop()


if __name__ == "__main__":
    main()
