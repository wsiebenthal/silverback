"""Turn config actions into results. Only minimize performs an OS action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from silverback.config import IMPLEMENTED_ACTIONS, STUB_ACTIONS, Action, AppConfig


@dataclass(frozen=True)
class ActionResult:
    action: str
    match: str
    implemented: bool
    ok: bool
    detail: str


class Minimizer(Protocol):
    def minimize_matching(self, match: str) -> ActionResult:
        """Minimize visible windows whose title contains match."""


def title_matches(title: str, match: str) -> bool:
    """Case-insensitive substring match against a window title."""
    if not title or not match:
        return False
    return match.casefold() in title.casefold()


def dispatch(action: Action, backend: Minimizer) -> ActionResult:
    if action.type == "minimize":
        return backend.minimize_matching(action.match)
    if action.type in STUB_ACTIONS:
        return ActionResult(
            action=action.type,
            match=action.match,
            implemented=False,
            ok=False,
            detail=f"{action.type} is not implemented yet; see ROADMAP.md",
        )
    return ActionResult(
        action=action.type,
        match=action.match,
        implemented=False,
        ok=False,
        detail=f"unknown action type {action.type!r}",
    )


def run_actions(
    config: AppConfig,
    backend: Minimizer,
    *,
    dry_run: bool = False,
) -> list[ActionResult]:
    results: list[ActionResult] = []
    for action in config.actions:
        if not action.enabled:
            continue
        if dry_run:
            implemented = action.type in IMPLEMENTED_ACTIONS
            if implemented:
                detail = "dry-run: not executed"
                ok = True
            elif action.type in STUB_ACTIONS:
                detail = f"{action.type} is not implemented yet; see ROADMAP.md"
                ok = False
            else:
                detail = f"unknown action type {action.type!r}"
                ok = False
            results.append(
                ActionResult(
                    action=action.type,
                    match=action.match,
                    implemented=implemented,
                    ok=ok,
                    detail=detail,
                )
            )
            continue
        results.append(dispatch(action, backend))
    return results


def exit_code_for(results: list[ActionResult]) -> int:
    """0 when every implemented action succeeded. Stubs do not fail the run."""
    for result in results:
        if result.implemented and not result.ok:
            return 1
    return 0


def format_result(result: ActionResult) -> str:
    if not result.implemented:
        tag = "stub"
    elif result.ok:
        tag = "ok"
    else:
        tag = "failed"
    return f"[{tag}] {result.action} {result.match!r}: {result.detail}"
