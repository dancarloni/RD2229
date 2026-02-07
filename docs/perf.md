# Performance notes

This document describes how to profile and improve performance for the core
calculus.

- Quick profile: `python tools/profile_calculus.py` (prints top 20 cumulative functions).
- For flamegraphs: run `python -m pyinstrument tools/profile_calculus.py` or use `snakeviz` on generated profile files.
- Caching: `src/core_calculus/geometry_cache.py` provides LRU caching for geometry invariants.
- Background execution: UI uses `src/utils/background.py` to run heavy calculations in a thread pool and update the UI via `tk_root.after` to keep the main loop responsive.
