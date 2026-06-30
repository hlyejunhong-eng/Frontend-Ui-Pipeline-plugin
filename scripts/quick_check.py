#!/usr/bin/env python3
"""Dependency-free repository checks for Frontend UI Pipeline."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "frontend-ui-ideation",
    "frontend-asset-production",
    "frontend-implementation",
]
COMMON_ICONS = [
    "home",
    "profile",
    "page",
    "scan",
    "cart",
    "payment",
    "chat",
    "confirm",
    "close",
    "back",
    "forward",
    "hot",
    "like",
    "settings",
    "help",
    "info",
    "wallet",
    "list",
    "favorite",
    "search",
]
FOUNDATION_TERMS = [
    "Buttons",
    "Numeric badges",
    "Generic cards",
    "Combobox",
    "Common icons",
    "Navigation bar",
    "Notice bar",
    "Search bar",
    "Section title",
    "Modal",
    "Transition animation",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def check_file(path: Path) -> str:
    if not path.exists():
        fail(f"Missing {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    if "TODO" in text or "[TODO" in text:
        fail(f"Placeholder text found in {path.relative_to(ROOT)}")
    return text


def check_binary(path: Path, *, min_bytes: int = 1) -> bytes:
    if not path.exists():
        fail(f"Missing {path.relative_to(ROOT)}")
    data = path.read_bytes()
    if len(data) < min_bytes:
        fail(f"{path.relative_to(ROOT)} is unexpectedly small")
    return data


def check_frontmatter(skill: str, text: str) -> None:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        fail(f"{skill}/SKILL.md is missing YAML frontmatter")
    frontmatter = match.group(1)
    if f"name: {skill}" not in frontmatter:
        fail(f"{skill}/SKILL.md frontmatter name is wrong")
    if "description:" not in frontmatter:
        fail(f"{skill}/SKILL.md frontmatter description is missing")


def main() -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(check_file(manifest_path))
    if manifest.get("name") != "frontend-ui-pipeline":
        fail("plugin.json name must be frontend-ui-pipeline")
    if manifest.get("skills") != "./skills/":
        fail("plugin.json skills path must be ./skills/")
    if not isinstance(manifest.get("interface"), dict):
        fail("plugin.json interface object is missing")
    ok("plugin manifest")

    for skill in SKILLS:
        skill_root = ROOT / "skills" / skill
        skill_md = check_file(skill_root / "SKILL.md")
        check_frontmatter(skill, skill_md)
        if "Non-Expert Mode" not in skill_md:
            fail(f"{skill}/SKILL.md must include Non-Expert Mode guidance")
        if "Quality Gate" not in skill_md and skill != "frontend-implementation":
            fail(f"{skill}/SKILL.md must include a Quality Gate")
        if skill == "frontend-implementation" and "runnable" not in skill_md:
            fail("frontend-implementation must require runnable frontend output")
        if skill == "frontend-ui-ideation":
            for required in ("Phase 2 generation guide", "Required Phase 2 Component Inventory"):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        if skill == "frontend-asset-production":
            for required in ("Required Foundation Kit", "complete foundational component kit"):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        agent_yaml = check_file(skill_root / "agents" / "openai.yaml")
        if f"$%s" % skill not in agent_yaml:
            fail(f"{skill}/agents/openai.yaml default prompt should mention ${skill}")
        ok(skill)

    readme = check_file(ROOT / "README.md")
    for required in (
        "Install",
        "codex plugin add frontend-ui-pipeline@personal",
        "PROMPTS.md",
        "examples/quickstart/app-flow-brief.md",
        "$frontend-ui-ideation",
        "$frontend-asset-production",
        "$frontend-implementation",
    ):
        if required not in readme:
            fail(f"README.md missing {required}")
    ok("README")

    check_file(ROOT / "PROMPTS.md")
    check_file(ROOT / "examples" / "quickstart" / "app-flow-brief.md")
    check_file(ROOT / "examples" / "outputs" / "phase1-ui-brief.example.md")
    check_file(ROOT / "examples" / "outputs" / "phase2-asset-handoff.example.md")
    check_file(ROOT / ".github" / "workflows" / "quick-check.yml")
    check_file(ROOT / "docs" / "quality-bar.md")
    ok("examples and CI")

    demo_root = ROOT / "examples" / "demo-draftpilot"
    phase1 = check_file(demo_root / "phase1" / "phase1-ui-brief.md")
    for required in ("Phase 2 Generation Guide", "Layer Order", "Adjustable Parameters", "Required Foundation Kit"):
        if required not in phase1:
            fail(f"demo phase1 brief missing {required}")

    phase2 = check_file(demo_root / "phase2" / "phase2-asset-handoff.md")
    for required in FOUNDATION_TERMS:
        if required not in phase2:
            fail(f"demo phase2 handoff missing {required}")

    manifest = json.loads(check_file(demo_root / "phase2" / "asset-manifest.json"))
    manifest_paths = {asset.get("path") for asset in manifest.get("assets", [])}
    for required_path in (
        "design-system/component-kit.css",
        "design-system/icon-sprite.svg",
        "design-system/component-gallery.html",
    ):
        if required_path not in manifest_paths:
            fail(f"demo asset manifest missing {required_path}")

    sprite = check_file(demo_root / "phase2" / "design-system" / "icon-sprite.svg")
    gallery = check_file(demo_root / "phase2" / "design-system" / "component-gallery.html")
    for icon in COMMON_ICONS:
        if f"id=\"icon-{icon}\"" not in sprite:
            fail(f"icon sprite missing icon-{icon}")
        if f">{icon}</span>" not in gallery:
            fail(f"component gallery missing visible label for {icon}")

    component_kit = check_file(demo_root / "phase2" / "design-system" / "component-kit.css")
    for required in (".fp-button", ".fp-badge", ".fp-card", ".fp-combobox", ".fp-nav", ".fp-notice", ".fp-search", ".fp-modal", "@keyframes fp-page-enter"):
        if required not in component_kit:
            fail(f"component kit missing {required}")

    implementation = check_file(demo_root / "phase3" / "implementation" / "index.html")
    for required in ("component-kit.css", "campaignType", "demoModal", "phase2/assets"):
        if required not in implementation:
            fail(f"demo implementation missing {required}")
    check_file(demo_root / "phase3" / "implementation" / "implementation-note.md")

    for png_path in (
        demo_root / "phase1" / "phase1-preview-desktop.png",
        demo_root / "phase1" / "phase1-preview-mobile.png",
        demo_root / "phase2" / "asset-review" / "contact-sheet.png",
        demo_root / "phase2" / "design-system" / "component-gallery.png",
        demo_root / "evidence" / "screenshots" / "draftpilot-desktop.png",
        demo_root / "evidence" / "screenshots" / "draftpilot-mobile.png",
    ):
        png = check_binary(png_path, min_bytes=1024)
        if not png.startswith(b"\x89PNG\r\n\x1a\n"):
            fail(f"{png_path.relative_to(ROOT)} is not a PNG")
    ok("end-to-end demo")

    check_file(ROOT / "LICENSE")
    ok("license")
    print("All checks passed.")


if __name__ == "__main__":
    main()
