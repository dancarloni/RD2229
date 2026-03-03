#!/usr/bin/env python3
"""tools/diagnose.py – CLI for querying the DiagnosticsService event log.

Usage::

    # Show all sessions
    python tools/diagnose.py --sessions

    # Show all events in a session
    python tools/diagnose.py --session run_20260101_120000_abc1234

    # Filter events by source
    python tools/diagnose.py --session run_20260101_120000_abc1234 --source verifier

    # Filter events by type
    python tools/diagnose.py --source pipeline --event-type error

    # Load events from a saved file and query
    python tools/diagnose.py --load diagnostics.json --sessions

    # Save current in-memory events to file
    python tools/diagnose.py --save diagnostics.json

    # Show latest N events
    python tools/diagnose.py --limit 20

Exit codes: 0 = success, 1 = error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--session", metavar="SESSION_ID", help="Filter events by session ID")
    parser.add_argument("--source", help="Filter events by source (e.g. verifier, pipeline, gui)")
    parser.add_argument("--event-type", help="Filter events by event type")
    parser.add_argument("--since", help="ISO-8601 timestamp: only events at or after this time")
    parser.add_argument("--limit", type=int, help="Maximum number of events to show")
    parser.add_argument("--sessions", action="store_true", help="List all sessions")
    parser.add_argument("--load", metavar="FILE", help="Load events from a previously saved JSON file")
    parser.add_argument("--save", metavar="FILE", help="Save current diagnostics to a JSON file")
    parser.add_argument("--json", action="store_true", help="Output events as JSON array")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        from src.rd2229.diagnostics import get_diagnostics
    except ImportError:
        print("ERROR: Cannot import DiagnosticsService. Run from repo root.", file=sys.stderr)
        return 1

    diag = get_diagnostics()

    if args.load:
        try:
            count = diag.load_from_file(args.load)
            print(f"Loaded {count} events from {args.load}")
        except FileNotFoundError:
            print(f"ERROR: File not found: {args.load}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"ERROR loading file: {exc}", file=sys.stderr)
            return 1

    if args.save:
        diag.save_to_file(args.save)
        print(f"Saved diagnostics to {args.save}")
        return 0

    if args.sessions:
        sessions = diag.list_sessions()
        if not sessions:
            print("No sessions recorded.")
            return 0
        if args.json:
            print(json.dumps(sessions, indent=2, ensure_ascii=False))
        else:
            print(f"{'Session ID':<40} {'Started':<28} {'Events':>8}")
            print("-" * 82)
            for s in sessions:
                print(
                    f"{s['session_id']:<40} "
                    f"{s.get('started', '')[:26]:<28} "
                    f"{s.get('event_count', 0):>8}"
                )
        return 0

    # Query events
    events = diag.query_events(
        session_id=args.session,
        source=args.source,
        event_type=args.event_type,
        since=args.since,
        limit=args.limit,
    )

    if not events:
        print("No events found matching filters.")
        return 0

    if args.json:
        print(json.dumps([e.to_dict() for e in events], indent=2, ensure_ascii=False))
    else:
        print(f"{'Timestamp':<28} {'Session':<20} {'Source':<14} {'Type':<20} Payload")
        print("-" * 110)
        for ev in events:
            ts = ev.timestamp[:26]
            sid = ev.session_id[:18]
            src = ev.source[:12]
            etype = ev.event_type[:18]
            payload_str = json.dumps(ev.payload, ensure_ascii=False)[:40]
            print(f"{ts:<28} {sid:<20} {src:<14} {etype:<20} {payload_str}")
        print(f"\nTotal: {len(events)} event(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
