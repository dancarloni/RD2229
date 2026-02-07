# Migration notes

This release introduces a new `src/` layout and compatibility shims under `app/` and `core/` to preserve legacy imports. Key changes:

- `core/*` modules moved to `src/core_calculus/core/*`.
- `app/domain`, `app/verification`, `app/ui` are now re-exported from `src/*` for compatibility.

If you import from `verification_table` or `app.*`, the compatibility shims should keep your code working. To migrate fully, update imports to `src.*` packages.
