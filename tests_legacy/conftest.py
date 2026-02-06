import os
import json
import pytest
from pathlib import Path
from sections_app.services.event_bus import EventBus, NOTIFICATION


@pytest.fixture
def notification_collector():
    bus = EventBus()
    bus.clear()
    collected = []

    def _collect(payload):
        collected.append(payload)

    bus.subscribe(NOTIFICATION, _collect)
    yield collected
    bus.clear()


def _check_repo_duplicates():
    """Check sections.json for duplicate ids or names.

    Returns list of anomaly messages (empty if ok).
    """
    repo_path = Path(__file__).resolve().parents[1] / 'data' / 'sections.json'
    if not repo_path.exists():
        return [f"Repository file missing: {repo_path}"]
    try:
        with repo_path.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception as e:
        return [f"Failed to read {repo_path}: {e}"]
    ids = []
    names = []
    msgs = []
    for s in data:
        sid = s.get('id')
        name = s.get('name')
        if sid in ids:
            msgs.append(f"Duplicate id: {sid}")
        else:
            ids.append(sid)
        if name in names:
            msgs.append(f"Duplicate name: {name}")
        else:
            names.append(name)
    return msgs


def pytest_configure(config):
    """If REPO_WATCHER_STRICT=1, run repo checks and exit on anomalies."""
    if os.environ.get('REPO_WATCHER_STRICT') == '1':
        msgs = _check_repo_duplicates()
        if msgs:
            raise SystemExit("Repository anomalies detected:\n" + "\n".join(msgs))
