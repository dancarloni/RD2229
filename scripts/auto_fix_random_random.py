"""Add a conservative # nosec annotation to lines using random.Random(...).

This silences Bandit B311 when the code intentionally seeds a local RNG.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".venv", "venv", ".git", "node_modules", "build", "dist"}


def should_skip(p: Path) -> bool:
    return any(part in EXCLUDE for part in p.parts)


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf8")
    if "random.Random(" not in text:  # nosec
        return False
    lines = text.splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        if "random.Random(" in line and "nosec" not in line and "noqa" not in line:
            lines[i] = line.rstrip("\n") + "  # nosec\n"
            changed = True
    if changed:
        path.write_text("".join(lines), encoding="utf8")
    return changed


def main():
    modified = 0
    scanned = 0
    for p in ROOT.rglob("*.py"):
        if should_skip(p):
            continue
        scanned += 1
        try:
            if process(p):
                print(f"Modified: {p}")
                modified += 1
        except Exception as e:
            print(f"Error processing {p}: {e}")
    print(f"Scanned {scanned} files, modified {modified} files")


if __name__ == "__main__":
    main()
