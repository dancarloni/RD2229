import json
from pathlib import Path

from src.methods.ta import TangentialAreaMethod


def test_golden_rd2229():
    p = Path(__file__).parent / "golden_rd2229.json"
    data = json.loads(p.read_text())
    method = TangentialAreaMethod()
    for item in data:
        res = method.compute(item["inputs"])
        # Sanity check: NA_depth should be a finite positive number within reasonable bounds
        na = res.get("NA_depth", None)
        assert na is not None
        assert na > 0
        assert na < 1e6  # sanity upper bound
