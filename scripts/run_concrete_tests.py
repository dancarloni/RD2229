"""Runner semplice per testare `concrete_strength` senza dipendenze esterne.

Esegue una serie di asserzioni e restituisce codice 0 in caso di successo,
1 in caso di fallimento.
"""
import sys

from rd2229.tools.concrete_strength import (
    CementType,
    SectionCondition,
    compute_allowable_compressive_stress,
    compute_allowable_shear,
)


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def main() -> int:
    try:
        s1 = compute_allowable_compressive_stress(
            120.0, CementType.NORMAL, SectionCondition.SEMPLICEMENTE_COMPRESA, controlled_quality=False
        )
        assert approx(s1, 35.0)

        s2 = compute_allowable_compressive_stress(
            160.0, CementType.HIGH, SectionCondition.INFLESSA_PRESSOINFLESSA, controlled_quality=False
        )
        assert approx(s2, 50.0)

        s3 = compute_allowable_compressive_stress(
            200.0, CementType.NORMAL, SectionCondition.SEMPLICEMENTE_COMPRESA, controlled_quality=True
        )
        assert approx(s3, 60.0)

        service, maximum = compute_allowable_shear(CementType.NORMAL)
        assert service == 4.0 and maximum == 14.0

    except AssertionError:
        print("Test failed", file=sys.stderr)
        return 1

    print("All concrete_strength tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
