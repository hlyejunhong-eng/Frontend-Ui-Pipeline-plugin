---
name: frontend-asset-production
description: "Phase 2 of the frontend UI pipeline. Use when the user has a phase 1 UI brief and preview images and wants production-ready, pixel-matched art assets for components, backgrounds, illustrations, icons, masks, textures, sprites, and motion frames; correct asset naming; an asset manifest; and a supplemented Markdown handoff describing exact composition, placement, and calling rules. Requires a user asset review and explicit pass before final output. Can run alone or hand off to frontend-implementation."
---

# Frontend Asset Production

## Purpose

Convert an approved phase 1 UI brief and preview into real production art assets plus an exact assembly handoff. This stage may iterate on assets, but it must not finalize until the user explicitly approves the asset review package.

## Non-Expert Mode

Assume the user cannot judge file formats, density variants, motion frames, or implementation paths. Present the review package visually and explain approval choices in plain language: "approve", "revise visual style", "revise naming/organization", or "revise implementation mapping".

## Run Mode

Default to `production` mode unless the user asks for a social-media demo, quick demo, sales demo, or non-final preview.

- In `production` mode, stop at the user approval gate before final handoff or real app implementation.
- In `demo` mode, you may create a clearly labeled non-final standalone preview for storytelling, but do not hot-replace the real app until the user approves the assets.

## Inputs

Require:

- `phase1-ui-brief.md` or an equivalent design specification.
- One or more phase 1 preview images.
- Any brand assets, source screenshots, icons, fonts, or target platform constraints supplied by the user.

If phase 1 artifacts are missing, ask for them or run `$frontend-ui-ideation` first.

If the phase 1 preview exists but is too vague to slice into assets, tighten the design contract first by adding a short supplement to the phase 1 brief before generating assets.

## Workflow

1. Read and normalize the design contract:
   - Extract every required screen, layer, component, state, and motion requirement from the phase 1 brief.
   - Identify which visuals should be real image assets and which should remain CSS, native UI, or code-driven animation.
   - Create an asset plan before generating files.
   - Confirm that the Phase 1 brief includes a Phase 2 generation guide. If missing, add a short supplement before producing assets.
   - When a full foundation kit is required, use `../../scripts/generate_foundation_manifest.py` to create a per-state manifest scaffold, then update it with the real generated asset paths.

2. Produce assets:
   - Choose and document the asset strategy before generation: AI raster illustration, vector/Figma-style production, or CSS/SVG procedural assets.
   - Generate or build pixel-matched backgrounds, illustrations, masks, textures, icons, sprites, component overlays, and motion frames as needed.
   - Use transparent PNG/WebP for layered raster assets, SVG for crisp vector icons or masks, and JSON/CSS/keyframe descriptions for procedural motion when appropriate.
   - Export density variants when the frontend target needs them, such as `@1x`, `@2x`, and `@3x`.
   - Keep source and final assets separate when a tool produces editable source material.
   - If raster image generation is unavailable, produce the closest implementable asset set using SVG, CSS gradients, masks, and code-driven motion, then document what would improve with a dedicated raster generator.
   - Never use empty placeholder files as "assets"; every produced asset must render something meaningful.
   - Produce the complete foundational component kit required by Phase 1, even if only some components are used by the target screen.

3. Name and organize files:
   - Use lower-kebab-case names.
   - Use a predictable folder structure such as:
     - `assets/backgrounds/<screen>/<asset-name>@2x.png`
     - `assets/components/<component>/<component-state>@2x.png`
     - `assets/icons/<icon-name>.svg`
     - `assets/motion/<interaction>/<interaction-name>_000.png`
   - Encode purpose, screen/component, state, variant, and scale in the file name when useful.
   - Avoid generic names such as `image1.png`, `bg.png`, or `new-icon.svg`.

4. Create the review package:
   - Build a contact sheet or preview folder that lets the user inspect every generated asset.
   - Make the contact sheet work through `../../scripts/serve_review.py` or a local file open; do not rely only on browser support for external SVG sprite references under `file://`.
   - Include side-by-side comparison against the phase 1 preview when possible.
   - List known deviations, tradeoffs, and any assets that need user judgment.
   - Include a machine-readable `asset-manifest.json` when practical so Phase 3 can import assets without re-parsing prose.
   - Prefer one manifest entry per asset and per important component state when practical, rather than only one entry per component family.
   - If using the bundled manifest generator, keep its coverage counts in the review package so the user can see whether every required state is represented.
   - Run `../../scripts/validate_foundation_manifest.py <manifest-path>` before asking the user to approve assets; fix any missing component state, icon, or screen asset slot first.

