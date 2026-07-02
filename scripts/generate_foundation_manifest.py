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
    ("surface", "content-surface", "surfaces/{screen}/content-surface.svg"),
    ("mask", "special-mask", "masks/{screen}/special-mask.svg"),
    ("texture", "surface-texture", "textures/{screen}/surface-texture@2x.png"),
    ("overlay", "foreground-frame", "overlays/{screen}/foreground-frame.svg"),
    ("effect", "motion-overlay", "effects/{screen}/motion-overlay.svg"),
]

SCENERY_PLANE_ALLOCATION = {
    "base-background": {
        "sceneryPlane": "back",
        "depthBand": "back-00",
        "planePurpose": "establish the lowest illustration atmosphere, canvas color, and far-field scene.",
        "componentizationRule": "Generate as full-bleed scenery, not as a UI component.",
    },
    "depth-overlay": {
        "sceneryPlane": "back",
        "depthBand": "back-10",
        "planePurpose": "add far-field depth, grid, light falloff, and environmental atmosphere.",
        "componentizationRule": "Generate as a transparent depth plane that may sit above the base background only.",
    },
    "primary-illustration": {
        "sceneryPlane": "mid",
        "depthBand": "mid-00",
        "planePurpose": "carry the main illustration motif and product-specific visual identity.",
        "componentizationRule": "Generate as an illustration-level component with transparent edges and stable crop anchors.",
    },
    "content-surface": {
        "sceneryPlane": "content",
        "depthBand": "content-00",
        "planePurpose": "hold UI panels, cards, and material surfaces that can cover midground illustration.",
        "componentizationRule": "Generate as reusable surface treatment or CSS/native component plane, not baked into background scenery.",
    },
    "special-mask": {
        "sceneryPlane": "content",
        "depthBand": "content-10",
        "planePurpose": "clip or reveal only its owning content or illustration plane.",
        "componentizationRule": "Generate as a mask attached to a named owner plane; never as a global flattened image.",
    },
    "surface-texture": {
        "sceneryPlane": "content",
        "depthBand": "content-20",
        "planePurpose": "add material feel inside UI surfaces without degrading text readability.",
        "componentizationRule": "Generate as clipped texture or pseudo-element treatment.",
    },
    "foreground-frame": {
        "sceneryPlane": "front",
        "depthBand": "front-00",
        "planePurpose": "preserve top-plane atmosphere, border ornaments, rim lights, glints, and edge frames.",
        "componentizationRule": "Generate as transparent foreground decoration above content surfaces.",
    },
    "motion-overlay": {
        "sceneryPlane": "front",
        "depthBand": "front-10",
        "planePurpose": "represent transient top-plane motion, sweeps, particles, and feedback effects.",
        "componentizationRule": "Generate as motion overlay or frame sequence, never flattened into static background.",
    },
}

