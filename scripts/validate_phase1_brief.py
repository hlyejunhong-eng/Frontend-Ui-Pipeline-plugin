#!/usr/bin/env python3
"""Validate that a Phase 1 UI brief can safely drive Phase 2 asset production."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from generate_foundation_manifest import COMMON_ICONS, FOUNDATION_COMPONENTS


REQUIRED_SECTIONS = {
    "context": ("context",),
    "source audit": ("source audit", "source evidence"),
    "preview": ("preview",),
    "layout spec": ("layout spec", "layout"),
    "background spec": ("background spec", "background"),
    "component spec": ("component spec", "component"),
    "copy spec": ("copy spec", "copy"),
    "button and control spec": ("button and control spec", "control spec"),
    "motion spec": ("motion spec", "motion"),
    "phase 2 generation guide": ("phase 2 generation guide",),
    "asset expectations": ("asset expectations", "asset list"),
    "acceptance checklist": ("acceptance checklist",),
}

REQUIRED_GUIDE_BLOCKS = {
    "layer map": ("layer map", "layer order", "layering"),
    "adjustable parameters": ("adjustable parameters", "refinement parameters"),
    "asset naming rules": ("asset naming rules", "naming rules"),
    "export rules": ("export rules",),
    "responsive crop rules": ("responsive crop rules", "responsive crop"),
    "complete component inventory": (
        "complete phase 2 component inventory",
        "complete foundation component inventory",
        "required phase 2 component inventory",
    ),
}

REQUIRED_LAYER_TERMS = [
    "background",
    "grid",
    "illustration",
    "card",
    "control",
    "text",
    "effect",
    "mask",
    "motion",
]

REQUIRED_PARAMETER_TERMS = [
    "opacity",
    "blur",
    "shadow",
    "highlight",
    "saturation",
    "stroke",
    "radius",
    "spacing",
    "duration",
    "easing",
    "crop",
]

COMPONENT_ALIASES = {
    "button": ("button", "buttons"),
    "numeric-badge": ("numeric badge", "numeric badges", "badge", "badges"),
    "card": ("card", "cards", "generic card", "generic cards"),
    "combobox": ("combobox", "combobox select", "select"),
    "navigation": ("navigation", "navigation bar", "nav"),
    "notice-bar": ("notice bar", "notice", "banner"),
    "search-bar": ("search bar", "search"),
    "section-title": ("section title", "section titles"),
    "modal": ("modal", "sheet", "dialog"),
    "transition": ("transition", "transition animation", "motion"),
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def normalize(value: str) -> str:
    lowered = value.lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", lowered)


def split_lines(text: str) -> list[str]:
    return [normalize(line) for line in text.splitlines()]


def has_any(text: str, aliases: tuple[str, ...]) -> bool:
    normalized = normalize(text)
    return any(normalize(alias).strip() in normalized for alias in aliases)


def state_matches(lines: list[str], state: str) -> bool:
    words = normalize(state).split()
    return any(all(word in line.split() for word in words) for line in lines)


def require_sections(text: str) -> None:
    missing = [
        section for section, aliases in REQUIRED_SECTIONS.items() if not has_any(text, aliases)
    ]
    if missing:
        fail("Missing required brief sections: " + ", ".join(missing))
    ok(f"brief sections: {len(REQUIRED_SECTIONS)}")


def require_phase2_guide(text: str) -> None:
    missing_blocks = [
        block for block, aliases in REQUIRED_GUIDE_BLOCKS.items() if not has_any(text, aliases)
    ]
    if missing_blocks:
        fail("Missing Phase 2 guide blocks: " + ", ".join(missing_blocks))

    normalized = normalize(text)
    missing_layers = [term for term in REQUIRED_LAYER_TERMS if term not in normalized]
    missing_parameters = [term for term in REQUIRED_PARAMETER_TERMS if term not in normalized]
    if missing_layers:
        fail("Missing Phase 2 layer terms: " + ", ".join(missing_layers))
    if missing_parameters:
        fail("Missing adjustable parameter terms: " + ", ".join(missing_parameters))
    ok("phase 2 generation guide")


def require_foundation_inventory(text: str) -> None:
    lines = split_lines(text)
    missing_states = []
    for component, states in FOUNDATION_COMPONENTS.items():
        aliases = COMPONENT_ALIASES.get(component, (component,))
        if not any(has_any(line, aliases) for line in lines):
            missing_states.append(component)
            continue
        for state in states:
            if not state_matches(lines, state):
                missing_states.append(f"{component}/{state}")

    missing_icons = [icon for icon in COMMON_ICONS if not state_matches(lines, icon)]
    if missing_states:
        fail("Missing foundation component states: " + ", ".join(missing_states))
    if missing_icons:
        fail("Missing common icons: " + ", ".join(missing_icons))
    ok(f"foundation component states: {sum(len(states) for states in FOUNDATION_COMPONENTS.values())}")
    ok(f"common icons: {len(COMMON_ICONS)}")


def require_preview_paths(text: str) -> None:
    preview_matches = re.findall(r"phase1-[a-z0-9-]*preview[a-z0-9-]*\.(?:png|jpg|jpeg|webp)", text, re.I)
    if not preview_matches:
        fail("Missing Phase 1 preview image path such as phase1-preview-desktop.png")
    ok(f"preview image references: {len(set(preview_matches))}")


def validate_brief(path: Path) -> None:
    if not path.exists():
        fail(f"Phase 1 brief does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < 1200:
        fail("Phase 1 brief is too short to be an implementation-grade handoff")
    require_sections(text)
    require_preview_paths(text)
    require_phase2_guide(text)
    require_foundation_inventory(text)
    ok("phase 1 brief is ready for Phase 2")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 1 UI brief readiness.")
    parser.add_argument("brief", help="Path to phase1-ui-brief.md")
    return parser.parse_args()


def main() -> None:
    validate_brief(Path(parse_args().brief).expanduser().resolve())


if __name__ == "__main__":
    main()
