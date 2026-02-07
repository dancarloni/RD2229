"""Profile core calculus with cProfile and print a short summary."""

from __future__ import annotations

import cProfile
import pstats
from io import StringIO

from src.core_calculus.geometry_cache import section_inertia


def workload():
    # Small synthetic workload that repeatedly computes section inertia
    for w in [0.1, 0.2, 0.3, 0.4, 0.5]:
        for h in [0.1, 0.2, 0.5, 1.0]:
            for t in [0.0, 0.01, 0.02]:
                _ = section_inertia(w, h, thickness=t)


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    workload()
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())
