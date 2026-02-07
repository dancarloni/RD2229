from __future__ import annotations

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
    ) -> Future:
        future = self._executor.submit(fn, *args)

        if callback:

            def _on_done(fut: Future) -> None:
                try:
                    result = fut.result()
                except Exception as e:
                    # propagate exceptions to callback as well so caller can decide
                    result = e
                if tk_root is not None:
                    try:
                        tk_root.after(0, lambda: callback(result))
                    except Exception:
                        # If scheduling failed, call synchronously as fallback
                        callback(result)
                else:
                    callback(result)

            future.add_done_callback(_on_done)

        return future

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait)
