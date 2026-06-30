#!/usr/bin/env python3
"""Dependency-free visual artifact checks for previews, contact sheets, and screenshots."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def png_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(PNG_SIGNATURE) or len(data) < 24:
        return None
    return struct.unpack(">II", data[16:24])


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[index : index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height = int.from_bytes(data[index + 3 : index + 5], "big")
            width = int.from_bytes(data[index + 5 : index + 7], "big")
            return width, height
        index += segment_length
    return None


def svg_size(text: str) -> tuple[int, int] | None:
    if "<svg" not in text.lower():
        return None
    width_match = re.search(r'\bwidth=["\']?([0-9.]+)', text, re.I)
    height_match = re.search(r'\bheight=["\']?([0-9.]+)', text, re.I)
    if width_match and height_match:
        return round(float(width_match.group(1))), round(float(height_match.group(1)))
    viewbox_match = re.search(r'\bviewBox=["\']\s*[-0-9.]+\s+[-0-9.]+\s+([0-9.]+)\s+([0-9.]+)', text, re.I)
    if viewbox_match:
        return round(float(viewbox_match.group(1))), round(float(viewbox_match.group(2)))
    return None


def html_ok(text: str) -> bool:
    lowered = text.lower()
    return "<html" in lowered or "<!doctype html" in lowered or ("<body" in lowered and "</" in lowered)


def inspect_file(path: Path, args: argparse.Namespace) -> None:
    if not path.exists():
        fail(f"Missing visual artifact: {path}")
    if path.stat().st_size < args.min_bytes:
        fail(f"Visual artifact is too small: {path} ({path.stat().st_size} bytes)")

    suffix = path.suffix.lower()
    data = path.read_bytes()
    dimensions = None
    artifact_type = suffix.lstrip(".") or "unknown"

    if suffix == ".png":
        dimensions = png_size(data)
        artifact_type = "png"
    elif suffix in {".jpg", ".jpeg"}:
        dimensions = jpeg_size(data)
        artifact_type = "jpeg"
    elif suffix == ".svg":
        text = data.decode("utf-8", errors="replace")
        dimensions = svg_size(text)
        artifact_type = "svg"
    elif suffix in {".html", ".htm"}:
        text = data.decode("utf-8", errors="replace")
        if not html_ok(text):
            fail(f"HTML artifact does not look renderable: {path}")
        ok(f"{path}: html {path.stat().st_size} bytes")
        return
    else:
        fail(f"Unsupported visual artifact type for {path}")

    if not dimensions:
        fail(f"Could not read dimensions for {path}")
    width, height = dimensions
    if width < args.min_width or height < args.min_height:
        fail(f"{path} dimensions {width}x{height} below minimum {args.min_width}x{args.min_height}")
    ok(f"{path}: {artifact_type} {width}x{height} {path.stat().st_size} bytes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check preview, contact-sheet, and screenshot artifacts.")
    parser.add_argument("paths", nargs="+", help="Image, SVG, or HTML files to inspect.")
    parser.add_argument("--min-width", type=int, default=1)
    parser.add_argument("--min-height", type=int, default=1)
    parser.add_argument("--min-bytes", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for raw_path in args.paths:
        inspect_file(Path(raw_path).expanduser().resolve(), args)


if __name__ == "__main__":
    main()
