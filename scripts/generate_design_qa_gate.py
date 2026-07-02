#!/usr/bin/env python3
"""Generate a blocking design QA report for Phase 3 implementation screenshots."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE):
        fail(f"Expected PNG file: {path}")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def load_diff(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    if not path.exists():
        fail(f"Visual diff JSON does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid visual diff JSON: {exc}")
    if not isinstance(payload, dict):
        fail("Visual diff JSON must be an object")
    return payload


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    source = Path(args.source_preview).expanduser().resolve()
    screenshot = Path(args.implementation_screenshot).expanduser().resolve()
    blockers = []
    if not source.exists():
        blockers.append(f"Missing source preview: {source}")
    if not screenshot.exists():
        blockers.append(f"Missing implementation screenshot: {screenshot}")

    source_size = None
    screenshot_size = None
    if not blockers:
        source_size = png_size(source)
        screenshot_size = png_size(screenshot)
        if source_size[0] < args.min_width or source_size[1] < args.min_height:
            blockers.append(f"Source preview too small: {source_size[0]}x{source_size[1]}")
        if screenshot_size[0] < args.min_width or screenshot_size[1] < args.min_height:
            blockers.append(f"Implementation screenshot too small: {screenshot_size[0]}x{screenshot_size[1]}")

    diff = load_diff(Path(args.visual_diff_json).expanduser().resolve() if args.visual_diff_json else None)
    similarity_pct = None
    if diff and not diff.get("passed"):
        blockers.append("Visual diff report did not pass.")
    if diff:
        if isinstance(diff.get("similarityPct"), (int, float)):
            similarity_pct = float(diff["similarityPct"])
        elif isinstance(diff.get("diffPct"), (int, float)):
            similarity_pct = 100.0 - float(diff["diffPct"])
        if similarity_pct is None:
            blockers.append("Visual diff JSON does not contain diffPct or similarityPct.")
        elif similarity_pct < args.min_similarity_pct:
            blockers.append(
                f"Similarity {similarity_pct:.6f}% is below required {args.min_similarity_pct:.6f}%."
            )
    if not diff and args.require_diff:
        blockers.append("Visual diff JSON is required but was not provided.")

    final_result = "blocked" if blockers else "passed"
    return {
        "schemaVersion": "frontend-ui-pipeline.design-qa-gate.v1",
        "sourcePreview": str(source),
        "implementationScreenshot": str(screenshot),
        "sourceSize": source_size,
        "implementationSize": screenshot_size,
        "visualDiffJson": args.visual_diff_json,
        "visualDiffPassed": diff.get("passed") if diff else None,
        "similarityPct": round(similarity_pct, 6) if similarity_pct is not None else None,
        "minSimilarityPct": args.min_similarity_pct,
        "blockers": blockers,
        "finalResult": final_result,
        "mustFixBeforeHandoff": blockers,
        "checks": [
            "Reference preview exists and is readable.",
            "Implementation screenshot exists and is readable.",
            "Visual diff passes when provided or required.",
            f"Implementation screenshot is at least {args.min_similarity_pct}% similar to the Phase 1 source preview.",
            "No visible layout breakage, text overflow, missing assets, or wrong interaction state remains.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    blocker_lines = [f"- {item}" for item in report["blockers"]] or ["- None."]
    check_lines = [f"- {item}" for item in report["checks"]]
    source_size = report["sourceSize"] or ["unknown", "unknown"]
    screenshot_size = report["implementationSize"] or ["unknown", "unknown"]
    return "\n".join(
        [
            "# Design QA Gate",
            "",
            f"final result: {report['finalResult']}",
            "",
            "## Inputs",
            "",
            f"- Source preview: `{report['sourcePreview']}`",
            f"- Implementation screenshot: `{report['implementationScreenshot']}`",
            f"- Source size: `{source_size[0]}x{source_size[1]}`",
            f"- Implementation size: `{screenshot_size[0]}x{screenshot_size[1]}`",
            f"- Visual diff JSON: `{report['visualDiffJson'] or 'not provided'}`",
            f"- Visual diff passed: `{report['visualDiffPassed']}`",
            f"- Similarity: `{report['similarityPct'] if report['similarityPct'] is not None else 'unknown'}%`",
            f"- Required similarity: `{report['minSimilarityPct']}%`",
            "",
            "## Blocking Issues",
            "",
            *blocker_lines,
            "",
            "## Checks",
            "",
            *check_lines,
            "",
            "Do not hand off Phase 3 unless `final result: passed`.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a blocking design QA report.")
    parser.add_argument("--source-preview", required=True, help="Approved Phase 1 preview PNG.")
    parser.add_argument("--implementation-screenshot", required=True, help="Phase 3 implementation screenshot PNG.")
    parser.add_argument("--visual-diff-json", default="", help="Optional compare_visual_artifacts.py JSON report.")
    parser.add_argument("--require-diff", action="store_true", help="Require a visual diff JSON report.")
    parser.add_argument("--min-similarity-pct", type=float, default=99.0, help="Minimum similarity percentage required for final Phase 3 handoff.")
    parser.add_argument("--min-width", type=int, default=320)
    parser.add_argument("--min-height", type=int, default=240)
    parser.add_argument("--output-md", required=True, help="Output design-qa.md path.")
    parser.add_argument("--output-json", default="", help="Optional JSON output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(args)
    output_md = Path(args.output_md).expanduser().resolve()
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown(report), encoding="utf-8")
    if args.output_json:
        output_json = Path(args.output_json).expanduser().resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {output_json}")
    print(f"Wrote {output_md}")
    print(f"final result: {report['finalResult']}")


if __name__ == "__main__":
    main()
