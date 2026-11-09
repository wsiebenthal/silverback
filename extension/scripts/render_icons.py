#!/usr/bin/env python3
"""Draw the simple Silver Back mark used by the extension icons."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


def write_png(path: Path, size: int) -> None:
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(pixel(x, y, size))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def pixel(x: int, y: int, size: int) -> tuple[int, int, int, int]:
    background = (30, 42, 50, 255)
    silver = (213, 221, 227, 255)
    if not in_rounded_rect(x, y, size):
        return (0, 0, 0, 0)
    cx = (size - 1) / 2
    cy = (size - 1) / 2
    radius = size * 0.30
    punch_x = cx - size * 0.14
    punch_r = size * 0.24
    if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
        if (x - punch_x) ** 2 + (y - cy) ** 2 <= punch_r ** 2:
            return background
        return silver
    return background


def in_rounded_rect(x: int, y: int, size: int) -> bool:
    inset = size * 0.06
    radius = size * 0.22
    left = inset
    top = inset
    right = size - 1 - inset
    bottom = size - 1 - inset
    if left + radius <= x <= right - radius and top <= y <= bottom:
        return True
    if top + radius <= y <= bottom - radius and left <= x <= right:
        return True
    for ox, oy in (
        (left + radius, top + radius),
        (right - radius, top + radius),
        (left + radius, bottom - radius),
        (right - radius, bottom - radius),
    ):
        if (x - ox) ** 2 + (y - oy) ** 2 <= radius ** 2:
            return True
    return False


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "icons"
    out.mkdir(parents=True, exist_ok=True)
    for size in (16, 48, 128):
        write_png(out / f"icon{size}.png", size)


if __name__ == "__main__":
    main()
