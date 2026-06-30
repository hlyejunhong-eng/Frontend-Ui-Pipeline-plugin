#!/usr/bin/env python3
"""Dependency-free repository checks for Frontend UI Pipeline."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
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
IGNORED_NON_PLUGIN_PATHS = [
    "PROMPTS.md",
    "docs/",
    "examples/",
    "launch-kit/",
    ".github/ISSUE_TEMPLATE/",
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
            for required in ("Phase 2 generation guide", "Required Phase 2 Component Inventory", "First Run Checklist"):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        if skill == "frontend-asset-production":
            for required in ("Required Foundation Kit", "complete foundational component kit", "Run Mode", "SVG Sprite Review Rule"):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        if skill == "frontend-implementation":
            for required in ("Run Mode", "uni-app", "HBuilderX"):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        agent_yaml = check_file(skill_root / "agents" / "openai.yaml")
        if f"$%s" % skill not in agent_yaml:
            fail(f"{skill}/agents/openai.yaml default prompt should mention ${skill}")
        ok(skill)

    readme = check_file(ROOT / "README.md")
    for required in (
        "Overview",
        "简介",
        "安装步骤",
        "Installation",
        "codex plugin add frontend-ui-pipeline@personal",
        "Codex 应用",
        "Codex app",
        "新建一个线程",
        "Create a new thread",
        "底部消息输入框",
        "bottom message box",
        "旧页面截图",
        "Old screen screenshot",
        "本地项目路径",
        "Local project path",
        "localhost",
        "Figma 链接",
        "Figma link",
        "通用全流程 Prompt",
        "Full Pipeline Prompt",
        "First Run Checklist",
        "Demo 模式",
        "Demo Mode",
        "uni-app",
        "HBuilderX",
        "阶段输出标准",
        "Phase Output Standards",
        "Phase 1",
        "Phase 2",
        "Phase 3",
        "$frontend-ui-ideation",
        "$frontend-asset-production",
        "$frontend-implementation",
        "本地校验",
        "Local Check",
        "阶段二本地审核服务器",
        "Phase 2 Local Review Server",
        "serve_review.py",
        "阶段二 Manifest 验收器",
        "Phase 2 Manifest Validator",
        "validate_foundation_manifest.py",
    ):
        if required not in readme:
            fail(f"README.md missing {required}")
    ok("README")

    gitignore = check_file(ROOT / ".gitignore")
    for ignored_path in IGNORED_NON_PLUGIN_PATHS:
        if ignored_path not in gitignore:
            fail(f".gitignore missing {ignored_path}")
    ok("ignore rules")

    check_file(ROOT / ".github" / "workflows" / "quick-check.yml")
    check_file(ROOT / "scripts" / "install_local_marketplace.py")
    manifest_generator = ROOT / "scripts" / "generate_foundation_manifest.py"
    check_file(manifest_generator)
    manifest_validator = ROOT / "scripts" / "validate_foundation_manifest.py"
    check_file(manifest_validator)
    review_server = ROOT / "scripts" / "serve_review.py"
    check_file(review_server)
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "asset-manifest.json"
        subprocess.run(
            [
                sys.executable,
                str(manifest_generator),
                "--project",
                "quick-check",
                "--screen",
                "dashboard",
                "--target-route",
                "/dashboard",
                "--status",
                "review-pending",
                "--output",
                str(output_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        generated = json.loads(output_path.read_text(encoding="utf-8"))
        entries = generated.get("entries", [])
        expected_total = 89
        if generated.get("coverage", {}).get("commonIcons") != len(COMMON_ICONS):
            fail("foundation manifest generator must cover all common icons")
        if generated.get("coverage", {}).get("totalEntries") != expected_total:
            fail("foundation manifest generator total entry count changed unexpectedly")
        if len(entries) != expected_total:
            fail("foundation manifest generator output is missing required foundation states")
        validator_check = subprocess.run(
            [
                sys.executable,
                str(manifest_validator),
                str(output_path),
                "--require-status",
                "review-pending",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "common icons: 20" not in validator_check.stdout:
            fail("foundation manifest validator did not verify common icon coverage")
        review_root = Path(temp_dir) / "review"
        review_root.mkdir()
        (review_root / "component-contact-sheet.html").write_text(
            "<!doctype html><title>Review</title><h1>ok</h1>\n",
            encoding="utf-8",
        )
        server_check = subprocess.run(
            [
                sys.executable,
                str(review_server),
                str(review_root),
                "--entry",
                "component-contact-sheet.html",
                "--check",
                "--quiet",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "Review URL:" not in server_check.stdout:
            fail("review server check did not print a Review URL")
    ok("scripts and CI")

    check_file(ROOT / "LICENSE")
    ok("license")
    print("All checks passed.")


if __name__ == "__main__":
    main()
