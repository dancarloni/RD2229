"""Package for discoverable application modules.

Modules placed in this package expose:
- MODULE_SPEC: dict with keys: key, name, description, (optional) icon
- create_module(master, **deps) -> returns a window-like object with .mainloop()

This package is scanned by ModuleRegistry to populate the module selector.
"""

# package marker
__all__ = []
