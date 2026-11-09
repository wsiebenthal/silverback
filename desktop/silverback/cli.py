"""Command line interface for the Silver Back desktop companion."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Iterator

from silverback import __version__
from silverback.actions import exit_code_for, format_result, run_actions
from silverback.backends import describe_minimize_support, get_backend
from silverback.config import ConfigError, load_config, resolve_config_path
from silverback.listener import Debouncer, Outcome, handle_line
from silverback.serial_io import SerialError, iter_serial_lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="silverback",
        description="Silver Back desktop companion. Runs configured actions when a presence sensor reports an approach.",
    )
    parser.add_argument("--version", action="version", version=f"silverback {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    trigger = commands.add_parser(
        "trigger",
        help="Run actions for a simulated approach, with no sensor attached",
    )
    _add_config_arg(trigger)
    trigger.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the actions that would run and leave windows alone",
    )

    listen = commands.add_parser(
        "listen",
        help="Read sensor events from USB serial, or from stdin with --stdin",
    )
    _add_config_arg(listen)
    listen.add_argument("--port", help="Serial port. Overrides serial.port in the config")
    listen.add_argument("--baud", type=int, help="Baud rate. Overrides serial.baud in the config")
    listen.add_argument(
        "--stdin",
        action="store_true",
        help="Read NDJSON events from stdin instead of a serial port",
    )
    listen.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse events and report actions without touching windows",
    )

    doctor = commands.add_parser("doctor", help="Print platform support and config status")
    _add_config_arg(doctor)

    check = commands.add_parser("check-config", help="Validate a config file and print it")
    _add_config_arg(check)
    return parser


def _add_config_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        help="Path to a JSON config file. Defaults to SILVERBACK_CONFIG, ./silverback.config.json, or ~/.config/silverback/config.json",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "trigger":
            return cmd_trigger(args)
        if args.command == "listen":
            return cmd_listen(args)
        if args.command == "doctor":
            return cmd_doctor(args)
        if args.command == "check-config":
            return cmd_check_config(args)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except SerialError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"error: unknown command {args.command}", file=sys.stderr)
    return 2


def cmd_trigger(args: argparse.Namespace) -> int:
    config = load_config(resolve_config_path(args.config))
    print("simulated approach")
    results = run_actions(config, get_backend(), dry_run=args.dry_run)
    if not results:
        print("no enabled actions")
        return 0
    for result in results:
        print(format_result(result))
    return exit_code_for(results)


def cmd_listen(args: argparse.Namespace) -> int:
    if args.stdin and args.port:
        raise ConfigError("pass either --stdin or --port, not both")
    if args.baud is not None and args.baud <= 0:
        raise ConfigError("baud must be a positive integer")
    config = load_config(resolve_config_path(args.config))
    if args.stdin:
        lines: Iterator[str] = iter(sys.stdin)
    else:
        port = args.port or config.serial.port
        if not port:
            raise ConfigError(
                "no serial port configured. Set serial.port, pass --port, or replay a file with --stdin"
            )
        baud = args.baud if args.baud is not None else config.serial.baud
        lines = iter_serial_lines(port, baud)

    backend = get_backend()
    debouncer = Debouncer(config.debounce_ms)
    try:
        for line in lines:
            outcome = handle_line(
                line,
                config,
                backend,
                debouncer,
                _now_ms(),
                dry_run=args.dry_run,
            )
            _print_outcome(outcome)
    except KeyboardInterrupt:
        print("stopped", file=sys.stderr)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    print(f"silverback {__version__}")
    print(f"platform: {sys.platform}")
    print(f"minimize: {describe_minimize_support()}")
    print("extension bridge: planned (the desktop app does not message the browser yet)")
    print("usb serial listen: implemented; opening a port needs hardware")
    try:
        path = resolve_config_path(args.config)
        config = load_config(path)
    except ConfigError as exc:
        print(f"config: {exc}", file=sys.stderr)
        return 2
    enabled = [action for action in config.actions if action.enabled]
    print(f"config: {path}")
    print(f"debounce_ms: {config.debounce_ms}")
    print(f"serial: port={config.serial.port or '(none)'} baud={config.serial.baud}")
    print(f"enabled actions: {len(enabled)}")
    for action in enabled:
        print(f"  - {action.type} {action.match!r}")
    return 0


def cmd_check_config(args: argparse.Namespace) -> int:
    path = resolve_config_path(args.config)
    config = load_config(path)
    print(f"config: {path}")
    print(f"version: {config.version}")
    print(f"debounce_ms: {config.debounce_ms}")
    print(f"serial: port={config.serial.port or '(none)'} baud={config.serial.baud}")
    for action in config.actions:
        state = "enabled" if action.enabled else "disabled"
        print(f"  - {action.type} {action.match!r} ({state})")
    return 0


def _print_outcome(outcome: Outcome | None) -> None:
    if outcome is None:
        return
    if outcome.error:
        print(f"ignored: {outcome.error}", file=sys.stderr)
        return
    if outcome.note:
        print(outcome.note)
    for result in outcome.results:
        print(format_result(result))


def _now_ms() -> int:
    return int(time.monotonic() * 1000)
