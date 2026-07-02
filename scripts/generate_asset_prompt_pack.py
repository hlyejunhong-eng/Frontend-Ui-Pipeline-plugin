#!/usr/bin/env python3
"""Generate a Phase 2 art-asset prompt pack from a Phase 1 brief and manifest."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


STRATEGY_NOTES = {
    "hybrid": "Use raster generation for rich backgrounds and illustrations, SVG/vector for icons and masks, and CSS/SVG for reusable component states and motion primitives.",
    "raster": "Use AI raster generation for illustration-heavy layers, then export transparent PNG/WebP layers plus SVG masks and CSS state rules.",
    "vector": "Use Figma/vector production for editable shapes, symbols, icons, masks, and components, then export SVG plus production CSS tokens.",
    "css-svg": "Use procedural SVG and CSS for deterministic assets, component states, icon sprites, and motion keyframes when raster tools are unavailable.",
}

SECTION_HINTS = [
    "Source Visual Inventory",
    "Selected Direction",
    "Layer Preservation Contract",
    "Background Spec",
    "Component Spec",
    "Motion Spec",
    "Phase 2 Generation Guide",
    "Asset Expectations",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_text(path: Path) -> str:
    if not path.exists():
        fail(f"Phase 1 brief does not exist: {path}")
    return path.read_text(encoding="utf-8")


def load_optional_text(path_value: str) -> str:
    if not path_value:
        return ""
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        fail(f"Source visual inventory does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    if len(text) <= 2600:
        return text.strip()
    return text[:2600].rstrip() + "\n..."


def load_manifest(path: Path) -> dict:
    if not path.exists():
        fail(f"Manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Manifest is not valid JSON: {exc}")
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        fail("Manifest must be a JSON object with an entries array")
    return payload


def extract_section(text: str, heading: str, max_chars: int = 1800) -> str:
    pattern = re.compile(
        rf"^##+\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##+\s+|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return ""
    body = match.group("body").strip()
    if len(body) <= max_chars:
        return body
    return body[:max_chars].rstrip() + "\n..."


def brief_style_contract(text: str) -> str:
    parts = []
    for heading in SECTION_HINTS:
        section = extract_section(text, heading)
        if section:
            parts.append(f"### {heading}\n{section}")
    if parts:
        return "\n\n".join(parts)
    clipped = text.strip()[:2600]
    return clipped + ("\n..." if len(text.strip()) > 2600 else "")


def group_entries(entries: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        if isinstance(entry, dict):
            grouped[str(entry.get("category", "unknown"))].append(entry)
    return grouped


def grouped_components(entries: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("category", "")) in {"component", "motion", "icon"}:
            grouped[str(entry.get("component", "unknown"))].append(entry)
    return grouped


def entry_line(entry: dict) -> str:
    entry_id = entry.get("id", "")
    state = entry.get("state", "")
    asset_path = entry.get("assetPath", "")
    layer = entry.get("layer", "")
    layer_role = entry.get("layerRole", "")
    scenery_plane = entry.get("sceneryPlane", "")
    depth_band = entry.get("depthBand", "")
    plane_purpose = entry.get("planePurpose", "")
    z_index = entry.get("zIndex", "")
    group = entry.get("compositingGroup", "")
    occlusion = entry.get("occlusionPolicy", "")
    selector = entry.get("selector", "")
    symbol = entry.get("symbol", "")
    suffix = []
    if selector:
        suffix.append(f"selector `{selector}`")
    if symbol:
        suffix.append(f"symbol `{symbol}`")
    if layer:
        suffix.append(f"layer `{layer}`")
    if layer_role:
        suffix.append(f"role `{layer_role}`")
    if scenery_plane:
        suffix.append(f"scenery `{scenery_plane}`")
    if depth_band:
        suffix.append(f"depth `{depth_band}`")
    if plane_purpose:
        suffix.append(f"purpose `{plane_purpose}`")
    if z_index != "":
        suffix.append(f"z `{z_index}`")
    if group:
        suffix.append(f"group `{group}`")
    if occlusion:
        suffix.append(f"occlusion `{occlusion}`")
    suffix_text = "; ".join(suffix)
    return f"- `{entry_id}` -> `{asset_path}`; state `{state}`" + (f"; {suffix_text}" if suffix_text else "")


def build_prompt_pack(args: argparse.Namespace, brief: str, manifest: dict, source_inventory: str = "") -> str:
    entries = [entry for entry in manifest["entries"] if isinstance(entry, dict)]
    grouped = group_entries(entries)
    components = grouped_components(entries)
    coverage = manifest.get("coverage", {})
    project = manifest.get("project", {})
    project_name = project.get("name", args.project)
    screen = project.get("screen", args.screen)
    style_name = project.get("styleName", args.style_name)
    target_route = project.get("targetRoute", "")
    assets_root = manifest.get("assetsRoot", "assets")
    status = manifest.get("status", "planned")
    layer_contract = manifest.get("layerContract", {}) if isinstance(manifest.get("layerContract"), dict) else {}
    foundation_count = coverage.get("foundationComponents", {})
    if isinstance(foundation_count, dict):
        foundation_total = sum(foundation_count.values())
    else:
        foundation_total = "unknown"

    lines = [
        f"# Phase 2 Asset Prompt Pack: {screen or project_name}",
        "",
        "## Source",
        "",
        f"- Project: `{project_name}`",
        f"- Screen: `{screen}`",
        f"- Target route: `{target_route}`",
        f"- Style name: `{style_name}`",
        f"- Assets root: `{assets_root}`",
        f"- Manifest status: `{status}`",
        f"- Strategy: `{args.strategy}`",
        "",
        "## Strategy",
        "",
        STRATEGY_NOTES[args.strategy],
        "",
        "Use this pack to generate real frontend-consumable assets. Do not create mood boards, empty placeholders, or screenshots that cannot be sliced into the manifest paths.",
        "",
        "## Global Style Contract",
        "",
        brief_style_contract(brief),
        "",
        "## Source Visual Inventory",
        "",
        source_inventory
        or "Use the Source Visual Inventory section in the Phase 1 brief. If no code inventory exists, record that Phase 1 did not have source code access.",
        "",
        "Phase 2 must generate corresponding assets/components for source-derived buttons, controls, component families, icons/media, visual states, and interaction settings. If a source-derived item is replaced by a new approved component, document the mapping instead of silently dropping it.",
        "",
        "## Negative Prompt / Avoid",
        "",
        "- Avoid generic SaaS cards, stock-photo atmosphere, unreadable small text, decorative blobs, mismatched icon styles, and assets that cannot be exported separately.",
        "- Avoid baking live copy into background art unless the manifest entry is explicitly a text image.",
        "- Avoid flattening foreground frames, rim lights, bevels, glints, masks, particles, or card-edge decoration into the base background when content surfaces sit between them.",
        "- Avoid merging assets across different z-index, compositing group, or occlusion policy values.",
        "- Avoid changing the approved color, typography, radius, stroke, shadow, and motion language from Phase 1.",
        "",
        "## Layer Preservation Contract",
        "",
        "Treat the approved preview like a staged illustration, not a single flat image. Preserve the atmosphere by splitting only along visual planes that can be recomposed without changing depth.",
        "",
        "## Scenery Plane Allocation",
        "",
        "Before generating any illustration-level component, assign the page scenery into back, mid, content, interaction, and front planes. Generate components from that allocation, not from arbitrary cropping.",
        "",
        "- Back scenery: far-field background, environmental light, large gradients, horizon/grid/depth context.",
        "- Mid scenery: product motif, character/object/scene illustration, depth anchors, visual focal shapes.",
        "- Content plane: panels, cards, glass/material surfaces, masks, clipped texture.",
        "- Interaction plane: text, controls, icons, input affordances, stateful UI.",
        "- Front scenery: foreground frame, edge ornaments, glints, particles, motion sweeps, top-plane atmosphere.",
        "",
        "- Base background and ambient depth stay on the lowest planes.",
        "- Primary illustration/motifs remain behind or around content surfaces unless the Phase 1 layer map says otherwise.",
        "- Content surfaces are their own layer above background/illustration and below labels, controls, and foreground decoration.",
        "- Foreground frames, edge ornaments, rim lights, alert glows, particles, and motion overlays remain transparent top-plane assets when they visually sit above content.",
        "- Only merge assets when their `compositingGroup`, z-index band, and occlusion policy match.",
        "",
        *[f"- {rule}" for rule in layer_contract.get("rules", []) if isinstance(rule, str)],
        "",
        "## Layered Asset Prompts",
        "",
        "### AI Raster Prompt",
        "",
        "Generate layered raster assets only for background depth, illustration, texture, and atmospheric effects. Export transparent PNG/WebP layers when the foreground must remain composable.",
        "",
    ]

    for category in ("background", "illustration", "surface", "texture", "effect", "mask", "overlay"):
        items = grouped.get(category, [])
        if not items:
            continue
        lines.extend([f"#### {category.title()} Assets", ""])
        for entry in items:
            lines.extend(
                [
                    entry_line(entry),
                    f"  Prompt: create `{entry.get('state', '')}` for `{screen}` in the approved `{style_name}` direction. Preserve layer role `{entry.get('layerRole', entry.get('layer', category))}`, z-index `{entry.get('zIndex', '')}`, compositing group `{entry.get('compositingGroup', '')}`, transparent edges when composited, and export to the exact manifest path.",
                    f"  Scenery plane: {entry.get('sceneryPlane', 'unspecified')} / {entry.get('depthBand', 'unspecified')}. Purpose: {entry.get('planePurpose', 'follow the scenery allocation')}",
                    f"  Componentization: {entry.get('componentizationRule', 'generate according to the owning visual plane')}",
                    f"  Occlusion: {entry.get('occlusionPolicy', 'follow the Phase 1 layer map')}",
                    f"  Must remain separate from: {', '.join(str(item) for item in entry.get('mustRemainSeparateFrom', [])) if isinstance(entry.get('mustRemainSeparateFrom'), list) else entry.get('mustRemainSeparateFrom', '')}",
                    "  Refinement knobs: opacity, blur, grain, saturation, crop anchor, highlight intensity, mask softness, z-index, blend mode, and foreground overlap tolerance.",
                    "",
                ]
            )

    lines.extend(
        [
            "### Figma/Vector Prompt",
            "",
            "Create editable vector assets for icons, masks, rails, component outlines, and reusable symbols. Keep names lower-kebab-case and match manifest ids.",
            "",
        ]
    )
    for entry in grouped.get("icon", []):
        lines.append(entry_line(entry))
    if grouped.get("icon"):
        lines.extend(
            [
                "",
                "Icon requirements: one visual language, consistent stroke, aligned optical center, 24 px base grid, readable at 16 px and 32 px, no emoji fallback.",
                "",
            ]
        )

    lines.extend(
        [
            "### CSS/SVG Component Prompt",
            "",
            "Generate the foundation component kit as frontend-ready CSS/SVG primitives. Keep every state represented, even when the target screen does not currently use it.",
            "",
        ]
    )
    for component, items in sorted(components.items()):
        if component == "common-icon":
            continue
        states = ", ".join(str(item.get("state", "")) for item in items)
        lines.extend([f"#### {component}", "", f"States: {states}", ""])
        for entry in items:
            lines.append(entry_line(entry))
        lines.append("")

    lines.extend(
        [
            "## Motion Prompt",
            "",
            "Create motion primitives as CSS keyframes, JSON descriptors, or frame sequences only when frames are required. Include trigger, duration, easing, delay, loop behavior, and reduced-motion fallback.",
            "",
        ]
    )
    for entry in components.get("transition", []):
        lines.append(entry_line(entry))
    lines.extend(
        [
            "",
            "## Review Checklist",
            "",
            f"- Screen asset slots: `{coverage.get('screenAssetSlots', 'unknown')}`",
            f"- Foundation states: `{foundation_total}`",
            f"- Common icons: `{coverage.get('commonIcons', 'unknown')}`",
            f"- Total manifest entries: `{coverage.get('totalEntries', len(entries))}`",
            "- Every asset renders visibly in the contact sheet.",
            "- Every generated file path matches the manifest or the manifest is updated before validation.",
            "- Every manifest entry keeps layerRole, zIndex, compositingGroup, occlusionPolicy, mayMergeWith, mustRemainSeparateFrom, and alphaRequired.",
            "- Every manifest entry keeps sceneryPlane, depthBand, planePurpose, and componentizationRule.",
            "- Source-derived buttons, components, icons/media, visual states, and interaction settings are generated or explicitly mapped to approved replacements.",
            "- Top-plane decoration that crosses over content remains a separate transparent asset and is visible in the asset-assembled primary screen preview.",
            "- The user must approve the review package before final Phase 2 handoff or Phase 3 implementation.",
            "",
            "## Commands",
            "",
            "```bash",
            "python3 <plugin-root>/scripts/validate_foundation_manifest.py <phase2-folder>/asset-manifest.json --require-status review-pending",
            "python3 <plugin-root>/scripts/serve_review.py <phase2-folder>/review --entry component-contact-sheet.html",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Phase 2 asset prompt pack.")
    parser.add_argument("--phase1-brief", required=True, help="Path to phase1-ui-brief.md")
    parser.add_argument("--manifest", required=True, help="Path to Phase 2 asset manifest JSON")
    parser.add_argument("--source-visual-inventory", default="", help="Optional phase1-source-visual-inventory.md/json path")
    parser.add_argument("--output", required=True, help="Destination Markdown file")
    parser.add_argument("--strategy", choices=sorted(STRATEGY_NOTES), default="hybrid")
    parser.add_argument("--project", default="frontend-ui-pipeline")
    parser.add_argument("--screen", default="target-screen")
    parser.add_argument("--style-name", default="approved-style")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    brief_path = Path(args.phase1_brief).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    pack = build_prompt_pack(args, load_text(brief_path), load_manifest(manifest_path), load_optional_text(args.source_visual_inventory))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(pack, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
