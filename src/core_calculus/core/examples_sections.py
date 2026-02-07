from .geometry import (
    CircularHollowSection,
    InvertedTSection,
    PiSection,
    RectangularHollowSection,
)
from .section_properties import compute_section_properties


def print_props(s):
    p = compute_section_properties(s)
    print(
        f"{s.__class__.__name__}: area={p.area:.2f}, "
        f"cx={p.centroid_x:.2f}, cy={p.centroid_y:.2f}, "
        f"Ix={p.ix:.2f}, Iy={p.iy:.2f}"
    )


if __name__ == "__main__":
    sec1 = InvertedTSection(
        flange_width=200.0, flange_thickness=20.0, web_thickness=10.0, web_height=160.0
    )
    sec2 = PiSection(width=200.0, top_thickness=20.0, leg_thickness=10.0, leg_height=160.0)
    sec3 = RectangularHollowSection(
        outer_width=200.0, outer_height=100.0, inner_width=160.0, inner_height=60.0
    )
    sec4 = CircularHollowSection(outer_diameter=100.0, inner_diameter=60.0)

    for s in (sec1, sec2, sec3, sec4):
        print_props(s)
