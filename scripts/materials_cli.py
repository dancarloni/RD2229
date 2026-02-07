"""CLI per la gestione dei materiali (usa `materials_manager`).

Questa CLI è separata dalle routine di calcolo e serve solo come
interfaccia testuale/di utilità per aggiungere, modificare e rimuovere
materiali persistiti in `data/materials.json`.

Esempi:
  python scripts/materials_cli.py list
  python scripts/materials_cli.py add --name C120 --sigma_c28 120 --cement normal
  python scripts/materials_cli.py get --name C120
  python scripts/materials_cli.py update --name C120 --set sigma_c28=150
  python scripts/materials_cli.py delete --name C120 --yes
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict

from tools.materials_manager import (
    add_material,
    delete_material,
    get_material,
    list_materials,
    update_material,
)


def cmd_list(args: argparse.Namespace) -> int:
    mats = list_materials()
    if not mats:
        print("No materials saved")
        return 0
    for m in mats:
        print(f"- {m.get('name')}: type={m.get('type')}, sigma_c={m.get('sigma_c')}")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    m = get_material(args.name)
    if not m:
        print(f"Material '{args.name}' not found", file=sys.stderr)
        return 2
    print(json.dumps(m, indent=2, ensure_ascii=False))
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    mat: Dict = {
        "name": args.name,
        "type": args.type,
    }
    if args.type == "concrete":
        mat.update(
            {
                "cement_type": args.cement,
                "sigma_c28": float(args.sigma_c28) if args.sigma_c28 is not None else None,
                "condition": args.condition,
                "controlled_quality": args.controlled,
            }
        )
    try:
        add_material(mat)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    print(f"Material '{args.name}' added")
    return 0


def _parse_set_pairs(pairs: str) -> Dict[str, object]:
    updates: Dict[str, object] = {}
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"Invalid set expression: {item}")
        k, v = item.split("=", 1)
        # try to convert numeric
        try:
            if "." in v:
                vv = float(v)
            else:
                vv = int(v)
        except Exception:
            if v.lower() in ("true", "false"):
                vv = v.lower() == "true"
            else:
                vv = v
        updates[k] = vv
    return updates


def cmd_update(args: argparse.Namespace) -> int:
    try:
        updates = _parse_set_pairs(args.set)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        update_material(args.name, updates)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    print(f"Material '{args.name}' updated")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        confirm = input(f"Delete material '{args.name}'? [y/N]: ")
        if confirm.lower() != "y":
            print("Aborted")
            return 1
    try:
        delete_material(args.name)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Material '{args.name}' deleted")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="materials_cli")
    sp = p.add_subparsers(dest="cmd")

    sp_list = sp.add_parser("list", help="List all materials")
    sp_list.set_defaults(func=cmd_list)

    sp_get = sp.add_parser("get", help="Get material by name")
    sp_get.add_argument("--name", required=True)
    sp_get.set_defaults(func=cmd_get)

    sp_add = sp.add_parser("add", help="Add new material")
    sp_add.add_argument("--name", required=True)
    sp_add.add_argument("--type", choices=["concrete", "steel"], default="concrete")
    sp_add.add_argument("--cement", choices=["normal", "high", "aluminous"], default="normal")
    sp_add.add_argument("--sigma_c28", type=float, help="sigma_c28 in Kg/cm²")
    sp_add.add_argument(
        "--condition",
        choices=["semplicemente_compresa", "inflesse_presso_inflesse", "conglomerato_speciale"],
        default="semplicemente_compresa",
    )
    sp_add.add_argument("--controlled", action="store_true", help="Controlled quality flag")
    sp_add.set_defaults(func=cmd_add)

    sp_upd = sp.add_parser("update", help="Update material fields")
    sp_upd.add_argument("--name", required=True)
    sp_upd.add_argument("--set", nargs="+", required=True, help="key=value pairs to set")
    sp_upd.set_defaults(func=cmd_update)

    sp_del = sp.add_parser("delete", help="Delete material")
    sp_del.add_argument("--name", required=True)
    sp_del.add_argument("--yes", action="store_true", help="Skip confirmation")
    sp_del.set_defaults(func=cmd_delete)

    return p


def main(argv=None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    if not hasattr(args, "func"):
        p.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
