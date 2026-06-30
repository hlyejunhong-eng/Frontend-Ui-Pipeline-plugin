# Quality Bar

Frontend UI Pipeline should produce work that can move from idea to shipped frontend. Use this bar to judge whether a run succeeded.

## Phase 1 Succeeds When

- The agent inspected the source app, screenshot, URL, Figma frame, or other concrete source artifact.
- The output includes `phase1-ui-brief.md`.
- The output includes at least one preview image or screenshot of a generated HTML/CSS preview.
- The brief specifies layout, background, components, copy, buttons, states, click feedback, and motion.
- The brief names the assets Phase 2 should produce.
- A non-designer can read the brief and understand what will be built.

## Phase 1 Fails When

- It only gives mood words such as "modern", "premium", or "clean".
- It does not produce a preview.
- It ignores real product copy, route structure, or data states.
- It cannot tell Phase 2 what assets to create.

## Phase 2 Succeeds When

- The output contains real asset files that render visible UI material.
- Asset names are specific and predictable.
- The review package lets the user inspect the assets visually.
- The user explicitly approves the assets before final handoff.
- `phase2-asset-handoff.md` maps assets to layers, components, states, import paths, and motion triggers.
- Phase 3 can import the assets without guessing what each file is for.

## Phase 2 Fails When

- It creates empty placeholders or generic files such as `image1.png`.
- It skips user asset review.
- It writes prose about assets without producing files.
- It cannot explain how assets should be composed in the frontend.

## Phase 3 Succeeds When

- The final result is runnable frontend code.
- Assets from Phase 2 are imported or served from stable paths.
- Real APIs are used when available.
- If APIs are unavailable, mocks match the preview data shape and visual density.
- Desktop and mobile screenshots are captured or a concrete external blocker is documented.
- Lint, typecheck, tests, build, or the closest available project checks were run.
- The user gets a local URL or exact run command.

## Phase 3 Fails When

- It stops at a static design image.
- It leaves assets disconnected from the app.
- It hides missing API work inside unstructured mock data.
- It claims pixel match without browser screenshots or visual comparison.
- It changes unrelated parts of the app.

## Minimum Evidence For A Complete Run

A complete pipeline run should leave:

- `phase1-ui-brief.md`
- Phase 1 preview image or screenshot
- approved asset folder
- asset review package
- `phase2-asset-handoff.md`
- frontend code changes
- verification command output
- desktop and mobile screenshots, when the app can run locally
