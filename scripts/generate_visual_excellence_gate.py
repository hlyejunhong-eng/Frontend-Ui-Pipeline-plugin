#!/usr/bin/env python3
"""Validate and document the Phase 1 visual excellence gate."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


CRITERIA = [
    "composition",
    "hierarchy",
    "typography",
    "spacing",
    "asset_richness",
    "interaction_clarity",
    "product_fidelity",
    "implementation_feasibility",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def rel(path: Path, root: Path) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def parse_option(raw: str) -> dict[str, str]:
    parts = raw.split("|", 3)
    if len(parts) != 4:
        fail("--option must look like id|Name|preview-path|summary")
    option_id, name, preview, summary = [part.strip() for part in parts]
    if not option_id or not name or not preview:
        fail("--option requires non-empty id, name, and preview path")
    return {"id": option_id, "name": name, "preview": preview, "summary": summary}


def parse_score(raw: str) -> tuple[str, int]:
    if "=" not in raw:
        fail("--score must look like criterion=8")
    key, value = raw.split("=", 1)
    key = key.strip()
    if key not in CRITERIA:
        fail(f"Unknown score criterion: {key}")
    try:
        score = int(value)
    except ValueError:
        fail(f"Score must be an integer: {raw}")
    if score < 0 or score > 10:
        fail(f"Score must be between 0 and 10: {raw}")
    return key, score


def validate_options(options: list[dict[str, str]], selected: str, root: Path) -> dict[str, Any]:
    if len(options) != 3:
        fail(f"Phase 1 visual gate requires exactly 3 visual options, got {len(options)}")
    ids = [option["id"] for option in options]
    if len(set(ids)) != 3:
        fail("Visual option ids must be unique")
    if selected not in ids:
        fail("Selected option must match one of the 3 option ids")
    for option in options:
        preview = Path(option["preview"]).expanduser()
        if not preview.is_absolute():
            preview = (root / preview).resolve()
        option["previewAbsolute"] = str(preview)
        option["previewExists"] = preview.exists()
        if not preview.exists():
            fail(f"Preview does not exist for option {option['id']}: {preview}")
    return next(option for option in options if option["id"] == selected)


def validate_scores(scores: dict[str, int], min_score: int) -> bool:
    missing = [criterion for criterion in CRITERIA if criterion not in scores]
    if missing:
        fail("Missing visual taste scores: " + ", ".join(missing))
    failed = [criterion for criterion, score in scores.items() if score < min_score]
    if failed:
        fail("Selected visual option failed taste criteria: " + ", ".join(failed))
    return True


def build_gate(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        fail(f"Root does not exist: {root}")
    brief = Path(args.phase1_brief).expanduser().resolve()
    if not brief.exists():
        fail(f"Phase 1 brief does not exist: {brief}")
    options = [parse_option(raw) for raw in args.option]
    selected = validate_options(options, args.selected_option, root)
    scores = dict(parse_score(raw) for raw in args.score)
    passed = validate_scores(scores, args.min_score)
    selected_preview = Path(selected["previewAbsolute"])
    return {
        "schemaVersion": "frontend-ui-pipeline.visual-excellence-gate.v1",
        "phase1Brief": str(brief),
        "root": str(root),
        "optionCount": len(options),
        "options": options,
        "selectedOption": selected["id"],
        "selectedName": selected["name"],
        "selectedPreview": str(selected_preview),
        "scores": scores,
        "minScore": args.min_score,
        "passed": passed,
        "phase2Allowed": passed,
        "rules": [
            "Generate exactly three independent visual options before Phase 2.",
            "Use the selected option as the visual source of truth.",
            "Favor real raster/ImageGen assets for backgrounds, illustrations, textures, and rich visual motifs.",
            "Use CSS/SVG procedural art only as a fallback or for crisp icons, masks, and component primitives.",
            "Do not average effort across foundation components before the primary screen visual target is strong.",
        ],
    }


def markdown(gate: dict[str, Any], output_dir: Path) -> str:
    option_lines = []
    for option in gate["options"]:
        selected = " selected" if option["id"] == gate["selectedOption"] else ""
        option_lines.append(
            f"- `{option['id']}`{selected}: **{option['name']}** -> `{rel(Path(option['previewAbsolute']), output_dir)}`. {option['summary']}"
        )
    score_lines = [f"- {criterion}: `{gate['scores'][criterion]}/10`" for criterion in CRITERIA]
    rule_lines = [f"- {rule}" for rule in gate["rules"]]
    return "\n".join(
        [
            "# Phase 1 Visual Excellence Gate",
            "",
            f"- Phase 1 brief: `{gate['phase1Brief']}`",
            f"- Selected option: `{gate['selectedOption']}` / **{gate['selectedName']}**",
            f"- Selected preview: `{rel(Path(gate['selectedPreview']), output_dir)}`",
            f"- Minimum score: `{gate['minScore']}/10`",
            f"- Gate passed: `{'yes' if gate['passed'] else 'no'}`",
            f"- Phase 2 allowed: `{'yes' if gate['phase2Allowed'] else 'no'}`",
            "",
            "## Visual Options",
            "",
            *option_lines,
            "",
            "## Visual Taste Scores",
            "",
            *score_lines,
            "",
            "## Hard Rules",
            "",
            *rule_lines,
            "",
            "Do not start Phase 2 until this gate passes and the selected preview is treated as the visual source of truth.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Phase 1 visual excellence gate report.")
    parser.add_argument("--root", required=True, help="Run folder or Phase 1 folder used to resolve relative preview paths.")
    parser.add_argument("--phase1-brief", required=True, help="Path to phase1-ui-brief.md.")
    parser.add_argument("--option", action="append", default=[], help="Visual option as id|Name|preview-path|summary. Repeat exactly 3 times.")
    parser.add_argument("--selected-option", required=True, help="Selected option id.")
    parser.add_argument("--score", action="append", default=[], help="Selected visual score as criterion=8. Required for all criteria.")
    parser.add_argument("--min-score", type=int, default=8, help="Minimum score for each criterion.")
    parser.add_argument("--output-dir", required=True, help="Output directory for gate Markdown and JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    gate = build_gate(args)
    output_json = output_dir / "phase1-visual-excellence-gate.json"
    output_md = output_dir / "phase1-visual-excellence-gate.md"
    output_json.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(markdown(gate, output_dir), encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print(f"Gate passed: {'yes' if gate['passed'] else 'no'}")


if __name__ == "__main__":
    main()