5. Mandatory user approval:
   - Stop and ask the user to review the asset package.
   - Do not write the final phase 2 handoff until the user explicitly says the assets pass or approves a specific revision.
   - If the user requests changes, revise assets and repeat the review gate.

6. Finalize the phase 2 handoff:
   - Write `phase2-asset-handoff.md` beside the asset folder or in the user-provided output directory.
   - Supplement the phase 1 brief rather than replacing it.

## Required Handoff Content

The final Markdown document must include:

- Source references: phase 1 brief path, preview image paths, and approved review package path.
- Asset manifest: file path, type, dimensions, scale, transparency, color mode, purpose, owning screen/component, and state.
- Assembly map: exact layer order, placement coordinates, sizing rules, object-fit rules, masks, blend modes, and responsive behavior.
- Component usage rules: which assets each component imports, fallback behavior, and when to use CSS or native UI instead of images.
- Motion asset rules: frame order, frame rate, duration, looping, easing, trigger, start/end states, and reduced-motion fallback.
- Implementation notes: target import paths, bundler/public folder assumptions, preloading strategy, cache busting, and optimization instructions.
- Acceptance checklist for `$frontend-implementation`.

## Required Foundation Kit

Phase 2 must generate the full style-matched kit below unless the user explicitly narrows scope after seeing the risk:

- Buttons: primary, secondary, ghost, danger, disabled, loading, icon-only, and pressed states.
- Numeric badges: neutral, accent, success, warning, danger, dot, and count variants.
- Generic cards: flat, elevated, selected, disabled, media, metric, and action-card variants.
- Combobox/select: closed, open, selected, search-filtered, empty, disabled, and error states.
- Common icons: home, profile, generic page, scan, cart, payment, chat, confirm, close, back, forward, hot, like, settings, help, info, wallet, list, favorite, and search.
- Navigation bar: desktop sidebar/topbar and mobile compact navigation.
- Notice bar: info, success, warning, danger, and dismissible variants.
- Search bar: idle, focused, with-value, loading, empty-result, and clear-button states.
- Section title: eyebrow, title, subtitle, action slot, and divider variants.
- Modal: default, destructive confirmation, form modal, mobile sheet, overlay, close action, and focus state.
- Transition animation: page enter/exit, modal enter/exit, button press, hover, loading shimmer, and reduced-motion fallback.

Represent this kit as real frontend-consumable assets: SVG icon sprites or files, CSS component tokens, motion keyframes, component preview HTML, raster/vector illustration layers, and `asset-manifest.json` entries.

## Foundation Manifest Generator

Use the bundled script when the Phase 2 output needs the full foundation kit and the target repo does not already provide an equivalent manifest:

```bash
python3 ../../scripts/generate_foundation_manifest.py \
  --project "<project-name>" \
  --screen "<screen-name>" \
  --target-route "<route-or-component>" \
  --style-name "<approved-style-name>" \
  --status review-pending \
  --phase1-brief "<path-to-phase1-ui-brief.md>" \
  --preview "<path-to-preview.png>" \
  --output "<phase2-folder>/asset-manifest.json"
```

After generation, replace scaffold paths with the real generated asset paths and keep one entry per important component state.

Validate coverage before review:

```bash
python3 ../../scripts/validate_foundation_manifest.py "<phase2-folder>/asset-manifest.json"
```

Use `--require-status approved` before Phase 3 if the manifest is supposed to represent final approved assets.

## SVG Sprite Review Rule

If you generate SVG sprites, verify the review page actually shows every icon. If external `<use href="sprite.svg#id">` is blank in a local `file://` review, run the bundled review server or inline the preview paths in the contact sheet. Keep the production sprite if it is still the best import format.

## Review Server

Use the bundled server for contact sheets, SVG sprites, fonts, and relative asset paths:

```bash
python3 ../../scripts/serve_review.py "<phase2-folder>/review" --entry component-contact-sheet.html
```

Report the printed `Review URL` to the user. If you only need to validate the folder in automation, add `--check`.

## Quality Gate

Final output must include:

- Approved real asset files.
- `phase2-asset-handoff.md`.
- An asset review package the user can inspect visually.
- A manifest or table that maps every asset to a component, state, layer, and import/calling path.
- A complete foundational component kit covering buttons, badges, cards, combobox, common icons, navigation, notice bar, search bar, section titles, modal, and transition animations.
- A clear statement that the user approved the final asset package.
- A phase readiness checklist showing whether Phase 3 can start immediately.
- A short handoff note naming the next recommended skill: `$frontend-implementation`.
