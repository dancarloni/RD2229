# Contributing

See `docs/index.md` for development setup and testing.

Development environment:
- Use the devcontainer configuration for reproducible development.
- Run `pip install -r requirements-dev.txt` to install dev tools.
- Run `pre-commit install` to enable pre-commit hooks.

Testing:
- Run `pytest -q`.
- Property tests use `hypothesis` and are executed in CI.
