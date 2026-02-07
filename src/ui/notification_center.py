from __future__ import annotations

import logging
import tkinter as tk
from typing import Any, Dict, List, Optional

from sections_app.services.event_bus import NOTIFICATION, EventBus
from sections_app.services.notification_settings import load_notification_settings

logger = logging.getLogger(__name__)

# Pylint: the notification center uses defensive catching and occasionally
# accesses protected members for UI interop; suppress noisy warnings for
# broad exception handlers and protected access in this module.
# pylint: disable=broad-exception-caught, protected-access


class NotificationCenter:
    """A small NotificationCenter that subscribes to EventBus.NOTIFICATION.

    In GUI mode it provides a simple Toplevel history window and transient toasts.
    In headless/test mode (master is None) it records notifications into `history`
    and does not try to create windows.
    """

    def __init__(self, master: Optional[tk.Misc] = None):
        self.master = master
        self.headless = master is None
        self.history: List[Dict[str, Any]] = []
        self._subscribed = False
        self._win: Optional[tk.Toplevel] = None
        self._listbox: Optional[tk.Listbox] = None
        self._load_settings()
        self._subscribe()
        if not self.headless:
            try:
                self._create_window()
            except Exception:
                logger.exception("Unable to create NotificationCenter window; switching to headless mode")
                self.headless = True

    def _load_settings(self) -> None:
        self.settings = load_notification_settings()

    def _subscribe(self) -> None:
        if not self._subscribed:
            EventBus().subscribe(NOTIFICATION, self._on_notification)
            self._subscribed = True

    def _unsubscribe(self) -> None:
        if self._subscribed:
            try:
                EventBus().unsubscribe(NOTIFICATION, self._on_notification)
            except Exception:
                pass
            self._subscribed = False

    def _create_window(self) -> None:
        self._win = tk.Toplevel(self.master)
        self._win.title("Notifications")
        self._win.geometry("420x240")
        frame = tk.Frame(self._win)
        frame.pack(fill="both", expand=True)
        self._listbox = tk.Listbox(frame)
        self._listbox.pack(fill="both", expand=True)

    def _should_display(self, payload: Dict[str, Any]) -> bool:
        lvl = payload.get("level", "info")
        level_setting = self.settings.get("level", "errors_only")
        if level_setting == "errors_only":
            return lvl in ("error", "confirm")
        if level_setting == "warnings_and_errors":
            return lvl in ("warning", "error", "confirm")
        return True

    def _on_notification(self, payload: Dict[str, Any]) -> None:
        try:
            # Refresh settings on each notification to pick up edits
            self._load_settings()
            if not self._should_display(payload):
                # still store in history for debugging
                self.history.append(payload)
                return
            self.history.append(payload)
            # Handle confirm specially
            if payload.get("level") == "confirm":
                self._handle_confirm(payload)
            else:
                self._show_toast(payload)
        except Exception:
            logger.exception("Error handling notification")

    def _show_toast(self, payload: Dict[str, Any]) -> None:
        text = f"{payload.get('title','')}: {payload.get('message','')}"
        logger.info("Notification toast: %s", text)
        if self.headless:
            return
        # show ephemeral label bottom-right of master
        try:
            parent = self.master or self._win
            lbl = tk.Label(parent, text=text, bg="#333", fg="white")
            lbl.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
            parent.after(3000, lbl.destroy)
            # add short line to listbox
            if self._listbox is not None:
                self._listbox.insert(tk.END, text)
        except Exception:
            logger.exception("Error showing toast")

    def _handle_confirm(self, payload: Dict[str, Any]) -> None:
        # If headless, do not block: leave payload in history so tests can call respond
        if self.headless:
            return
        respond = payload.get("respond")
        title = payload.get("title", "Confirm")
        message = payload.get("message", "")
        try:
            dlg = tk.Toplevel(self.master)
            dlg.title(title)
            lbl = tk.Label(dlg, text=message, wraplength=380)
            lbl.pack(padx=8, pady=8)
            btns = tk.Frame(dlg)
            btns.pack(pady=(0, 8))

            def do_yes():
                try:
                    if callable(respond):
                        respond(True)
                except Exception:
                    logger.exception("Error in confirm respond")
                dlg.destroy()

            def do_no():
                try:
                    if callable(respond):
                        respond(False)
                except Exception:
                    logger.exception("Error in confirm respond")
                dlg.destroy()

            tk.Button(btns, text="Yes", command=do_yes).pack(side="left", padx=6)
            tk.Button(btns, text="No", command=do_no).pack(side="left", padx=6)
        except Exception:
            logger.exception("Error showing confirm dialog")

    def destroy(self) -> None:
        self._unsubscribe()
        if self._win is not None and getattr(self._win, "winfo_exists", None) and self._win.winfo_exists():
            try:
                self._win.destroy()
            except Exception:
                pass
