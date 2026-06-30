# Copy-Paste Prompts

Use these prompts as starter commands in Codex after installing the plugin.

## Full Pipeline

```text
Use the Frontend UI Pipeline to redesign and implement this app flow.

Target:
- Repo or app path: <path>
- Route or screen: <route>
- Current state source: <screenshot, local URL, Figma link, or app recording>

Goal:
Make this flow feel like a premium custom product for <target users>. I do not know UI design or frontend implementation, so guide the process and make the decisions that are safe to make.

Requirements:
- Start with Phase 1 and produce the Markdown brief plus preview images.
- Use Phase 2 to create named production art assets and stop for my review before finalizing.
- Use Phase 3 to implement the approved assets in the real frontend.
- Connect real APIs if they exist. If they do not exist, create mock data that matches the preview exactly.
- Show verification results and the local URL when done.
```

## Phase 1 Only: Premium UI Brief

```text
Use $frontend-ui-ideation on this existing app flow.

Target:
- <route, screen name, screenshot, local URL, Figma link, or repo path>

What I want:
- A high-end custom UI direction.
- Preview image(s) that show the real target screen or flow.
- A phase1-ui-brief.md file with pixel-level requirements for layout, background, components, copy, buttons, states, click feedback, and motion.

If the design direction is unclear, propose three directions and recommend one.
```

## Phase 2 Only: Real Assets

```text
Use $frontend-asset-production with these Phase 1 artifacts.

Inputs:
- Brief: <path to phase1-ui-brief.md>
- Preview image(s): <paths>

Create:
- production-ready named assets
- a review contact sheet or preview folder
- an asset manifest
- phase2-asset-handoff.md with exact layer order, placement, responsive rules, import paths, and motion calling rules

Important:
Stop and ask me to approve the assets before writing the final handoff.
```

## Phase 3 Only: Real Frontend Implementation

```text
Use $frontend-implementation with these approved Phase 2 artifacts.

Inputs:
- Asset handoff: <path to phase2-asset-handoff.md>
- Approved assets: <asset folder>
- Target frontend route/component: <path or route>

Implement:
- the approved visual design in the real app
- click feedback, hover/focus/press states, transitions, and reduced-motion fallback
- real API connections if available
- exact mock data if real APIs are unavailable

Verify:
- run available lint/typecheck/build/tests
- start the dev server if needed
- capture desktop and mobile screenshots
- report any remaining risks
```

## If You Only Have A Screenshot

```text
Use $frontend-ui-ideation from this screenshot.

I only have a screenshot, not a repo yet. Create the Phase 1 premium UI brief and preview anyway. Make the brief detailed enough that a later Phase 2 can generate assets and a later Phase 3 can implement it in React, Vue, or plain HTML.
```

## If You Have A Repo But No Design Taste

```text
Use the Frontend UI Pipeline on this repo. I do not have a visual direction. Inspect the current app, infer what the product is trying to do, propose three premium UI directions, choose the strongest one unless I object, and continue toward real implementation.
```
