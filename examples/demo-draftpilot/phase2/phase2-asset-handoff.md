# Phase 2 Asset Handoff: DraftPilot Onboarding Dashboard

## Source References

- Phase 1 brief: [`../phase1/phase1-ui-brief.md`](../phase1/phase1-ui-brief.md)
- Asset manifest: [`asset-manifest.json`](asset-manifest.json)
- Review package: [`asset-review/contact-sheet.html`](asset-review/contact-sheet.html)
- Approval: demo asset package approved for Phase 3.

## Asset Manifest

| Path | Type | Component | State | Purpose |
| --- | --- | --- | --- | --- |
| `assets/backgrounds/onboarding/editorial-ribbon.svg` | SVG | page background | default | Custom editorial background accent |
| `assets/icons/brand-voice.svg` | SVG | setup step | active | Brand voice step icon |
| `assets/icons/connect-website.svg` | SVG | setup step | upcoming | Website connection icon |
| `assets/icons/create-campaign.svg` | SVG | setup step | upcoming | Campaign creation icon |
| `design-system/component-kit.css` | CSS | foundation kit | all | Buttons, badges, cards, combobox, nav, notices, search, section title, modal, motion |
| `design-system/icon-sprite.svg` | SVG sprite | foundation icons | all | Common icon set for app-wide reuse |
| `design-system/component-gallery.html` | HTML | review package | all | Visual review of the complete foundation kit |

## Complete Foundation Kit Coverage

Generated whether or not the onboarding page uses every component:

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

## Assembly Map

1. Render base page fill `#F7F2EA`.
2. Place `editorial-ribbon.svg` in the page background:
   - desktop: absolute, top `24px`, right `-120px`, width `720px`, z-index `0`
   - tablet: top `80px`, right `-220px`, width `620px`
   - mobile: hidden under `720px`
3. Render app shell at z-index `1`.
4. Use icon SVG files inside setup rows:
   - `brand-voice.svg` for active first row
   - `connect-website.svg` for second row
   - `create-campaign.svg` for third row
5. Icons inherit row color through `currentColor`.
6. Import `design-system/component-kit.css` before screen-specific CSS so the implementation can reuse the full style system.
7. Keep `design-system/icon-sprite.svg` available for future routes even when individual screen icons use separate SVG files.

## Motion Rules

- Page entrance: `.app-shell` uses `fade-rise` for 360 ms.
- CTA press: CSS transform `scale(0.985)` while active.
- Setup row hover: translate x `2px` over 140 ms.
- Progress ring: CSS `stroke-dashoffset` animation over 700 ms.
- Foundation kit adds `fp-page-enter`, `fp-modal-enter`, `fp-shimmer`, and `fp-spin`.
- Reduced motion: disable transforms and long transitions.

## Implementation Notes

- Demo implementation path: `../phase3/implementation/`.
- Asset paths are loaded from `../../phase2/assets/...`.
- Foundation kit stylesheet is loaded from `../../phase2/design-system/component-kit.css`.
- No real API exists, so Phase 3 uses `mockOnboardingSteps` in `app.js`.
- Mock shape:

```js
{
  id: "brand-voice",
  title: "Add brand voice",
  description: "Teach DraftPilot how your company sounds.",
  status: "active",
  icon: "brand-voice.svg"
}
```

## Phase 3 Readiness Checklist

- [x] Assets render visible material.
- [x] Assets use specific lower-kebab-case names.
- [x] Asset review package exists.
- [x] Foundation component gallery exists.
- [x] Complete base component kit is generated.
- [x] User approval is recorded for this demo.
- [x] Implementation paths are specified.
- [x] Mock data shape is specified.
