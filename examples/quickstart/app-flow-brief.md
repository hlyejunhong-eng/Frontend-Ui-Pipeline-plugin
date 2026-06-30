# Quickstart Example Input

Copy this into Codex to test the plugin on a small app flow.

```text
Use the Frontend UI Pipeline to redesign and implement this onboarding dashboard.

Target:
- App type: AI writing assistant for small business owners
- Screen: onboarding dashboard after signup
- Current UI: plain white page with a left sidebar, a welcome headline, three setup steps, and a "Create first campaign" button
- Target users: busy founders who are not technical

Current copy:
- Heading: Welcome to DraftPilot
- Subheading: Set up your workspace and create your first campaign.
- Step 1: Add brand voice
- Step 2: Connect website
- Step 3: Create first campaign
- Primary button: Create first campaign
- Secondary button: Skip for now

Goal:
Make it feel like a premium custom SaaS product, not a template dashboard.

Run the pipeline:
1. Phase 1 should create a premium UI brief and preview.
2. Phase 2 should generate production art assets and stop for my review.
3. Phase 3 should implement it. If no real API exists, mock the data exactly like the preview.
```

## What A Good Result Should Include

- A clear visual direction, not just "modern SaaS".
- A `phase1-ui-brief.md` with layout, copy, states, and motion.
- Assets named by purpose and component.
- A `phase2-asset-handoff.md` with import and assembly rules.
- A real frontend route or component wired with mock onboarding data if no API exists.
