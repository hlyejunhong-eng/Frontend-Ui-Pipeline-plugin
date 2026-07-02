#!/usr/bin/env python3
"""Generate the final Phase 2 asset handoff after explicit user approval."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_MARKERS = (
    "approve",
    "approved",
    "pass",
    "passed",
    "accepted",
    "go ahead",
    "looks good",
    "通过",
    "同意",
    "确认",
    "可以",
)
ASSET_REVIEW_DECISION_SCHEMA = "frontend-ui-pipeline.asset-review-decision.v1"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"File does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"Expected a JSON object in {path}")
    return payload


def relpath(raw_path: str, output_path: Path) -> str:
    if not raw_path:
        return ""
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        return raw_path
    try:
        return os.path.relpath(path, output_path.parent)
    except ValueError:
        return str(path)


def approval_is_explicit(text: str) -> bool:
    lowered = text.strip().lower()
    return any(marker in lowered for marker in APPROVAL_MARKERS)


def approval_from_decision(path: str) -> str:
    if not path:
        return ""
    payload = load_json(Path(path).expanduser().resolve())
    if payload.get("schemaVersion") != ASSET_REVIEW_DECISION_SCHEMA:
        fail(f"approval-decision must use schema {ASSET_REVIEW_DECISION_SCHEMA}.")
    if payload.get("approved") is not True or payload.get("handoffAllowed") is not True:
        decision = payload.get("decision", "unknown")
        fail(f"Phase 2 asset review decision is not approved for handoff: {decision}")
    text = str(payload.get("approvalText") or payload.get("message") or "").strip()
    if not text:
        fail("approval-decision is approved but does not contain approvalText or message.")
    return text


def normalize_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(manifest.get("entries"), list):
        return [entry for entry in manifest["entries"] if isinstance(entry, dict)]

    entries: list[dict[str, Any]] = []
    for asset in manifest.get("assets", []):
        if not isinstance(asset, dict):
            continue
        states = asset.get("states") or asset.get("symbols") or []
        state_label = ", ".join(states) if isinstance(states, list) else str(states)
        entries.append(
            {
                "id": asset.get("owner", asset.get("path", "asset")),
                "category": asset.get("type", "asset"),
                "component": asset.get("owner", ""),
                "state": state_label or "default",
                "assetPath": asset.get("path", ""),
                "layer": asset.get("layer", ""),
                "sceneryPlane": asset.get("sceneryPlane", ""),
                "depthBand": asset.get("depthBand", ""),
                "planePurpose": asset.get("planePurpose", ""),
                "componentizationRule": asset.get("componentizationRule", ""),
                "layerRole": asset.get("layerRole", asset.get("layer", "")),
                "zIndex": asset.get("zIndex", ""),
                "compositingGroup": asset.get("compositingGroup", ""),
                "occlusionPolicy": asset.get("occlusionPolicy", ""),
                "mayMergeWith": asset.get("mayMergeWith", []),
                "mustRemainSeparateFrom": asset.get("mustRemainSeparateFrom", []),
                "alphaRequired": asset.get("alphaRequired", ""),
                "implementationHint": asset.get("implementationHint", ""),
                "purpose": asset.get("purpose", ""),
                "importRule": asset.get("importRule", ""),
                "dimensions": asset.get("dimensions", ""),
                "transparent": asset.get("transparent", ""),
            }
        )
    return entries


def project_value(manifest: dict[str, Any], key: str, fallback: str = "") -> str:
    project = manifest.get("project")
    if isinstance(project, dict) and project.get(key):
        return str(project[key])
    if manifest.get(key):
        return str(manifest[key])
    return fallback


def coverage_lines(manifest: dict[str, Any], entries: list[dict[str, Any]]) -> list[str]:
    coverage = manifest.get("coverage", {})
    if isinstance(coverage, dict):
        foundation = coverage.get("foundationComponents", {})
        foundation_total = sum(foundation.values()) if isinstance(foundation, dict) else "unknown"
        return [
            f"- Screen asset slots: `{coverage.get('screenAssetSlots', 'unknown')}`",
            f"- Foundation states: `{foundation_total}`",
            f"- Common icons: `{coverage.get('commonIcons', 'unknown')}`",
            f"- Total manifest entries: `{coverage.get('totalEntries', len(entries))}`",
        ]

    categories: dict[str, int] = {}
    for entry in entries:
        category = str(entry.get("category", "asset"))
        categories[category] = categories.get(category, 0) + 1
    lines = [f"- Total manifest entries: `{len(entries)}`"]
    lines.extend(f"- {category}: `{count}`" for category, count in sorted(categories.items()))
    return lines


def asset_table(entries: list[dict[str, Any]], output_path: Path) -> list[str]:
    lines = [
        "| Asset | Type | Component/State | Scenery | Layer Role | Z | Separate From | Import Rule |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        asset_path = relpath(str(entry.get("assetPath", "")), output_path)
        component = str(entry.get("component", ""))
        state = str(entry.get("state", ""))
        component_state = f"{component}/{state}".strip("/")
        separate_from = ", ".join(str(item) for item in entry.get("mustRemainSeparateFrom", [])[:4]) if isinstance(entry.get("mustRemainSeparateFrom"), list) else str(entry.get("mustRemainSeparateFrom", ""))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                asset_path,
                entry.get("category", ""),
                component_state,
                f"{entry.get('sceneryPlane', '')}/{entry.get('depthBand', '')}".strip("/"),
                entry.get("layerRole", entry.get("layer", "")),
                entry.get("zIndex", ""),
                separate_from,
                str(entry.get("importRule", "")).replace("\n", " "),
            )
        )
    return lines


def sortable_z(entry: dict[str, Any]) -> tuple[float, str]:
    value = entry.get("zIndex")
    if isinstance(value, (int, float)):
        return float(value), str(entry.get("id", entry.get("assetPath", "")))
    return 9999.0, str(entry.get("id", entry.get("assetPath", "")))


def assembly_lines(manifest: dict[str, Any], entries: list[dict[str, Any]]) -> list[str]:
    assembly = manifest.get("assemblyMap")
    if isinstance(assembly, list) and assembly:
        return [f"{index}. {item}" for index, item in enumerate(assembly, 1)]

    lines = []
    for entry in sorted(entries, key=sortable_z):
        if str(entry.get("category", "")) == "component" and str(entry.get("assetPath", "")).endswith(".css"):
            continue
        label = str(entry.get("assetPath", entry.get("id", "")))
        role = str(entry.get("layerRole", entry.get("layer", "")))
        z_index = entry.get("zIndex", "")
        policy = str(entry.get("occlusionPolicy", ""))
        lines.append(f"{len(lines) + 1}. `z={z_index}` `{role}`: {label}. {policy}")
    if not lines:
        lines.append("1. Use the manifest order as the assembly order, then refine by Phase 1 layer map.")
    return lines


def layer_contract_lines(manifest: dict[str, Any], entries: list[dict[str, Any]]) -> list[str]:
    contract = manifest.get("layerContract") if isinstance(manifest.get("layerContract"), dict) else {}
    rules = contract.get("rules") if isinstance(contract.get("rules"), list) else []
    lines = [
        "- Build separate stacking contexts for background, illustration, content surfaces, controls, foreground decoration, and motion overlays.",
        "- Do not flatten assets across different `compositingGroup`, `zIndex`, or `occlusionPolicy` values.",
        "- Foreground frames, rim lights, bevels, glints, masks, and particles that visually sit above content must remain transparent overlay assets.",
    ]
    lines.extend(f"- {rule}" for rule in rules)
    screen_entries = [
        entry
        for entry in entries
        if str(entry.get("id", "")).startswith("screen/") or entry.get("category") in {"background", "illustration", "surface", "mask", "texture", "overlay", "effect"}
    ]
    if screen_entries:
        lines.extend(["", "| Layer Role | Z | Group | Occlusion | Must Remain Separate From |", "| --- | --- | --- | --- | --- |"])
        for entry in sorted(screen_entries, key=sortable_z):
            separate_from = ", ".join(str(item) for item in entry.get("mustRemainSeparateFrom", [])[:6]) if isinstance(entry.get("mustRemainSeparateFrom"), list) else str(entry.get("mustRemainSeparateFrom", ""))
            lines.append(
                "| `{}` | `{}` | `{}` | {} | `{}` |".format(
                    entry.get("layerRole", entry.get("layer", "")),
                    entry.get("zIndex", ""),
                    entry.get("compositingGroup", ""),
                    str(entry.get("occlusionPolicy", "")).replace("\n", " "),
                    separate_from,
                )
            )
    return lines


def scenery_plane_lines(manifest: dict[str, Any], entries: list[dict[str, Any]]) -> list[str]:
    screen_entries = [
        entry
        for entry in entries
        if str(entry.get("id", "")).startswith("screen/")
        or entry.get("category") in {"background", "illustration", "surface", "mask", "texture", "overlay", "effect"}
    ]
    lines = [
        "- Assign and generate scenery before illustration-level component production: back scenery, mid scenery, content plane, interaction plane, then front scenery.",
        "- Preserve the Phase 1 atmosphere by keeping each scenery plane's purpose, crop anchor, occlusion behavior, and componentization rule intact.",
    ]
    if screen_entries:
        lines.extend(["", "| Scenery Plane | Depth Band | Asset | Purpose | Componentization |", "| --- | --- | --- | --- | --- |"])
        for entry in sorted(screen_entries, key=sortable_z):
            lines.append(
                "| `{}` | `{}` | `{}` | {} | {} |".format(
                    entry.get("sceneryPlane", ""),
                    entry.get("depthBand", ""),
                    entry.get("assetPath", entry.get("id", "")),
                    str(entry.get("planePurpose", "")).replace("\n", " "),
                    str(entry.get("componentizationRule", "")).replace("\n", " "),
                )
            )
    return lines


def component_usage(entries: list[dict[str, Any]]) -> list[str]:
    components: dict[str, set[str]] = {}
    for entry in entries:
        component = str(entry.get("component", "") or entry.get("category", "asset"))
        state = str(entry.get("state", "default"))
        components.setdefault(component, set()).add(state)
    lines = []
    for component, states in sorted(components.items()):
        state_list = ", ".join(sorted(states))
        lines.append(f"- `{component}`: states `{state_list}`.")
    return lines


def source_derived_component_mapping(args: argparse.Namespace, entries: list[dict[str, Any]]) -> list[str]:
    lines = [
        "- Phase 2 must preserve the Phase 1 Source Visual Inventory coverage: existing buttons, controls, component families, icons/media patterns, visual states, and interaction settings must be generated or explicitly mapped to approved replacements.",
    ]
    if args.source_visual_inventory:
        source_path = Path(args.source_visual_inventory).expanduser()
        if not source_path.exists():
            fail(f"source-visual-inventory does not exist: {source_path}")
        lines.append(f"- Source visual inventory: `{args.source_visual_inventory}`")
    else:
        lines.append("- Source visual inventory: see `phase1-ui-brief.md` or `phase2-asset-prompt-pack.md`.")

    components: dict[str, set[str]] = {}
    for entry in entries:
        category = str(entry.get("category", ""))
        if category not in {"component", "icon", "motion"}:
            continue
        component = str(entry.get("component", category) or category)
        state = str(entry.get("state", "default") or "default")
        components.setdefault(component, set()).add(state)
    lines.extend(["", "| Phase 2 Component/Asset | Covered States | Source-Derived Use |", "| --- | --- | --- |"])
    for component, states in sorted(components.items()):
        lines.append(f"| `{component}` | `{', '.join(sorted(states))}` | Map source-derived usage to this approved generated item or document replacement. |")
    if not components:
        lines.append("| - | - | No generated component/icon/motion entries found; return to Phase 2 before implementation. |")
    return lines


def phase3_component_reuse_contract(entries: list[dict[str, Any]]) -> list[str]:
    visible_components: dict[str, set[str]] = {}
    for entry in entries:
        category = str(entry.get("category", "") or entry.get("type", "")).lower()
        asset_path = str(entry.get("assetPath", "")).lower()
        if category == "html" or asset_path.endswith(".html") or "review" in asset_path:
            continue
        component = str(entry.get("component", "") or entry.get("category", "") or "asset")
        state = str(entry.get("state", "default") or "default")
        visible_components.setdefault(component, set()).add(state)

    lines = [
        "- Phase 3 must treat this approved Phase 2 manifest as a closed visible component inventory.",
        "- Do not generate new visible component families, visual states, borders, fills, shadows, ornaments, icon treatments, illustration layers, or motion states during implementation.",
        "- If live copy must bind to an approved background or component slot, Phase 3 may add invisible text-binding boxes, transparent text fields, or hidden backing text frames solely for layout/data/focus binding.",
        "- Text-binding helpers must not introduce visible border, background, radius, shadow, decoration, or component silhouette unless that visual treatment already appears in the approved Phase 2 manifest.",
        "- If a required visible component is missing, return to `$frontend-asset-production` for revision instead of inventing it in Phase 3.",
        "",
        "| Approved Component | Approved States |",
        "| --- | --- |",
    ]
    for component, states in sorted(visible_components.items()):
        lines.append(f"| `{component}` | `{', '.join(sorted(states))}` |")
    if not visible_components:
        lines.append("| - | No visible component entries were found; Phase 3 must return to Phase 2 before implementation. |")
    return lines


def motion_rules(entries: list[dict[str, Any]]) -> list[str]:
    motion_entries = [
        entry
        for entry in entries
        if entry.get("category") == "motion" or "transition" in str(entry.get("component", "")) or "motion" in str(entry.get("layer", ""))
    ]
    if not motion_entries:
        return [
            "- Use Phase 1 motion spec for page enter/exit, modal enter/exit, button press, hover, loading shimmer, and reduced-motion fallback.",
        ]
    return [
        f"- `{entry.get('id', entry.get('assetPath', 'motion'))}`: trigger from Phase 1 motion spec; preserve reduced-motion fallback."
        for entry in motion_entries
    ]


def build_markdown(args: argparse.Namespace, manifest: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    output_path = Path(args.output).expanduser().resolve()
    screen = project_value(manifest, "screen", project_value(manifest, "name", "target-screen"))
    target_route = project_value(manifest, "targetRoute", project_value(manifest, "target_route", ""))
    style_name = project_value(manifest, "styleName", project_value(manifest, "style_name", ""))
    approved_at = args.approved_at or datetime.now(timezone.utc).isoformat(timespec="seconds")

    source_lines = [
        f"- Phase 1 brief: `{relpath(args.phase1_brief or project_value(manifest, 'phase1Brief'), output_path)}`",
        f"- Asset manifest: `{relpath(args.manifest, output_path)}`",
        f"- Prompt pack: `{relpath(args.prompt_pack, output_path)}`" if args.prompt_pack else "- Prompt pack: not provided",
        f"- Review packet: `{relpath(args.review_packet, output_path)}`" if args.review_packet else "- Review packet: not provided",
        f"- Contact sheet: `{relpath(args.contact_sheet, output_path)}`" if args.contact_sheet else "- Contact sheet: not provided",
        f"- Asset-assembled primary screen preview: `{relpath(args.assembly_preview, output_path)}`" if args.assembly_preview else "- Asset-assembled primary screen preview: not provided",
        f"- Visual diff report: `{relpath(args.visual_diff_report, output_path)}`" if args.visual_diff_report else "- Visual diff report: not provided",
    ]

    lines = [
        f"# Phase 2 Asset Handoff: {screen}",
        "",
        "## Approval",
        "",
        f"- Approved by: `{args.approved_by}`",
        f"- Approved at: `{approved_at}`",
        f"- Approval text: `{args.approval_text.strip()}`",
        f"- Manifest status at handoff: `{manifest.get('status', 'unknown')}`",
        "",
        "## Source References",
        "",
        *source_lines,
        "",
        "## Target",
        "",
        f"- Target route/component: `{target_route}`" if target_route else "- Target route/component: not provided",
        f"- Approved style: `{style_name}`" if style_name else "- Approved style: see Phase 1 brief",
        f"- Target framework/runtime: `{args.target_runtime}`" if args.target_runtime else "- Target framework/runtime: inspect in Phase 3",
        "",
        "## Coverage",
        "",
        *coverage_lines(manifest, entries),
        "",
        "## Asset Manifest",
        "",
        *asset_table(entries, output_path),
        "",
        "## Assembly Map",
        "",
        *assembly_lines(manifest, entries),
        "",
        "## Layer Preservation Contract",
        "",
        *layer_contract_lines(manifest, entries),
        "",
        "## Scenery Plane Allocation",
        "",
        *scenery_plane_lines(manifest, entries),
        "",
        "## Component Usage Rules",
        "",
        *component_usage(entries),
        "",
        "## Source-Derived Component Mapping",
        "",
        *source_derived_component_mapping(args, entries),
        "",
        "## Phase 3 Component Reuse Contract",
        "",
        *phase3_component_reuse_contract(entries),
        "",
        "## Motion Rules",
        "",
        *motion_rules(entries),
        "",
        "## Implementation Notes",
        "",
        "- Copy or import assets according to the `Asset Manifest` table; do not rename files in Phase 3 unless the manifest is updated at the same time.",
        "- Preserve the Layer Preservation Contract with separate DOM/CSS stacking contexts; do not collapse foreground decorations into background images.",
        "- Preserve the Scenery Plane Allocation; map back scenery, mid scenery, content plane, interaction plane, and front scenery into separate implementation layers before pixel tuning.",
        "- Implement `foreground-frame` and other top-plane decoration as transparent overlays above content surfaces when present.",
        "- Preserve and reuse the Phase 2 foundation kit even if the target screen currently uses only part of it; do not add new visible component families or states in Phase 3.",
        "- Preserve the Source-Derived Component Mapping; existing code buttons, components, visual states, and interaction settings must have generated Phase 2 equivalents or documented replacements.",
        "- Use invisible text-binding boxes, transparent text fields, or hidden backing text frames only to bind live text to approved background/component positions.",
        "- Use CSS/native UI for scalable controls when the manifest import rule says the visual is code-driven.",
        "- Use image assets for backgrounds, illustrations, masks, textures, and sprite/icon files named in the manifest.",
        "- Keep mocks isolated if real callable APIs are unavailable; preserve existing API client contracts when they exist.",
        "- Capture desktop and mobile screenshots after implementation, then run visual artifact and visual diff checks when comparable PNGs are available.",
        "",
        "## Phase 3 Acceptance Checklist",
        "",
        "- Approved assets copied or imported into the target app.",
        "- Layer Preservation Contract implemented: background, content surfaces, controls, foreground decoration, and motion overlays retain their z-index order.",
        "- Scenery Plane Allocation implemented: back, mid, content, interaction, and front scenery retain their Phase 1 visual role.",
        "- Phase 3 Component Reuse Contract followed: every visible component maps to the approved Phase 2 manifest; added text-binding helpers are hidden/transparent except for live text.",
        "- Source-derived component mapping followed: existing buttons/components/states/interactions are covered by approved generated assets/components or documented replacements.",
        "- Every implemented page screenshot reaches at least 99% similarity against its Phase 1 page image after pixel adjustment.",
        "- Foundation CSS/icons/motion available to future screens.",
        "- Real APIs connected when callable, otherwise mocks match the preview data shape.",
        "- Desktop and mobile screenshots captured.",
        "- `check_visual_artifacts.py` passes for screenshots.",
        "- `compare_visual_artifacts.py` report attached when comparable preview/screenshot PNGs exist.",
        "- Text, buttons, cards, navigation, modal, search, notices, icons, and transitions match the approved style.",
        "- Remaining visual/API risks are listed before handoff.",
        "",
        "Next recommended skill: `$frontend-implementation`.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate final phase2-asset-handoff.md after explicit approval.")
    parser.add_argument("--manifest", required=True, help="Path to Phase 2 asset manifest JSON.")
    parser.add_argument("--output", required=True, help="Output Markdown path, usually phase2-asset-handoff.md.")
    parser.add_argument("--approval-text", default="", help="Exact user approval text. Optional when --approval-decision is approved.")
    parser.add_argument("--approval-decision", default="", help="Optional phase2-asset-review-decision.json path.")
    parser.add_argument("--approved-by", default="user", help="Approver name or role.")
    parser.add_argument("--approved-at", default="", help="Approval timestamp. Defaults to current UTC time.")
    parser.add_argument("--phase1-brief", default="", help="Optional Phase 1 brief path.")
    parser.add_argument("--source-visual-inventory", default="", help="Optional phase1-source-visual-inventory.md/json path.")
    parser.add_argument("--prompt-pack", default="", help="Optional Phase 2 asset prompt pack path.")
    parser.add_argument("--review-packet", default="", help="Optional Phase 2 review packet Markdown or HTML path.")
    parser.add_argument("--contact-sheet", default="", help="Optional contact sheet path.")
    parser.add_argument("--assembly-preview", default="", help="Optional primary screen preview assembled from generated Phase 2 assets.")
    parser.add_argument("--visual-diff-report", default="", help="Optional visual diff report path.")
    parser.add_argument("--target-runtime", default="", help="Optional frontend runtime such as React, Vue, or uni-app.")
    parser.add_argument("--require-approved-status", action="store_true", help="Require manifest status to be approved.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    decision_text = approval_from_decision(args.approval_decision)
    normalized_approval = (args.approval_text or decision_text).strip()
    args.approval_text = normalized_approval
    if not approval_is_explicit(normalized_approval):
        fail("approval-text must contain an explicit approval/pass decision before final handoff can be generated.")

    manifest_path = Path(args.manifest).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    manifest = load_json(manifest_path)
    if args.require_approved_status and manifest.get("status") != "approved":
        fail("Manifest status must be approved when --require-approved-status is used.")
    entries = normalize_entries(manifest)
    if not entries:
        fail("Manifest does not contain asset entries.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_markdown(args, manifest, entries), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
