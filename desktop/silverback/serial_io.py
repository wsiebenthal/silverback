"""USB serial line iterator. Hardware is required to exercise this."""

from __future__ import annotations

from collections.abc import Iterator


class SerialError(Exception):
    """The serial port could not be opened or pyserial is missing."""


def iter_serial_lines(port: str, baud: int) -> Iterator[str]:
    """Yield decoded lines from a USB serial port.

    readline uses a 1 second timeout so the process can notice shutdown.
    Empty reads caused by the timeout are skipped.
    """
    try:
        import serial
    except ImportError as exc:
        raise SerialError(
            "pyserial is not installed. Install the desktop package to listen on USB serial."
        ) from exc
    try:
        handle = serial.Serial(port, baudrate=baud, timeout=1)
    except serial.SerialException as exc:
        raise SerialError(f"could not open serial port {port}: {exc}") from exc
    try:
        while True:
            raw = handle.readline()
            if not raw:
                continue
            yield raw.decode("utf-8", errors="replace")
    finally:
        handle.close()
