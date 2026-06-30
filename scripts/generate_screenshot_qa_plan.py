#!/usr/bin/env python3
"""Generate a Phase 3 screenshot QA plan and optional Playwright capture script."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


DEFAULT_VIEWPORTS = [
    ("mobile", 390, 844),
    ("desktop", 1365, 916),
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"Inspection JSON does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid inspection JSON: {exc}")
    if not isinstance(payload, dict):
        fail("Inspection JSON must be an object.")
    return payload


def rel(path: Path, root: Path) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned or "target-screen"


def parse_viewport(raw: str) -> tuple[str, int, int]:
    if ":" not in raw or "x" not in raw:
        fail(f"Viewport must look like name:390x844, got {raw}")
    name, size = raw.split(":", 1)
    width, height = size.lower().split("x", 1)
    try:
        return slug(name), int(width), int(height)
    except ValueError:
        fail(f"Viewport dimensions must be integers, got {raw}")


def route_from_inspection(inspection: dict[str, Any]) -> str:
    target = inspection.get("target", {})
    route = target.get("route", {}) if isinstance(target, dict) else {}
    requested = target.get("requested") if isinstance(target, dict) else ""
    return str(route.get("path") or requested or "").strip("/")


def build_url(base_url: str, route_url: str, route: str) -> str:
    if route_url:
        if route_url.startswith(("http://", "https://", "file://")):
            return route_url
        if not base_url:
            return f"<running-app-url>/{route_url.lstrip('/')}"
        if route_url.startswith("#"):
            return base_url.rstrip("/") + "/" + route_url
        return urljoin(base_url.rstrip("/") + "/", route_url.lstrip("/"))
    if not base_url:
        return ""
    if route:
        return urljoin(base_url.rstrip("/") + "/", route.lstrip("/"))
    return base_url


def playwright_script(cases: list[dict[str, Any]]) -> str:
    return """import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const cases = %s;

