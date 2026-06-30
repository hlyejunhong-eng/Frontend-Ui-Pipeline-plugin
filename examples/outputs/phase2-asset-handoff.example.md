# Example Phase 2 Asset Handoff

This abbreviated example shows the level of specificity expected from `$frontend-asset-production`.

## Source References

- Phase 1 brief: `phase1-ui-brief.md`
- Approved preview: `phase1-preview-desktop.png`
- Review package: `asset-review/contact-sheet.png`
- User approval: approved in chat before final handoff.

## Asset Manifest

| Path | Type | Size | Purpose | Component |
| --- | --- | --- | --- | --- |
| `assets/backgrounds/onboarding/editorial-ribbon@2x.png` | PNG | 1280 x 720 | hero background accent | page background |
| `assets/icons/brand-voice.svg` | SVG | 24 x 24 | setup step icon | setup step |
| `assets/icons/connect-website.svg` | SVG | 24 x 24 | setup step icon | setup step |
| `assets/icons/create-campaign.svg` | SVG | 24 x 24 | setup step icon | setup step |

## Assembly Map

1. Render base page fill `#F7F4EE`.
2. Place `editorial-ribbon@2x.png` absolutely:
   - desktop: right 0, top 56 px, width 620 px
   - tablet: right -80 px, top 80 px, width 520 px
   - mobile: hide asset below 640 px
3. Render app UI above background at z-index 2.
4. Icons import as inline SVG so hover color can be controlled by CSS.

## Motion Rules

- CTA press is CSS transform, not image frames.
- Background is static.
- Step hover uses CSS transform and icon color transition.
- Reduced motion disables all transforms.

## Implementation Notes

- Put assets under `src/assets/frontend-ui-pipeline/onboarding/` for bundled imports.
- Preload the background image on the onboarding route.
- Keep mock data in `src/features/onboarding/mockOnboardingSteps.ts` if no API exists.

## Acceptance Checklist

- Asset paths match imports exactly.
- No generic filenames remain.
- User approved final review package.
