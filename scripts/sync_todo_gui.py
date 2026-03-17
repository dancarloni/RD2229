#!/usr/bin/env python3
"""Sincronizza i TODO GUI tra piano tecnico e registro generale.

Uso rapido:
    python scripts/sync_todo_gui.py --update-gui --update-main

Comportamento:
- Estrae i TODO GUI da `docs/PIANO_LAVORO.md` (pattern `- [ ] GUI-...` / `- [x] GUI-...`).
- Aggiorna il blocco sincronizzato in `docs/PIANO_LAVORO_GUI.md` tra:
  `<!-- TODO_SYNC:START -->` e `<!-- TODO_SYNC:END -->`
- Opzionalmente aggiorna/crea una sezione in `docs/PIANO_LAVORO.md` con riepilogo sync.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

MAIN_PLAN = Path("docs/PIANO_LAVORO.md")
GUI_PLAN = Path("docs/PIANO_LAVORO_GUI.md")

SYNC_START = "<!-- TODO_SYNC:START -->"
SYNC_END = "<!-- TODO_SYNC:END -->"

MAIN_SYNC_START = "<!-- GUI_TODO_SYNC:START -->"
MAIN_SYNC_END = "<!-- GUI_TODO_SYNC:END -->"

GUI_TODO_PATTERN = re.compile(r"^- \[(?P<state>[ xX])\] (?P<label>GUI-[^\n]+)$")


def _read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def extract_gui_todos(main_text: str) -> list[tuple[bool, str]]:
    todos: list[tuple[bool, str]] = []
    for line in main_text.splitlines():
        match = GUI_TODO_PATTERN.match(line.strip())
        if match:
            done = match.group("state").lower() == "x"
            todos.append((done, match.group("label")))
    return todos


def build_sync_block(todos: list[tuple[bool, str]]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(todos)
    done = sum(1 for state, _ in todos if state)
    pending = total - done

    lines = [
        SYNC_START,
        f"- Sync timestamp: {now}",
        f"- TODO GUI totali: {total}",
        f"- Completati: {done}",
        f"- Da fare: {pending}",
        "- Riepilogo:",
    ]
    for state, label in todos:
        mark = "x" if state else " "
        lines.append(f"  - [{mark}] {label}")
    lines.append(SYNC_END)
    return "\n".join(lines)


def replace_block(text: str, start_marker: str, end_marker: str, new_block: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker)

    if start == -1 or end == -1 or end < start:
        return text.rstrip() + "\n\n" + new_block + "\n"

    end += len(end_marker)
    return text[:start] + new_block + text[end:]


def build_main_summary_block(todos: list[tuple[bool, str]]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(todos)
    done = sum(1 for state, _ in todos if state)
    pending = total - done

    lines = [
        MAIN_SYNC_START,
        "### GUI TODO Sync (auto)",
        f"- Ultimo sync: {now}",
        f"- Stato: {done}/{total} completati, {pending} aperti",
        "- Fonte tecnica: `docs/PIANO_LAVORO_GUI.md`",
        "- Comando: `python scripts/sync_todo_gui.py --update-gui --update-main`",
        MAIN_SYNC_END,
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync TODO GUI tra piano tecnico e piano generale")
    parser.add_argument(
        "--update-gui", action="store_true", help="Aggiorna blocco sync in PIANO_LAVORO_GUI.md"
    )
    parser.add_argument(
        "--update-main", action="store_true", help="Aggiorna riepilogo sync in PIANO_LAVORO.md"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Mostra solo riepilogo senza scrivere"
    )
    args = parser.parse_args()

    main_text = _read(MAIN_PLAN)
    todos = extract_gui_todos(main_text)

    if not todos:
        print("Nessun TODO GUI trovato nel piano generale.")
        return 1

    print(f"TODO GUI trovati: {len(todos)}")

    if args.update_gui:
        gui_text = _read(GUI_PLAN)
        sync_block = build_sync_block(todos)
        updated_gui = replace_block(gui_text, SYNC_START, SYNC_END, sync_block)
        if not args.dry_run:
            _write(GUI_PLAN, updated_gui)
        print("Aggiornamento GUI plan: OK")

    if args.update_main:
        summary_block = build_main_summary_block(todos)
        updated_main = replace_block(main_text, MAIN_SYNC_START, MAIN_SYNC_END, summary_block)
        if not args.dry_run:
            _write(MAIN_PLAN, updated_main)
        print("Aggiornamento main plan: OK")

    if not args.update_gui and not args.update_main:
        done = sum(1 for state, _ in todos if state)
        print(f"Stato TODO GUI: {done}/{len(todos)} completati")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
