#!/usr/bin/env python3
"""Scan frontend source code for visual components and interaction settings."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


INCLUDED_EXTENSIONS = {
    ".astro",
    ".css",
    ".html",
    ".js",
    ".jsx",
    ".less",
    ".scss",
    ".svelte",
    ".ts",
    ".tsx",
    ".vue",
}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".next",
    ".nuxt",
    ".output",
    ".turbo",
    ".vite",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "unpackage",
    "vendor",
}
MAX_FILE_BYTES = 500_000

PATTERNS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "buttonsAndControls": [
        ("button element", re.compile(r"<\s*(button|Button|van-button|el-button|uni-button)\b", re.I)),
        ("button class", re.compile(r"\b(btn|button|primary|secondary|ghost|danger|disabled|pressed)\b", re.I)),
        ("form control", re.compile(r"<\s*(input|select|textarea|Input|Select|Checkbox|Radio|Switch|Slider)\b", re.I)),
        ("click binding", re.compile(r"(@click|onClick|onclick|bindtap|onTap|@tap)\b", re.I)),
    ],
    "componentDefinitions": [
        ("react component", re.compile(r"\b(function|const|class)\s+[A-Z][A-Za-z0-9_]*\b")),
        ("vue component", re.compile(r"\b(defineComponent|export\s+default|components\s*:|setup\s*\()", re.I)),
        ("template block", re.compile(r"<\s*template\b", re.I)),
        ("props contract", re.compile(r"\b(props|defineProps|PropTypes|emits|defineEmits)\b", re.I)),
    ],
    "componentUsages": [
        ("component tag", re.compile(r"<\s*[A-Z][A-Za-z0-9_.:-]*\b")),
        ("uni primitive", re.compile(r"<\s*(view|text|scroll-view|swiper|image|button)\b", re.I)),
        ("class binding", re.compile(r"\b(className|class=|:class|v-bind:class)\b")),
        ("slot usage", re.compile(r"\b(slot|v-slot|children)\b", re.I)),
    ],
    "visualStyleSettings": [
        ("layout style", re.compile(r"\b(display|position|top|right|bottom|left|width|height|min-width|max-width|gap|grid|flex)\b", re.I)),
        ("spacing style", re.compile(r"\b(padding|margin|inset|safe-area)\b", re.I)),
        ("surface style", re.compile(r"\b(background|background-color|border|border-radius|box-shadow|shadow|backdrop-filter)\b", re.I)),
        ("type color style", re.compile(r"\b(color|font-size|font-weight|font-family|line-height|letter-spacing)\b", re.I)),
        ("layer style", re.compile(r"\b(z-index|opacity|overflow|clip-path|mask|filter|mix-blend-mode)\b", re.I)),
        ("design token", re.compile(r"(--[a-z0-9-]+|theme\.|tokens?\.|var\()", re.I)),
    ],
    "interactionMotionSettings": [
        ("pseudo state", re.compile(r"(:hover|:focus|:active|:disabled|:checked|:focus-visible)\b", re.I)),
        ("motion style", re.compile(r"\b(transition|animation|transform|keyframes|duration|easing|cubic-bezier)\b", re.I)),
        ("pointer event", re.compile(r"\b(onMouseEnter|onMouseLeave|onPointer|mouseenter|mouseleave|touchstart|touchend)\b", re.I)),
        ("gesture", re.compile(r"\b(drag|swipe|press|longpress|tap|pan|scroll)\b", re.I)),
    ],
    "stateFeedbackSettings": [
        ("loading state", re.compile(r"\b(loading|skeleton|spinner|shimmer|pending)\b", re.I)),
        ("disabled state", re.compile(r"\b(disabled|readonly|aria-disabled)\b", re.I)),
        ("feedback state", re.compile(r"\b(error|empty|success|warning|danger|selected|active|checked|toast|modal|dialog)\b", re.I)),
        ("accessibility state", re.compile(r"\b(aria-|role=|tabindex|focus-visible)\b", re.I)),
    ],
    "iconMediaSettings": [
        ("icon usage", re.compile(r"\b(icon|Icon|lucide|heroicon|svg-sprite|sprite)\b")),
        ("svg", re.compile(r"<\s*svg\b|<\s*use\b", re.I)),
        ("image usage", re.compile(r"<\s*(img|image|Image)\b|\b(background-image|src=|asset|static/|public/)\b", re.I)),
    ],
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def rel(path: Path, root: Path) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def is_source_file(path: Path) -> bool:
    return path.suffix.lower() in INCLUDED_EXTENSIONS


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def iter_source_files(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if len(files) >= max_files:
            break
        if not path.is_file() or should_skip(path.relative_to(root)):
            continue
        if is_source_file(path):
            files.append(path)
    return files


def excerpt(line: str, limit: int = 180) -> str:
    cleaned = re.sub(r"\s+", " ", line.strip())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def scan_file(path: Path, root: Path) -> list[dict[str, Any]]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return []
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    hits: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for category, patterns in PATTERNS.items():
            for label, pattern in patterns:
                if pattern.search(line):
                    hits.append(
                        {
                            "category": category,
                            "signal": label,
                            "file": rel(path, root),
                            "line": line_no,
                            "excerpt": excerpt(line),
                        }
                    )
                    break
    return hits


def trim_hits(hits: list[dict[str, Any]], max_hits_per_category: int) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    trimmed = []
    for hit in hits:
        category = str(hit["category"])
        if counts[category] >= max_hits_per_category:
            continue
        counts[category] += 1
        trimmed.append(hit)
    return trimmed


def summarize(hits: list[dict[str, Any]], files: list[Path], root: Path) -> dict[str, Any]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    files_by_category: dict[str, set[str]] = defaultdict(set)
    for hit in hits:
        by_category[str(hit["category"])].append(hit)
        files_by_category[str(hit["category"])].add(str(hit["file"]))
    return {
        "filesScanned": len(files),
        "sourceFiles": [rel(path, root) for path in files[:120]],
        "hitCount": len(hits),
        "categoryCounts": {category: len(items) for category, items in sorted(by_category.items())},
        "filesByCategory": {category: sorted(paths)[:30] for category, paths in sorted(files_by_category.items())},
    }


def build_inventory(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"Source root does not exist or is not a directory: {root}")
    files = iter_source_files(root, args.max_files)
    all_hits: list[dict[str, Any]] = []
    for path in files:
        all_hits.extend(scan_file(path, root))
    hits = trim_hits(all_hits, args.max_hits_per_category)
    return {
        "schemaVersion": "frontend-ui-pipeline.source-visual-inventory.v1",
        "root": str(root),
        "targetRoute": args.target_route,
        "targetName": args.target_name,
        "summary": summarize(hits, files, root),
        "hits": hits,
        "phase1Usage": [
            "Record this inventory in phase1-ui-brief.md under Source Visual Inventory.",
            "Use it to preserve existing buttons, components, visual states, and interaction settings in the Phase 2 generation guide.",
        ],
        "phase2Usage": [
            "Generate or map Phase 2 assets for source-derived buttons, component families, visual states, icons, and motion settings.",
            "When a source-derived component should not be generated, explain the mapping to an approved replacement component.",
        ],
    }


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    hits = payload["hits"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for hit in hits:
        grouped[str(hit["category"])].append(hit)

    lines = [
        "# Phase 1 Source Visual Inventory",
        "",
        f"- Source root: `{payload['root']}`",
        f"- Target route/component: `{payload.get('targetRoute') or 'not provided'}`",
        f"- Target name: `{payload.get('targetName') or 'not provided'}`",
        f"- Files scanned: `{summary['filesScanned']}`",
        f"- Visual/interaction hits retained: `{summary['hitCount']}`",
        "",
        "## Why This Exists",
        "",
        "Phase 1 must inspect source code for existing buttons, components, and visual interaction settings before generating a redesign brief. Phase 2 must use this inventory when deciding which assets and component states to generate.",
        "",
        "## Category Counts",
        "",
        "| Category | Hits | Example Files |",
        "| --- | --- | --- |",
    ]
    for category, count in summary["categoryCounts"].items():
        examples = ", ".join(f"`{path}`" for path in summary["filesByCategory"].get(category, [])[:5])
        lines.append(f"| `{category}` | `{count}` | {examples or '-'} |")
    if not summary["categoryCounts"]:
        lines.append("| - | `0` | No source visual signals found. |")

    lines.extend(
        [
            "",
            "## Source-Derived Component Requirements",
            "",
            "- Preserve or explicitly map every discovered button/control family.",
            "- Preserve or explicitly map every discovered component family and stateful variant.",
            "- Preserve or explicitly map hover, focus, active, disabled, loading, selected, empty, error, success, warning, transition, animation, and gesture settings.",
            "- Phase 2 must generate corresponding assets/components for these source-derived requirements or document why an approved replacement covers them.",
            "",
        ]
    )

    for category in sorted(grouped):
        lines.extend([f"## {category}", ""])
        for hit in grouped[category]:
            lines.append(
                f"- `{hit['file']}:{hit['line']}` `{hit['signal']}` - {hit['excerpt']}"
            )
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 1 source visual inventory from frontend code.")
    parser.add_argument("root", help="Frontend source/project root to scan.")
    parser.add_argument("--target-route", default="", help="Optional target route, page, or component name.")
    parser.add_argument("--target-name", default="", help="Optional human-readable target name.")
    parser.add_argument("--output-md", required=True, help="Output phase1-source-visual-inventory.md path.")
    parser.add_argument("--output-json", default="", help="Optional JSON output path.")
    parser.add_argument("--max-files", type=int, default=600)
    parser.add_argument("--max-hits-per-category", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_inventory(args)
    output_md = Path(args.output_md).expanduser().resolve()
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown(payload), encoding="utf-8")
    if args.output_json:
        output_json = Path(args.output_json).expanduser().resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {output_json}")
    print(f"Wrote {output_md}")
    print(f"Files scanned: {payload['summary']['filesScanned']}")
    print(f"Hits retained: {payload['summary']['hitCount']}")


if __name__ == "__main__":
    main()
