#!/usr/bin/env python3
"""Diagnose a local Frontend UI Pipeline plugin installation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLUGIN_NAME = "frontend-ui-pipeline"
REQUIRED_SKILLS = (
    "frontend-ui-ideation",
    "frontend-asset-production",
    "frontend-implementation",
)
START_PROMPT = """Use $frontend-ui-ideation to redesign this existing app flow.

Input:
- <paste an old screenshot, local project path, localhost URL, Figma link, or page description>

Goal:
- Create a premium UI brief and preview first.
- Then generate the complete Phase 2 asset kit and stop for my asset approval.
- After I approve the assets, implement it in the real frontend; use real APIs when available, otherwise use same-shape mocks.
"""


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def status_line(label: str, status: str, detail: str = "") -> str:
    suffix = f" - {detail}" if detail else ""
    return f"- {label}: `{status}`{suffix}"


def repo_status(repo: Path) -> tuple[list[str], str]:
    lines: list[str] = []
    manifest_path = repo / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    if not manifest:
        lines.append(status_line("Plugin manifest", "missing", str(manifest_path)))
        return lines, "unknown"

    version = str(manifest.get("version", "unknown"))
    name = manifest.get("name")
    lines.append(status_line("Plugin manifest", "ok", f"{name} {version}"))

    for skill in REQUIRED_SKILLS:
        skill_path = repo / "skills" / skill / "SKILL.md"
        lines.append(
            status_line(f"Skill {skill}", "ok" if skill_path.exists() else "missing", str(skill_path))
        )

    for script in (
        "install_local_marketplace.py",
        "quick_check.py",
        "generate_pipeline_runbook.py",
    ):
        script_path = repo / "scripts" / script
        lines.append(status_line(f"Script {script}", "ok" if script_path.exists() else "missing"))

    return lines, version


def marketplace_status(marketplace_path: Path) -> list[str]:
    payload = load_json(marketplace_path)
    if not payload:
        return [status_line("Marketplace entry", "missing", f"run scripts/install_local_marketplace.py")]

    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        return [status_line("Marketplace entry", "invalid", str(marketplace_path))]

    for plugin in plugins:
        if not isinstance(plugin, dict) or plugin.get("name") != PLUGIN_NAME:
            continue
        source = plugin.get("source") if isinstance(plugin.get("source"), dict) else {}
        source_path = source.get("path", "")
        marketplace_name = payload.get("name", "personal")
        detail = f"{marketplace_name}: {source_path or 'no source path'}"
        return [status_line("Marketplace entry", "ok", detail)]

    return [status_line("Marketplace entry", "missing", f"run scripts/install_local_marketplace.py")]


def installed_cache_status(home: Path, expected_version: str) -> list[str]:
    cache_root = home / ".codex" / "plugins" / "cache" / "personal" / PLUGIN_NAME
    if not cache_root.exists():
        return [status_line("Installed cache", "missing", f"run codex plugin add {PLUGIN_NAME}@personal")]

    versions = sorted(path.name for path in cache_root.iterdir() if path.is_dir())
    if not versions:
        return [status_line("Installed cache", "missing", f"run codex plugin add {PLUGIN_NAME}@personal")]

    latest = versions[-1]
    status = "ok" if expected_version == "unknown" or expected_version in versions else "version-mismatch"
    detail = f"installed: {', '.join(versions)}"
    if status == "version-mismatch":
        detail += f"; repo version: {expected_version}; rerun codex plugin add {PLUGIN_NAME}@personal"
    return [status_line("Installed cache", status, detail)]


def expected_location_status(repo: Path, home: Path) -> list[str]:
    expected = home / "plugins" / PLUGIN_NAME
    if repo.resolve() == expected.resolve():
        return [status_line("Repo location", "ok", str(expected))]
    return [
        status_line(
            "Repo location",
            "warning",
            f"recommended path is {expected}; current path is {repo}",
        )
    ]


def parse_args() -> argparse.Namespace:
    default_repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Diagnose Frontend UI Pipeline installation.")
    parser.add_argument("--repo", default=str(default_repo), help="Plugin repository root.")
    parser.add_argument("--home", default=str(Path.home()), help="Home directory to inspect.")
    parser.add_argument("--marketplace", default="", help="Marketplace JSON path. Defaults to <home>/.agents/plugins/marketplace.json.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    home = Path(args.home).expanduser().resolve()
    marketplace = (
        Path(args.marketplace).expanduser().resolve()
        if args.marketplace
        else home / ".agents" / "plugins" / "marketplace.json"
    )

    repo_lines, version = repo_status(repo)
    lines = [
        "# Frontend UI Pipeline Install Doctor",
        "",
        *repo_lines,
        *expected_location_status(repo, home),
        *marketplace_status(marketplace),
        *installed_cache_status(home, version),
        "",
        "## Next Commands",
        "",
        "```bash",
        "python3 scripts/install_local_marketplace.py",
        f"codex plugin add {PLUGIN_NAME}@personal",
        "```",
        "",
        "Open a new Codex thread after reinstalling so the three skills are loaded.",
        "",
        "## Next Start Prompt",
        "",
        "```text",
        START_PROMPT.strip(),
        "```",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
