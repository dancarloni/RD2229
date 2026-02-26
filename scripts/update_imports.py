#!/usr/bin/env python3
# script minimale: aggiorna import testuali ricorsivamente
import argparse
import pathlib
import re


def replace_in_file(path, reps):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"Skipped {path} (not UTF-8)")
        return
    new = text
    for old, newv in reps.items():
        new = re.sub(r"\b" + re.escape(old) + r"(\b|[\.\:])", lambda m: newv + m.group(1), new)
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("Updated", path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--replacements", nargs="*", help="old:new")
    args = p.parse_args()
    reps = dict(r.split(":", 1) for r in (args.replacements or []))
    for f in pathlib.Path(args.root).rglob("*.py"):
        replace_in_file(f, reps)


if __name__ == "__main__":
    main()
