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
   - Confirm that Phase 1 has a selected visual target and a passing visual excellence gate. If missing, return to `$frontend-ui-ideation` before generating assets.
   - Identify which visuals should be real image assets and which should remain CSS, native UI, or code-driven animation.
   - Create an asset plan before generating files.
   - Confirm that the Phase 1 brief includes a Phase 2 generation guide. If missing, add a short supplement before producing assets.
   - When a full foundation kit is required, use `../../scripts/generate_foundation_manifest.py` to create a per-state manifest scaffold, then update it with the real generated asset paths.
   - Use `../../scripts/generate_asset_prompt_pack.py` after the manifest exists to create a practical production prompt pack for raster, Figma/vector, and CSS/SVG asset generation. Use the pack to drive asset production rather than relying on vague art direction prose.

2. Produce assets:
   - Choose and document the asset strategy before generation: AI raster illustration, vector/Figma-style production, or CSS/SVG procedural assets.
   - Produce the primary screen hero asset set first: selected-preview background, primary illustration or motif, texture/depth layer, key icon treatment, component surface treatment, and the first motion/feedback cue. Do not spread effort across the whole foundation kit until the selected screen can look excellent.
   - Generate or build pixel-matched backgrounds, illustrations, masks, textures, icons, sprites, component overlays, and motion frames as needed.
   - Prefer real raster/ImageGen or editable bitmap assets for backgrounds, illustrations, textures, rich lighting, and custom motifs. Use CSS/SVG procedural assets only for crisp UI primitives, masks, scalable icons, keyframes, or fallback when image generation is unavailable.
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
   - Visually inspect contact sheets and approval HTML for clipped titles, overflowing labels, unreadable text, missing glyphs, hidden icons, and bottom/right-edge truncation. Regenerate the review artifact before asking for approval if text or controls are cut off.
   - Run `../../scripts/check_visual_artifacts.py` on contact sheet images and review HTML when the bundled script is available.
   - Run `../../scripts/compare_visual_artifacts.py` when you have a Phase 1 preview PNG and a comparable Phase 2 contact sheet or asset preview PNG; attach the JSON or Markdown report to the review package.
   - Include side-by-side comparison against the phase 1 preview when possible.
   - List known deviations, tradeoffs, and any assets that need user judgment.
   - Include a machine-readable `asset-manifest.json` when practical so Phase 3 can import assets without re-parsing prose.
   - Prefer one manifest entry per asset and per important component state when practical, rather than only one entry per component family.
   - If using the bundled manifest generator, keep its coverage counts in the review package so the user can see whether every required state is represented.
   - Run `../../scripts/validate_foundation_manifest.py <manifest-path>` before asking the user to approve assets; fix any missing component state, icon, or screen asset slot first.
   - Use `../../scripts/generate_asset_review_packet.py` to create a non-designer approval packet with coverage, contact sheet, decision options, and exact user reply text for approval or revision.
   - Include an asset-assembled primary screen preview in the review package. This preview must be rendered from the generated Phase 2 assets and component treatments, not copied from the Phase 1 preview screenshot.
   - Run `../../scripts/generate_pipeline_runbook.py --run-root <run-root>` when the bundled script is available so the user can see that the next required action is asset approval.
   - Run `../../scripts/generate_pipeline_completion_audit.py --run-root <run-root>` when the bundled script is available so the approval blocker and foundation-kit coverage are explicit evidence.

5. Mandatory user approval:
   - Stop and ask the user to review the asset package.
   - Do not write the final phase 2 handoff until the user explicitly says the assets pass or approves a specific revision.
   - If the user requests changes, revise assets and repeat the review gate.

6. Finalize the phase 2 handoff:
   - Use `../../scripts/generate_phase2_handoff.py` when the bundled script is available so approval text, manifest entries, assembly rules, component usage, motion rules, and Phase 3 acceptance checks are captured consistently.
   - Write `phase2-asset-handoff.md` beside the asset folder or in the user-provided output directory.
   - Supplement the phase 1 brief rather than replacing it.
   - Regenerate `pipeline-runbook.md` after the final handoff so the next prompt points to `$frontend-implementation`.
   - Regenerate `pipeline-completion-audit.md` after the final handoff so Phase 3 can see which objective requirements are already proven and which still need screenshots or Design QA.

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