SCREEN_LAYER_CONTRACT = {
    "base-background": {
        "layerRole": "background-base",
        "zIndex": -100,
        "compositingGroup": "background-system",
        "occlusionPolicy": "full-bleed lowest plane; never covers content or foreground decoration",
        "mayMergeWith": ["depth-overlay"],
        "mustRemainSeparateFrom": ["content-surface", "foreground-frame", "motion-overlay"],
        "alphaRequired": False,
        "implementationHint": "absolute inset 0; z-index:-100",
    },
    "depth-overlay": {
        "layerRole": "background-depth",
        "zIndex": -90,
        "compositingGroup": "background-system",
        "occlusionPolicy": "above base background, below illustration and all content surfaces",
        "mayMergeWith": ["base-background"],
        "mustRemainSeparateFrom": ["content-surface", "foreground-frame"],
        "alphaRequired": True,
        "implementationHint": "absolute inset 0; z-index:-90; pointer-events:none",
    },
    "primary-illustration": {
        "layerRole": "illustration-midground",
        "zIndex": -70,
        "compositingGroup": "illustration-system",
        "occlusionPolicy": "behind content surfaces unless the Phase 1 layer map marks a transparent overlap zone",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["content-surface", "foreground-frame", "interactive-controls"],
        "alphaRequired": True,
        "implementationHint": "absolute motif plane; z-index:-70; pointer-events:none",
    },
    "content-surface": {
        "layerRole": "content-surface",
        "zIndex": -20,
        "compositingGroup": "content-system",
        "occlusionPolicy": "above background and illustration; below text, controls, and foreground frame",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "depth-overlay", "primary-illustration", "foreground-frame"],
        "alphaRequired": True,
        "implementationHint": "surface container background/border plane; z-index:-20",
    },
    "special-mask": {
        "layerRole": "mask-or-clip",
        "zIndex": -10,
        "compositingGroup": "content-system",
        "occlusionPolicy": "clips or reveals its owning surface/illustration only; never flattens unrelated planes",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "foreground-frame", "interactive-controls"],
        "alphaRequired": True,
        "implementationHint": "CSS mask or clip-path on owning layer; preserve source asset",
    },
    "surface-texture": {
        "layerRole": "material-texture",
        "zIndex": -5,
        "compositingGroup": "content-system",
        "occlusionPolicy": "clipped inside surfaces or applied as blend overlay that never reduces text legibility",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "foreground-frame", "text-content"],
        "alphaRequired": True,
        "implementationHint": "surface pseudo-element; z-index:-5; mix-blend-mode only if readable",
    },
    "foreground-frame": {
        "layerRole": "foreground-decoration",
        "zIndex": 50,
        "compositingGroup": "foreground-decoration-system",
        "occlusionPolicy": "above content surfaces and background; may overlap card edges without covering readable text",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "depth-overlay", "primary-illustration", "content-surface"],
        "alphaRequired": True,
        "implementationHint": "absolute inset or anchored overlay; z-index:50; pointer-events:none",
    },
    "motion-overlay": {
        "layerRole": "motion-overlay",
        "zIndex": 70,
        "compositingGroup": "motion-system",
        "occlusionPolicy": "top transient visual effects; never bakes into static background",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "content-surface", "foreground-frame"],
        "alphaRequired": True,
        "implementationHint": "absolute animated overlay; z-index:70; reduced-motion fallback",
    },
}

FOUNDATION_LAYER_CONTRACT = {
    "component": {
        "sceneryPlane": "interaction",
        "depthBand": "interaction-00",
        "planePurpose": "carry readable controls and stateful UI above content surfaces.",
        "componentizationRule": "Generate as reusable frontend component treatment.",
        "layerRole": "interactive-controls",
        "zIndex": 10,
        "compositingGroup": "ui-controls",
        "occlusionPolicy": "above content surfaces, below foreground decoration and modal overlays",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "depth-overlay", "foreground-frame"],
        "alphaRequired": False,
        "implementationHint": "normal UI stacking context; preserve focus and press states",
    },
    "icon": {
        "sceneryPlane": "interaction",
        "depthBand": "interaction-10",
        "planePurpose": "support labels and controls with consistent icon language.",
        "componentizationRule": "Generate as SVG sprite or icon component in the control layer.",
        "layerRole": "ui-icons",
        "zIndex": 12,
        "compositingGroup": "ui-controls",
        "occlusionPolicy": "same plane as labels and controls; never bake into background art",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "depth-overlay"],
        "alphaRequired": True,
        "implementationHint": "inline SVG or icon component in the control layer",
    },
    "motion": {
        "sceneryPlane": "front",
        "depthBand": "front-20",
        "planePurpose": "add triggered interaction feedback above controls.",
        "componentizationRule": "Generate as CSS keyframes, JSON descriptor, or transparent motion frames.",
        "layerRole": "interaction-motion",
        "zIndex": 30,
        "compositingGroup": "motion-system",
        "occlusionPolicy": "triggered feedback above controls; never permanently obscures content",
        "mayMergeWith": [],
        "mustRemainSeparateFrom": ["base-background", "foreground-frame"],
        "alphaRequired": True,
        "implementationHint": "CSS keyframes/JSON descriptor with reduced-motion fallback",
    },
}

