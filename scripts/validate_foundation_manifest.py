#!/usr/bin/env python3
"""Validate Phase 2 foundation manifest coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_foundation_manifest import COMMON_ICONS, FOUNDATION_COMPONENTS, SCREEN_ASSET_SLOTS


REQUIRED_LAYER_FIELDS = (
    "sceneryPlane",
    "depthBand",
    "planePurpose",
    "componentizationRule",
    "layerRole",
    "zIndex",
    "compositingGroup",
    "occlusionPolicy",
    "mayMergeWith",
    "mustRemainSeparateFrom",
    "alphaRequired",
)


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def load_manifest(path: Path) -> dict:
    if not path.exists():
        fail(f"Manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Manifest is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        fail("Manifest root must be a JSON object")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        fail("Manifest must contain an entries array")
    return payload


def entry_matches(entry: dict, component: str, state: str) -> bool:
    entry_component = str(entry.get("component", ""))
    entry_state = str(entry.get("state", ""))
    entry_id = str(entry.get("id", ""))
    if entry_component == component and entry_state == state:
        return True
    return f"/{component}/{state}" in entry_id or entry_id.endswith(f"{component}/{state}")


def icon_matches(entry: dict, icon: str) -> bool:
    if str(entry.get("symbol", "")) == icon:
        return True
    if str(entry.get("component", "")) == "common-icon" and str(entry.get("state", "")) == icon:
        return True
    return str(entry.get("id", "")).endswith(f"/icon/{icon}")


def screen_slot_matches(entry: dict, category: str, state: str) -> bool:
    entry_category = str(entry.get("category", ""))
    entry_state = str(entry.get("state", ""))
    entry_id = str(entry.get("id", ""))
    if entry_category == category and entry_state == state:
        return True
    return f"/{category}/{state}" in entry_id


def validate_status(entries: list[dict], required_status: str) -> None:
    if not required_status:
        return
    mismatches = [
        str(entry.get("id", entry.get("assetPath", "<unknown>")))
        for entry in entries
        if str(entry.get("status", "")) != required_status
    ]
    if mismatches:
        preview = ", ".join(mismatches[:8])
        fail(f"{len(mismatches)} entries do not have status {required_status}: {preview}")


def validate_layer_contract(payload: dict, entries: list[dict]) -> None:
    layer_contract = payload.get("layerContract")
    if not isinstance(layer_contract, dict):
        fail("Manifest must contain a layerContract object")
    if layer_contract.get("schemaVersion") != "frontend-ui-pipeline.layer-contract.v1":
        fail("layerContract schemaVersion must be frontend-ui-pipeline.layer-contract.v1")
    scenery_allocation = layer_contract.get("sceneryPlaneAllocation")
    if not isinstance(scenery_allocation, dict):
        fail("layerContract must contain sceneryPlaneAllocation")

    missing_fields = []
    bad_types = []
    for entry in entries:
        entry_id = str(entry.get("id", entry.get("assetPath", "<unknown>")))
        for field in REQUIRED_LAYER_FIELDS:
            if field not in entry:
                missing_fields.append(f"{entry_id}:{field}")
        if "zIndex" in entry and not isinstance(entry.get("zIndex"), (int, float)):
            bad_types.append(f"{entry_id}:zIndex")
        for field in ("mayMergeWith", "mustRemainSeparateFrom"):
            if field in entry and not isinstance(entry.get(field), list):
                bad_types.append(f"{entry_id}:{field}")
        if "alphaRequired" in entry and not isinstance(entry.get("alphaRequired"), bool):
            bad_types.append(f"{entry_id}:alphaRequired")
        if "sceneryPlane" in entry and str(entry.get("sceneryPlane")) not in {"back", "mid", "content", "interaction", "front"}:
            bad_types.append(f"{entry_id}:sceneryPlane")

    if missing_fields:
        fail("Missing layer contract fields: " + ", ".join(missing_fields[:12]))
    if bad_types:
        fail("Invalid layer contract field types: " + ", ".join(bad_types[:12]))

    by_state = {str(entry.get("state")): entry for entry in entries if str(entry.get("id", "")).startswith("screen/")}
    required_order = [
        ("base-background", -100),
        ("content-surface", -20),
        ("foreground-frame", 50),
    ]
    missing = [state for state, _z in required_order if state not in by_state]
    if missing:
        fail("Missing layer preservation screen slots: " + ", ".join(missing))
    if not (
        by_state["base-background"]["zIndex"]
        < by_state["content-surface"]["zIndex"]
        < by_state["foreground-frame"]["zIndex"]
    ):
        fail("Layer order must keep base-background below content-surface below foreground-frame")

    required_planes = {
        "base-background": "back",
        "primary-illustration": "mid",
        "content-surface": "content",
        "foreground-frame": "front",
    }
    for state, plane in required_planes.items():
        if state not in by_state:
            fail(f"Missing required scenery state: {state}")
        if by_state[state].get("sceneryPlane") != plane:
            fail(f"{state} must be assigned to sceneryPlane {plane}")

    foreground_separate = set(by_state["foreground-frame"].get("mustRemainSeparateFrom", []))
    for required in ("base-background", "content-surface"):
        if required not in foreground_separate:
            fail(f"foreground-frame must remain separate from {required}")


def validate_manifest(args: argparse.Namespace) -> None:
    payload = load_manifest(Path(args.manifest).expanduser().resolve())
    entries = payload["entries"]
    normalized_entries = [entry for entry in entries if isinstance(entry, dict)]
    if len(normalized_entries) != len(entries):
        fail("Every manifest entry must be a JSON object")

    missing_components = []
    for component, states in FOUNDATION_COMPONENTS.items():
        for state in states:
            if not any(entry_matches(entry, component, state) for entry in normalized_entries):
                missing_components.append(f"{component}/{state}")

    missing_icons = [
        icon for icon in COMMON_ICONS if not any(icon_matches(entry, icon) for entry in normalized_entries)
    ]

    missing_screen_slots = []
    if args.require_screen_slots:
        for category, state, _path in SCREEN_ASSET_SLOTS:
            if not any(screen_slot_matches(entry, category, state) for entry in normalized_entries):
                missing_screen_slots.append(f"{category}/{state}")

    validate_status(normalized_entries, args.require_status)
    if args.require_layer_contract:
        validate_layer_contract(payload, normalized_entries)

    if missing_components:
        fail("Missing foundation component states: " + ", ".join(missing_components))
    if missing_icons:
        fail("Missing common icons: " + ", ".join(missing_icons))
    if missing_screen_slots:
        fail("Missing screen asset slots: " + ", ".join(missing_screen_slots))

    expected_component_states = sum(len(states) for states in FOUNDATION_COMPONENTS.values())
    ok(f"foundation component states: {expected_component_states}")
    ok(f"common icons: {len(COMMON_ICONS)}")
    if args.require_screen_slots:
        ok(f"screen asset slots: {len(SCREEN_ASSET_SLOTS)}")
    if args.require_layer_contract:
        ok("layer preservation contract")
        ok("scenery plane allocation")
    ok(f"entries inspected: {len(normalized_entries)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate full foundation manifest coverage.")
    parser.add_argument("manifest", help="Path to asset-manifest.json or generated foundation manifest.")
    parser.add_argument(
        "--no-screen-slots",
        dest="require_screen_slots",
        action="store_false",
        help="Only validate foundation components and icons.",
    )
    parser.add_argument(
        "--require-status",
        default="",
        help="Require every entry to have this status, such as review-pending or approved.",
    )
    parser.add_argument(
        "--no-layer-contract",
        dest="require_layer_contract",
        action="store_false",
        help="Skip layer preservation contract validation for legacy manifests.",
    )
    parser.set_defaults(require_screen_slots=True)
    parser.set_defaults(require_layer_contract=True)
    return parser.parse_args()


def main() -> None:
    validate_manifest(parse_args())


if __name__ == "__main__":
    main()
