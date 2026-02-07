"""Utilities for running background tasks in a thread pool and dispatching
results back to the GUI/main thread.

This module provides a small helper `BackgroundExecutor` which submits callables
to a background threadpool and will schedule a completion callback on a
Tkinter `tk_root` using `tk_root.after(0, ...)` when available.
"""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Optional


class BackgroundExecutor:
    """Lightweight ThreadPoolExecutor wrapper that schedules completion callbacks
    on the Tkinter main thread when a ``tk_root`` is provided.

    Usage:
        bg = BackgroundExecutor(max_workers=4)
        bg.submit(func, args..., callback=cb, tk_root=root)
    """

    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(
        self,
        fn: Callable[..., Any],
        *args: Any,
        callback: Optional[Callable[[Any], None]] = None,
        tk_root: Optional[Any] = None,
    ) -> Future[Any]:
        """Submit ``fn`` to the background thread pool.

        If ``callback`` is provided it will be called with the result (or with the
        exception instance if the callable raised) once the future completes. If
        ``tk_root`` is provided, the callback will be scheduled on the Tkinter
        main thread via ``tk_root.after(0, ...)``; otherwise it will be called
        synchronously from the worker thread.
        """
        future = self._executor.submit(fn, *args)

        if callback:

            def _on_done(fut: Future[Any]) -> None:
                try:
                    result = fut.result()
                except Exception as e:  # pylint: disable=broad-exception-caught
                    # Log the exception and pass the exception object to the callback
                    logging.exception("Background task raised an exception")
                    result = e
                if tk_root is not None:
                    try:
                        tk_root.after(0, lambda: callback(result))
                    except Exception:  # pylint: disable=broad-exception-caught
                        # Scheduling failed; call callback synchronously as fallback
                        logging.exception("Failed to schedule callback on tk_root")
                        callback(result)
                else:
                    callback(result)

            future.add_done_callback(_on_done)

        return future

    def shutdown(self, wait: bool = True) -> None:
        """Shut down the underlying executor.

        Args:
            wait: if True block until all work is done.

        """
        self._executor.shutdown(wait=wait)