LAYER_CONTRACT_RULES = [
    "Before generating illustration-level components, analyze the page as back scenery, mid scenery, content plane, interaction plane, and front scenery.",
    "Only merge assets that share the same compositingGroup, zIndex band, and occlusionPolicy.",
    "Never bake foreground frames, rim lights, bevels, glints, masks, or particles into a base background when content surfaces sit between them.",
    "Content surfaces must stay above background and illustration planes but below text, controls, and declared foreground decoration.",
    "Any asset that overlaps both background and content must be transparent and exported as its own overlay unless the Phase 1 brief explicitly allows flattening.",
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


def with_layer_contract(entry: dict, contract: dict) -> dict:
    enriched = dict(entry)
    enriched.update(contract)
    return enriched


def build_manifest(args: argparse.Namespace) -> dict:
    screen = slugify(args.screen)
    assets_root = args.assets_root.strip("/").rstrip("/")
    css_path = args.foundation_css
    icon_sprite = args.icon_sprite

    entries = []
    for slot_type, slot_name, path_template in SCREEN_ASSET_SLOTS:
        path = path_template.format(screen=screen)
        contract = SCREEN_LAYER_CONTRACT[slot_name]
        scenery = SCENERY_PLANE_ALLOCATION[slot_name]
        entries.append(
            with_layer_contract(
                {
                "id": f"screen/{screen}/{slot_type}/{slot_name}",
                "category": slot_type,
                "component": screen,
                "state": slot_name,
                "assetPath": f"{assets_root}/{path}",
                "layer": contract["layerRole"],
                "status": args.status,
                "purpose": f"{slot_name} asset for {args.screen}",
                "importRule": "Replace this scaffold path with the generated asset path if the art tool exports a different file.",
                },
                {**scenery, **contract},
            )
        )

    for component, states in FOUNDATION_COMPONENTS.items():
        for state in states:
            category = "motion" if component == "transition" else "component"
            contract_key = "motion" if category == "motion" else "component"
            contract = FOUNDATION_LAYER_CONTRACT[contract_key]
            entries.append(
                with_layer_contract(
                    {
                    "id": f"foundation/{component}/{state}",
                    "category": category,
                    "component": component,
                    "state": state,
                    "assetPath": f"{assets_root}/{css_path}",
                    "selector": selector_for(component, state),
                    "layer": contract["layerRole"],
                    "status": args.status,
                    "purpose": f"{component} {state} foundation state",
                    "importRule": "Import the foundation CSS once, then apply the selector in the target frontend.",
                    },
                    contract,
                )
            )

    for icon in COMMON_ICONS:
        contract = FOUNDATION_LAYER_CONTRACT["icon"]
        entries.append(
            with_layer_contract(
                {
                "id": f"foundation/icon/{icon}",
                "category": "icon",
                "component": "common-icon",
                "state": icon,
                "assetPath": f"{assets_root}/{icon_sprite}",
                "symbol": icon,
                "layer": contract["layerRole"],
                "status": args.status,
                "purpose": f"{icon} icon in the shared foundation set",
                "importRule": "Use the SVG symbol from the shared sprite, or replace with an equivalent per-icon SVG file if the target runtime requires it.",
                },
                contract,
            )
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
        "layerContract": {
            "schemaVersion": "frontend-ui-pipeline.layer-contract.v1",
            "contentPlaneZIndex": 0,
            "rules": LAYER_CONTRACT_RULES,
            "sceneryPlaneAllocation": {
                state: SCENERY_PLANE_ALLOCATION[state]
                for _category, state, _path in SCREEN_ASSET_SLOTS
            },
            "screenSlots": {
                state: SCREEN_LAYER_CONTRACT[state]
                for _category, state, _path in SCREEN_ASSET_SLOTS
            },
            "foundationLayers": FOUNDATION_LAYER_CONTRACT,
        },
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