## Primary Screen First Rule

Before expanding the complete foundation kit, make the selected Phase 1 screen visually convincing:

- Lock the selected Phase 1 preview as the visual source of truth.
- Generate or assemble the main background, illustration/motif, surface material, key icon style, and one representative motion/feedback cue.
- Produce a contact sheet section that compares the primary screen asset set against the selected preview.
- Only after the primary screen set is visually strong, expand the full foundation kit for buttons, badges, cards, combobox, common icons, navigation, notice bar, search bar, section title, modal, and transitions.
- If the primary screen does not pass the review, revise it before spending time on the unused foundation states.

## Asset-Assembled Primary Preview Rule

Phase 2 must prove that the generated assets can recreate the selected screen:

- Produce `review/primary-screen-asset-assembly.png` or an equivalent HTML/PNG preview assembled from generated backgrounds, illustration layers, textures, masks, icons, component CSS, and motion treatments.
- Do not copy `phase1-preview-*.png` into the Phase 2 review folder and present it as asset evidence.
- If using the bundled review packet generator, pass `--assembly-preview "<phase2-folder>/review/primary-screen-asset-assembly.png"` and `--visual-diff-report "<phase2-folder>/review/visual-diff-primary-screen.md"` when those files exist.
- Run `../../scripts/compare_visual_artifacts.py` against the Phase 1 preview and this asset assembly when dimensions are comparable.
- If the diff fails because the assembly is not a final app screenshot, keep the report and explain the deviation in the approval packet. Phase 3 screenshots remain the final pixel gate.
- Record this preview in `asset-manifest.json` evidence when practical, for example `phase2PrimaryAssemblyPreview`, `phase2PrimaryAssemblyHtml`, and `assemblyUsesGeneratedAssets=true`.

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

## Asset Prompt Pack Generator

Use the bundled prompt-pack generator when the user is non-technical, the asset strategy includes AI raster/vector generation, or the Phase 1 style needs to be translated into concrete production prompts:

```bash
python3 ../../scripts/generate_asset_prompt_pack.py \
  --phase1-brief "<path-to-phase1-ui-brief.md>" \
  --manifest "<phase2-folder>/asset-manifest.json" \
  --strategy hybrid \
  --output "<phase2-folder>/phase2-asset-prompt-pack.md"
```

The output must name layer prompts, AI raster prompts, Figma/vector prompts, CSS/SVG component prompts, refinement knobs, manifest paths, and the approval checklist. Keep it beside the Phase 2 review package so a non-designer can understand what was generated and what can be revised.

## SVG Sprite Review Rule

If you generate SVG sprites, verify the review page actually shows every icon. If external `<use href="sprite.svg#id">` is blank in a local `file://` review, run the bundled review server or inline the preview paths in the contact sheet. Keep the production sprite if it is still the best import format.

## Review Server

Use the bundled server for contact sheets, SVG sprites, fonts, and relative asset paths:

```bash
python3 ../../scripts/serve_review.py "<phase2-folder>/review" --entry component-contact-sheet.html
```

Report the printed `Review URL` to the user. If you only need to validate the folder in automation, add `--check`.

## Asset Review Packet Generator

Use the bundled review packet generator before the mandatory user approval gate:

```bash
python3 ../../scripts/generate_asset_review_packet.py \
  --manifest "<phase2-folder>/asset-manifest.json" \
  --phase1-brief "<path-to-phase1-ui-brief.md>" \
  --prompt-pack "<phase2-folder>/phase2-asset-prompt-pack.md" \
  --contact-sheet "<phase2-folder>/review/phase2-contact-sheet.png" \
  --assembly-preview "<phase2-folder>/review/primary-screen-asset-assembly.png" \
  --visual-diff-report "<phase2-folder>/review/visual-diff-primary-screen.md" \
  --review-url "<review-server-url>" \
  --output-dir "<phase2-folder>/review"
```

