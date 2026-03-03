#!/usr/bin/env python3
"""tools/fetch_norma.py – Normative Fetcher: archive and index normative sources.

Downloads (or registers) a normative source (PDF/HTML) and creates a
structured extract tree under ``docs/_norme/<NORM_ID>/``:

  docs/_norme/
    NTC2018/
      metadata.json          # title, version, date, source_url, sha256, clauses list
      extracts/
        4_1_2_1.md           # per-clause/article markdown extract
        ...
    RD2229/
      metadata.json
      extracts/
        art_1.md
        ...

Usage::

    # Register a local PDF and create skeleton extracts
    python tools/fetch_norma.py --norm NTC2018 --source path/to/ntc2018.pdf

    # Register from URL (downloads to docs/_norme/NTC2018/source/)
    python tools/fetch_norma.py --norm NTC2018 --url https://example.com/ntc2018.pdf

    # List available norms
    python tools/fetch_norma.py --list

    # Show metadata for a norm
    python tools/fetch_norma.py --show NTC2018

    # Add/update a clause extract (non-verbatim: references, summaries, metadata only)
    python tools/fetch_norma.py --norm NTC2018 --add-extract 4.1.2.1 --text "Ref: NTC2018 §4.1.2.1 – armature longitudinali (vedi testo ufficiale MIT)"

Policy:
    Saving the full source PDF/HTML is allowed only with explicit ``--allow-full-save``
    flag (owner authorization).
    Extracts MUST NOT contain verbatim normative text (see docs/MANIFESTO_GOVERNANCE.md §2.5).
    Only non-verbatim user-authored summaries, clause references (ID, article, paragraph),
    official links, and derived metadata/hashes are permitted in ``docs/_norme/``.

Exit codes: 0 = success, 1 = error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_NORME_DIR = _ROOT / "docs" / "_norme"

KNOWN_NORMS: dict[str, dict] = {
    "NTC2018": {
        "title": "Norme Tecniche per le Costruzioni 2018",
        "issuer": "MIT",
        "year": 2018,
        "gu_ref": "G.U. n.42 del 20/02/2018",
    },
    "RD2229": {
        "title": "Regio Decreto 16/11/1939 n.2229 – Norme per la esecuzione delle opere in conglomerato cementizio semplice od armato",
        "issuer": "Regio Decreto",
        "year": 1939,
        "gu_ref": "G.U. n.92 del 18/04/1940",
    },
    "DM96": {
        "title": "Decreto Ministeriale 09/01/1996 – Norme tecniche per il calcolo, l'esecuzione ed il collaudo delle strutture in cemento armato normale e precompresso",
        "issuer": "MIT",
        "year": 1996,
        "gu_ref": "G.U. n.29 del 05/02/1996 Suppl. Ord.",
    },
    "DM92": {
        "title": "Decreto Ministeriale 14/02/1992 – Norme tecniche per l'esecuzione delle opere in cemento armato normale e precompresso e per le strutture metalliche",
        "issuer": "MIT",
        "year": 1992,
        "gu_ref": "G.U. n.65 del 18/03/1992 Suppl. Ord.",
    },
    "EN1992": {
        "title": "EN 1992-1-1 – Eurocode 2: Design of concrete structures",
        "issuer": "CEN",
        "year": 2004,
        "gu_ref": "EN 1992-1-1:2004",
    },
    "EN1991": {
        "title": "EN 1991-1-4 – Eurocode 1: Actions on structures – Wind actions",
        "issuer": "CEN",
        "year": 2005,
        "gu_ref": "EN 1991-1-4:2005",
    },
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm_dir(norm_id: str, norme_dir: Path | None = None) -> Path:
    base = norme_dir if norme_dir is not None else _NORME_DIR
    return base / norm_id


def _metadata_path(norm_id: str, norme_dir: Path | None = None) -> Path:
    return _norm_dir(norm_id, norme_dir) / "metadata.json"


def _extracts_dir(norm_id: str, norme_dir: Path | None = None) -> Path:
    return _norm_dir(norm_id, norme_dir) / "extracts"


def load_metadata(norm_id: str, norme_dir: Path | None = None) -> dict:
    mp = _metadata_path(norm_id, norme_dir)
    if mp.exists():
        return json.loads(mp.read_text(encoding="utf-8"))
    return {}


def save_metadata(norm_id: str, meta: dict, norme_dir: Path | None = None) -> None:
    mp = _metadata_path(norm_id, norme_dir)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _clause_to_filename(clause_id: str) -> str:
    """Convert '4.1.2.1' → '4_1_2_1', 'art.1' → 'art_1'."""
    return clause_id.replace(".", "_").replace(" ", "_").replace("/", "_")


def init_norm(
    norm_id: str,
    source_url: str = "",
    source_path: str = "",
    norme_dir: Path | None = None,
) -> dict:
    """Initialise metadata for a norm and create directory skeleton."""
    nd = _norm_dir(norm_id, norme_dir)
    nd.mkdir(parents=True, exist_ok=True)
    _extracts_dir(norm_id, norme_dir).mkdir(parents=True, exist_ok=True)

    meta = load_metadata(norm_id, norme_dir)
    if not meta:
        known = KNOWN_NORMS.get(norm_id, {})
        meta = {
            "norm_id": norm_id,
            "title": known.get("title", norm_id),
            "issuer": known.get("issuer", ""),
            "year": known.get("year", None),
            "gu_ref": known.get("gu_ref", ""),
            "source_url": source_url,
            "source_files": [],
            "clauses": [],
            "_created": datetime.now(UTC).isoformat(),
            "_tool": "tools/fetch_norma.py",
        }
    else:
        if source_url:
            meta["source_url"] = source_url
    meta["_updated"] = datetime.now(UTC).isoformat()

    if source_path:
        sp = Path(source_path)
        if sp.exists():
            entry = {"path": str(sp), "sha256": _sha256_file(sp), "registered": datetime.now(UTC).isoformat()}
            existing_paths = {e["path"] for e in meta.get("source_files", [])}
            if str(sp) not in existing_paths:
                meta.setdefault("source_files", []).append(entry)

    save_metadata(norm_id, meta, norme_dir)
    return meta


def add_extract(
    norm_id: str,
    clause_id: str,
    text: str,
    norme_dir: Path | None = None,
) -> Path:
    """Write or overwrite a clause extract markdown file."""
    fname = _clause_to_filename(clause_id) + ".md"
    ep = _extracts_dir(norm_id, norme_dir) / fname
    ep.parent.mkdir(parents=True, exist_ok=True)
    header = f"# {norm_id} – {clause_id}\n\n"
    ep.write_text(header + text.strip() + "\n", encoding="utf-8")

    # Update metadata clause list
    meta = load_metadata(norm_id, norme_dir)
    clauses = meta.get("clauses", [])
    clause_ids = {c["id"] for c in clauses}
    if clause_id not in clause_ids:
        clauses.append({"id": clause_id, "file": f"extracts/{fname}"})
        meta["clauses"] = clauses
        save_metadata(norm_id, meta, norme_dir)

    return ep


def list_norms(norme_dir: Path | None = None) -> list[dict]:
    """Return list of registered norms in the norme directory."""
    base = norme_dir if norme_dir is not None else _NORME_DIR
    if not base.exists():
        return []
    result = []
    for nd in sorted(base.iterdir()):
        if nd.is_dir():
            meta = load_metadata(nd.name, base)
            result.append({
                "norm_id": nd.name,
                "title": meta.get("title", nd.name),
                "clauses": len(meta.get("clauses", [])),
                "source_files": len(meta.get("source_files", [])),
            })
    return result


def download_source(
    norm_id: str,
    url: str,
    allow_full_save: bool = False,
    norme_dir: Path | None = None,
) -> str | None:
    """Attempt to download a normative source from *url*.

    Requires ``--allow-full-save`` (owner authorisation).
    Returns local path if successful, None otherwise.
    """
    if not allow_full_save:
        print(
            "NOTE: Full source download requires --allow-full-save (owner authorisation).\n"
            "Only metadata and URL are recorded.",
            file=sys.stderr,
        )
        return None

    try:
        import urllib.request
    except ImportError:
        print("urllib not available", file=sys.stderr)
        return None

    source_dir = _norm_dir(norm_id, norme_dir) / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    fname = url.rstrip("/").split("/")[-1] or f"{norm_id}_source.pdf"
    dest = source_dir / fname
    print(f"  Downloading {url} → {dest}")
    try:
        urllib.request.urlretrieve(url, dest)  # noqa: S310
        return str(dest)
    except Exception as exc:
        print(f"  ERROR downloading: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--norm", help="Norm ID (e.g. NTC2018, RD2229, DM96)")
    parser.add_argument("--source", help="Path to local source file (PDF/HTML) to register")
    parser.add_argument("--url", help="URL of normative source to record (or download with --allow-full-save)")
    parser.add_argument("--allow-full-save", action="store_true", help="Allow downloading full source (owner auth)")
    parser.add_argument("--add-extract", metavar="CLAUSE_ID", help="Add/update a clause extract (requires --text)")
    parser.add_argument("--text", help="Text content for --add-extract")
    parser.add_argument("--text-file", help="File containing text for --add-extract")
    parser.add_argument("--list", action="store_true", help="List all registered norms")
    parser.add_argument("--show", metavar="NORM_ID", help="Show metadata for a norm")
    parser.add_argument("--norme-dir", default=str(_NORME_DIR), help=f"Base directory for norms (default: {_NORME_DIR})")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # Use explicit norme_dir for all operations (no global mutation)
    norme_dir = Path(args.norme_dir)

    if args.list:
        norms = list_norms(norme_dir)
        if not norms:
            print("No norms registered. Use --norm NTC2018 [--source ...] to register.")
            return 0
        print(f"{'Norm ID':<12} {'Clauses':>8} {'Sources':>8}  Title")
        print("-" * 80)
        for n in norms:
            print(f"{n['norm_id']:<12} {n['clauses']:>8} {n['source_files']:>8}  {n['title'][:50]}")
        return 0

    if args.show:
        meta = load_metadata(args.show, norme_dir)
        if not meta:
            print(f"Norm '{args.show}' not found. Register it with --norm {args.show}.", file=sys.stderr)
            return 1
        print(json.dumps(meta, indent=2, ensure_ascii=False))
        return 0

    if not args.norm:
        print("Specify --norm, --list, or --show. Use -h for help.", file=sys.stderr)
        return 1

    norm_id = args.norm.upper()
    print(f"=== fetch_norma: {norm_id} ===")

    # Download if URL given
    local_source = args.source
    if args.url:
        if args.allow_full_save:
            downloaded = download_source(norm_id, args.url, allow_full_save=True, norme_dir=norme_dir)
            if downloaded:
                local_source = downloaded
        # Always record the URL in metadata
        meta = init_norm(norm_id, source_url=args.url, source_path=local_source or "", norme_dir=norme_dir)
    else:
        meta = init_norm(norm_id, source_path=local_source or "", norme_dir=norme_dir)

    print(f"  Norm dir : {_norm_dir(norm_id, norme_dir)}")
    print(f"  Metadata : {_metadata_path(norm_id, norme_dir)}")
    print(f"  Clauses  : {len(meta.get('clauses', []))}")

    # Add extract if requested
    if args.add_extract:
        text = args.text or ""
        if args.text_file:
            text = Path(args.text_file).read_text(encoding="utf-8")
        if not text:
            print("--add-extract requires --text or --text-file", file=sys.stderr)
            return 1
        ep = add_extract(norm_id, args.add_extract, text, norme_dir=norme_dir)
        try:
            ep_display: Path | str = ep.relative_to(_ROOT)
        except ValueError:
            ep_display = ep
        print(f"  Extract  : {ep_display}")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
