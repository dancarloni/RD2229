# Contributing

See `docs/index.md` for development setup and testing.

## Development Environment

- Use the devcontainer configuration for reproducible development.
- Run `pip install -r requirements-dev.txt` to install dev tools.
- Run `pre-commit install` to enable pre-commit hooks (optional but recommended).

## ⚠️ MANDATORY: Pre-Commit Linting and Formatting

**Before every commit/push**, you **MUST** run these commands to avoid CI failures on GitHub:

```bash
# 1. Auto-fix linting errors
python -m ruff check . --fix

# 2. Auto-format code
python -m ruff format .

# 3. Sort imports
python -m isort . --profile black --line-length 100

# 4. Format with black
python -m black . --line-length 100

# 5. Final verification
python -m ruff check .
python -m flake8 .
python -m pytest -q
```

### Why This Is Required

Linting/import errors that don't appear locally can cause CI failures on GitHub due to:
- Environment differences (tool versions, Python versions, dependencies)
- Commands not executed locally before push
- Local caches masking errors

### Best Practices

- Run these commands **before** every `git commit`
- Verify that `ruff check .` returns "All checks passed!"
- Ensure tests pass: `pytest -q`
- If you're unsure about local/CI consistency, use Docker or GitHub Codespaces to replicate the CI environment

### Pre-commit Hooks (Recommended)

To automate these checks, install pre-commit hooks:

```bash
pre-commit install
```

This will run linting/formatting checks automatically before each commit. However, **the manual commands above remain the authoritative standard** for CI compliance.

## Testing

- Run `pytest -q` for the standard test suite.
- Property tests use `hypothesis` and are executed in CI.
- GUI tests (Tkinter/Qt) are in `tests_legacy/` and `tests/legacy_qt/` and are **not** run in CI.

