#!/usr/bin/env python3
"""Validate Phase 2 foundation manifest coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_foundation_manifest import COMMON_ICONS, FOUNDATION_COMPONENTS, SCREEN_ASSET_SLOTS


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
    parser.set_defaults(require_screen_slots=True)
    return parser.parse_args()


def main() -> None:
    validate_manifest(parse_args())


if __name__ == "__main__":
    main()
