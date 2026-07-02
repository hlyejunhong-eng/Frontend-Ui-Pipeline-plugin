#!/usr/bin/env python3
"""Dependency-free PNG visual diff for UI previews and implementation screenshots."""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    pa = abs(estimate - left)
    pb = abs(estimate - up)
    pc = abs(estimate - upper_left)
    if pa <= pb and pa <= pc:
        return left
    if pb <= pc:
        return up
    return upper_left


def read_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if not data.startswith(PNG_SIGNATURE):
        fail("Only PNG files are supported for visual comparison.")
    chunks = []
    offset = len(PNG_SIGNATURE)
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        chunks.append((chunk_type, chunk_data))
        offset += length + 12
        if chunk_type == b"IEND":
            break
    return chunks


def decode_png(path: Path) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    data = path.read_bytes()
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()

    for chunk_type, chunk_data in read_chunks(data):
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)

    if None in {width, height, bit_depth, color_type, interlace}:
        fail(f"Missing PNG header: {path}")
    if bit_depth != 8:
        fail(f"Unsupported PNG bit depth in {path}: {bit_depth}")
    if interlace != 0:
        fail(f"Interlaced PNGs are not supported: {path}")

    channel_counts = {0: 1, 2: 3, 4: 2, 6: 4}
    channels = channel_counts.get(color_type)
    if channels is None:
        fail(f"Unsupported PNG color type in {path}: {color_type}")

    raw = zlib.decompress(bytes(compressed))
    stride = width * channels
    rows: list[bytes] = []
    source_offset = 0
    previous = bytes(stride)

    for _row_index in range(height):
        if source_offset >= len(raw):
            fail(f"PNG data ended early: {path}")
        filter_type = raw[source_offset]
        source_offset += 1
        scanline = bytearray(raw[source_offset : source_offset + stride])
        source_offset += stride

        for index, value in enumerate(scanline):
            left = scanline[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                restored = value
            elif filter_type == 1:
                restored = value + left
            elif filter_type == 2:
                restored = value + up
            elif filter_type == 3:
                restored = value + ((left + up) // 2)
            elif filter_type == 4:
                restored = value + paeth(left, up, upper_left)
            else:
                fail(f"Unsupported PNG filter in {path}: {filter_type}")
            scanline[index] = restored & 0xFF
        rows.append(bytes(scanline))
        previous = bytes(scanline)

    pixels: list[tuple[int, int, int, int]] = []
    for row in rows:
        for index in range(0, len(row), channels):
            if color_type == 0:
                gray = row[index]
                pixels.append((gray, gray, gray, 255))
            elif color_type == 2:
                pixels.append((row[index], row[index + 1], row[index + 2], 255))
            elif color_type == 4:
                gray = row[index]
                pixels.append((gray, gray, gray, row[index + 1]))
            else:
                pixels.append((row[index], row[index + 1], row[index + 2], row[index + 3]))
    return width, height, pixels


def compare(args: argparse.Namespace) -> dict[str, object]:
    expected_path = Path(args.expected).expanduser().resolve()
    actual_path = Path(args.actual).expanduser().resolve()
    if not expected_path.exists():
        fail(f"Missing expected PNG: {expected_path}")
    if not actual_path.exists():
        fail(f"Missing actual PNG: {actual_path}")

    expected_width, expected_height, expected_pixels = decode_png(expected_path)
    actual_width, actual_height, actual_pixels = decode_png(actual_path)
    size_match = expected_width == actual_width and expected_height == actual_height
    if not size_match and not args.allow_size_mismatch:
        fail(
            "PNG dimensions differ: "
            f"expected {expected_width}x{expected_height}, actual {actual_width}x{actual_height}. "
            "Use --allow-size-mismatch to compare the overlapping area."
        )

    compare_width = min(expected_width, actual_width)
    compare_height = min(expected_height, actual_height)
    compared_pixels = compare_width * compare_height
    if compared_pixels == 0:
        fail("No overlapping pixels to compare.")

    differing_pixels = 0
    total_delta = 0
    max_delta = 0
    for y in range(compare_height):
        expected_row = y * expected_width
        actual_row = y * actual_width
        for x in range(compare_width):
            expected_pixel = expected_pixels[expected_row + x]
            actual_pixel = actual_pixels[actual_row + x]
            channel_delta = [abs(expected_pixel[i] - actual_pixel[i]) for i in range(4)]
            pixel_delta = max(channel_delta)
            max_delta = max(max_delta, pixel_delta)
            total_delta += sum(channel_delta) / 4
            if pixel_delta > args.pixel_tolerance:
                differing_pixels += 1

    diff_pct = differing_pixels / compared_pixels * 100
    similarity_pct = max(0.0, 100.0 - diff_pct)
    mean_delta = total_delta / compared_pixels
    passed = (
        diff_pct <= args.max_diff_pct
        and mean_delta <= args.max_mean_delta
        and (size_match or args.allow_size_mismatch)
    )

    return {
        "expected": str(expected_path),
        "actual": str(actual_path),
        "expectedSize": {"width": expected_width, "height": expected_height},
        "actualSize": {"width": actual_width, "height": actual_height},
        "sizeMatch": size_match,
        "comparedSize": {"width": compare_width, "height": compare_height},
        "comparedPixels": compared_pixels,
        "differingPixels": differing_pixels,
        "diffPct": round(diff_pct, 6),
        "similarityPct": round(similarity_pct, 6),
        "meanDelta": round(mean_delta, 6),
        "maxDelta": max_delta,
        "thresholds": {
            "pixelTolerance": args.pixel_tolerance,
            "maxDiffPct": args.max_diff_pct,
            "maxMeanDelta": args.max_mean_delta,
        },
        "passed": passed,
    }


def write_markdown(report: dict[str, object], output_path: Path) -> None:
    expected_size = report["expectedSize"]
    actual_size = report["actualSize"]
    compared_size = report["comparedSize"]
    thresholds = report["thresholds"]
    status = "PASS" if report["passed"] else "FAIL"
    output_path.write_text(
        "\n".join(
            [
                "# Visual Diff Report",
                "",
                f"Status: `{status}`",
                "",
                f"- Expected: `{report['expected']}`",
                f"- Actual: `{report['actual']}`",
                f"- Expected size: `{expected_size['width']}x{expected_size['height']}`",
                f"- Actual size: `{actual_size['width']}x{actual_size['height']}`",
                f"- Compared area: `{compared_size['width']}x{compared_size['height']}`",
                f"- Differing pixels: `{report['differingPixels']}` of `{report['comparedPixels']}`",
                f"- Difference: `{report['diffPct']}%`",
                f"- Similarity: `{report['similarityPct']}%`",
                f"- Mean channel delta: `{report['meanDelta']}`",
                f"- Max channel delta: `{report['maxDelta']}`",
                f"- Pixel tolerance: `{thresholds['pixelTolerance']}`",
                f"- Max allowed difference: `{thresholds['maxDiffPct']}%`",
                f"- Max allowed mean delta: `{thresholds['maxMeanDelta']}`",
                "",
                "Use this report as evidence for Phase 2 asset review or Phase 3 screenshot QA.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two PNG UI artifacts and report visual difference.")
    parser.add_argument("expected", help="Approved preview PNG or reference screenshot.")
    parser.add_argument("actual", help="Generated asset preview or implementation screenshot PNG.")
    parser.add_argument("--pixel-tolerance", type=int, default=4)
    parser.add_argument("--max-diff-pct", type=float, default=1.0)
    parser.add_argument("--max-mean-delta", type=float, default=3.0)
    parser.add_argument("--allow-size-mismatch", action="store_true")
    parser.add_argument("--output-json", help="Optional JSON report path.")
    parser.add_argument("--output-md", help="Optional Markdown report path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = compare(args)

    if args.output_json:
        Path(args.output_json).expanduser().resolve().write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.output_md:
        write_markdown(report, Path(args.output_md).expanduser().resolve())

    status = "[OK]" if report["passed"] else "[FAIL]"
    print(
        f"{status} visual diff {report['diffPct']}% "
        f"similarity={report['similarityPct']}% "
        f"mean_delta={report['meanDelta']} max_delta={report['maxDelta']} "
        f"size_match={report['sizeMatch']}"
    )
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
