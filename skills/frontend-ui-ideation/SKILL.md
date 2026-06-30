---
name: frontend-ui-ideation
description: "Phase 1 of the frontend UI pipeline. Use when the user wants to redesign an existing app, screen, route, or product flow into a premium custom UI concept; collect ideas from current code, screenshots, URLs, Figma, or a running app; generate illustration-level UI and motion direction previews; and produce a Markdown design specification with pixel-level requirements for backgrounds, layout, components, text, buttons, states, click feedback, and animations. Can run alone or hand off to frontend-asset-production."
---

# Frontend UI Ideation

## Purpose

Turn an existing frontend experience into a premium redesign brief with visual previews and implementation-grade requirements. This is the concept and specification stage, not the final asset slicing or code implementation stage.

## Non-Expert Mode

Assume the user may not know design language, frontend architecture, or asset production terms. Translate vague goals into concrete product and UI decisions. When the user says "make it premium" or "you decide", do not ask for taste words; inspect the app, infer the strongest direction, and document the decision.

## First Run Checklist

When this is the user's first run or the input is vague, state the concrete starting point in plain language:

- Confirm the target artifact: screenshot, project path, localhost URL, Figma link, or page description.
- Name the exact screen, route, or component you will inspect first.
- If the installed skills are not visible in the current thread, tell the user to open a new Codex thread after plugin installation.
- If the user wants a quick public demo, mark the run as `demo`; otherwise use `production`.

## Inputs

Accept any combination of:

- Existing app code, route names, local dev server, screenshots, Figma frames, product URLs, or app recordings.
- User goals, brand preferences, audience, target devices, accessibility constraints, and "must keep" product behavior.
- Prior product context or design artifacts.

Ask only for information that blocks a credible design brief. If the user provided a runnable app or source code, inspect it before asking broad questions.

If the user provides no runnable app, screenshot, URL, Figma frame, or code target, create a small intake checklist and ask for one concrete source artifact before attempting visual ideation.

## Workflow

1. Establish the design target:
   - Identify the exact screen, route, component set, or product flow.
   - Capture the current state with screenshots when possible.
   - If screenshots cannot be captured, create source evidence from route paths, code excerpts, API maps, state inventories, and a clear reason screenshots were unavailable.
   - Inventory real copy, controls, data states, loading states, error states, empty states, and navigation transitions.
   - Note existing API/data constraints and implementation boundaries that later stages must respect.

2. Collect and shape ideas:
   - Derive product background, user intent, emotional tone, and visual opportunity from the existing app.
   - If the design direction is open, propose three distinct art directions and ask the user to choose one.
   - If the user says to decide, pick the strongest direction and record the rationale in the brief.
   - Prefer high-craft, custom interface ideas over generic dashboard, card, or landing-page patterns.

3. Create preview imagery:
   - Generate or assemble preview images for the selected direction.
   - Preview images must show the actual target screen or flow, not vague mood boards.
   - Use realistic UI composition, text, control density, stateful components, and motion cues.
   - Save preview files with stable names such as `phase1-preview-desktop.png`, `phase1-preview-mobile.png`, or `phase1-flow-preview.png`.
   - If image generation is unavailable, create a static HTML/CSS preview or local prototype and capture screenshots from it. Do not skip the preview requirement.

4. Write the phase 1 Markdown specification:
   - Create a handoff folder unless the user provided one. Suggested shape: `frontend-ui-pipeline/phase1-<screen-or-flow>/`.
   - Write `phase1-ui-brief.md` in that folder.
   - Include all preview image paths and any source screenshots used.
   - Treat the document as the contract for asset production and implementation.
   - Run `../../scripts/validate_phase1_brief.py <path-to-phase1-ui-brief.md>` when the plugin script is available. Fix missing guide, layer, parameter, component, icon, or preview coverage before handing off to Phase 2.

5. Create an artifact index:
   - Write or include a short "handoff index" section listing every produced file, why it exists, and which phase consumes it.
   - Include unresolved questions only when they genuinely affect asset production or implementation.

6. Create the Phase 2 generation guide:
   - Include a dedicated "Phase 2 Generation Guide" section in `phase1-ui-brief.md`.
   - Specify illustration and UI layer order, such as base background, illustration planes, component surfaces, buttons, text, effects, masks, particles, and motion overlays.
   - Specify adjustable parameters for later refinement: opacity, blur, grain, shadow strength, highlight intensity, saturation, line weight, icon stroke, radius, spacing, motion duration, easing, and responsive crop rules.
   - Specify a complete component asset inventory for Phase 2, including assets that are not used by the current screen but define the style system.
   - Specify style tokens that Phase 2 and Phase 3 must preserve: color, typography, radius, elevation, border, icon style, illustration style, and motion language.

## Required Brief Content

The Markdown document must include:

- Context: product background, target users, business intent, target surfaces, and known constraints.
- Source audit: current screen/flow structure, components, copy, states, and interaction model.
- Selected direction: visual narrative, art direction, tone, and why it fits.
- Layout spec: viewport sizes, grid, spacing scale, z-index/layering, alignment, safe areas, responsive behavior, and overflow rules.
- Background spec: shapes, imagery, texture, depth, gradients, lighting, blur, masks, and exact placement rules.
- Component spec: every component with dimensions, radii, borders, shadows, fill, typography, icon treatment, states, disabled/loading/error behavior, and data dependencies.
- Copy spec: all headings, labels, button text, helper text, tooltips, empty-state text, and error text.
- Button and control spec: hit area, icon usage, hover/press/focus/disabled states, cursor, and keyboard behavior.
- Motion spec: page transitions, component entrance, click feedback, hover, drag, loading, idle motion, easing, durations, delays, transform origins, and reduced-motion alternatives.
- Phase 2 generation guide: layer map, adjustable visual parameters, asset naming rules, export rules, responsive crop rules, and component coverage rules.
- Asset expectations: predicted asset list for phase 2, including backgrounds, illustrations, icons, motion frames, sprites, masks, textures, and the full foundational component kit.
- Acceptance checklist: precise criteria that phase 2 and phase 3 must satisfy.
- First run notes: what was opened, what was inspected, and what the user should do next if this is a new plugin install.

## Required Phase 2 Component Inventory

The Phase 1 brief must require Phase 2 to generate a complete style-matched foundation kit, even when the current screen uses only part of it:

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

## Quality Gate

Do not finish with prose only. Final output must provide:

- A `phase1-ui-brief.md` file.
- At least one preview image that represents the redesigned target UI.
- Evidence of source inspection, such as screenshots, route/component notes, or a clear statement that the source artifact was not available.
- A Phase 2 generation guide with layer order, adjustable parameters, and the full foundational component inventory.
- A passing `validate_phase1_brief.py` result when the bundled script is available.
- A phase readiness checklist showing whether Phase 2 can start immediately.
- A short handoff note naming the next recommended skill: `$frontend-asset-production`.
