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
ALLOWED_TRACKED_FILES = {
    ".gitignore",
    "LICENSE",
    "README.md",
}
ALLOWED_TRACKED_PREFIXES = (
    ".codex-plugin/",
    ".github/workflows/",
    "assets/",
    "scripts/",
    "skills/",
)
DISALLOWED_TRACKED_PREFIXES = (
    "docs/",
    "examples/",
    "launch-kit/",
    ".github/ISSUE_TEMPLATE/",
    ".validation-yaml-shim/",
)


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


def check_tracked_repository_contents() -> None:
    """Fail if the published Git repository tracks non-plugin material."""
    top_level = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if top_level.returncode != 0:
        ok("tracked repository contents")
        return

    try:
        git_root = Path(top_level.stdout.strip()).resolve()
    except OSError:
        ok("tracked repository contents")
        return

    if git_root != ROOT.resolve():
        ok("tracked repository contents")
        return

    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.splitlines()

    forbidden = []
    unexpected = []
    for path in tracked:
        is_forbidden = (
            path == "PROMPTS.md"
            or path.endswith(".pyc")
            or "__pycache__/" in path
            or path.startswith(DISALLOWED_TRACKED_PREFIXES)
        )
        if is_forbidden:
            forbidden.append(path)
            continue
        is_allowed = path in ALLOWED_TRACKED_FILES or path.startswith(ALLOWED_TRACKED_PREFIXES)
        if not is_allowed:
            unexpected.append(path)

    if forbidden:
        fail("Non-plugin files are tracked: " + ", ".join(forbidden))
    if unexpected:
        fail("Unexpected tracked files: " + ", ".join(unexpected))
    ok("tracked repository contents")


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
            for required in ("Phase 2 generation guide", "Required Phase 2 Component Inventory", "First Run Checklist", "check_visual_artifacts.py", "generate_pipeline_runbook.py"):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        if skill == "frontend-asset-production":
            for required in (
                "Required Foundation Kit",
                "complete foundational component kit",
                "Run Mode",
                "SVG Sprite Review Rule",
                "Asset Prompt Pack Generator",
                "Asset Review Packet Generator",
                "Phase 2 Handoff Generator",
                "Visual Artifact Checker",
                "Visual Diff Helper",
                "generate_pipeline_runbook.py",
            ):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        if skill == "frontend-implementation":
            for required in (
                "Run Mode",
                "uni-app",
                "HBuilderX",
                "check_visual_artifacts.py",
                "compare_visual_artifacts.py",
                "generate_phase2_handoff.py",
                "inspect_frontend_target.py",
                "generate_screenshot_qa_plan.py",
                "generate_implementation_patch_plan.py",
                "generate_pipeline_runbook.py",
                "Target Inspector",
                "Screenshot QA Plan",
                "Implementation Patch Plan",
            ):
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
        "流水线运行索引生成器",
        "Pipeline Runbook Generator",
        "generate_pipeline_runbook.py",
        "阶段二本地审核服务器",
        "Phase 2 Local Review Server",
        "serve_review.py",
        "阶段二 Manifest 验收器",
        "Phase 2 Manifest Validator",
        "validate_foundation_manifest.py",
        "阶段一 Brief 验收器",
        "Phase 1 Brief Validator",
        "validate_phase1_brief.py",
        "阶段二资产提示包生成器",
        "Phase 2 Asset Prompt Pack Generator",
        "generate_asset_prompt_pack.py",
        "阶段二资产审核包生成器",
        "Phase 2 Asset Review Packet Generator",
        "generate_asset_review_packet.py",
        "阶段二最终交接文档生成器",
        "Phase 2 Final Handoff Generator",
        "generate_phase2_handoff.py",
        "阶段三目标项目检查器",
        "Phase 3 Target Inspector",
        "inspect_frontend_target.py",
        "阶段三截图 QA 计划生成器",
        "Phase 3 Screenshot QA Plan Generator",
        "generate_screenshot_qa_plan.py",
        "阶段三实现补丁计划生成器",
        "Phase 3 Implementation Patch Plan Generator",
        "generate_implementation_patch_plan.py",
        "视觉产物检查器",
        "Visual Artifact Checker",
        "check_visual_artifacts.py",
        "视觉差异对比器",
        "Visual Diff Helper",
        "compare_visual_artifacts.py",
    ):
        if required not in readme:
            fail(f"README.md missing {required}")
    ok("README")

    gitignore = check_file(ROOT / ".gitignore")
    for ignored_path in IGNORED_NON_PLUGIN_PATHS:
        if ignored_path not in gitignore:
            fail(f".gitignore missing {ignored_path}")
    ok("ignore rules")
    check_tracked_repository_contents()

    check_file(ROOT / ".github" / "workflows" / "quick-check.yml")
    check_file(ROOT / "scripts" / "install_local_marketplace.py")
    runbook_generator = ROOT / "scripts" / "generate_pipeline_runbook.py"
    check_file(runbook_generator)
    phase1_validator = ROOT / "scripts" / "validate_phase1_brief.py"
    check_file(phase1_validator)
    manifest_generator = ROOT / "scripts" / "generate_foundation_manifest.py"
    check_file(manifest_generator)
    prompt_pack_generator = ROOT / "scripts" / "generate_asset_prompt_pack.py"
    check_file(prompt_pack_generator)
    review_packet_generator = ROOT / "scripts" / "generate_asset_review_packet.py"
    check_file(review_packet_generator)
    handoff_generator = ROOT / "scripts" / "generate_phase2_handoff.py"
    check_file(handoff_generator)
    target_inspector = ROOT / "scripts" / "inspect_frontend_target.py"
    check_file(target_inspector)
    screenshot_plan_generator = ROOT / "scripts" / "generate_screenshot_qa_plan.py"
    check_file(screenshot_plan_generator)
    patch_plan_generator = ROOT / "scripts" / "generate_implementation_patch_plan.py"
    check_file(patch_plan_generator)
    visual_checker = ROOT / "scripts" / "check_visual_artifacts.py"
    check_file(visual_checker)
    visual_diff_helper = ROOT / "scripts" / "compare_visual_artifacts.py"
    check_file(visual_diff_helper)
    manifest_validator = ROOT / "scripts" / "validate_foundation_manifest.py"
    check_file(manifest_validator)
    review_server = ROOT / "scripts" / "serve_review.py"
    check_file(review_server)
    with tempfile.TemporaryDirectory() as temp_dir:
        phase1_brief = Path(temp_dir) / "phase1-ui-brief.md"
        phase1_brief.write_text(
            """# Phase 1 UI Brief: Quick Check

## Context
Product context for a premium frontend flow.

## Source Audit
Route and source evidence were inspected.

## Preview Files
- `phase1-preview-desktop.png`
- `phase1-preview-mobile.png`

## Layout Spec
Grid, spacing, viewport, alignment, and responsive layout.

## Background Spec
Background, grid, illustration, texture, lighting, mask, and placement.

## Component Spec
Buttons, cards, inputs, navigation, modal, and stateful components.

## Copy Spec
Headings, labels, helper text, and errors.

## Button and Control Spec
Hit areas, keyboard order, focus, pressed, hover, disabled, and loading.

## Motion Spec
Page enter, page exit, modal enter, modal exit, button press, hover, loading shimmer, and reduced-motion fallback.

## Phase 2 Generation Guide

Layer map:
1. base background
2. grid and illustration
3. card surfaces
4. controls and text
5. effect overlays, special mask, and motion overlays

Adjustable parameters:
- opacity, blur, shadow, highlight intensity, saturation, stroke width, radius, spacing, duration, easing, and responsive crop.

Asset naming rules:
- lower-kebab-case with screen, component, state, and scale.

Export rules:
- SVG for icons and masks; PNG/WebP for raster illustration.

Responsive crop rules:
- anchor important illustration areas and never crop controls.

Complete Phase 2 component inventory:
- Buttons: primary, secondary, ghost, danger, disabled, loading, icon-only, pressed.
- Numeric badges: neutral, accent, success, warning, danger, dot, count.
- Generic cards: flat, elevated, selected, disabled, media, metric, action-card.
- Combobox/select: closed, open, selected, search-filtered, empty, disabled, error.
- Common icons: home, profile, generic page, scan, cart, payment, chat, confirm, close, back, forward, hot, like, settings, help, info, wallet, list, favorite, search.
- Navigation bar: desktop sidebar, desktop topbar, mobile compact.
- Notice bar: info, success, warning, danger, dismissible.
- Search bar: idle, focused, with-value, loading, empty-result, clear-button.
- Section title: eyebrow, title, subtitle, action slot, divider.
- Modal: default, destructive confirmation, form modal, mobile sheet, overlay, close action, focus.
- Transition animation: page enter, page exit, modal enter, modal exit, button press, hover, loading shimmer, reduced motion.

## Asset Expectations
Backgrounds, illustrations, masks, icons, component CSS, motion frames, and manifest.

## Acceptance Checklist
Phase 2 can start after validation passes.
""",
            encoding="utf-8",
        )
        phase1_check = subprocess.run(
            [sys.executable, str(phase1_validator), str(phase1_brief)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "phase 1 brief is ready for Phase 2" not in phase1_check.stdout:
            fail("phase 1 brief validator did not verify readiness")

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
        prompt_pack_path = Path(temp_dir) / "phase2-asset-prompt-pack.md"
        prompt_pack_check = subprocess.run(
            [
                sys.executable,
                str(prompt_pack_generator),
                "--phase1-brief",
                str(phase1_brief),
                "--manifest",
                str(output_path),
                "--strategy",
                "hybrid",
                "--output",
                str(prompt_pack_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not prompt_pack_path.exists() or "Wrote" not in prompt_pack_check.stdout:
            fail("asset prompt pack generator did not write output")
        prompt_pack = prompt_pack_path.read_text(encoding="utf-8")
        for required_prompt_text in (
            "Phase 2 Asset Prompt Pack",
            "AI Raster Prompt",
            "Figma/Vector Prompt",
            "CSS/SVG Component Prompt",
            "Common icons",
            "Total manifest entries",
        ):
            if required_prompt_text not in prompt_pack:
                fail(f"asset prompt pack missing {required_prompt_text}")
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
        contact_sheet = review_root / "phase2-contact-sheet.png"
        contact_sheet.write_bytes(
            bytes.fromhex(
                "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
                "0000000b49444154789c636000020000050001e221bc330000000049454e44ae426082"
            )
        )
        phase1_preview = Path(temp_dir) / "phase1-preview-mobile.png"
        phase1_preview.write_bytes(contact_sheet.read_bytes())
        review_html = review_root / "component-contact-sheet.html"
        review_html.write_text(
            "<!doctype html><title>Review</title><h1>ok</h1>\n",
            encoding="utf-8",
        )
        visual_check = subprocess.run(
            [
                sys.executable,
                str(visual_checker),
                str(contact_sheet),
                str(review_html),
                "--min-width",
                "1",
                "--min-height",
                "1",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "png 1x1" not in visual_check.stdout or "html" not in visual_check.stdout:
            fail("visual artifact checker did not inspect PNG and HTML outputs")
        diff_json = review_root / "visual-diff-report.json"
        diff_md = review_root / "visual-diff-report.md"
        visual_diff_check = subprocess.run(
            [
                sys.executable,
                str(visual_diff_helper),
                str(contact_sheet),
                str(contact_sheet),
                "--output-json",
                str(diff_json),
                "--output-md",
                str(diff_md),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "visual diff 0.0%" not in visual_diff_check.stdout:
            fail("visual diff helper did not report a zero-difference comparison")
        diff_report = json.loads(diff_json.read_text(encoding="utf-8"))
        if not diff_report.get("passed") or diff_report.get("differingPixels") != 0:
            fail("visual diff helper JSON did not prove matching PNGs")
        if "Visual Diff Report" not in diff_md.read_text(encoding="utf-8"):
            fail("visual diff helper did not write Markdown output")
        review_packet_check = subprocess.run(
            [
                sys.executable,
                str(review_packet_generator),
                "--manifest",
                str(output_path),
                "--phase1-brief",
                str(phase1_brief),
                "--prompt-pack",
                str(prompt_pack_path),
                "--contact-sheet",
                str(contact_sheet),
                "--review-url",
                "http://127.0.0.1:8000/component-contact-sheet.html",
                "--output-dir",
                str(review_root),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        approval_md = review_root / "phase2-asset-approval-packet.md"
        approval_html = review_root / "phase2-asset-approval-packet.html"
        if not approval_md.exists() or not approval_html.exists() or "Wrote" not in review_packet_check.stdout:
            fail("asset review packet generator did not write expected outputs")
        approval_text = approval_md.read_text(encoding="utf-8")
        for required_approval_text in (
            "Phase 2 Asset Approval Packet",
            "Approve assets",
            "Revise visual style",
            "Revise naming or organization",
            "Revise implementation mapping",
        ):
            if required_approval_text not in approval_text:
                fail(f"asset review packet missing {required_approval_text}")
        runbook_md = Path(temp_dir) / "pipeline-runbook.md"
        runbook_json = Path(temp_dir) / "pipeline-runbook.json"
        runbook_check = subprocess.run(
            [
                sys.executable,
                str(runbook_generator),
                "--run-root",
                str(temp_dir),
                "--project",
                "quick-check",
                "--target",
                "/dashboard",
                "--output-md",
                str(runbook_md),
                "--output-json",
                str(runbook_json),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "asset-approval-required" not in runbook_check.stdout or not runbook_md.exists() or not runbook_json.exists():
            fail("pipeline runbook generator did not report the Phase 2 approval gate")
        runbook = json.loads(runbook_json.read_text(encoding="utf-8"))
        if runbook.get("status", {}).get("key") != "asset-approval-required":
            fail("pipeline runbook should require asset approval before handoff")
        if not runbook.get("artifacts") or not runbook.get("approvalGate", {}).get("approvalText"):
            fail("pipeline runbook missing artifacts or approval text")
        runbook_text = runbook_md.read_text(encoding="utf-8")
        for required_runbook_text in (
            "Frontend UI Pipeline Runbook",
            "Next Prompt",
            "Approval Gate",
            "Artifact Index",
            "Assets approved. Generate phase2-asset-handoff.md",
        ):
            if required_runbook_text not in runbook_text:
                fail(f"pipeline runbook missing {required_runbook_text}")
        handoff_path = Path(temp_dir) / "phase2-asset-handoff.md"
        handoff_check = subprocess.run(
            [
                sys.executable,
                str(handoff_generator),
                "--manifest",
                str(output_path),
                "--phase1-brief",
                str(phase1_brief),
                "--prompt-pack",
                str(prompt_pack_path),
                "--review-packet",
                str(approval_md),
                "--contact-sheet",
                str(contact_sheet),
                "--visual-diff-report",
                str(diff_md),
                "--target-runtime",
                "quick-check-runtime",
                "--approved-by",
                "quick-check",
                "--approved-at",
                "2026-01-01T00:00:00Z",
                "--approval-text",
                "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation.",
                "--output",
                str(handoff_path),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not handoff_path.exists() or "Wrote" not in handoff_check.stdout:
            fail("phase 2 handoff generator did not write expected output")
        handoff_text = handoff_path.read_text(encoding="utf-8")
        for required_handoff_text in (
            "Phase 2 Asset Handoff",
            "## Approval",
            "## Asset Manifest",
            "## Assembly Map",
            "## Component Usage Rules",
            "## Phase 3 Acceptance Checklist",
            "$frontend-implementation",
        ):
            if required_handoff_text not in handoff_text:
                fail(f"phase 2 handoff missing {required_handoff_text}")
        rejected_handoff = subprocess.run(
            [
                sys.executable,
                str(handoff_generator),
                "--manifest",
                str(output_path),
                "--approval-text",
                "please wait",
                "--output",
                str(Path(temp_dir) / "should-not-exist.md"),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if rejected_handoff.returncode == 0:
            fail("phase 2 handoff generator must reject missing explicit approval")

        target_root = Path(temp_dir) / "target-uni-app"
        (target_root / "pages" / "grid").mkdir(parents=True)
        (target_root / "common").mkdir()
        (target_root / "static").mkdir()
        (target_root / "package.json").write_text(
            json.dumps(
                {
                    "id": "quick-check-uni-app",
                    "engines": {"HBuilderX": "^3.2.6", "uni-app": "^4.07"},
                    "dependencies": {"qrcodejs2": "^0.0.2"},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        (target_root / "manifest.json").write_text('{"name":"quick-check"}\n', encoding="utf-8")
        (target_root / "pages.json").write_text(
            json.dumps(
                {
                    "pages": [
                        {"path": "pages/grid/grid", "style": {"navigationStyle": "custom"}},
                        {"path": "pages/list/list", "style": {"navigationStyle": "custom"}},
                    ]
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        (target_root / "App.vue").write_text("<template><view /></template>\n", encoding="utf-8")
        (target_root / "main.js").write_text("import App from './App.vue'\n", encoding="utf-8")
        (target_root / "common" / "api.js").write_text(
            "export default { chat: { send(){ return uniCloud.callFunction({name:'chat'}) } } }\n",
            encoding="utf-8",
        )
        (target_root / "pages" / "grid" / "grid.vue").write_text(
            "<template><view>{{title}}</view></template><script>import api from '@/common/api.js'; export default { mounted(){ api.chat.send() } }</script>\n",
            encoding="utf-8",
        )
        inspection_json = Path(temp_dir) / "phase3-target-inspection.json"
        inspection_md = Path(temp_dir) / "phase3-target-inspection.md"
        inspection_check = subprocess.run(
            [
                sys.executable,
                str(target_inspector),
                str(target_root),
                "--target-route",
                "pages/grid/grid",
                "--output-json",
                str(inspection_json),
                "--output-md",
                str(inspection_md),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "frameworks=uni-app" not in inspection_check.stdout or "target=matched" not in inspection_check.stdout:
            fail("target inspector did not identify uni-app and the target route")
        inspection = json.loads(inspection_json.read_text(encoding="utf-8"))
        if "uni-app" not in inspection.get("frameworks", []):
            fail("target inspector JSON missing uni-app framework")
        if not inspection.get("target", {}).get("matched"):
            fail("target inspector JSON did not match target route")
        if not inspection.get("apiUsage", {}).get("apiFiles"):
            fail("target inspector did not find API client files")
        if not inspection.get("runtime", {}).get("externalRuntimeNotes"):
            fail("target inspector did not report external runtime notes for uni-app")
        if "Frontend Target Inspection" not in inspection_md.read_text(encoding="utf-8"):
            fail("target inspector did not write Markdown output")
        screenshot_plan_dir = Path(temp_dir) / "phase3-screenshot-qa"
        screenshot_plan_check = subprocess.run(
            [
                sys.executable,
                str(screenshot_plan_generator),
                "--inspection",
                str(inspection_json),
                "--base-url",
                "http://127.0.0.1:5173",
                "--route-url",
                "#/pages/grid/grid",
                "--approved-preview",
                str(contact_sheet),
                "--output-dir",
                str(screenshot_plan_dir),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        plan_md = screenshot_plan_dir / "phase3-screenshot-qa-plan.md"
        plan_json = screenshot_plan_dir / "phase3-screenshot-qa-plan.json"
        capture_script = screenshot_plan_dir / "capture-screenshots.mjs"
        if "Wrote" not in screenshot_plan_check.stdout or not plan_md.exists() or not plan_json.exists() or not capture_script.exists():
            fail("screenshot QA plan generator did not write expected outputs")
        plan = json.loads(plan_json.read_text(encoding="utf-8"))
        if len(plan.get("cases", [])) != 2:
            fail("screenshot QA plan must include mobile and desktop cases")
        if not plan.get("visualCheckCommand") or not plan.get("visualDiffCommands"):
            fail("screenshot QA plan missing visual check or diff commands")
        plan_text = plan_md.read_text(encoding="utf-8")
        for required_plan_text in (
            "Phase 3 Screenshot QA Plan",
            "Capture Command",
            "Visual Artifact Check",
            "Visual Diff Commands",
            "capture-screenshots.mjs",
        ):
            if required_plan_text not in plan_text:
                fail(f"screenshot QA plan missing {required_plan_text}")
        if "playwright" not in capture_script.read_text(encoding="utf-8"):
            fail("screenshot QA plan did not write a Playwright capture script")
        patch_plan_dir = Path(temp_dir) / "phase3-patch-plan"
        blocked_patch_plan_check = subprocess.run(
            [
                sys.executable,
                str(patch_plan_generator),
                "--manifest",
                str(output_path),
                "--inspection",
                str(inspection_json),
                "--screenshot-plan",
                str(plan_md),
                "--output-dir",
                str(patch_plan_dir),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        patch_plan_md = patch_plan_dir / "phase3-implementation-patch-plan.md"
        patch_plan_json = patch_plan_dir / "phase3-implementation-patch-plan.json"
        if "Blocked before editing: yes" not in blocked_patch_plan_check.stdout or not patch_plan_md.exists() or not patch_plan_json.exists():
            fail("implementation patch plan generator did not block before approval")
        blocked_plan = json.loads(patch_plan_json.read_text(encoding="utf-8"))
        if not blocked_plan.get("blockedBeforeEditing") or blocked_plan.get("approvalReady"):
            fail("implementation patch plan must block when Phase 2 approval is missing")
        approved_patch_plan_check = subprocess.run(
            [
                sys.executable,
                str(patch_plan_generator),
                "--manifest",
                str(output_path),
                "--inspection",
                str(inspection_json),
                "--approval-text",
                "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation.",
                "--screenshot-plan",
                str(plan_md),
                "--output-dir",
                str(patch_plan_dir),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "Blocked before editing: no" not in approved_patch_plan_check.stdout:
            fail("implementation patch plan generator did not unblock after approval")
        approved_plan = json.loads(patch_plan_json.read_text(encoding="utf-8"))
        if approved_plan.get("blockedBeforeEditing") or not approved_plan.get("copyOperations") or not approved_plan.get("fileOperations"):
            fail("implementation patch plan missing copy/file operations after approval")
        patch_plan_text = patch_plan_md.read_text(encoding="utf-8")
        for required_patch_plan_text in (
            "Phase 3 Implementation Patch Plan",
            "Copy Operations",
            "File Operations",
            "API Preservation",
            "Verification Steps",
        ):
            if required_patch_plan_text not in patch_plan_text:
                fail(f"implementation patch plan missing {required_patch_plan_text}")
        runbook_after_patch_md = Path(temp_dir) / "pipeline-runbook-after-patch.md"
        runbook_after_patch_json = Path(temp_dir) / "pipeline-runbook-after-patch.json"
        subprocess.run(
            [
                sys.executable,
                str(runbook_generator),
                "--run-root",
                str(temp_dir),
                "--project",
                "quick-check",
                "--target",
                "/dashboard",
                "--output-md",
                str(runbook_after_patch_md),
                "--output-json",
                str(runbook_after_patch_json),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        runbook_after_patch = json.loads(runbook_after_patch_json.read_text(encoding="utf-8"))
        if not runbook_after_patch.get("status", {}).get("phaseReadiness", {}).get("phase3PatchPlanned"):
            fail("pipeline runbook did not detect the implementation patch plan")
        if "Implementation patch plan" not in runbook_after_patch_md.read_text(encoding="utf-8"):
            fail("pipeline runbook did not index the implementation patch plan")
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
