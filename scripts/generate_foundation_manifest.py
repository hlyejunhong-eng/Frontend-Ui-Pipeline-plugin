#!/usr/bin/env python3
"""Generate a deterministic Phase 2 foundation asset manifest scaffold."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


COMMON_ICONS = [
    "home",
    "profile",
    "page",
    "scan",
    "cart",
    "payment",
    "chat",
    "confirm",
    "close",
    "back",
    "forward",
    "hot",
    "like",
    "settings",
    "help",
    "info",
    "wallet",
    "list",
    "favorite",
    "search",
]

FOUNDATION_COMPONENTS = {
    "button": [
        "primary",
        "secondary",
        "ghost",
        "danger",
        "disabled",
        "loading",
        "icon-only",
        "pressed",
    ],
    "numeric-badge": [
        "neutral",
        "accent",
        "success",
        "warning",
        "danger",
        "dot",
        "count",
    ],
    "card": [
        "flat",
        "elevated",
        "selected",
        "disabled",
        "media",
        "metric",
        "action-card",
    ],
    "combobox": [
        "closed",
        "open",
        "selected",
        "search-filtered",
        "empty",
        "disabled",
        "error",
    ],
    "navigation": [
        "desktop-sidebar",
        "desktop-topbar",
        "mobile-compact",
    ],
    "notice-bar": [
        "info",
        "success",
        "warning",
        "danger",
        "dismissible",
    ],
    "search-bar": [
        "idle",
        "focused",
        "with-value",
        "loading",
        "empty-result",
        "clear-button",
    ],
    "section-title": [
        "eyebrow",
        "title",
        "subtitle",
        "action-slot",
        "divider",
    ],
    "modal": [
        "default",
        "destructive-confirmation",
        "form-modal",
        "mobile-sheet",
        "overlay",
        "close-action",
        "focus",
    ],
    "transition": [
        "page-enter",
        "page-exit",
        "modal-enter",
        "modal-exit",
        "button-press",
        "hover",
        "loading-shimmer",
        "reduced-motion",
    ],
}

SCREEN_ASSET_SLOTS = [
    ("background", "base-background", "backgrounds/{screen}/base-background.svg"),
    ("background", "depth-overlay", "backgrounds/{screen}/depth-overlay.svg"),
    ("illustration", "primary-illustration", "illustrations/{screen}/primary-illustration@2x.png"),
    ("mask", "special-mask", "masks/{screen}/special-mask.svg"),
    ("texture", "surface-texture", "textures/{screen}/surface-texture@2x.png"),
    ("effect", "motion-overlay", "effects/{screen}/motion-overlay.svg"),
]


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "screen"


def selector_for(component: str, state: str) -> str:
    prefix = {
        "button": "fup-btn",
        "numeric-badge": "fup-badge",
        "card": "fup-card",
        "combobox": "fup-combobox",
        "navigation": "fup-nav",
        "notice-bar": "fup-notice",
        "search-bar": "fup-search",
        "section-title": "fup-section",
        "modal": "fup-modal",
        "transition": "fup-transition",
    }[component]
    if state in {"default", "idle", "closed", "neutral", "flat", "title"}:
        return f".{prefix}"
    return f".{prefix}-{state}"


def build_manifest(args: argparse.Namespace) -> dict:
    screen = slugify(args.screen)
    assets_root = args.assets_root.strip("/").rstrip("/")
    css_path = args.foundation_css
    icon_sprite = args.icon_sprite

    entries = []
    for slot_type, slot_name, path_template in SCREEN_ASSET_SLOTS:
        path = path_template.format(screen=screen)
        entries.append(
            {
                "id": f"screen/{screen}/{slot_type}/{slot_name}",
                "category": slot_type,
                "component": screen,
                "state": slot_name,
                "assetPath": f"{assets_root}/{path}",
                "layer": slot_type,
                "status": args.status,
                "purpose": f"{slot_name} asset for {args.screen}",
                "importRule": "Replace this scaffold path with the generated asset path if the art tool exports a different file.",
            }
        )

    for component, states in FOUNDATION_COMPONENTS.items():
        for state in states:
            category = "motion" if component == "transition" else "component"
            entries.append(
                {
                    "id": f"foundation/{component}/{state}",
                    "category": category,
                    "component": component,
                    "state": state,
                    "assetPath": f"{assets_root}/{css_path}",
                    "selector": selector_for(component, state),
                    "layer": "motion" if category == "motion" else "controls",
                    "status": args.status,
                    "purpose": f"{component} {state} foundation state",
                    "importRule": "Import the foundation CSS once, then apply the selector in the target frontend.",
                }
            )

    for icon in COMMON_ICONS:
        entries.append(
            {
                "id": f"foundation/icon/{icon}",
                "category": "icon",
                "component": "common-icon",
                "state": icon,
                "assetPath": f"{assets_root}/{icon_sprite}",
                "symbol": icon,
                "layer": "icons",
                "status": args.status,
                "purpose": f"{icon} icon in the shared foundation set",
                "importRule": "Use the SVG symbol from the shared sprite, or replace with an equivalent per-icon SVG file if the target runtime requires it.",
            }
        )

    coverage = {
        "screenAssetSlots": len(SCREEN_ASSET_SLOTS),
        "foundationComponents": {
            component: len(states) for component, states in FOUNDATION_COMPONENTS.items()
        },
        "commonIcons": len(COMMON_ICONS),
        "totalEntries": len(entries),
    }

    return {
        "schemaVersion": "frontend-ui-pipeline.foundation-manifest.v1",
        "project": {
            "name": args.project,
            "screen": args.screen,
            "targetRoute": args.target_route,
            "styleName": args.style_name,
            "mode": args.mode,
            "phase1Brief": args.phase1_brief,
            "previews": args.preview,
        },
        "assetsRoot": assets_root,
        "status": args.status,
        "coverage": coverage,
        "entries": entries,
        "approvalRequiredBeforeImplementation": args.mode == "production",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic foundation asset manifest scaffold for Phase 2."
    )
    parser.add_argument("--project", default="frontend-ui-pipeline")
    parser.add_argument("--screen", default="target-screen")
    parser.add_argument("--target-route", default="")
    parser.add_argument("--style-name", default="")
    parser.add_argument("--mode", choices=["production", "demo"], default="production")
    parser.add_argument(
        "--status",
        choices=["planned", "review-pending", "approved", "implemented"],
        default="planned",
    )
    parser.add_argument("--phase1-brief", default="")
    parser.add_argument("--preview", action="append", default=[])
    parser.add_argument("--assets-root", default="assets")
    parser.add_argument(
        "--foundation-css",
        default="components/foundation/foundation-kit.css",
        help="Path under assets root for the generated foundation CSS.",
    )
    parser.add_argument(
        "--icon-sprite",
        default="icons/foundation-icons.svg",
        help="Path under assets root for the shared icon sprite.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Destination JSON path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_manifest(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Entries: {manifest['coverage']['totalEntries']}")


if __name__ == "__main__":
    main()
