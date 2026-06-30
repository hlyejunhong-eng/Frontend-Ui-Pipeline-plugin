# Example Phase 1 UI Brief

This abbreviated example shows the level of specificity expected from `$frontend-ui-ideation`.

## Context

Product: DraftPilot, an AI writing assistant for small business owners.

Target flow: onboarding dashboard after signup.

User intent: finish setup quickly and create the first campaign without learning a complex product.

## Selected Direction

Direction: "Command center with warm editorial craft."

Rationale: the user needs confidence and momentum. The UI should feel premium and guided, with a strong setup path and subtle brand-building atmosphere.

## Layout Spec

- Desktop canvas: 1440 x 1024.
- Main grid: sidebar 248 px, content max-width 1040 px, right rail 280 px.
- Page padding: 32 px desktop, 20 px tablet, 16 px mobile.
- Primary content begins at x 296, y 40.
- Setup step cards use a 12 px vertical gap and fixed min-height of 104 px.
- Mobile stacks sidebar actions into a top toolbar and renders steps as full-width rows.

## Background Spec

- Base fill: `#F7F4EE`.
- Content background: soft radial light behind the hero area, centered at 62% x / 18% y.
- Decorative asset: abstract paper-ribbon shape behind the setup progress panel.
- No decorative element may obscure text or buttons.

## Component Spec

### Primary CTA

- Label: `Create first campaign`.
- Height: 48 px.
- Border radius: 8 px.
- Fill: `#111827`.
- Text: 15 px, 600 weight, white.
- Hover: lift y -1 px, shadow opacity +12%.
- Press: scale 0.985 for 90 ms.
- Focus: 2 px outline, `#2563EB`, offset 3 px.

### Setup Step

- Width: fluid.
- Height: 104 px desktop, min-height 96 px mobile.
- Border: 1 px solid rgba(17, 24, 39, 0.12).
- Radius: 8 px.
- Icon slot: 40 x 40 px.
- Completed state uses check icon and muted fill.
- Active state uses darker heading and visible CTA affordance.

## Motion Spec

- Page entrance: content fades from 0 to 1 and translates y 10 px to 0 over 320 ms.
- Step hover: icon rotates 2 degrees and card translates x 2 px over 140 ms.
- CTA press: scale to 0.985 over 90 ms, then spring back over 160 ms.
- Reduced motion: remove transforms and keep opacity changes under 120 ms.

## Phase 2 Asset Expectations

- `assets/backgrounds/onboarding/editorial-ribbon@2x.png`
- `assets/icons/brand-voice.svg`
- `assets/icons/connect-website.svg`
- `assets/icons/create-campaign.svg`
- optional CTA shimmer frames only if implementation cannot use CSS.

## Acceptance Checklist

- The screen reads as premium and custom at first glance.
- CTA and setup path remain obvious.
- No text overlaps at 375 px width.
- Motion has reduced-motion fallback.
