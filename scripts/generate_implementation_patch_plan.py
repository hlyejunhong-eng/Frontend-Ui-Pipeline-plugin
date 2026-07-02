#!/usr/bin/env python3
"""Generate a Phase 3 implementation patch plan before editing a real app."""

from __future__ import annotations

import argparse
import json
import os
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


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"JSON file does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"Expected JSON object in {path}")
    return payload


def rel(path: Path, root: Path) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def explicit_approval(text: str) -> bool:
    lowered = text.strip().lower()
    return any(marker in lowered for marker in APPROVAL_MARKERS)


def handoff_has_approval(path: Path | None) -> bool:
    if not path or not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "## Approval" in text and explicit_approval(text)


def normalize_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(manifest.get("entries"), list):
        return [entry for entry in manifest["entries"] if isinstance(entry, dict)]

    entries: list[dict[str, Any]] = []
    for asset in manifest.get("assets", []) if isinstance(manifest.get("assets"), list) else []:
        if not isinstance(asset, dict):
            continue
        states = asset.get("states") or asset.get("symbols") or asset.get("components") or []
        if isinstance(states, list):
            if states and isinstance(states[0], dict):
                state_label = ", ".join(str(item.get("name", "component")) for item in states[:12])
            else:
                state_label = ", ".join(str(item) for item in states[:24])
        else:
            state_label = str(states)
        entries.append(
            {
                "id": asset.get("owner", asset.get("path", "asset")),
                "category": asset.get("type", "asset"),
                "component": asset.get("owner", asset.get("type", "asset")),
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


def asset_path_map(inspection: dict[str, Any]) -> dict[str, str]:
    paths = {}
    for item in inspection.get("assetPaths", []) if isinstance(inspection.get("assetPaths"), list) else []:
        if isinstance(item, dict) and item.get("kind") and item.get("path"):
            paths[str(item["kind"])] = str(item["path"])
    return paths


def strip_assets_prefix(path: Path) -> Path:
    parts = list(path.parts)
    if parts and parts[0] == "assets":
        return Path(*parts[1:]) if len(parts) > 1 else Path(path.name)
    return path


def classify_entry(entry: dict[str, Any]) -> str:
    raw_type = str(entry.get("category", "") or entry.get("type", "")).lower()
    raw_path = str(entry.get("assetPath", "")).lower()
    if raw_type == "html" or raw_path.endswith(".html") or "review" in raw_path:
        return "review-only"
    if "css" in raw_type or raw_path.endswith(".css"):
        return "style"
    if "icon" in raw_type or "icons/" in raw_path or "sprite" in raw_type:
        return "icon"
    if "background" in raw_type or "backgrounds/" in raw_path:
        return "background"
    if "motion" in raw_type or "motion/" in raw_path:
        return "motion"
    if "component" in raw_type or "components/" in raw_path:
        return "component"
    return "asset"


def destination_for(entry: dict[str, Any], paths: dict[str, str]) -> str:
    asset_path = Path(str(entry.get("assetPath", "")))
    filename = asset_path.name or "asset"
    kind = classify_entry(entry)
    static_base = paths.get("static-assets") or paths.get("assets") or "public/frontend-ui-pipeline/"
    static_base = static_base.rstrip("/") + "/"
    shared_style = paths.get("shared-style", "src/styles/frontend-ui-pipeline.css")

    if kind == "style":
        return shared_style
    if kind == "icon":
        return static_base + "icons/" + filename
    if kind == "background":
        relative = strip_assets_prefix(asset_path)
        return static_base + relative.as_posix()
    if kind == "motion":
        relative = strip_assets_prefix(asset_path)
        return static_base + relative.as_posix()
    if kind == "component":
        relative = strip_assets_prefix(asset_path)
        return static_base + relative.as_posix()
    return static_base + strip_assets_prefix(asset_path).as_posix()


def source_for(entry: dict[str, Any], manifest_path: Path) -> Path:
    raw = str(entry.get("assetPath", ""))
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path
    return (manifest_path.parent / path).resolve()


def build_copy_operations(entries: list[dict[str, Any]], manifest_path: Path, inspection: dict[str, Any]) -> list[dict[str, Any]]:
    paths = asset_path_map(inspection)
    operations = []
    by_copy_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entry in entries:
        if not entry.get("assetPath"):
            continue
        kind = classify_entry(entry)
        if kind == "review-only":
            continue
        source = source_for(entry, manifest_path)
        destination = destination_for(entry, paths)
        key = (kind, str(source), destination)
        if key not in by_copy_key:
            operation = {
                "kind": kind,
                "source": str(source),
                "sourceExists": source.exists(),
                "destination": destination,
                "component": entry.get("component", ""),
                "state": entry.get("state", ""),
                "importRule": entry.get("importRule", ""),
                "sceneryPlane": entry.get("sceneryPlane", ""),
                "depthBand": entry.get("depthBand", ""),
                "planePurpose": entry.get("planePurpose", ""),
                "componentizationRule": entry.get("componentizationRule", ""),
                "layerRole": entry.get("layerRole", entry.get("layer", "")),
                "zIndex": entry.get("zIndex", ""),
                "compositingGroup": entry.get("compositingGroup", ""),
                "occlusionPolicy": entry.get("occlusionPolicy", ""),
                "implementationHint": entry.get("implementationHint", ""),
                "alphaRequired": entry.get("alphaRequired", ""),
                "components": [],
                "states": [],
                "layerRoles": [],
                "sceneryPlanes": [],
                "depthBands": [],
                "planePurposes": [],
                "zIndexes": [],
                "compositingGroups": [],
                "occlusionPolicies": [],
                "mustRemainSeparateFrom": [],
                "entryCount": 0,
            }
            by_copy_key[key] = operation
            operations.append(operation)
        operation = by_copy_key[key]
        component = str(entry.get("component", "") or "")
        state = str(entry.get("state", "") or "")
        if component and component not in operation["components"]:
            operation["components"].append(component)
        if state and state not in operation["states"]:
            operation["states"].append(state)
        layer_role = str(entry.get("layerRole", entry.get("layer", "")) or "")
        if layer_role and layer_role not in operation["layerRoles"]:
            operation["layerRoles"].append(layer_role)
        scenery_plane = str(entry.get("sceneryPlane", "") or "")
        if scenery_plane and scenery_plane not in operation["sceneryPlanes"]:
            operation["sceneryPlanes"].append(scenery_plane)
        depth_band = str(entry.get("depthBand", "") or "")
        if depth_band and depth_band not in operation["depthBands"]:
            operation["depthBands"].append(depth_band)
        plane_purpose = str(entry.get("planePurpose", "") or "")
        if plane_purpose and plane_purpose not in operation["planePurposes"]:
            operation["planePurposes"].append(plane_purpose)
        z_index = entry.get("zIndex", "")
        if z_index != "" and z_index not in operation["zIndexes"]:
            operation["zIndexes"].append(z_index)
        group = str(entry.get("compositingGroup", "") or "")
        if group and group not in operation["compositingGroups"]:
            operation["compositingGroups"].append(group)
        policy = str(entry.get("occlusionPolicy", "") or "")
        if policy and policy not in operation["occlusionPolicies"]:
            operation["occlusionPolicies"].append(policy)
        separate_from = entry.get("mustRemainSeparateFrom", [])
        if isinstance(separate_from, list):
            for item in separate_from:
                label = str(item)
                if label and label not in operation["mustRemainSeparateFrom"]:
                    operation["mustRemainSeparateFrom"].append(label)
        operation["entryCount"] += 1
    return operations


def component_reuse_ledger(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ledger: dict[str, dict[str, Any]] = {}
    for entry in entries:
        category = str(entry.get("category", "") or entry.get("type", "")).lower()
        asset_path = str(entry.get("assetPath", "")).lower()
        if category == "html" or asset_path.endswith(".html") or "review" in asset_path:
            continue
        component = str(entry.get("component", "") or entry.get("category", "") or "asset")
        if component not in ledger:
            ledger[component] = {
                "component": component,
                "states": [],
                "categories": [],
                "assetPaths": [],
                "allowedVisibleUse": "Reuse the approved Phase 2 component/state only; do not invent a new visual variant in Phase 3.",
            }
        state = str(entry.get("state", "default") or "default")
        category_label = str(entry.get("category", "") or entry.get("type", "") or "asset")
        asset_label = str(entry.get("assetPath", "") or "")
        if state and state not in ledger[component]["states"]:
            ledger[component]["states"].append(state)
        if category_label and category_label not in ledger[component]["categories"]:
            ledger[component]["categories"].append(category_label)
        if asset_label and asset_label not in ledger[component]["assetPaths"]:
            ledger[component]["assetPaths"].append(asset_label)
    return [ledger[key] for key in sorted(ledger)]


def build_file_operations(inspection: dict[str, Any], copy_operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target = inspection.get("target", {}) if isinstance(inspection.get("target"), dict) else {}
    target_file = target.get("absoluteFile") or target.get("route", {}).get("file", "")
    frameworks = inspection.get("frameworks", [])
    paths = asset_path_map(inspection)
    operations = []
    if target_file:
        operations.append(
            {
                "action": "modify",
                "path": str(target_file),
                "reason": "Hot-replace the target route visual structure while preserving API methods and route behavior.",
            }
        )
    if any(item["kind"] == "style" for item in copy_operations):
        operations.append(
            {
                "action": "create-or-merge-style",
                "path": paths.get("shared-style", "src/styles/frontend-ui-pipeline.css"),
                "reason": "Install Phase 2 foundation CSS, tokens, and motion keyframes.",
            }
        )
    if "uni-app" in frameworks:
        operations.append(
            {
                "action": "preserve-runtime",
                "path": "pages.json, manifest.json, App.vue, main.js",
                "reason": "Keep uni-app routing, primitives, rpx conventions, and HBuilderX runtime assumptions intact.",
            }
        )
    return operations


def api_preservation(inspection: dict[str, Any]) -> list[dict[str, Any]]:
    api_usage = inspection.get("apiUsage", {}) if isinstance(inspection.get("apiUsage"), dict) else {}
    items = []
    for api_file in api_usage.get("apiFiles", [])[:30]:
        items.append({"path": api_file, "rule": "Preserve existing API client file and method contracts."})
    for signal, hits in api_usage.get("signals", {}).items():
        for hit in hits[:12]:
            items.append(
                {
                    "path": hit.get("file", ""),
                    "rule": f"Preserve {signal} usage unless replacing it with a same-shape fixture at the call boundary.",
                    "count": hit.get("count", 0),
                }
            )
    return items


def verification_steps(inspection: dict[str, Any], screenshot_plan: str) -> list[str]:
    runtime = inspection.get("runtime", {}) if isinstance(inspection.get("runtime"), dict) else {}
    steps = []
    for command in runtime.get("recommendedCommands", []):
        if isinstance(command, dict) and command.get("command"):
            steps.append(str(command["command"]))
    if not steps and runtime.get("externalRuntimeNotes"):
        steps.append("Open the project in HBuilderX or the project-specific uni-app runtime.")
    if screenshot_plan:
        steps.append(f"Use screenshot QA plan: {screenshot_plan}")
    steps.extend(
        [
            "Run check_visual_artifacts.py on captured desktop/mobile screenshots.",
            "Run compare_visual_artifacts.py against approved Phase 1 previews when comparable PNGs are available.",
        ]
    )
    return steps


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = Path(args.manifest).expanduser().resolve()
    inspection_path = Path(args.inspection).expanduser().resolve()
    manifest = load_json(manifest_path)
    inspection = load_json(inspection_path)
    entries = normalize_entries(manifest)
    if not entries:
        fail("Manifest contains no asset entries.")

    handoff_path = Path(args.phase2_handoff).expanduser().resolve() if args.phase2_handoff else None
    approval_ready = explicit_approval(args.approval_text) or handoff_has_approval(handoff_path)
    copy_operations = build_copy_operations(entries, manifest_path, inspection)
    missing_sources = [item for item in copy_operations if not item["sourceExists"]]
    target = inspection.get("target", {}) if isinstance(inspection.get("target"), dict) else {}
    target_matched = bool(target.get("matched"))
    blocked = (not approval_ready) or (not target_matched)

    return {
        "schemaVersion": "frontend-ui-pipeline.implementation-patch-plan.v1",
        "manifest": str(manifest_path),
        "inspection": str(inspection_path),
        "phase2Handoff": str(handoff_path) if handoff_path else "",
        "approvalReady": approval_ready,
        "targetMatched": target_matched,
        "blockedBeforeEditing": blocked,
        "blockers": [
            *([] if approval_ready else ["Phase 2 assets are not explicitly approved; do not edit the production app."]),
            *([] if target_matched else ["Target route/file is not matched; locate the exact implementation target first."]),
        ],
        "targetRoot": inspection.get("root", ""),
        "frameworks": inspection.get("frameworks", []),
        "targetFile": target.get("absoluteFile", ""),
        "copyOperations": copy_operations,
        "phase2ComponentLedger": component_reuse_ledger(entries),
        "componentReuseContract": {
            "visibleComponentInventoryClosed": True,
            "allowedAdditions": [
                "invisible text-binding boxes",
                "transparent text fields",
                "hidden backing text frames",
            ],
            "forbiddenAdditions": [
                "new visible component families",
                "new visible component states",
                "new visible borders",
                "new visible fills",
                "new visible shadows",
                "new visible ornaments",
                "new icon treatments",
                "new motion states",
            ],
            "missingVisibleComponentRule": "Return to Phase 2 asset production instead of inventing the visible component in Phase 3.",
        },
        "missingSourceAssets": missing_sources,
        "fileOperations": build_file_operations(inspection, copy_operations),
        "apiPreservation": api_preservation(inspection),
        "runtimeNotes": inspection.get("runtime", {}).get("externalRuntimeNotes", []),
        "verificationSteps": verification_steps(inspection, args.screenshot_plan),
        "implementationOrder": [
            "Confirm Phase 2 approval and target route match.",
            "Copy approved static assets to the planned destination paths.",
            "Map back scenery, mid scenery, content plane, interaction plane, and front scenery into explicit implementation layers.",
            "Create or merge shared foundation style files.",
            "Build UI only from the Phase 2 component ledger; add only invisible/transparent text-binding helpers when live text must attach to approved component/background slots.",
            "Create explicit stacking contexts from the layer preservation hints before composing UI surfaces.",
            "Modify the target route/component while preserving API contracts.",
            "Wire real APIs when callable; otherwise add same-shape fixtures at the call boundary.",
            "Run available build/test/runtime checks or external runtime instructions.",
            "Capture desktop/mobile screenshots and run visual checks/diffs.",
        ],
    }


def markdown(plan: dict[str, Any]) -> str:
    copy_rows = ["| Kind | Role/Z | Source | Destination | Exists |", "| --- | --- | --- | --- | --- |"]
    for item in plan["copyOperations"]:
        role_z = ", ".join(item.get("layerRoles", [])[:3])
        z_values = ", ".join(str(value) for value in item.get("zIndexes", [])[:3])
        scenery = ", ".join(item.get("sceneryPlanes", [])[:3])
        depth = ", ".join(item.get("depthBands", [])[:3])
        role_z = f"{scenery}:{depth} / {role_z} / {z_values}".strip(" /:")
        copy_rows.append(
            f"| `{item['kind']}` | `{role_z}` | `{item['source']}` | `{item['destination']}` | `{'yes' if item['sourceExists'] else 'no'}` |"
        )
    if len(copy_rows) == 2:
        copy_rows.append("| - | - | No copy operations | - | - |")

    file_rows = ["| Action | Path | Reason |", "| --- | --- | --- |"]
    for item in plan["fileOperations"]:
        file_rows.append(f"| `{item['action']}` | `{item['path']}` | {item['reason']} |")
    if len(file_rows) == 2:
        file_rows.append("| - | No file operations | - |")

    api_lines = []
    for item in plan["apiPreservation"]:
        count = f" Count: `{item.get('count')}`." if item.get("count") else ""
        api_lines.append(f"- `{item.get('path')}`: {item.get('rule')}{count}")
    if not api_lines:
        api_lines = ["- No API usage detected by the target inspector."]
    blocker_lines = [f"- {item}" for item in plan["blockers"]] or ["- None."]
    missing_lines = [f"- `{item['source']}` -> `{item['destination']}`" for item in plan["missingSourceAssets"]] or ["- None."]
    ledger_rows = ["| Approved Component | Approved States | Categories |", "| --- | --- | --- |"]
    for item in plan.get("phase2ComponentLedger", []):
        ledger_rows.append(
            "| `{}` | `{}` | `{}` |".format(
                item.get("component", ""),
                ", ".join(item.get("states", [])),
                ", ".join(item.get("categories", [])),
            )
        )
    if len(ledger_rows) == 2:
        ledger_rows.append("| - | No approved visible components found | Return to Phase 2 |")
    reuse_contract = plan.get("componentReuseContract", {})
    allowed_helper_lines = [f"- {item}" for item in reuse_contract.get("allowedAdditions", [])] or ["- None."]
    forbidden_component_lines = [f"- {item}" for item in reuse_contract.get("forbiddenAdditions", [])] or ["- None."]
    runtime_lines = [f"- {item}" for item in plan["runtimeNotes"]] or ["- None."]
    layer_hint_lines = []
    for item in plan["copyOperations"]:
        roles = ", ".join(item.get("layerRoles", [])) or str(item.get("layerRole", ""))
        z_values = ", ".join(str(value) for value in item.get("zIndexes", []))
        groups = ", ".join(item.get("compositingGroups", []))
        policies = " / ".join(item.get("occlusionPolicies", [])[:2])
        separate = ", ".join(item.get("mustRemainSeparateFrom", [])[:6])
        if roles or z_values or groups or policies or separate:
            layer_hint_lines.append(
                f"- `{item['destination']}`: role `{roles}`, z `{z_values}`, group `{groups}`, occlusion {policies or '`not specified`'}, separate from `{separate}`."
            )
    if not layer_hint_lines:
        layer_hint_lines = ["- No layer preservation hints were found in the manifest; return to Phase 2 before visual implementation."]
    scenery_hint_lines = []
    for item in plan["copyOperations"]:
        planes = ", ".join(item.get("sceneryPlanes", []))
        bands = ", ".join(item.get("depthBands", []))
        purposes = " / ".join(item.get("planePurposes", [])[:2])
        if planes or bands or purposes:
            scenery_hint_lines.append(
                f"- `{item['destination']}`: scenery `{planes}`, depth `{bands}`, purpose {purposes or '`not specified`'}."
            )
    if not scenery_hint_lines:
        scenery_hint_lines = ["- No scenery plane hints were found in the manifest; return to Phase 2 before visual implementation."]
    verification_lines = [f"- `{item}`" if item.startswith(("npm ", "pnpm ", "yarn ", "Use ")) else f"- {item}" for item in plan["verificationSteps"]]
    order_lines = [f"{index}. {item}" for index, item in enumerate(plan["implementationOrder"], 1)]

    return "\n".join(
        [
            "# Phase 3 Implementation Patch Plan",
            "",
            "## Status",
            "",
            f"- Approval ready: `{'yes' if plan['approvalReady'] else 'no'}`",
            f"- Target matched: `{'yes' if plan['targetMatched'] else 'no'}`",
            f"- Blocked before editing: `{'yes' if plan['blockedBeforeEditing'] else 'no'}`",
            f"- Target root: `{plan['targetRoot']}`",
            f"- Target file: `{plan['targetFile'] or 'not matched'}`",
            f"- Frameworks: `{', '.join(plan['frameworks'])}`",
            "",
            "## Blockers",
            "",
            *blocker_lines,
            "",
            "## Copy Operations",
            "",
            *copy_rows,
            "",
            "## Missing Source Assets",
            "",
            *missing_lines,
            "",
            "## Phase 2 Component Reuse Ledger",
            "",
            *ledger_rows,
            "",
            "## Phase 3 Component Reuse Contract",
            "",
            f"- Visible component inventory closed: `{'yes' if reuse_contract.get('visibleComponentInventoryClosed') else 'no'}`",
            f"- Missing visible component rule: {reuse_contract.get('missingVisibleComponentRule', 'Return to Phase 2.')}",
            "- Allowed Phase 3 additions:",
            *allowed_helper_lines,
            "- Forbidden Phase 3 additions:",
            *forbidden_component_lines,
            "",
            "## File Operations",
            "",
            *file_rows,
            "",
            "## Layer Preservation Hints",
            "",
            *layer_hint_lines,
            "",
            "## Scenery Plane Hints",
            "",
            *scenery_hint_lines,
            "",
            "## API Preservation",
            "",
            *api_lines,
            "",
            "## Runtime Notes",
            "",
            *runtime_lines,
            "",
            "## Implementation Order",
            "",
            *order_lines,
            "",
            "## Verification Steps",
            "",
            *verification_lines,
            "",
            "Do not apply this plan to a production app while `Blocked before editing` is `yes`.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Phase 3 implementation patch plan.")
    parser.add_argument("--manifest", required=True, help="Phase 2 asset manifest JSON.")
    parser.add_argument("--inspection", required=True, help="Phase 3 target inspection JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory for patch plan Markdown and JSON.")
    parser.add_argument("--phase2-handoff", default="", help="Optional approved phase2-asset-handoff.md.")
    parser.add_argument("--approval-text", default="", help="Optional explicit approval text.")
    parser.add_argument("--screenshot-plan", default="", help="Optional phase3-screenshot-qa-plan.md path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(args)
    output_json = output_dir / "phase3-implementation-patch-plan.json"
    output_md = output_dir / "phase3-implementation-patch-plan.md"
    output_json.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(markdown(plan), encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print(f"Blocked before editing: {'yes' if plan['blockedBeforeEditing'] else 'no'}")


if __name__ == "__main__":
    main()
