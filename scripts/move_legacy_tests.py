"""Script to detect tests that likely belong to the legacy UI and suggest migration.

This is non-destructive and only prints candidates that import `tkinter` or
`ui.` modules and could be moved to `tests_legacy/`.
"""

import ast
from pathlib import Path


def find_legacy_tests(root: Path) -> list[Path]:
    candidates = []
    for p in root.rglob("test_*.py"):
        try:
            src = p.read_text(encoding="utf8")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        if n.name.startswith("tkinter") or n.name.startswith("ui"):
                            candidates.append(p)
                            raise StopIteration
                if isinstance(node, ast.ImportFrom):
                    if (node.module or "").startswith("tkinter") or (node.module or "").startswith(
                        "ui"
                    ):
                        candidates.append(p)
                        raise StopIteration
        except StopIteration:
            continue
        except Exception:
            continue
    return candidates


if __name__ == "__main__":
    root = Path("tests")
    cand = find_legacy_tests(root)
    if not cand:
        print("No obvious legacy tests found.")
    else:
        print("Candidates to move to tests_legacy:")
        for c in cand:
            print(" -", c)