The packet must give the user four plain decisions: approve assets, revise visual style, revise naming/organization, or revise implementation mapping. Treat only an explicit approval as permission to write final `phase2-asset-handoff.md`.

## Phase 2 Handoff Generator

After the user explicitly approves the asset review package, use the bundled handoff generator to create the final `phase2-asset-handoff.md`:

```bash
python3 ../../scripts/generate_phase2_handoff.py \
  --manifest "<phase2-folder>/asset-manifest.json" \
  --phase1-brief "<path-to-phase1-ui-brief.md>" \
  --prompt-pack "<phase2-folder>/phase2-asset-prompt-pack.md" \
  --review-packet "<phase2-folder>/review/phase2-asset-approval-packet.md" \
  --contact-sheet "<phase2-folder>/review/phase2-contact-sheet.png" \
  --visual-diff-report "<phase2-folder>/review/visual-diff-report.md" \
  --target-runtime "<target-runtime>" \
  --approved-by "<user-or-role>" \
  --approval-text "<exact-user-approval-message>" \
  --output "<phase2-folder>/phase2-asset-handoff.md"
```

The script must fail when approval text is missing or does not contain an explicit approval/pass decision. Do not bypass that guard in production mode.

## Visual Artifact Checker

Use the bundled visual artifact checker on Phase 2 review screenshots, contact sheets, SVGs, and HTML review pages:

```bash
python3 ../../scripts/check_visual_artifacts.py \
  "<phase2-folder>/review/phase2-contact-sheet.png" \
  "<phase2-folder>/review/phase2-asset-approval-packet.html" \
  --min-width 320 \
  --min-height 240
```

## Visual Diff Helper

Use the bundled visual diff helper when a Phase 2 asset preview or contact sheet is meant to match an approved Phase 1 preview. It compares two PNG files without external dependencies and can write JSON and Markdown evidence:

```bash
python3 ../../scripts/compare_visual_artifacts.py \
  "<phase1-folder>/phase1-preview-mobile.png" \
  "<phase2-folder>/review/phase2-contact-sheet.png" \
  --allow-size-mismatch \
  --output-md "<phase2-folder>/review/visual-diff-report.md" \
  --output-json "<phase2-folder>/review/visual-diff-report.json"
```

Use this report as QA evidence, not as a replacement for user approval. If the diff fails, either fix visible mismatches or document why the compared artifacts are intentionally different compositions.

## Quality Gate

Final output must include:

- Approved real asset files.
- `phase2-asset-handoff.md`, preferably generated with `generate_phase2_handoff.py` after explicit approval.
- `phase2-asset-prompt-pack.md` or an equivalent asset-generation prompt record when generated assets used raster, Figma/vector, or CSS/SVG prompt production.
- Evidence that the primary selected screen asset set was produced before the full foundation expansion.
- An asset review package the user can inspect visually.
- `phase2-asset-approval-packet.md` and/or `phase2-asset-approval-packet.html` when the bundled review packet generator is available.
- Visual inspection evidence that contact sheet and approval packet text does not clip, overflow, disappear at page edges, or render as missing glyphs.
- Passing visual artifact checks for review images or HTML when the bundled checker is available.
- A visual diff report when a comparable Phase 1 preview and Phase 2 asset preview/contact sheet are available.
- A primary screen asset assembly preview built from generated Phase 2 assets, not a copied Phase 1 screenshot.
- A manifest or table that maps every asset to a component, state, layer, and import/calling path.
- A complete foundational component kit covering buttons, badges, cards, combobox, common icons, navigation, notice bar, search bar, section titles, modal, and transition animations.
- A generated or refreshed `pipeline-runbook.md` when the bundled script is available.
- A clear statement that the user approved the final asset package.
- A phase readiness checklist showing whether Phase 3 can start immediately.
- A short handoff note naming the next recommended skill: `$frontend-implementation`.
