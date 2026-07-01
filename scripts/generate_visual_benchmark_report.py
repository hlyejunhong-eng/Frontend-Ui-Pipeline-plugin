#!/usr/bin/env python3
"""Generate a Phase 1 competitive visual benchmark report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
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

PRODUCT_DESIGN_BASELINE = {criterion: 8 for criterion in CRITERIA}

BRIEF_MARKER_GROUPS = [
    ("Selected Direction", ["Selected Direction"]),
    ("Phase 2 Generation Guide", ["Phase 2 Generation Guide"]),
    ("Layer Map", ["Layer Map"]),
    ("Adjustable Parameters", ["Adjustable Parameters"]),
    ("Asset Naming Rules", ["Asset Naming Rules"]),
    ("Export Rules", ["Export Rules"]),
    ("Responsive Crop Rules", ["Responsive Crop Rules"]),
    ("Phase 2 Component Inventory", ["Required Phase 2 Component Inventory", "Complete Phase 2 Component Inventory", "Complete Phase 2 component inventory"]),
    ("Motion Spec", ["Motion Spec"]),
    ("Asset Expectations", ["Asset Expectations"]),
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        fail(f"Could not parse JSON: {path}")
    if not isinstance(payload, dict):
        fail(f"JSON root must be an object: {path}")
    return payload


def resolve_path(raw: str, root: Path) -> Path:
    path = Path(raw).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"Root must be an existing directory: {root}")
    brief = resolve_path(args.phase1_brief, root)
    if not brief.exists():
        fail(f"Phase 1 brief does not exist: {brief}")
    gate_path = resolve_path(args.visual_gate, root)
    if not gate_path.exists():
        fail(f"Visual gate JSON does not exist: {gate_path}")
    gate = load_json(gate_path)
    brief_text = brief.read_text(encoding="utf-8", errors="replace")
    scores = gate.get("scores") if isinstance(gate.get("scores"), dict) else {}
    missing_scores = [criterion for criterion in CRITERIA if criterion not in scores]
    if missing_scores:
        fail("Visual gate is missing scores: " + ", ".join(missing_scores))

    normalized_scores = {criterion: int(scores[criterion]) for criterion in CRITERIA}
    selected_preview_raw = args.selected_preview or gate.get("selectedPreview") or ""
    selected_preview = resolve_path(str(selected_preview_raw), root) if selected_preview_raw else None
    option_count = int(gate.get("optionCount") or 0)
    advantage_criteria = [
        criterion
        for criterion in CRITERIA
        if normalized_scores[criterion] > PRODUCT_DESIGN_BASELINE[criterion]
    ]
    tied_criteria = [
        criterion
        for criterion in CRITERIA
        if normalized_scores[criterion] == PRODUCT_DESIGN_BASELINE[criterion]
    ]
    below_criteria = [
        criterion
        for criterion in CRITERIA
        if normalized_scores[criterion] < PRODUCT_DESIGN_BASELINE[criterion]
    ]
    brief_lower = brief_text.lower()
    marker_results = {
        label: any(marker.lower() in brief_lower for marker in alternatives)
        for label, alternatives in BRIEF_MARKER_GROUPS
    }
    missing_markers = [label for label, present in marker_results.items() if not present]
    score_average = round(mean(normalized_scores.values()), 3)
    baseline_average = round(mean(PRODUCT_DESIGN_BASELINE.values()), 3)
    margin = round(score_average - baseline_average, 3)
    passed = (
        gate.get("passed") is True
        and gate.get("phase2Allowed") is True
        and option_count == 3
        and selected_preview is not None
        and selected_preview.exists()
        and score_average >= args.min_average
        and len(advantage_criteria) >= args.min_advantages
        and not below_criteria
        and not missing_markers
    )
    return {
        "schemaVersion": "frontend-ui-pipeline.visual-benchmark.v1",
        "root": str(root),
        "phase1Brief": str(brief),
        "visualGate": str(gate_path),
        "selectedOption": gate.get("selectedOption", ""),
        "selectedName": gate.get("selectedName", ""),
        "selectedPreview": str(selected_preview) if selected_preview else "",
        "selectedPreviewExists": bool(selected_preview and selected_preview.exists()),
        "competitorBaseline": "product-design.default-ideation",
        "scores": normalized_scores,
        "baselineScores": PRODUCT_DESIGN_BASELINE,
        "scoreAverage": score_average,
        "baselineAverage": baseline_average,
        "averageMargin": margin,
        "advantageCriteria": advantage_criteria,
        "tiedCriteria": tied_criteria,
        "belowCriteria": below_criteria,
        "minAverage": args.min_average,
        "minAdvantages": args.min_advantages,
        "optionCount": option_count,
        "briefMarkers": marker_results,
        "missingBriefMarkers": missing_markers,
        "passed": passed,
        "phase2Allowed": passed,
        "rules": [
            "Treat Product Design's strong default as a baseline, not the ceiling.",
            "Require exactly three independent visual options before Phase 2.",
            "Require the selected direction to beat the baseline on multiple criteria, not only tie it.",
            "Require Phase 2 generation guidance so the visual target can become real assets and production frontend.",
        ],
    }


def markdown(report: dict[str, Any], output_dir: Path) -> str:
    score_rows = ["| Criterion | Pipeline | Product Design Baseline | Delta |", "| --- | ---: | ---: | ---: |"]
    for criterion in CRITERIA:
        score = report["scores"][criterion]
        baseline = report["baselineScores"][criterion]
        score_rows.append(f"| `{criterion}` | `{score}` | `{baseline}` | `{score - baseline:+d}` |")
    marker_rows = ["| Required brief marker | Present |", "| --- | --- |"]
    for marker, present in report["briefMarkers"].items():
        marker_rows.append(f"| {marker} | `{'yes' if present else 'no'}` |")
    advantage = ", ".join(report["advantageCriteria"]) or "none"
    below = ", ".join(report["belowCriteria"]) or "none"
    missing = ", ".join(report["missingBriefMarkers"]) or "none"
    return "\n".join(
        [
            "# Phase 1 Product Design Benchmark",
            "",
            f"- Competitor baseline: `{report['competitorBaseline']}`",
            f"- Selected option: `{report['selectedOption']}` / **{report['selectedName']}**",
            f"- Selected preview: `{rel(Path(report['selectedPreview']), output_dir) if report['selectedPreview'] else ''}`",
            f"- Visual gate: `{rel(Path(report['visualGate']), output_dir)}`",
            f"- Score average: `{report['scoreAverage']}`",
            f"- Baseline average: `{report['baselineAverage']}`",
            f"- Average margin: `{report['averageMargin']:+.3f}`",
            f"- Advantage criteria: `{advantage}`",
            f"- Below-baseline criteria: `{below}`",
            f"- Missing brief markers: `{missing}`",
            f"- Benchmark passed: `{'yes' if report['passed'] else 'no'}`",
            f"- Phase 2 allowed: `{'yes' if report['phase2Allowed'] else 'no'}`",
            "",
            "## Score Comparison",
            "",
            *score_rows,
            "",
            "## Brief-To-Asset Evidence",
            "",
            *marker_rows,
            "",
            "## Rules",
            "",
            *[f"- {rule}" for rule in report["rules"]],
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Phase 1 visual benchmark report against Product Design's default ideation baseline.")
    parser.add_argument("--root", required=True, help="Run folder or Phase 1 folder.")
    parser.add_argument("--phase1-brief", required=True, help="Path to phase1-ui-brief.md.")
    parser.add_argument("--visual-gate", required=True, help="Path to phase1-visual-excellence-gate.json.")
    parser.add_argument("--selected-preview", default="", help="Optional selected preview path. Defaults to the gate selectedPreview.")
    parser.add_argument("--min-average", type=float, default=8.5, help="Minimum average selected-direction score.")
    parser.add_argument("--min-advantages", type=int, default=4, help="Minimum number of criteria that must beat the Product Design baseline.")
    parser.add_argument("--output-dir", required=True, help="Output directory for benchmark Markdown and JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    output_json = output_dir / "phase1-visual-benchmark.json"
    output_md = output_dir / "phase1-visual-benchmark.md"
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(markdown(report, output_dir), encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print(f"Benchmark passed: {'yes' if report['passed'] else 'no'}")


if __name__ == "__main__":
    main()
