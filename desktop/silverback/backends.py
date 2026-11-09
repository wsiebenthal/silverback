"""Per-OS window minimizers.

Linux uses xdotool and therefore an X11 session. macOS uses osascript and
needs Accessibility permission. Windows uses ShowWindow. Only the Linux path
is exercised by the tests in this repository.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any

from silverback.actions import ActionResult, title_matches

Runner = Callable[..., Any]
Which = Callable[[str], str | None]

_MAC_SCRIPT = r"""on run argv
  if (count of argv) < 1 then
    return "0"
  end if
  set needle to item 1 of argv
  set hits to 0
  tell application "System Events"
    set procs to every process whose background only is false
    repeat with p in procs
      try
        repeat with w in windows of p
          try
            set windowName to name of w as text
            ignoring case
              if windowName contains needle then
                set value of attribute "AXMinimized" of w to true
                set hits to hits + 1
              end if
            end ignoring
          end try
        end repeat
      end try
    end repeat
  end tell
  return hits as text
end run
"""


def _failed(match: str, detail: str) -> ActionResult:
    return ActionResult(
        action="minimize",
        match=match,
        implemented=True,
        ok=False,
        detail=detail,
    )


def _ok(match: str, detail: str) -> ActionResult:
    return ActionResult(
        action="minimize",
        match=match,
        implemented=True,
        ok=True,
        detail=detail,
    )


class LinuxBackend:
    """Minimize X11 windows with xdotool. Wayland is a later backend."""

    def __init__(
        self,
        runner: Runner = subprocess.run,
        which: Which = shutil.which,
    ) -> None:
        self._runner = runner
        self._which = which

    def minimize_matching(self, match: str) -> ActionResult:
        if not match.strip():
            return _failed(match, "empty match")
        if self._which("xdotool") is None:
            return _failed(
                match,
                "xdotool is not installed; Linux minimize currently supports X11 via xdotool",
            )
        search = self._runner(
            ["xdotool", "search", "--onlyvisible", "--name", re.escape(match)],
            capture_output=True,
            text=True,
            check=False,
        )
        window_ids = [line.strip() for line in (search.stdout or "").splitlines() if line.strip()]
        minimized: list[str] = []
        errors: list[str] = []
        for window_id in window_ids:
            name_proc = self._runner(
                ["xdotool", "getwindowname", window_id],
                capture_output=True,
                text=True,
                check=False,
            )
            name = (name_proc.stdout or "").strip()
            if name and not title_matches(name, match):
                continue
            proc = self._runner(
                ["xdotool", "windowminimize", window_id],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                minimized.append(name or window_id)
            else:
                err = (proc.stderr or "").strip()
                if err:
                    errors.append(err)
        if not minimized:
            detail = errors[0] if errors else "no visible window title matches"
            return _failed(match, detail)
        return _ok(match, f"minimized {len(minimized)} window(s): " + ", ".join(minimized))


class MacOSBackend:
    """Minimize windows by title through System Events.

    The match is passed as an AppleScript argument, not interpolated into the
    script. osascript exits non-zero when Accessibility permission is missing.
    """

    def __init__(
        self,
        runner: Runner = subprocess.run,
        which: Which = shutil.which,
    ) -> None:
        self._runner = runner
        self._which = which

    def minimize_matching(self, match: str) -> ActionResult:
        if not match.strip():
            return _failed(match, "empty match")
        if self._which("osascript") is None:
            return _failed(match, "osascript is not available")
        proc = self._runner(
            ["osascript", "-", match],
            input=_MAC_SCRIPT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or "").strip() or f"osascript exited {proc.returncode}"
            return _failed(match, detail)
        text = (proc.stdout or "").strip()
        try:
            hits = int(text)
        except ValueError:
            hits = 0
        if hits <= 0:
            return _failed(match, "no window title matches")
        return _ok(match, f"minimized {hits} window(s)")


class WindowsBackend:
    """Minimize top-level visible windows whose title contains the match.

    Uses SW_MINIMIZE (6). This path has not been run on Windows in this repo.
    """

    def minimize_matching(self, match: str) -> ActionResult:
        if not match.strip():
            return _failed(match, "empty match")
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows.argtypes = [enum_proc, wintypes.LPARAM]
        user32.EnumWindows.restype = wintypes.BOOL
        user32.IsWindowVisible.argtypes = [wintypes.HWND]
        user32.IsWindowVisible.restype = wintypes.BOOL
        user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        user32.GetWindowTextLengthW.restype = ctypes.c_int
        user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        user32.GetWindowTextW.restype = ctypes.c_int
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = wintypes.BOOL

        found: list[tuple[int, str]] = []

        def callback(hwnd: int, _lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value
            if title_matches(title, match):
                found.append((hwnd, title))
            return True

        user32.EnumWindows(enum_proc(callback), 0)
        if not found:
            return _failed(match, "no window title matches")
        titles: list[str] = []
        for hwnd, title in found:
            user32.ShowWindow(hwnd, 6)
            titles.append(title)
        return _ok(match, f"minimized {len(titles)} window(s): " + ", ".join(titles))


def get_backend() -> LinuxBackend | MacOSBackend | WindowsBackend:
    if sys.platform == "win32":
        return WindowsBackend()
    if sys.platform == "darwin":
        return MacOSBackend()
    return LinuxBackend()


def describe_minimize_support() -> str:
    if sys.platform == "win32":
        return "Win32 ShowWindow SW_MINIMIZE (not run on Windows in this repository)"
    if sys.platform == "darwin":
        tool = "found" if shutil.which("osascript") else "missing"
        return f"osascript {tool}; Accessibility permission is required"
    tool = shutil.which("xdotool")
    shown = "DISPLAY is set" if os.environ.get("DISPLAY") else "DISPLAY is unset"
    if tool:
        return f"X11 via xdotool ({tool}); {shown}. A Wayland backend is future work"
    return f"X11 via xdotool (xdotool is not installed); {shown}. A Wayland backend is future work"
