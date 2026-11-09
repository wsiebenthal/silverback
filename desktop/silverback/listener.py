"""Apply debounce and run actions for one sensor line."""

from __future__ import annotations

from dataclasses import dataclass

from silverback.actions import ActionResult, Minimizer, run_actions
from silverback.config import AppConfig
from silverback.protocol import Event, ProtocolError, parse_line


class Debouncer:
    """Suppress repeated approach events inside a time window.

    The window is measured from the last accepted approach. A clear event
    does not reset it. Occupancy tracking is described in ROADMAP.md.
    """

    def __init__(self, window_ms: int) -> None:
        self.window_ms = window_ms
        self._last: dict[str, int] = {}

    def allow(self, key: str, now_ms: int) -> bool:
        if self.window_ms <= 0:
            self._last[key] = now_ms
            return True
        previous = self._last.get(key)
        if previous is not None and now_ms - previous < self.window_ms:
            return False
        self._last[key] = now_ms
        return True


@dataclass(frozen=True)
class Outcome:
    event: Event | None
    error: str | None
    suppressed: bool
    note: str | None
    results: tuple[ActionResult, ...]


def handle_line(
    line: str,
    config: AppConfig,
    backend: Minimizer,
    debouncer: Debouncer,
    now_ms: int,
    *,
    dry_run: bool = False,
) -> Outcome | None:
    """Handle one line. Blank lines return None so the caller can skip them."""
    if not line.strip():
        return None
    try:
        event = parse_line(line)
    except ProtocolError as exc:
        return Outcome(None, str(exc), False, None, ())

    if event.type == "hello":
        fw = event.fw or "?"
        transport = event.transport or "?"
        return Outcome(event, None, False, f"hello fw={fw} transport={transport}", ())

    if event.type == "heartbeat":
        return Outcome(event, None, False, "heartbeat", ())

    if event.state == "clear":
        return Outcome(
            event,
            None,
            False,
            "clear received; restoring windows is not implemented yet",
            (),
        )

    if not debouncer.allow("approach", now_ms):
        return Outcome(event, None, True, "approach suppressed by debounce", ())

    results = run_actions(config, backend, dry_run=dry_run)
    return Outcome(event, None, False, "approach", tuple(results))
