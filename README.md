# Frontend UI Pipeline

[![Quick Check](https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin/actions/workflows/quick-check.yml/badge.svg)](https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin/actions/workflows/quick-check.yml)
[![Release](https://img.shields.io/github/v/release/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin)](https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Create premium custom UI, art assets, motion specs, and real frontend implementations from an existing app flow.

This Codex plugin is built for people who do not draw UI, design visual systems, or write frontend code every day. Give Codex an existing screen, route, screenshot, Figma frame, or app flow, then run the pipeline in three focused stages:

1. **Ideation**: turn the current product flow into a high-end UI direction, preview image, and pixel-level Markdown spec.
2. **Asset Production**: generate and name production art assets, motion frames, backgrounds, icons, masks, sprites, and an exact assembly handoff.
3. **Implementation**: install the approved assets into the real frontend app, connect real APIs when available, and use faithful mocks when needed.

The goal is simple: help non-designers and non-frontend specialists ship a polished, custom interface that can actually land in production.

## Why This Exists

Most AI UI generators stop at a pretty picture. This plugin forces the missing handoff:

- **Phase 1 creates the design contract**: background, components, copy, buttons, state rules, motion, and acceptance criteria.
- **Phase 2 creates the real asset package**: named files, dimensions, layer order, responsive placement, and user approval before final handoff.
- **Phase 3 changes the actual app**: imports assets, builds layout, wires APIs or mocks, runs checks, and verifies screenshots.

## Install

### 1. Clone the plugin

```bash
mkdir -p ~/plugins
git clone https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin.git ~/plugins/frontend-ui-pipeline
```

### 2. Register it in your personal Codex marketplace

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/install_local_marketplace.py
```

### 3. Add it in Codex

```bash
codex plugin add frontend-ui-pipeline@personal
```

Then start a new Codex thread so the plugin skills are loaded.

## Update

```bash
cd ~/plugins/frontend-ui-pipeline
git pull
python3 scripts/install_local_marketplace.py
codex plugin add frontend-ui-pipeline@personal
```

Start a new thread after updating.

## Quick Check

Run this after cloning or changing the plugin:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/quick_check.py
```

It verifies the manifest, three skills, UI metadata, and common placeholder mistakes without external dependencies.

## Try It In 5 Minutes

1. Install the plugin.
2. Open [examples/quickstart/app-flow-brief.md](examples/quickstart/app-flow-brief.md).
3. Paste the example prompt into a new Codex thread.
4. Let Phase 1 create the first brief and preview.

For more starter prompts, use [PROMPTS.md](PROMPTS.md).

## Quality Bar

This plugin is meant to create shippable frontend work, not just attractive mockups. See [docs/quality-bar.md](docs/quality-bar.md) for the pass/fail criteria each phase should meet.

## How To Use

Use one phase at a time when you want control, or run the whole pipeline when you already know the target app flow.

### Full Pipeline Prompt

```text
Use the Frontend UI Pipeline on this app flow.
Target: <route, screen, repo path, screenshot, Figma link, or local URL>
Goal: make it feel like a premium custom product, then create assets and implement it in the real frontend.
```

### Phase 1: UI Ideation

```text
Use $frontend-ui-ideation to redesign this existing app flow into a premium UI brief and preview.
```

Output:

- `phase1-ui-brief.md`
- one or more preview images
- pixel-level requirements for layout, background, components, text, buttons, states, click feedback, and motion

### Phase 2: Asset Production

```text
Use $frontend-asset-production with this phase 1 brief and preview. Generate the real assets, then ask me to review before finalizing.
```

Output:

- approved asset files
- named backgrounds, component overlays, icons, masks, textures, sprites, or motion frames
- `phase2-asset-handoff.md`
- exact layer order, placement, responsive rules, import paths, and motion calling rules

Phase 2 must stop for user review before final output.

### Phase 3: Frontend Implementation

```text
Use $frontend-implementation with the approved phase 2 assets. Hot-replace the real frontend route. Connect real APIs if available; otherwise mock it to match the preview.
```

Output:

- real frontend code changes
- imported assets and motion
- real API wiring or isolated mock data
- verification commands and screenshots
- local dev server URL when needed

## Included Skills

| Skill | When to use it |
| --- | --- |
| `$frontend-ui-ideation` | Collect ideas from an existing app and produce a premium UI spec plus preview. |
| `$frontend-asset-production` | Turn the approved spec into production art assets and an asset handoff. |
| `$frontend-implementation` | Implement the approved assets into the real frontend app. |

## Example Outputs

These examples show the expected handoff quality:

- [Phase 1 brief example](examples/outputs/phase1-ui-brief.example.md)
- [Phase 2 asset handoff example](examples/outputs/phase2-asset-handoff.example.md)

## What You Need To Provide

Best inputs:

- a repo path, local route, or running app URL
- screenshots or Figma frames if the app is not runnable
- the business goal and target users
- any brand assets or style references
- API docs or notes, if available

If you do not know the design direction, say that. Phase 1 is designed to discover it with you.

## What This Plugin Does Not Promise

- It cannot guarantee GitHub stars, product-market fit, or production approval by itself.
- It does not replace legal review, accessibility certification, brand approval, or security review.
- It should not silently overwrite unrelated app code; Phase 3 is scoped to the requested screen or flow.

## Roadmap To A 2k-Star Repo

The practical path is:

- ship a frictionless install path
- publish before/after demos from real app flows
- keep the README short enough to try in five minutes
- collect issues from early users and improve the pipeline prompts
- add a gallery of successful UI transformations
- make Phase 2 asset review especially reliable

See [docs/launch-playbook.md](docs/launch-playbook.md) for the public launch checklist.

## Contributing

Issues and pull requests are welcome. Good contributions improve one of three things:

- better output quality for non-designers
- fewer steps from install to first successful UI
- more reliable frontend implementation handoff

## License

MIT
