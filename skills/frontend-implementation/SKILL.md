---
name: frontend-implementation
description: "Phase 3 of the frontend UI pipeline. Use when the user has approved phase 2 assets and a handoff spec and wants the real frontend implemented or hot-replaced in an existing application with pixel-matched layout, backgrounds, components, and motion. Connect real callable APIs when available; otherwise build faithful mocks that match the approved preview. Includes repo inspection, asset integration, implementation, responsive QA, screenshots, and local dev server handoff."
---

# Frontend Implementation

## Purpose

Implement the approved phase 2 design handoff into the actual frontend application. This stage integrates assets, connects real APIs when available, creates faithful mocks when needed, and verifies that the result matches the approved preview.

## Non-Expert Mode

Assume the user may not know how to run the app, choose a route, or verify visual quality. Inspect the repo, choose the safest implementation path, start the app when possible, and report the final URL and checks in plain language.

## Inputs

Prefer:

- `phase2-asset-handoff.md`.
- Approved asset folder.
- Phase 1 preview images and `phase1-ui-brief.md`.
- Target repo, route, component, or page to replace.

If phase 2 assets are not approved, ask the user to approve them or run `$frontend-asset-production` first.

If no existing frontend repo is provided, create a runnable standalone implementation in a clearly named output folder and explain how it can be copied into a real app later. Do not treat "no repo" as permission to stop at a mockup image.

## Workflow

1. Inspect the application:
   - Read project structure, package metadata, router setup, component conventions, styling system, asset pipeline, and existing API clients.
   - Locate the route, screen, or component that should receive the hot replacement.
   - Preserve unrelated behavior and project patterns.
   - Ask before changing scope if the target replacement area is ambiguous.

2. Plan integration:
   - Map each phase 2 asset to the correct public path, import path, CSS module, component prop, or animation primitive.
   - Decide which visual elements are image assets and which should be rendered with CSS, canvas, SVG, or native components.
   - Define responsive breakpoints and exact layout constraints from the phase 1 and phase 2 documents.

3. Connect data:
   - Use existing real APIs or service clients when they are present and callable.
   - Respect authentication, error handling, loading, pagination, and caching patterns already used by the app.
   - If no real API is available, create local mocks that exactly match the preview data density, labels, avatar/image slots, numbers, and edge cases.
   - Keep mock data isolated and clearly named so it can be replaced later.
   - If an API exists but cannot be called because credentials or network access are missing, preserve the API client integration point and add a local fixture with the same response shape.

4. Implement the UI:
   - Import and place approved assets exactly according to the phase 2 assembly map.
   - Build pixel-matched layout, components, backgrounds, typography, and states.
   - Implement click feedback, hover/focus/press states, page transitions, loading motion, and reduced-motion fallback.
   - Use the app's existing design system and utility conventions when they can satisfy the spec.
   - Add missing local components only when needed for fidelity or maintainability.

5. Hot replace into the real app:
   - Wire the new implementation into the actual route or component requested by the user.
   - Avoid unrelated refactors, broad styling resets, or deleting existing code outside the requested surface.
   - Keep the app runnable after every major edit.

6. Verify:
   - Run the relevant formatter, typecheck, lint, tests, and build commands when available.
   - Start the local dev server for app-based work.
   - Capture desktop and mobile screenshots with Playwright or the available browser tool.
   - Compare screenshots against the approved preview and phase 2 assembly map.
   - Fix visible mismatches, broken assets, layout shifts, text overflow, inaccessible focus states, and animation defects before handing back.

7. Package the handoff:
   - Add or update a short implementation note that lists how to run the screen, where assets live, where mocks live, and how to swap mocks for real APIs.
   - Keep this note close to the changed frontend code or in the phase handoff folder.

## Implementation Standards

- Treat the approved preview as the visual source of truth and the phase 2 handoff as the assembly source of truth.
- Use stable dimensions for fixed-format UI such as toolbars, boards, cards, counters, media slots, and icon buttons.
- Ensure text never overlaps adjacent content or escapes controls on supported viewports.
- Prefer real browser verification over code inspection for final visual acceptance.
- Do not claim pixel matching if screenshots were not captured or compared.
- Do not leave final work as an isolated image when code can be produced. The final artifact must be runnable frontend code or a clear explanation of the external blocker.

## Final Output

Report:

- Files changed.
- Real APIs connected or mocks created.
- Verification commands run and their result.
- Screenshot paths or a clear reason screenshots could not be captured.
- Local URL for the running app when a dev server is required.
- Any remaining visual, API, or product risks.
