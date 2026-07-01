#!/usr/bin/env python3
"""Create a ready-to-send start prompt for Frontend UI Pipeline."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLUGIN_NAME = "frontend-ui-pipeline"
START_SKILL = "$frontend-ui-ideation"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value.strip(), re.I))


def input_kind(raw: str) -> dict[str, Any]:
    value = raw.strip()
    if not value:
        fail("Input values cannot be empty.")

    if is_url(value):
        lowered = value.lower()
        if "figma.com/" in lowered:
            kind = "figma-link"
        elif "localhost" in lowered or "127.0.0.1" in lowered or "0.0.0.0" in lowered:
            kind = "localhost-url"
        else:
            kind = "url"
        return {"kind": kind, "value": value, "exists": None, "absolutePath": ""}

    path_value = Path(value).expanduser()
    if path_value.exists():
        resolved = path_value.resolve()
        suffix = resolved.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            kind = "screenshot"
        elif resolved.is_dir():
            kind = "local-project-path"
        elif suffix in {".vue", ".tsx", ".jsx", ".ts", ".js", ".html", ".css", ".scss"}:
            kind = "source-file"
        else:
            kind = "local-file"
        return {"kind": kind, "value": value, "exists": True, "absolutePath": str(resolved)}

    return {"kind": "page-description", "value": value, "exists": False, "absolutePath": ""}


def build_prompt(args: argparse.Namespace, inputs: list[dict[str, Any]], run_root: Path) -> str:
    project = args.project.strip() or "Unnamed project"
    target = args.target.strip() or "infer from the provided input"
    context = args.context.strip()
    mode = args.mode
    input_lines = []
    for item in inputs:
        label = item["kind"]
        value = item["absolutePath"] or item["value"]
        exists = ""
        if item["exists"] is False and item["kind"] != "page-description":
            exists = " (path not found, treat as description unless I correct it)"
        input_lines.append(f"- {label}: {value}{exists}")

    context_block = f"\nExtra context:\n{context}\n" if context else ""
    return "\n".join(
        [
            f"Use {START_SKILL} to redesign this existing app flow.",
            "",
            f"Project: {project}",
            f"Target: {target}",
            f"Run mode: {mode}",
            f"Save all generated artifacts under: {run_root}",
            "",
            "Input:",
            *input_lines,
            context_block.rstrip(),
            "",
            "Goal:",
            "- Create a premium custom UI direction that feels more polished than a generic Product Design output.",
            "- Phase 1 must inspect the real source, generate exactly three visual directions, select or recommend one, and write phase1-ui-brief.md.",
            "- Phase 1 must include a Phase 2 generation guide with layer order, adjustable parameters, naming/export rules, responsive crop rules, and the full foundation component inventory.",
            "- Phase 2 must generate the selected-screen assets first, then the complete Phase 2 asset kit and foundation asset kit: backgrounds, illustrations, buttons, numeric badges, cards, combobox, common icons, nav, notice, search, section title, modal, and transitions.",
            "- Phase 2 must stop for my asset approval before writing the final phase2-asset-handoff.md.",
            "- After I approve assets, Phase 3 must implement the real frontend; connect real APIs when callable, otherwise use same-shape mocks.",
            "- Generate runbook and completion audit evidence as the pipeline progresses.",
            "",
            "Do not hot-replace production code until Phase 2 assets are explicitly approved.",
        ]
    ).replace("\n\n\n", "\n\n")


def markdown(payload: dict[str, Any]) -> str:
    input_rows = ["| Kind | Value | Exists |", "| --- | --- | --- |"]
    for item in payload["inputs"]:
        value = item.get("absolutePath") or item["value"]
        exists = item["exists"]
        exists_text = "n/a" if exists is None else ("yes" if exists else "no")
        input_rows.append(f"| `{item['kind']}` | `{value}` | `{exists_text}` |")
    return "\n".join(
        [
            "# Frontend UI Pipeline Start",
            "",
            f"- Project: `{payload['project']}`",
            f"- Target: `{payload['target']}`",
            f"- Mode: `{payload['mode']}`",
            f"- Created at: `{payload['createdAt']}`",
            "",
            "## Ready-To-Send Codex Prompt",
            "",
            "```text",
            payload["prompt"],
            "```",
            "",
            "## Inputs",
            "",
            *input_rows,
            "",
            "## How To Use",
            "",
            "1. Install the plugin and run `codex plugin add frontend-ui-pipeline@personal`.",
            "2. Open a new Codex thread so the skills load.",
            "3. Paste the ready-to-send prompt above into the bottom message box.",
            "4. Attach or paste the referenced screenshot, URL, Figma link, path, or page description if it is not already visible to Codex.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a ready-to-send Frontend UI Pipeline start prompt.")
    parser.add_argument("--input", action="append", required=True, help="Screenshot path, project path, localhost URL, Figma link, source file, or page description. Can repeat.")
    parser.add_argument("--project", default="", help="Project or product name.")
    parser.add_argument("--target", default="", help="Target route, screen, component, or flow.")
    parser.add_argument("--mode", choices=("production", "demo"), default="production", help="Run mode for the pipeline.")
    parser.add_argument("--context", default="", help="Extra product, brand, audience, API, or business context.")
    parser.add_argument("--run-root", default="./frontend-ui-pipeline-run", help="Folder where pipeline artifacts should be saved.")
    parser.add_argument("--output-md", default="", help="Markdown output path. Defaults to <run-root>/pipeline-start.md.")
    parser.add_argument("--output-json", default="", help="JSON output path. Defaults to <run-root>/pipeline-start.json.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    inputs = [input_kind(raw) for raw in args.input]
    prompt = build_prompt(args, inputs, run_root)
    payload = {
        "schemaVersion": "frontend-ui-pipeline.start.v1",
        "plugin": PLUGIN_NAME,
        "project": args.project.strip() or "Unnamed project",
        "target": args.target.strip() or "infer from input",
        "mode": args.mode,
        "runRoot": str(run_root),
        "createdAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "inputs": inputs,
        "prompt": prompt,
    }
    output_md = Path(args.output_md).expanduser().resolve() if args.output_md else run_root / "pipeline-start.md"
    output_json = Path(args.output_json).expanduser().resolve() if args.output_json else run_root / "pipeline-start.json"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown(payload), encoding="utf-8")
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print("")
    print(prompt)


if __name__ == "__main__":
    main()
