#!/usr/bin/env python3
"""Generate a non-designer Phase 2 asset approval packet."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path


APPROVAL_CHOICES = [
    (
        "Approve assets",
        "The style, naming, coverage, and implementation mapping are acceptable. Phase 2 can finalize the handoff.",
        "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation.",
    ),
    (
        "Revise visual style",
        "The asset names and coverage are useful, but the look needs adjustment before handoff.",
        "Revise visual style: <describe color, density, illustration, icon, or motion changes>.",
    ),
    (
        "Revise naming or organization",
        "The visuals are acceptable, but filenames, folders, manifest paths, or grouping need cleanup.",
        "Revise naming/organization: <describe required folder, filename, or manifest changes>.",
    ),
    (
        "Revise implementation mapping",
        "The assets are acceptable, but layer order, CSS selectors, import paths, or motion triggers need changes.",
        "Revise implementation mapping: <describe placement, selector, import, or motion changes>.",
    ),
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_manifest(path: Path) -> dict:
    if not path.exists():
        fail(f"Manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Manifest is not valid JSON: {exc}")
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        fail("Manifest must be a JSON object with an entries array")
    return payload


def relpath(target: str, output_dir: Path) -> str:
    if not target:
        return ""
    path = Path(target).expanduser()
    if not path.is_absolute():
        return target
    try:
        return os.path.relpath(path, output_dir)
    except ValueError:
        return str(path)


def coverage_lines(manifest: dict) -> list[str]:
    coverage = manifest.get("coverage", {})
    foundation = coverage.get("foundationComponents", {})
    foundation_total = sum(foundation.values()) if isinstance(foundation, dict) else "unknown"
    return [
        f"- Screen asset slots: `{coverage.get('screenAssetSlots', 'unknown')}`",
        f"- Foundation states: `{foundation_total}`",
        f"- Common icons: `{coverage.get('commonIcons', 'unknown')}`",
        f"- Total manifest entries: `{coverage.get('totalEntries', len(manifest.get('entries', [])))}`",
    ]


def first_entries(manifest: dict, limit: int = 16) -> list[str]:
    lines = []
    for entry in manifest.get("entries", [])[:limit]:
        if not isinstance(entry, dict):
            continue
        lines.append(
            f"- `{entry.get('id', '')}` -> `{entry.get('assetPath', '')}` "
            f"({entry.get('category', '')}/{entry.get('state', '')})"
        )
    return lines


def known_review_notes(args: argparse.Namespace, manifest: dict, output_dir: Path) -> list[str]:
    """Explain what the reviewer should judge before approval."""
    assembly_preview = relpath(args.assembly_preview, output_dir)
    visual_diff_report = relpath(args.visual_diff_report, output_dir)
    notes = [
        "Judge the style fidelity, asset coverage, naming/organization, and Phase 3 implementation mapping.",
    ]
    if assembly_preview:
        notes.append(
            f"`{assembly_preview}` is the primary screen assembled from generated Phase 2 assets; do not treat the Phase 1 preview screenshot as proof that assets can be assembled."
        )
    else:
        notes.append(
            "No asset-assembled primary screen preview was provided. Before approval, generate one from the Phase 2 assets or clearly mark why this run is blocked."
        )
    if visual_diff_report:
        notes.append(
            f"`{visual_diff_report}` records the visual diff. If it fails because the comparison is an asset assembly rather than a final app screenshot, document that and keep Phase 3 screenshot QA as the final pixel gate."
        )
    if manifest.get("evidence", {}).get("assemblyUsesGeneratedAssets") is True:
        notes.append("The manifest evidence marks `assemblyUsesGeneratedAssets=true`.")
    return [f"- {note}" for note in notes]


def build_markdown(args: argparse.Namespace, manifest: dict, output_dir: Path) -> str:
    project = manifest.get("project", {})
    contact_sheet = relpath(args.contact_sheet, output_dir)
    assembly_preview = relpath(args.assembly_preview, output_dir)
    visual_diff_report = relpath(args.visual_diff_report, output_dir)
    prompt_pack = relpath(args.prompt_pack, output_dir)
    phase1_brief = relpath(args.phase1_brief, output_dir)
    manifest_path = relpath(args.manifest, output_dir)
    lines = [
        f"# Phase 2 Asset Approval Packet: {project.get('screen', project.get('name', 'target-screen'))}",
        "",
        "## What To Review",
        "",
        "Review whether the generated assets match the approved Phase 1 style, cover the full foundation kit, and can be assembled by Phase 3 without guessing.",
        "",
        "## Source Files",
        "",
        f"- Phase 1 brief: `{phase1_brief}`" if phase1_brief else "- Phase 1 brief: not provided",
        f"- Asset manifest: `{manifest_path}`",
        f"- Asset prompt pack: `{prompt_pack}`" if prompt_pack else "- Asset prompt pack: not provided",
        f"- Contact sheet: `{contact_sheet}`" if contact_sheet else "- Contact sheet: not provided",
        f"- Asset-assembled primary screen preview: `{assembly_preview}`" if assembly_preview else "- Asset-assembled primary screen preview: not provided",
        f"- Visual diff report: `{visual_diff_report}`" if visual_diff_report else "- Visual diff report: not provided",
        f"- Review URL: {args.review_url}" if args.review_url else "- Review URL: not provided",
        "",
        "## Coverage",
        "",
        *coverage_lines(manifest),
        "",
        "## Visual Contact Sheet",
        "",
    ]
    if contact_sheet:
        lines.extend([f"![Phase 2 contact sheet]({contact_sheet})", ""])
    else:
        lines.extend(["No contact sheet path was provided.", ""])

    lines.extend(["## Primary Screen Asset Assembly", ""])
    if assembly_preview:
        lines.extend(
            [
                f"![Primary screen asset assembly]({assembly_preview})",
                "",
                "This preview must be built from generated Phase 2 assets, not copied from the Phase 1 source screenshot.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "No asset-assembled primary screen preview was provided.",
                "",
            ]
        )

    lines.extend(["## Known Review Notes", "", *known_review_notes(args, manifest, output_dir), ""])

    lines.extend(
        [
            "## Decision Options",
            "",
            "Send exactly one of these decisions back to Codex:",
            "",
        ]
    )
    for title, description, message in APPROVAL_CHOICES:
        lines.extend([f"### {title}", "", description, "", "```text", message, "```", ""])

    lines.extend(
        [
            "## Quick Asset Sample",
            "",
            *first_entries(manifest),
            "",
            "## Approval Gate",
            "",
            "Do not generate the final `phase2-asset-handoff.md` or hot-replace the real application until the user explicitly approves the assets.",
            "",
        ]
    )
    return "\n".join(lines)


def build_html(markdown: str, args: argparse.Namespace, manifest: dict, output_dir: Path) -> str:
    project = manifest.get("project", {})
    contact_sheet = relpath(args.contact_sheet, output_dir)
    assembly_preview = relpath(args.assembly_preview, output_dir)
    coverage = coverage_lines(manifest)
    notes_html = "\n".join(f"<li>{html.escape(line[2:] if line.startswith('- ') else line)}</li>" for line in known_review_notes(args, manifest, output_dir))
    choices_html = "\n".join(
        "<article><h3>{}</h3><p>{}</p><pre>{}</pre></article>".format(
            html.escape(title), html.escape(description), html.escape(message)
        )
        for title, description, message in APPROVAL_CHOICES
    )
    sample_html = "\n".join(f"<li>{html.escape(line)}</li>" for line in first_entries(manifest))
    coverage_html = "\n".join(f"<li>{html.escape(line)}</li>" for line in coverage)
    image_html = (
        f'<img src="{html.escape(contact_sheet)}" alt="Phase 2 contact sheet">'
        if contact_sheet
        else "<p>No contact sheet path was provided.</p>"
    )
    assembly_html = (
        f'<img src="{html.escape(assembly_preview)}" alt="Primary screen assembled from Phase 2 assets">'
        if assembly_preview
        else "<p>No asset-assembled primary screen preview was provided.</p>"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Phase 2 Asset Approval Packet</title>
  <style>
    :root {{ color-scheme: dark; --bg:#0b0f12; --panel:#121a22; --line:#294755; --text:#f6f1df; --muted:#9da6a7; --accent:#25d6a2; --gold:#e8c36a; --red:#d84b4b; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }}
    main {{ max-width:1120px; margin:0 auto; padding:32px 20px 56px; }}
    header {{ border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:24px; }}
    h1 {{ margin:0 0 8px; font-size:clamp(28px,4vw,46px); letter-spacing:0; }}
    h2 {{ margin:32px 0 12px; font-size:22px; }}
    h3 {{ margin:0 0 8px; font-size:17px; color:var(--gold); }}
    p, li {{ color:var(--muted); line-height:1.6; }}
    img {{ width:100%; border:1px solid var(--line); border-radius:8px; background:#091014; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; }}
    article {{ border:1px solid var(--line); background:var(--panel); border-radius:8px; padding:16px; }}
    pre {{ white-space:pre-wrap; word-break:break-word; color:var(--accent); background:#071015; border-radius:6px; padding:12px; overflow:auto; }}
    code {{ color:var(--accent); }}
    .status {{ color:var(--accent); font-weight:700; }}
  </style>
</head>
<body>
<main>
  <header>
    <p class="status">Phase 2 asset approval gate</p>
    <h1>{html.escape(str(project.get('screen', project.get('name', 'target-screen'))))}</h1>
    <p>Review style fidelity, asset coverage, naming, and implementation mapping before Phase 2 final handoff.</p>
  </header>
  <section>
    <h2>Coverage</h2>
    <ul>{coverage_html}</ul>
  </section>
  <section>
    <h2>Contact Sheet</h2>
    {image_html}
  </section>
  <section>
    <h2>Primary Screen Asset Assembly</h2>
    {assembly_html}
    <p>This preview must be assembled from generated Phase 2 assets, not copied from the Phase 1 source screenshot.</p>
  </section>
  <section>
    <h2>Known Review Notes</h2>
    <ul>{notes_html}</ul>
  </section>
  <section>
    <h2>Decision Options</h2>
    <div class="grid">{choices_html}</div>
  </section>
  <section>
    <h2>Quick Asset Sample</h2>
    <ul>{sample_html}</ul>
  </section>
  <section>
    <h2>Raw Markdown</h2>
    <pre>{html.escape(markdown)}</pre>
  </section>
</main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 2 asset approval packet.")
    parser.add_argument("--manifest", required=True, help="Path to Phase 2 asset manifest JSON")
    parser.add_argument("--output-dir", required=True, help="Directory for approval Markdown and HTML")
    parser.add_argument("--phase1-brief", default="", help="Optional Phase 1 brief path")
    parser.add_argument("--prompt-pack", default="", help="Optional Phase 2 asset prompt pack path")
    parser.add_argument("--contact-sheet", default="", help="Optional contact sheet image path")
    parser.add_argument("--assembly-preview", default="", help="Optional primary screen preview assembled from generated Phase 2 assets")
    parser.add_argument("--visual-diff-report", default="", help="Optional visual diff report for Phase 1 preview versus Phase 2 assembly or contact sheet")
    parser.add_argument("--review-url", default="", help="Optional local review server URL")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(manifest_path)
    markdown = build_markdown(args, manifest, output_dir)
    markdown_path = output_dir / "phase2-asset-approval-packet.md"
    html_path = output_dir / "phase2-asset-approval-packet.html"
    markdown_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(build_html(markdown, args, manifest, output_dir), encoding="utf-8")
    print(f"Wrote {markdown_path}")
    print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
