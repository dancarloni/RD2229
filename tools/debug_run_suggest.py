import warnings

warnings.warn(
    "tools.debug_run_suggest is deprecated and moved to src.legacy.tools.debug_run_suggest;"
    " this module is a legacy GUI helper and should not be imported in headless contexts.",
    DeprecationWarning,
)


def run_legacy():
    """Import and run the legacy GUI debug script if needed.

    This function performs a lazy import of the legacy script so importing
    `tools.debug_run_suggest` does not require a display or tkinter at import time.
    """
    from src.legacy.tools import debug_run_suggest as legacy

    # The legacy module executes on import; returning the module is enough.
    return legacy


if __name__ == "__main__":
    run_legacy()
