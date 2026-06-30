# Phase 1 UI Brief: DraftPilot Onboarding Dashboard

## Context

DraftPilot helps small business owners create AI-assisted marketing campaigns. The onboarding dashboard appears immediately after signup and must guide a non-technical founder through setup without making the product feel heavy.

Target users are busy founders who want confidence, momentum, and a clear first action. The design should feel premium, editorial, and guided rather than like a generic SaaS checklist.

## Source Audit

Source input: [`../input/original-flow.md`](../input/original-flow.md)

Current structure:

- Sidebar navigation.
- Main welcome headline and subheading.
- Three setup steps.
- Primary CTA: `Create first campaign`.
- Secondary CTA: `Skip for now`.

Data states:

- First setup step is active.
- Other steps are upcoming.
- No real API is available for this demo, so Phase 3 should use local mock data with a shape that can be replaced by an onboarding API later.

## Selected Direction

Direction: **Editorial command center**.

The screen uses a warm paper base, dark editorial typography, precise setup rows, and a soft ribbon-like background asset to create a crafted feel without making the UI decorative at the expense of action.

Why it fits:

- Warm base color makes the product feel less technical.
- High-contrast CTA keeps the next action obvious.
- Step rows feel operational and shippable.
- Background asset adds custom identity while remaining implementable with SVG/CSS.

## Layout Spec

- Desktop target: 1440 x 1024.
- Mobile target: 390 x 844.
- Desktop shell: left sidebar 248 px; main content minmax 0 1fr; insight rail 304 px.
- Desktop page padding: 28 px.
- Mobile: single-column layout with compact top navigation.
- Main content max width: 1160 px.
- Step list gap: 12 px.
- Minimum touch target: 44 px.
- Border radius: 8 px for actionable panels and buttons.
- No content may overlap at 375 px width.

## Background Spec

- Base fill: `#F7F2EA`.
- Ink color: `#17201B`.
- Accent blue: `#2E6BFF`.
- Accent green: `#2E8B67`.
- Subtle border: `rgba(23, 32, 27, 0.12)`.
- Background art: `editorial-ribbon.svg`, placed top right on desktop, hidden under 720 px width.
- Background art must sit behind UI at z-index 0 and never cover text.

## Component Spec

### Sidebar

- Width: 248 px desktop.
- Background: `rgba(255, 252, 246, 0.74)`.
- Border: `1px solid rgba(23, 32, 27, 0.1)`.
- Backdrop blur: 16 px.
- Brand mark: 36 x 36 px.
- Active nav item: dark fill, white text, radius 8 px.

### Hero Block

- Eyebrow: `Workspace setup`.
- Heading: `Welcome to DraftPilot`.
- Heading size: clamp 36 px to 64 px.
- Supporting copy max width: 620 px.
- Primary CTA: 48 px tall, dark fill, white text, 8 px radius.
- Secondary CTA: transparent, 1 px border.

### Setup Step Row

- Height: 104 px desktop; min-height 96 px mobile.
- Icon slot: 44 x 44 px.
- Row background: `rgba(255, 252, 246, 0.86)`.
- Active row has left accent bar `#2E6BFF`.
- Upcoming rows keep lower contrast and no accent bar.
- Hover translates x 2 px on devices that support hover.

### Insight Rail

- Width: 304 px desktop.
- Shows setup progress, suggested first campaign, and confidence metrics.
- Collapses below main content under 980 px.

## Copy Spec

- Heading: `Welcome to DraftPilot`
- Subheading: `Set up your workspace and create your first campaign without wrestling with a blank page.`
- Step 1: `Add brand voice`
- Step 2: `Connect website`
- Step 3: `Create first campaign`
- Primary CTA: `Create first campaign`
- Secondary CTA: `Skip for now`

## Motion Spec

