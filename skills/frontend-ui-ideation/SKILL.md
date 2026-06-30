---
name: frontend-ui-ideation
description: "Phase 1 of the frontend UI pipeline. Use when the user wants to redesign an existing app, screen, route, or product flow into a premium custom UI concept; collect ideas from current code, screenshots, URLs, Figma, or a running app; generate illustration-level UI and motion direction previews; and produce a Markdown design specification with pixel-level requirements for backgrounds, layout, components, text, buttons, states, click feedback, and animations. Can run alone or hand off to frontend-asset-production."
---

# Frontend UI Ideation

## Purpose

Turn an existing frontend experience into a premium redesign brief with visual previews and implementation-grade requirements. This is the concept and specification stage, not the final asset slicing or code implementation stage.

## Inputs

Accept any combination of:

- Existing app code, route names, local dev server, screenshots, Figma frames, product URLs, or app recordings.
- User goals, brand preferences, audience, target devices, accessibility constraints, and "must keep" product behavior.
- Prior product context or design artifacts.

Ask only for information that blocks a credible design brief. If the user provided a runnable app or source code, inspect it before asking broad questions.

## Workflow

1. Establish the design target:
   - Identify the exact screen, route, component set, or product flow.
   - Capture the current state with screenshots when possible.
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

4. Write the phase 1 Markdown specification:
   - Create a handoff folder unless the user provided one. Suggested shape: `frontend-ui-pipeline/phase1-<screen-or-flow>/`.
   - Write `phase1-ui-brief.md` in that folder.
   - Include all preview image paths and any source screenshots used.
   - Treat the document as the contract for asset production and implementation.

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
- Asset expectations: predicted asset list for phase 2, including backgrounds, illustrations, icons, motion frames, sprites, masks, and textures.
- Acceptance checklist: precise criteria that phase 2 and phase 3 must satisfy.

## Quality Gate

Do not finish with prose only. Final output must provide:

- A `phase1-ui-brief.md` file.
- At least one preview image that represents the redesigned target UI.
- A short handoff note naming the next recommended skill: `$frontend-asset-production`.
