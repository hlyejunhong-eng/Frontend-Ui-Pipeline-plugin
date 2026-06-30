# Demo: DraftPilot Onboarding Dashboard

This end-to-end demo shows what the plugin should produce for a non-designer/non-frontend user.

Input:

- A plain onboarding dashboard description for an AI writing assistant.
- No design files.
- No real API.

Pipeline output:

1. Phase 1: [`phase1/phase1-ui-brief.md`](phase1/phase1-ui-brief.md)
2. Phase 1 preview screenshots:
   - [`phase1/phase1-preview-desktop.png`](phase1/phase1-preview-desktop.png)
   - [`phase1/phase1-preview-mobile.png`](phase1/phase1-preview-mobile.png)
3. Phase 2: [`phase2/phase2-asset-handoff.md`](phase2/phase2-asset-handoff.md)
4. Phase 2 asset manifest: [`phase2/asset-manifest.json`](phase2/asset-manifest.json)
5. Phase 2 visual review: [`phase2/asset-review/contact-sheet.html`](phase2/asset-review/contact-sheet.html)
6. Phase 3 runnable frontend: [`phase3/implementation/index.html`](phase3/implementation/index.html)
7. Phase 3 implementation note: [`phase3/implementation/implementation-note.md`](phase3/implementation/implementation-note.md)
8. Verification screenshots:
   - [`evidence/screenshots/draftpilot-desktop.png`](evidence/screenshots/draftpilot-desktop.png)
   - [`evidence/screenshots/draftpilot-mobile.png`](evidence/screenshots/draftpilot-mobile.png)

## Run It

Open:

```text
examples/demo-draftpilot/phase3/implementation/index.html
```

No build step is required.

## What This Proves

- Phase 1 can turn a vague product brief into a pixel-level design contract.
- Phase 1 can hand Phase 2 a concrete generation guide with layer order and adjustable parameters.
- Phase 2 can create named assets, a complete foundation component kit, common icons, and composition instructions without empty placeholders.
- Phase 3 can ship a real, responsive frontend using assets and mocks when no API exists.
