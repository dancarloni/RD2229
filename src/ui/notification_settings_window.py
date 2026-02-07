from __future__ import annotations

import logging
import tkinter as tk
from typing import Any, Dict, Optional

from sections_app.services.notification import notify_info  # type: ignore[import]
from sections_app.services.notification_settings import (
    load_notification_settings,  # type: ignore[import]
    save_notification_settings,  # type: ignore[import]
)

logger = logging.getLogger(__name__)

# Pylint: some UI initialization uses expression-only calls and broad exception
# handling intentionally to support headless mode; silence the corresponding warnings.
# pylint: disable=broad-exception-caught, expression-not-assigned

class NotificationSettingsWindow:
    """Settings editor for notification preferences.

    If `master` is None the window operates in headless mode (no actual Toplevel)
    and exposes a programmatic interface for tests.
    """

    def __init__(self, master: Optional[tk.Misc] = None, settings_path: Optional[str] = None):
        self.master = master
        self.headless = master is None
        self._settings_path = settings_path
        self._settings = load_notification_settings()
        self._build_ui() if not self.headless else None

    def _build_ui(self) -> None:
        self._win = tk.Toplevel(self.master)
        self._win.title("Notification Settings")
        frame = tk.Frame(self._win)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Level (radio)
        tk.Label(frame, text="Notification level:").grid(row=0, column=0, sticky="w")
        self.level_var = tk.StringVar(value=self._settings.get("level", "errors_only"))
        levels = [
            ("Errors only", "errors_only"),
            ("Warnings+Errors", "warnings_and_errors"),
            ("All", "all"),
        ]
        for i, (lab, val) in enumerate(levels):
            tk.Radiobutton(frame, text=lab, variable=self.level_var, value=val).grid(row=0, column=1 + i, sticky="w")

        # Show toasts
        self.show_toasts_var = tk.BooleanVar(value=self._settings.get("show_toasts", True))
        tk.Checkbutton(frame, text="Show transient toasts", variable=self.show_toasts_var).grid(
            row=1, column=0, columnspan=3, sticky="w"
        )

        # Confirm default
        tk.Label(frame, text="Confirm default action:").grid(row=2, column=0, sticky="w")
        self.confirm_var = tk.StringVar(value=self._settings.get("confirm_default", "ask"))
        tk.Radiobutton(frame, text="Ask user", variable=self.confirm_var, value="ask").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(frame, text="Default Yes", variable=self.confirm_var, value="default_yes").grid(
            row=2, column=2, sticky="w"
        )
        tk.Radiobutton(frame, text="Default No", variable=self.confirm_var, value="default_no").grid(
            row=2, column=3, sticky="w"
        )

        # Silent sources
        tk.Label(frame, text="Silent sources (comma-separated):").grid(row=3, column=0, sticky="w")
        self.silent_entry = tk.Entry(frame, width=60)
        self.silent_entry.grid(row=4, column=0, columnspan=4, sticky="we", pady=(0, 8))
        self.silent_entry.insert(0, ",".join(self._settings.get("silent_sources", [])))

        # Buttons
        btns = tk.Frame(frame)
        btns.grid(row=5, column=0, columnspan=4, pady=(4, 0))
        tk.Button(btns, text="Save", command=self._on_save).pack(side="left", padx=6)
        tk.Button(btns, text="Cancel", command=self._on_cancel).pack(side="left", padx=6)

    def _on_save(self) -> None:
        s = {
            "level": (getattr(self, "level_var", None).get() if not self.headless else self._settings.get("level")),
            "show_toasts": (
                getattr(self, "show_toasts_var", None).get() if not self.headless else self._settings.get("show_toasts")
            ),
            "silent_sources": [
                x.strip()
                for x in (
                    getattr(self, "silent_entry", None).get()
                    if not self.headless
                    else ",".join(self._settings.get("silent_sources", []))
                ).split(",")
                if x.strip()
            ],
            "confirm_default": (
                getattr(self, "confirm_var", None).get() if not self.headless else self._settings.get("confirm_default")
            ),
        }
        save_notification_settings(s)
        # Emit an informative notification so NotificationCenter notices and reloads
        notify_info("Notification Settings", "Settings saved")
        try:
            if not self.headless and getattr(self, "_win", None) is not None:
                self._win.destroy()
        except Exception:
            logger.exception("Error closing settings window")

    def _on_cancel(self) -> None:
        try:
            if not self.headless and getattr(self, "_win", None) is not None:
                self._win.destroy()
        except Exception:
            logger.exception("Error closing settings window")

    # Programmatic helpers for tests
    def set_settings(self, settings: Dict[str, Any]) -> None:
        self._settings = dict(settings)

    def save(self) -> None:
        # Save using API and trigger notify
        save_notification_settings(self._settings)
        notify_info("Notification Settings", "Settings saved")

    def get_settings(self) -> Dict[str, Any]:
        return dict(self._settings)
