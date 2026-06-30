---
name: frontend-asset-production
description: "Phase 2 of the frontend UI pipeline. Use when the user has a phase 1 UI brief and preview images and wants production-ready, pixel-matched art assets for components, backgrounds, illustrations, icons, masks, textures, sprites, and motion frames; correct asset naming; an asset manifest; and a supplemented Markdown handoff describing exact composition, placement, and calling rules. Requires a user asset review and explicit pass before final output. Can run alone or hand off to frontend-implementation."
---

# Frontend Asset Production

## Purpose

Convert an approved phase 1 UI brief and preview into real production art assets plus an exact assembly handoff. This stage may iterate on assets, but it must not finalize until the user explicitly approves the asset review package.

## Non-Expert Mode

Assume the user cannot judge file formats, density variants, motion frames, or implementation paths. Present the review package visually and explain approval choices in plain language: "approve", "revise visual style", "revise naming/organization", or "revise implementation mapping".

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

2. Produce assets:
   - Generate or build pixel-matched backgrounds, illustrations, masks, textures, icons, sprites, component overlays, and motion frames as needed.
   - Use transparent PNG/WebP for layered raster assets, SVG for crisp vector icons or masks, and JSON/CSS/keyframe descriptions for procedural motion when appropriate.
   - Export density variants when the frontend target needs them, such as `@1x`, `@2x`, and `@3x`.
   - Keep source and final assets separate when a tool produces editable source material.
   - If raster image generation is unavailable, produce the closest implementable asset set using SVG, CSS gradients, masks, and code-driven motion, then document what would improve with a dedicated raster generator.
   - Never use empty placeholder files as "assets"; every produced asset must render something meaningful.

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
   - Include side-by-side comparison against the phase 1 preview when possible.
   - List known deviations, tradeoffs, and any assets that need user judgment.
   - Include a machine-readable `asset-manifest.json` when practical so Phase 3 can import assets without re-parsing prose.

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

## Quality Gate

Final output must include:

- Approved real asset files.
- `phase2-asset-handoff.md`.
- An asset review package the user can inspect visually.
- A manifest or table that maps every asset to a component, state, layer, and import/calling path.
- A clear statement that the user approved the final asset package.
- A phase readiness checklist showing whether Phase 3 can start immediately.
- A short handoff note naming the next recommended skill: `$frontend-implementation`.