const browser = await chromium.launch();
for (const item of cases) {
  if (!item.url || item.url.includes('<')) {
    console.log(`Skipping ${item.name}: missing URL`);
    continue;
  }
  const page = await browser.newPage({ viewport: { width: item.width, height: item.height } });
  await page.goto(item.url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(item.waitMs);
  fs.mkdirSync(path.dirname(item.output), { recursive: true });
  await page.screenshot({ path: item.output, fullPage: item.fullPage });
  console.log(`Wrote ${item.output}`);
  await page.close();
}
await browser.close();
""" % json.dumps(cases, ensure_ascii=False, indent=2)


def build_plan(args: argparse.Namespace, inspection: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    route = route_from_inspection(inspection)
    target_name = slug(args.target_name or route or "target-screen")
    viewports = [parse_viewport(raw) for raw in args.viewport] if args.viewport else DEFAULT_VIEWPORTS
    target_url = build_url(args.base_url, args.route_url, route)
    screenshot_dir = output_dir / "screenshots"
    script_path = output_dir / "capture-screenshots.mjs"

    cases = []
    for name, width, height in viewports:
        output_path = screenshot_dir / f"{target_name}-{name}.png"
        cases.append(
            {
                "name": f"{target_name}-{name}",
                "url": target_url or "<start-app-and-fill-url>",
                "width": width,
                "height": height,
                "output": str(output_path),
                "waitMs": args.wait_ms,
                "fullPage": args.full_page,
            }
        )

    screenshot_paths = [case["output"] for case in cases]
    visual_check_command = [
        "python3",
        "<plugin-root>/scripts/check_visual_artifacts.py",
        *screenshot_paths,
        "--min-width",
        "320",
        "--min-height",
        "240",
    ]
    diff_commands = []
    previews = args.approved_preview or []
    for preview in previews:
        preview_path = str(Path(preview).expanduser())
        preview_name = slug(Path(preview).stem)
        for case in cases:
            diff_commands.append(
                [
                    "python3",
                    "<plugin-root>/scripts/compare_visual_artifacts.py",
                    preview_path,
                    case["output"],
                    "--allow-size-mismatch",
                    "--output-md",
                    str(output_dir / f"visual-diff-{preview_name}-to-{case['name']}.md"),
                    "--output-json",
                    str(output_dir / f"visual-diff-{preview_name}-to-{case['name']}.json"),
                ]
            )

    external_notes = inspection.get("runtime", {}).get("externalRuntimeNotes", [])
    recommended_commands = inspection.get("runtime", {}).get("recommendedCommands", [])
    return {
        "schemaVersion": "frontend-ui-pipeline.screenshot-qa-plan.v1",
        "inspectionRoot": inspection.get("root", ""),
        "frameworks": inspection.get("frameworks", []),
        "targetRoute": route,
        "targetUrl": target_url,
        "requiresExternalRuntime": bool(external_notes) and not args.base_url,
        "externalRuntimeNotes": external_notes,
        "recommendedRunCommands": recommended_commands,
        "cases": cases,
        "playwrightScript": str(script_path),
        "visualCheckCommand": visual_check_command,
        "visualDiffCommands": diff_commands,
        "approvedPreviews": previews,
        "notes": [
            "Run the target app first, then execute the generated Playwright script when a browser URL is available.",
            "Use check_visual_artifacts.py after screenshots are captured.",
            "Use compare_visual_artifacts.py when approved preview PNGs are available.",
        ],
    }


def markdown(plan: dict[str, Any], output_dir: Path) -> str:
    case_lines = [
        f"- `{case['name']}`: `{case['width']}x{case['height']}` -> `{rel(Path(case['output']), output_dir)}` at `{case['url']}`"
        for case in plan.get("cases", [])
    ]
    command_lines = [
        f"- `{item.get('command')}` -> `{item.get('script')}`" for item in plan.get("recommendedRunCommands", [])
    ] or ["- No npm run commands detected."]
    external_lines = [f"- {note}" for note in plan.get("externalRuntimeNotes", [])] or ["- None."]
    diff_lines = [" ".join(command) for command in plan.get("visualDiffCommands", [])] or ["No visual diff commands generated because no approved preview was provided."]
    return "\n".join(
        [
            "# Phase 3 Screenshot QA Plan",
            "",
            f"- Inspection root: `{plan.get('inspectionRoot')}`",
            f"- Frameworks: `{', '.join(plan.get('frameworks', []))}`",
            f"- Target route: `{plan.get('targetRoute')}`",
            f"- Target URL: `{plan.get('targetUrl') or 'not provided'}`",
            f"- Requires external runtime before capture: `{plan.get('requiresExternalRuntime')}`",
            f"- Playwright script: `{rel(Path(plan.get('playwrightScript')), output_dir)}`",
            "",
            "## Run Commands",
            "",
            *command_lines,
            "",
            "## External Runtime Notes",
            "",
            *external_lines,
            "",
            "## Screenshot Cases",
            "",
            *case_lines,
            "",
            "## Capture Command",
            "",
            "```bash",
            "node " + rel(Path(plan.get("playwrightScript")), output_dir),
            "```",
            "",
            "## Visual Artifact Check",
            "",
            "```bash",
            " ".join(plan.get("visualCheckCommand", [])),
            "```",
            "",
            "## Visual Diff Commands",
            "",
            "```bash",
            "\n".join(diff_lines),
            "```",
            "",
            "If the target app cannot expose a browser URL, use the external runtime noted above and capture equivalent screenshots manually, then run the visual checks on those files.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a screenshot QA plan for Phase 3.")
    parser.add_argument("--inspection", required=True, help="Path to phase3-target-inspection.json.")
    parser.add_argument("--output-dir", required=True, help="Directory for plan JSON, Markdown, and capture script.")
    parser.add_argument("--base-url", default="", help="Running app base URL, such as http://127.0.0.1:5173.")
    parser.add_argument("--route-url", default="", help="Route URL/path to capture. Use '#/pages/x/y' for uni-app H5 hashes.")
    parser.add_argument("--target-name", default="", help="Name used for screenshot files.")
    parser.add_argument("--approved-preview", action="append", default=[], help="Approved preview PNG for visual diff commands. Can repeat.")
    parser.add_argument("--viewport", action="append", default=[], help="Viewport like mobile:390x844. Can repeat.")
    parser.add_argument("--wait-ms", type=int, default=1200)
    parser.add_argument("--full-page", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inspection = load_json(Path(args.inspection).expanduser().resolve())
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(args, inspection, output_dir)
    (output_dir / "phase3-screenshot-qa-plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "phase3-screenshot-qa-plan.md").write_text(markdown(plan, output_dir), encoding="utf-8")
    Path(plan["playwrightScript"]).write_text(playwright_script(plan["cases"]), encoding="utf-8")
    print(f"Wrote {output_dir / 'phase3-screenshot-qa-plan.md'}")
    print(f"Wrote {output_dir / 'phase3-screenshot-qa-plan.json'}")
    print(f"Wrote {plan['playwrightScript']}")


if __name__ == "__main__":
    main()
