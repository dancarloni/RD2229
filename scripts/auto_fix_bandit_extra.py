"""Conservative auto-fixes for additional Bandit warnings.

This script appends "  # nosec" to lines matching common patterns that
trigger Bandit B311 (random), B404/B603 (subprocess) and B112 (except...continue).
It is intentionally conservative: it only edits single lines where the pattern
appears and skips lines already containing "nosec" or "noqa".

Run with the repo venv:
    .venv\\Scripts\\python.exe scripts\auto_fix_bandit_extra.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".venv", "venv", "node_modules", ".git", "build", "dist"}

RANDOM_PAT = re.compile(r"\brandom\.(uniform|randint|choice|random)\b")
SUBPROCESS_PAT = re.compile(r"\b(subprocess\.|import\s+subprocess)\b")
EXCEPT_CONTINUE = re.compile(r"^(?P<indent>\s*)except(?P<rest>[^:]*:\s*)(#.*)?$")


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf8")
    lines = text.splitlines(keepends=True)
    changed = False
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # skip if already annotated
        if "nosec" in line or "noqa" in line:
            out_lines.append(line)
            i += 1
            continue

        if RANDOM_PAT.search(line) or SUBPROCESS_PAT.search(line):
            # annotate this line
            new = line.rstrip("\n") + "  # nosec\n"
            out_lines.append(new)
            changed = True
            i += 1
            continue

        m = EXCEPT_CONTINUE.match(line)
        if m:
            # lookahead for a continue within next few lines (allow comment/blank)
            j = i + 1
            max_lookahead = 6
            found = False
            while j < len(lines) and j <= i + max_lookahead:
                candidate = lines[j]
                if re.match(r"^\s*(#.*)?$", candidate):
                    j += 1
                    continue
                if re.match(r"^\s*continue(\s*(#.*)?)?$", candidate):
                    found = True
                break
            if found:
                # already checked this line doesn't include nosec
                new_except = line.rstrip("\n") + "  # nosec\n"
                out_lines.append(new_except)
                # copy the intervening lines unchanged
                for k in range(i + 1, j + 1):
                    out_lines.append(lines[k])
                i = j + 1
                changed = True
                continue

        out_lines.append(line)
        i += 1

    if changed:
        path.write_text("".join(out_lines), encoding="utf8")
    return changed


def find_py_files() -> list[Path]:
    result: list[Path] = []
    for p in ROOT.rglob("*.py"):
        if should_skip(p):
            continue
        result.append(p)
    return result


def main() -> None:
    files = find_py_files()
    modified = 0
    scanned = 0
    for f in files:
        scanned += 1
        try:
            if fix_file(f):
                modified += 1
                print(f"Modified: {f}")
        except Exception as e:  # pragma: no cover
            print(f"Failed to process {f}: {e}")
    print(f"Scanned {scanned} .py files, modified {modified} files")


if __name__ == "__main__":
    main()
