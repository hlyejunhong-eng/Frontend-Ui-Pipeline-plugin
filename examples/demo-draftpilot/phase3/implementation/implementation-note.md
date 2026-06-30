# Phase 3 Implementation Note

## Run Command

Open `index.html` directly in a browser:

```text
examples/demo-draftpilot/phase3/implementation/index.html
```

No package install or build step is required.

## Assets Used

- Background: `../../phase2/assets/backgrounds/onboarding/editorial-ribbon.svg`
- Step icons: `../../phase2/assets/icons/*.svg`
- Foundation kit: `../../phase2/design-system/component-kit.css`
- Foundation icon sprite: `../../phase2/design-system/icon-sprite.svg`

## Mock Data

No real API exists in this demo. The implementation uses `mockOnboardingSteps` in `app.js` with the same shape documented in `phase2/phase2-asset-handoff.md`.

Replace the mock later with an onboarding endpoint that returns:

```js
{
  id: string,
  title: string,
  description: string,
  status: "active" | "upcoming" | "complete",
  icon: string
}
```

## Reusable Foundation Kit

The implementation imports the Phase 2 foundation kit before screen-specific styles. It also uses several base components that are not strictly required by the original onboarding flow:

- notice bar
- search bar
- combobox
- numeric badge
- modal
- secondary foundation button

This proves the Phase 2 style system can expand beyond the first screen.

## Verification Evidence

- Desktop screenshot: `../../evidence/screenshots/draftpilot-desktop.png`
- Mobile screenshot: `../../evidence/screenshots/draftpilot-mobile.png`
- Component gallery screenshot: `../../phase2/design-system/component-gallery.png`
