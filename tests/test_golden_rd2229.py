import json
from pathlib import Path
from src.methods.ta import TangentialAreaMethod


def test_golden_rd2229():
    data = json.loads(Path(__file__).parent / "golden_rd2229.json" .read_text())
    method = TangentialAreaMethod()
    for item in data:
        res = method.compute(item["inputs"])
        # Compare NA_depth with tolerance (golden tolerance 1e-3)
        expected = item["expected"]["NA_depth"]
        assert abs(res.get("NA_depth", 0.0) - expected) < 1e-3