- Page entrance: opacity 0 to 1, translate y 10 px to 0, 360 ms, ease-out.
- CTA hover: translate y -1 px; shadow increases.
- CTA press: scale 0.985 for 90 ms then return over 160 ms.
- Step hover: translate x 2 px, 140 ms.
- Progress ring animates stroke dash offset over 700 ms.
- Reduced motion: disable transform animation and keep opacity transition under 120 ms.

## Phase 2 Asset Expectations

- `assets/backgrounds/onboarding/editorial-ribbon.svg`
- `assets/icons/brand-voice.svg`
- `assets/icons/connect-website.svg`
- `assets/icons/create-campaign.svg`
- `design-system/component-kit.css`
- `design-system/icon-sprite.svg`
- `design-system/component-gallery.html`
- `asset-manifest.json`
- `asset-review/contact-sheet.html`

## Phase 2 Generation Guide

Phase 2 must generate the complete DraftPilot foundation kit, not only assets used by this onboarding screen.

### Layer Order

1. **Base background**: warm paper fill `#F7F2EA`.
2. **Illustration background**: `editorial-ribbon.svg`, soft organic editorial shape, z-index 0.
3. **Layout surfaces**: sidebar, setup rows, cards, rail panels, modal surfaces, notice bars.
4. **Action layer**: buttons, search bar, combobox, navigation controls, close/back/forward controls.
5. **Text layer**: headings, section titles, labels, badges, helper text.
6. **Effects layer**: shadows, blur, borders, selected rings, hover/press transforms.
7. **Motion layer**: page enter, modal enter, button press, shimmer/loading, reduced-motion fallback.

### Adjustable Parameters

- Background opacity: 0.72 to 1.0.
- Background crop: desktop right offset from `-80px` to `-180px`; hide under 720 px width.
- Surface opacity: 0.78 to 0.94.
- Backdrop blur: 10 px to 18 px.
- Shadow strength: 8% to 18% black/brown alpha.
- Border alpha: 0.08 to 0.16.
- Accent saturation: reduce by up to 12% for conservative enterprise screens.
- Icon stroke: 1.6 px to 2 px.
- Radius: fixed 8 px unless the target app already uses a stricter system.
- Button press scale: 0.98 to 0.99.
- Motion duration: 120 ms for micro-interactions, 320-420 ms for page entrance.
- Reduced motion: remove transform and keep opacity transitions under 120 ms.

### Required Foundation Kit

Generate these base components whether or not the current onboarding screen uses them:

- Buttons: primary, secondary, ghost, danger, disabled, loading, icon-only, pressed.
- Numeric badges: neutral, accent, success, warning, danger, dot, count.
- Generic cards: flat, elevated, selected, disabled, media, metric, action-card.
- Combobox/select: closed, open, selected, search-filtered, empty, disabled, error.
- Common icons: home, profile, generic page, scan, cart, payment, chat, confirm, close, back, forward, hot, like, settings, help, info, wallet, list, favorite, search.
- Navigation bar: desktop sidebar/topbar and mobile compact nav.
- Notice bar: info, success, warning, danger, dismissible.
- Search bar: idle, focused, with-value, loading, empty-result, clear-button.
- Section title: eyebrow, title, subtitle, action slot, divider.
- Modal: default, destructive confirmation, form modal, mobile sheet, overlay, close action, focus state.
- Transition animation: page enter/exit, modal enter/exit, button press, hover, loading shimmer, reduced-motion fallback.

### Export Rules

- Use SVG for icons and implementable vector illustration.
- Use CSS tokens for component surfaces and motion when raster assets are unnecessary.
- Use lower-kebab-case names.
- Include `asset-manifest.json` entries for every asset and design-system file.
- Include a visual review page showing all generated base components before Phase 3 starts.

## Acceptance Checklist

- The UI feels custom before the user reads the copy.
- The primary next action is visible above the fold.
- All assets have specific names and render visible material.
- Phase 2 receives a complete component generation guide with layer order and adjustable parameters.
- Phase 2 generates the complete foundation kit, including components not used by the current screen.
- The implementation can run with local mock onboarding data.
- Desktop and mobile screenshots are captured for Phase 3 verification.
