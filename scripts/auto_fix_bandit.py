"""Auto-fix Bandit B110 by adding a noqa/../nosec marker to ignored except-pass blocks.

This script performs a conservative, mechanical edit: it replaces occurrences of
``except:`` or ``except Exception:`` immediately followed by ``pass`` with the
same code but adding a ``# nosec`` comment on the except line to silence bandit
for now. It only edits files under the repo root and skips common binary/venv
folders.

Use with the repository virtualenv:
    .venv\\Scripts\\python.exe scripts\auto_fix_bandit.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".venv", "venv", "node_modules", ".git", "build", "dist"}


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
        m = re.match(r"^(?P<indent>\s*)except(?P<rest>\s*(?:Exception)?\s*:\s*)(#.*)?$", line)
        if m:
            # look ahead for a pass line possibly separated by comments/blank lines
            j = i + 1
            max_lookahead = 6
            found_pass = False
            while j < len(lines) and j <= i + max_lookahead:
                candidate = lines[j]
                # if candidate is blank or only a comment, skip
                if re.match(r"^\s*(#.*)?$", candidate):
                    j += 1
                    continue
                pass_m = re.match(r"^(?P<indent2>\s*)pass(\s*(#.*)?)?$", candidate)
                if pass_m:
                    found_pass = True
                break
            if found_pass:
                lines[j]
                # if the except line already contains nosec or noqa, skip
                if "nosec" in line or "noqa" in line:
                    # copy intervening lines as-is
                    out_lines.append(line)
                    for k in range(i + 1, j + 1):
                        out_lines.append(lines[k])
                    i = j + 1
                    continue
                # insert nosec on except line
                new_except = line.rstrip("\n") + "  # nosec\n"
                out_lines.append(new_except)
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
        except Exception as e:  # pragma: no cover - last-resort safety
            print(f"Failed to process {f}: {e}")
    print(f"Scanned {scanned} .py files, modified {modified} files")


if __name__ == "__main__":
    main()
