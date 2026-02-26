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


# ---------------------------------------------------------------------------
# Tkinter-dependent test collection guard
# ---------------------------------------------------------------------------
# When ``tkinter`` is not available (e.g. CI without a display), test files
# that import tkinter at module level – directly or transitively – would cause
# collection errors that abort the entire test run.  We detect the situation
# here and dynamically build ``collect_ignore`` so pytest can still collect
# and run all non-GUI tests normally.

try:
    import tkinter  # noqa: F401
    _TKINTER_AVAILABLE = True
except ImportError:
    _TKINTER_AVAILABLE = False

if not _TKINTER_AVAILABLE:
    import re as _re

    _tests_dir = Path(__file__).parent
    # Match direct tkinter imports AND imports of known tkinter-dependent modules
    # (e.g. materials_repository, sections_app.ui.*, verification_table)
    _tkinter_pattern = _re.compile(
        r'^\s*('
        r'import\s+tkinter|from\s+tkinter'
        r'|import\s+tk\b|from\s+tk\b'
        r'|(?:from|import)\s+materials_repository'
        r'|from\s+sections_app\.ui'
        r'|import\s+sections_app\.ui'
        r'|(?:from|import)\s+verification_table'
        r')',
        _re.MULTILINE,
    )

    def _imports_tkinter_directly(path: Path) -> bool:
        """Return True if the file imports tkinter (directly or via known wrappers)."""
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
            return bool(_tkinter_pattern.search(text))
        except OSError:
            return False

    collect_ignore: list = [
        str(p)
        for p in sorted(_tests_dir.glob('test_*.py'))
        if _imports_tkinter_directly(p)
    ]
