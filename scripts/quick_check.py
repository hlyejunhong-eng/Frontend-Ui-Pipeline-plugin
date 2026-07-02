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
            for required in (
                "Phase 2 generation guide",
                "Layer Preservation Contract",
                "Scenery Plane Allocation",
                "Required Phase 2 Component Inventory",
                "First Run Checklist",
                "Visual Taste Rubric",
                "Design Brief Lock",
                "target viewport dimensions",
                "three visual",
                "Do not infer visual style from filenames alone",
                "missing glyphs",
                "tofu boxes",
                "generate_visual_excellence_gate.py",
                "generate_visual_benchmark_report.py",
                "check_visual_artifacts.py",
                "generate_pipeline_runbook.py",
                "generate_pipeline_completion_audit.py",
            ):
                if required not in skill_md:
                    fail(f"{skill}/SKILL.md missing {required}")
        if skill == "frontend-asset-production":
            for required in (
                "Required Foundation Kit",
                "complete foundational component kit",
                "Layer Preservation Contract",
                "Scenery Plane Allocation",
                "phase2-scenery-plane-allocation.md",
                "layerRole",
                "sceneryPlane",
                "depthBand",
                "componentizationRule",
                "zIndex",
                "occlusionPolicy",
                "Run Mode",
                "SVG Sprite Review Rule",
                "Asset Prompt Pack Generator",
                "Asset Review Packet Generator",
                "Asset Review Decision Recorder",
                "record_asset_review_decision.py",
                "phase2-asset-review-decision",
                "Phase 2 Handoff Generator",
                "Visual Artifact Checker",
                "Visual Diff Helper",
                "Primary Screen First Rule",
                "Asset-Assembled Primary Preview Rule",
                "--assembly-preview",
                "Phase 1 preview screenshot",
                "Layer and Occlusion Review",
                "selected visual target",
                "real raster/ImageGen",
                "clipped titles",
                "overflowing labels",
                "generate_pipeline_runbook.py",
                "generate_pipeline_completion_audit.py",
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
                "generate_design_qa_gate.py",
                "generate_pipeline_runbook.py",
                "generate_pipeline_completion_audit.py",
                "Target Inspector",
                "Screenshot QA Plan",
                "Implementation Patch Plan",
                "Design QA Gate",
                "Catalog every visual asset",
                "Layer Preservation Contract",
                "Scenery Plane Allocation",
                "stacking contexts",
                "Measure the approved preview",
                "99% similarity",
                "pixel adjustment loop",
                "--min-similarity-pct 99",
                "Phase 3 Component Reuse Contract",
                "allowed component ledger",
                "invisible/transparent text-binding boxes",
                "Do not create a new visible button",
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
        "Install Doctor",
        "安装诊断",
        "启动向导",
        "Start Wizard",
        "start_pipeline.py",
        "pipeline-start.md",
        "Demo 模式",
        "Demo Mode",
        "uni-app",
        "HBuilderX",
        "阶段输出标准",
        "Phase Output Standards",
        "Phase 1",
        "Phase 2",
        "Phase 3",
        "Quality Gates",
        "质量门禁",
        "asset-assembled primary screen preview",
        "visual diff / assembly diff",
        "Layer Preservation Contract",
        "Scenery Plane Allocation",
        "phase2-scenery-plane-allocation.md",
        "99% similarity",
        "--min-similarity-pct",
        "Phase 2 Component Reuse Ledger",
        "Phase 3 Component Reuse Contract",
        "隐藏/透明文本框",
        "transparent text fields",
        "Layer and Occlusion Review",
        "layer preservation contract",
        "z-index",
        "occlusion policy",
        "Phase 3 screenshot QA",
        "$frontend-ui-ideation",
        "$frontend-asset-production",
        "$frontend-implementation",
        "本地校验",
        "Local Check",
        "diagnose_install.py",
        "流水线运行索引生成器",
        "Pipeline Runbook Generator",
        "generate_pipeline_runbook.py",
        "流水线完成度审计",
        "Pipeline Completion Audit Generator",
        "generate_pipeline_completion_audit.py",
        "案例包生成器",
        "Case Study Pack Generator",
        "generate_case_study_pack.py",
        "case-study-pack",
        "阶段一视觉卓越门",
        "Phase 1 Visual Excellence Gate",
        "generate_visual_excellence_gate.py",
        "Product Design 基准门",
        "Product Design Benchmark",
        "generate_visual_benchmark_report.py",
        "missing glyphs",
        "tofu boxes",
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
        "阶段二资产审核决定记录器",
        "Phase 2 Asset Review Decision Recorder",
        "record_asset_review_decision.py",
        "phase2-asset-review-decision.json",
        "primary-screen-asset-assembly.png",
        "--assembly-preview",
        "clipped headings",
        "right/bottom-edge truncation",
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
        "阶段三 Design QA 门",
        "Phase 3 Design QA Gate",
        "generate_design_qa_gate.py",
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
    start_wizard = ROOT / "scripts" / "start_pipeline.py"
    check_file(start_wizard)
    install_doctor = ROOT / "scripts" / "diagnose_install.py"
    check_file(install_doctor)
    runbook_generator = ROOT / "scripts" / "generate_pipeline_runbook.py"
    check_file(runbook_generator)
    completion_audit_generator = ROOT / "scripts" / "generate_pipeline_completion_audit.py"
    check_file(completion_audit_generator)
    case_study_generator = ROOT / "scripts" / "generate_case_study_pack.py"
    check_file(case_study_generator)
    visual_excellence_gate = ROOT / "scripts" / "generate_visual_excellence_gate.py"
    check_file(visual_excellence_gate)
    visual_benchmark_gate = ROOT / "scripts" / "generate_visual_benchmark_report.py"
    check_file(visual_benchmark_gate)
    phase1_validator = ROOT / "scripts" / "validate_phase1_brief.py"
    check_file(phase1_validator)
    manifest_generator = ROOT / "scripts" / "generate_foundation_manifest.py"
    check_file(manifest_generator)
    prompt_pack_generator = ROOT / "scripts" / "generate_asset_prompt_pack.py"
    check_file(prompt_pack_generator)
    review_packet_generator = ROOT / "scripts" / "generate_asset_review_packet.py"
    check_file(review_packet_generator)
    review_decision_recorder = ROOT / "scripts" / "record_asset_review_decision.py"
    check_file(review_decision_recorder)
    handoff_generator = ROOT / "scripts" / "generate_phase2_handoff.py"
    check_file(handoff_generator)
    target_inspector = ROOT / "scripts" / "inspect_frontend_target.py"
    check_file(target_inspector)
    screenshot_plan_generator = ROOT / "scripts" / "generate_screenshot_qa_plan.py"
    check_file(screenshot_plan_generator)
    patch_plan_generator = ROOT / "scripts" / "generate_implementation_patch_plan.py"
    check_file(patch_plan_generator)
    design_qa_gate = ROOT / "scripts" / "generate_design_qa_gate.py"
    check_file(design_qa_gate)
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

## Selected Direction
Selected direction: Executive Command.

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

Scenery Plane Allocation:
The selected page image must be read as foreground midground background depth before any asset slicing. Back scenery carries the far-field atmosphere, mid scenery / midground carries the primary illustration motif, content plane carries cards and readable surfaces, interaction plane carries controls and text, and front scenery carries foreground frames, particles, rim lights, and border ornaments.

| Page | sceneryPlane | depthBand | planePurpose | componentizationRule |
| --- | --- | --- | --- | --- |
| dashboard | back scenery | back-00 | far-field atmosphere and base color world | generate as the base background layer |
| dashboard | mid scenery / midground | mid-00 | primary illustration motif and depth cue | generate as an illustration-level component |
| dashboard | content plane | content-00 | card material and readable content surfaces | generate as separate translucent surfaces |
| dashboard | interaction plane | interaction-00 | controls, copy, inputs, and live UI states | render as UI components |
| dashboard | front scenery | front-00 | foreground frame, glints, particles, and decorative borders | generate as transparent overlays above content edges |

Layer Preservation Contract:

| Asset | layerRole | zIndex | compositingGroup | occlusionPolicy | mayMergeWith | mustRemainSeparateFrom | alphaRequired |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base background | background base | -100 | background system | behind all content | depth overlay | content surface, foreground decoration | false |
| depth overlay | background depth | -90 | background system | below illustration and content surface | base background | foreground decoration | true |
| illustration motif | illustration midground | -70 | illustration system | behind content surface | none | content surface, foreground decoration | true |
| content surface | content surface | -20 | content system | above background, below text controls | none | base background, foreground decoration | true |
| controls and text | interactive controls | 10 | ui controls | above content surface | none | base background | false |
| foreground decoration | foreground decoration | 50 | foreground decoration system | above content surface and card edges | none | base background, content surface | true |
| motion overlay | motion overlay | 70 | motion system | above trigger region | none | base background | true |

Do not flatten foreground decoration, rim lights, masks, particles, or border ornaments into the base background. They must remain separate transparent overlays when they sit above cards or controls.

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
        expected_total = 91
        if generated.get("coverage", {}).get("commonIcons") != len(COMMON_ICONS):
            fail("foundation manifest generator must cover all common icons")
        if generated.get("coverage", {}).get("totalEntries") != expected_total:
            fail("foundation manifest generator total entry count changed unexpectedly")
        if len(entries) != expected_total:
            fail("foundation manifest generator output is missing required foundation states")
        if generated.get("coverage", {}).get("screenAssetSlots") != 8:
            fail("foundation manifest generator must include layer preservation screen slots")
        if generated.get("layerContract", {}).get("schemaVersion") != "frontend-ui-pipeline.layer-contract.v1":
            fail("foundation manifest generator must include a layer preservation contract")
        if not generated.get("layerContract", {}).get("sceneryPlaneAllocation"):
            fail("foundation manifest generator must include scenery plane allocation")
        for field in (
            "layerRole",
            "sceneryPlane",
            "depthBand",
            "planePurpose",
            "componentizationRule",
            "zIndex",
            "compositingGroup",
            "occlusionPolicy",
            "mayMergeWith",
            "mustRemainSeparateFrom",
            "alphaRequired",
        ):
            if any(field not in entry for entry in entries):
                fail(f"foundation manifest entries missing {field}")
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
            "Layer Preservation Contract",
            "Scenery Plane Allocation",
            "scenery",
            "Componentization",
            "z `",
            "occlusion",
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
        if "layer preservation contract" not in validator_check.stdout:
            fail("foundation manifest validator did not verify the layer preservation contract")
        if "scenery plane allocation" not in validator_check.stdout:
            fail("foundation manifest validator did not verify scenery plane allocation")
        review_root = Path(temp_dir) / "review"
        review_root.mkdir()
        doctor_home = Path(temp_dir) / "doctor-home"
        doctor_marketplace = doctor_home / ".agents" / "plugins" / "marketplace.json"
        doctor_cache = doctor_home / ".codex" / "plugins" / "cache" / "personal" / "frontend-ui-pipeline" / manifest.get("version", "")
        doctor_marketplace.parent.mkdir(parents=True)
        doctor_cache.mkdir(parents=True)
        doctor_marketplace.write_text(
            json.dumps(
                {
                    "name": "personal",
                    "interface": {"displayName": "Personal"},
                    "plugins": [
                        {
                            "name": "frontend-ui-pipeline",
                            "source": {"source": "local", "path": "./plugins/frontend-ui-pipeline"},
                            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                            "category": "Design",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        doctor_check = subprocess.run(
            [
                sys.executable,
                str(install_doctor),
                "--repo",
                str(ROOT),
                "--home",
                str(doctor_home),
                "--marketplace",
                str(doctor_marketplace),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for required_doctor_text in (
            "Frontend UI Pipeline Install Doctor",
            "Plugin manifest",
            "Script start_pipeline.py",
            "Script generate_pipeline_completion_audit.py",
            "Script generate_case_study_pack.py",
            "Script record_asset_review_decision.py",
            "Script generate_visual_benchmark_report.py",
            "Marketplace entry",
            "Installed cache",
            "Next Start Prompt",
            "$frontend-ui-ideation",
        ):
            if required_doctor_text not in doctor_check.stdout:
                fail(f"install doctor missing {required_doctor_text}")
        contact_sheet = review_root / "phase2-contact-sheet.png"
        contact_sheet.write_bytes(
            bytes.fromhex(
                "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
                "0000000b49444154789c636000020000050001e221bc330000000049454e44ae426082"
            )
        )
        phase1_preview = Path(temp_dir) / "phase1-preview-mobile.png"
        phase1_preview.write_bytes(contact_sheet.read_bytes())
        visual_options = []
        for option_id in ("option-a", "option-b", "option-c"):
            option_path = Path(temp_dir) / f"{option_id}.png"
            option_path.write_bytes(contact_sheet.read_bytes())
            visual_options.extend(
                [
                    "--option",
                    f"{option_id}|{option_id.title()}|{option_path}|Quick check visual direction",
                ]
            )
        visual_gate_dir = Path(temp_dir) / "phase1-visual-gate"
        visual_gate_check = subprocess.run(
            [
                sys.executable,
                str(visual_excellence_gate),
                "--root",
                str(temp_dir),
                "--phase1-brief",
                str(phase1_brief),
                *visual_options,
                "--selected-option",
                "option-a",
                "--score",
                "composition=9",
                "--score",
                "hierarchy=9",
                "--score",
                "typography=8",
                "--score",
                "spacing=8",
                "--score",
                "asset_richness=9",
                "--score",
                "interaction_clarity=8",
                "--score",
                "product_fidelity=9",
                "--score",
                "implementation_feasibility=8",
                "--output-dir",
                str(visual_gate_dir),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        visual_gate_md = visual_gate_dir / "phase1-visual-excellence-gate.md"
        visual_gate_json = visual_gate_dir / "phase1-visual-excellence-gate.json"
        if "Gate passed: yes" not in visual_gate_check.stdout or not visual_gate_md.exists() or not visual_gate_json.exists():
            fail("visual excellence gate did not pass with three valid options")
        visual_gate = json.loads(visual_gate_json.read_text(encoding="utf-8"))
        if visual_gate.get("optionCount") != 3 or visual_gate.get("selectedOption") != "option-a" or not visual_gate.get("phase2Allowed"):
            fail("visual excellence gate JSON did not prove Phase 2 readiness")
        visual_benchmark_check = subprocess.run(
            [
                sys.executable,
                str(visual_benchmark_gate),
                "--root",
                str(temp_dir),
                "--phase1-brief",
                str(phase1_brief),
                "--visual-gate",
                str(visual_gate_json),
                "--output-dir",
                str(visual_gate_dir),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        visual_benchmark_md = visual_gate_dir / "phase1-visual-benchmark.md"
        visual_benchmark_json = visual_gate_dir / "phase1-visual-benchmark.json"
        if "Benchmark passed: yes" not in visual_benchmark_check.stdout or not visual_benchmark_md.exists() or not visual_benchmark_json.exists():
            fail("visual benchmark did not pass with the selected option")
        visual_benchmark = json.loads(visual_benchmark_json.read_text(encoding="utf-8"))
        if visual_benchmark.get("schemaVersion") != "frontend-ui-pipeline.visual-benchmark.v1":
            fail("visual benchmark JSON schema version is wrong")
        if visual_benchmark.get("averageMargin") < 0.5 or len(visual_benchmark.get("advantageCriteria", [])) < 4:
            fail("visual benchmark did not prove enough Product Design baseline advantage")
        review_html = review_root / "component-contact-sheet.html"
        review_html.write_text(
            "<!doctype html><title>Review</title><h1>ok</h1>\n",
            encoding="utf-8",
        )
        assembly_preview = review_root / "primary-screen-asset-assembly.png"
        assembly_preview.write_bytes(contact_sheet.read_bytes())
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
        if "visual diff 0.0%" not in visual_diff_check.stdout or "similarity=100.0%" not in visual_diff_check.stdout:
            fail("visual diff helper did not report a zero-difference comparison")
        diff_report = json.loads(diff_json.read_text(encoding="utf-8"))
        if not diff_report.get("passed") or diff_report.get("differingPixels") != 0 or diff_report.get("similarityPct") != 100.0:
            fail("visual diff helper JSON did not prove matching PNGs")
        if "Visual Diff Report" not in diff_md.read_text(encoding="utf-8") or "Similarity" not in diff_md.read_text(encoding="utf-8"):
            fail("visual diff helper did not write Markdown output")
        pipeline_start_dir = Path(temp_dir) / "pipeline-start-run"
        start_check = subprocess.run(
            [
                sys.executable,
                str(start_wizard),
                "--input",
                str(phase1_brief),
                "--input",
                "http://127.0.0.1:5173/#/pages/grid/grid",
                "--project",
                "quick-check",
                "--target",
                "/dashboard",
                "--mode",
                "demo",
                "--context",
                "Verify that non-expert users get a ready-to-send prompt.",
                "--run-root",
                str(pipeline_start_dir),
                "--output-md",
                str(Path(temp_dir) / "pipeline-start.md"),
                "--output-json",
                str(Path(temp_dir) / "pipeline-start.json"),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        start_md = Path(temp_dir) / "pipeline-start.md"
        start_json = Path(temp_dir) / "pipeline-start.json"
        if "Use $frontend-ui-ideation" not in start_check.stdout or not start_md.exists() or not start_json.exists():
            fail("start wizard did not write expected outputs")
        start_payload = json.loads(start_json.read_text(encoding="utf-8"))
        if start_payload.get("schemaVersion") != "frontend-ui-pipeline.start.v1":
            fail("start wizard JSON schema version is wrong")
        if start_payload.get("mode") != "demo" or len(start_payload.get("inputs", [])) != 2:
            fail("start wizard did not preserve mode and inputs")
        start_text = start_md.read_text(encoding="utf-8")
        for required_start_text in (
            "Ready-To-Send Codex Prompt",
            "$frontend-ui-ideation",
            "complete Phase 2 asset kit",
            "Do not hot-replace production code",
        ):
            if required_start_text not in start_text:
                fail(f"start wizard output missing {required_start_text}")
        design_qa_md = review_root / "design-qa.md"
        design_qa_json = review_root / "design-qa.json"
        design_qa_check = subprocess.run(
            [
                sys.executable,
                str(design_qa_gate),
                "--source-preview",
                str(contact_sheet),
                "--implementation-screenshot",
                str(contact_sheet),
                "--visual-diff-json",
                str(diff_json),
                "--require-diff",
                "--min-similarity-pct",
                "99",
                "--min-width",
                "1",
                "--min-height",
                "1",
                "--output-md",
                str(design_qa_md),
                "--output-json",
                str(design_qa_json),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "final result: passed" not in design_qa_check.stdout:
            fail("design QA gate did not pass matching screenshots")
        design_qa = json.loads(design_qa_json.read_text(encoding="utf-8"))
        design_qa_text = design_qa_md.read_text(encoding="utf-8")
        if (
            design_qa.get("finalResult") != "passed"
            or design_qa.get("minSimilarityPct") != 99.0
            or design_qa.get("similarityPct") != 100.0
            or "final result: passed" not in design_qa_text
            or "Required similarity" not in design_qa_text
        ):
            fail("design QA gate did not write a passing report")
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
                "--assembly-preview",
                str(assembly_preview),
                "--visual-diff-report",
                str(diff_md),
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
            "Primary Screen Asset Assembly",
            "Asset-assembled primary screen preview",
            "Visual diff report",
            "Layer and Occlusion Review",
            "Scenery",
            "foreground decoration",
        ):
            if required_approval_text not in approval_text:
                fail(f"asset review packet missing {required_approval_text}")
        pending_decision_check = subprocess.run(
            [
                sys.executable,
                str(review_decision_recorder),
                "--decision",
                "review-pending",
                "--message",
                "Waiting for user approval.",
                "--manifest",
                str(output_path),
                "--review-packet",
                str(approval_md),
                "--contact-sheet",
                str(contact_sheet),
                "--assembly-preview",
                str(assembly_preview),
                "--visual-diff-report",
                str(diff_md),
                "--output-dir",
                str(review_root),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        decision_md = review_root / "phase2-asset-review-decision.md"
        decision_json = review_root / "phase2-asset-review-decision.json"
        if "Handoff allowed: no" not in pending_decision_check.stdout or not decision_md.exists() or not decision_json.exists():
            fail("asset review decision recorder did not write pending decision")
        pending_decision = json.loads(decision_json.read_text(encoding="utf-8"))
        if pending_decision.get("schemaVersion") != "frontend-ui-pipeline.asset-review-decision.v1" or pending_decision.get("handoffAllowed"):
            fail("pending asset review decision must block handoff")
        if "Review pending" not in decision_md.read_text(encoding="utf-8"):
            fail("asset review decision markdown missing pending label")
        revision_root = Path(temp_dir) / "review-revision"
        revision_decision_check = subprocess.run(
            [
                sys.executable,
                str(review_decision_recorder),
                "--decision",
                "revise-visual-style",
                "--message",
                "Increase contrast and rebuild the hero illustration.",
                "--manifest",
                str(output_path),
                "--review-packet",
                str(approval_md),
                "--output-dir",
                str(revision_root),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        revision_decision = json.loads((revision_root / "phase2-asset-review-decision.json").read_text(encoding="utf-8"))
        if "Handoff allowed: no" not in revision_decision_check.stdout or not revision_decision.get("revisionRequired"):
            fail("revision asset review decision must require revision and block handoff")
        rejected_pending_handoff = subprocess.run(
            [
                sys.executable,
                str(handoff_generator),
                "--manifest",
                str(output_path),
                "--approval-decision",
                str(decision_json),
                "--output",
                str(Path(temp_dir) / "should-not-exist-pending.md"),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if rejected_pending_handoff.returncode == 0:
            fail("phase 2 handoff generator must reject pending asset review decisions")
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
        readiness = runbook.get("status", {}).get("phaseReadiness", {})
        if not readiness.get("phase1VisualGateReady"):
            fail("pipeline runbook did not detect the Phase 1 visual excellence gate")
        if not readiness.get("phase1VisualBenchmarkReady"):
            fail("pipeline runbook did not detect the Phase 1 Product Design benchmark")
        if not readiness.get("phase2AssemblyPreviewReady"):
            fail("pipeline runbook did not detect the Phase 2 asset-assembled primary screen preview")
        if readiness.get("phase2ReviewDecisionApproved"):
            fail("pipeline runbook must not approve Phase 2 when the review decision is pending")
        if not readiness.get("phase3DesignQaPassed"):
            fail("pipeline runbook did not detect the passing Phase 3 design QA gate")
        if not runbook.get("artifacts") or not runbook.get("approvalGate", {}).get("approvalText"):
            fail("pipeline runbook missing artifacts or approval text")
        runbook_text = runbook_md.read_text(encoding="utf-8")
        for required_runbook_text in (
            "Frontend UI Pipeline Runbook",
            "Pipeline start prompt",
            "Next Prompt",
            "Approval Gate",
            "Artifact Index",
            "Visual excellence gate",
            "Product Design benchmark",
            "Asset-assembled primary screen preview",
            "Asset review decision",
            "Design QA gate",
            "Assets approved. Generate phase2-asset-handoff.md",
        ):
            if required_runbook_text not in runbook_text:
                fail(f"pipeline runbook missing {required_runbook_text}")
        approved_decision_check = subprocess.run(
            [
                sys.executable,
                str(review_decision_recorder),
                "--decision",
                "approve-assets",
                "--message",
                "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation.",
                "--manifest",
                str(output_path),
                "--review-packet",
                str(approval_md),
                "--contact-sheet",
                str(contact_sheet),
                "--assembly-preview",
                str(assembly_preview),
                "--visual-diff-report",
                str(diff_md),
                "--output-dir",
                str(review_root),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        approved_decision = json.loads(decision_json.read_text(encoding="utf-8"))
        if "Handoff allowed: yes" not in approved_decision_check.stdout or not approved_decision.get("handoffAllowed"):
            fail("approved asset review decision must allow handoff")
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
                "--assembly-preview",
                str(assembly_preview),
                "--visual-diff-report",
                str(diff_md),
                "--target-runtime",
                "quick-check-runtime",
                "--approved-by",
                "quick-check",
                "--approved-at",
                "2026-01-01T00:00:00Z",
                "--approval-decision",
                str(decision_json),
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
            "## Layer Preservation Contract",
            "## Scenery Plane Allocation",
            "99% similarity",
            "Asset-assembled primary screen preview",
            "## Component Usage Rules",
            "## Phase 3 Component Reuse Contract",
            "invisible text-binding boxes",
            "Do not generate new visible component families",
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
        if plan.get("maxDiffPct") != 1.0 or plan.get("minSimilarityPct") != 99.0:
            fail("screenshot QA plan must default to 99% similarity")
        if not all("--max-diff-pct" in command and "1.0" in command for command in plan.get("visualDiffCommands", [])):
            fail("screenshot QA visual diff commands must enforce max 1% diff")
        plan_text = plan_md.read_text(encoding="utf-8")
        for required_plan_text in (
            "Phase 3 Screenshot QA Plan",
            "Capture Command",
            "Visual Artifact Check",
            "Visual Diff Commands",
            "99% Similarity Gate",
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
        reuse_contract = approved_plan.get("componentReuseContract", {})
        if not reuse_contract.get("visibleComponentInventoryClosed") or "invisible text-binding boxes" not in reuse_contract.get("allowedAdditions", []):
            fail("implementation patch plan must enforce the Phase 3 component reuse contract")
        if not approved_plan.get("phase2ComponentLedger"):
            fail("implementation patch plan must include the Phase 2 component reuse ledger")
        copy_keys = [
            (item.get("kind"), item.get("source"), item.get("destination"))
            for item in approved_plan.get("copyOperations", [])
        ]
        if len(copy_keys) != len(set(copy_keys)):
            fail("implementation patch plan copy operations must be deduplicated")
        patch_plan_text = patch_plan_md.read_text(encoding="utf-8")
        for required_patch_plan_text in (
            "Phase 3 Implementation Patch Plan",
            "Copy Operations",
            "File Operations",
            "Layer Preservation Hints",
            "Scenery Plane Hints",
            "Phase 2 Component Reuse Ledger",
            "Phase 3 Component Reuse Contract",
            "invisible text-binding boxes",
            "new visible component families",
            "API Preservation",
            "Verification Steps",
        ):
            if required_patch_plan_text not in patch_plan_text:
                fail(f"implementation patch plan missing {required_patch_plan_text}")
        runbook_after_patch_md = Path(temp_dir) / "pipeline-runbook-after-patch.md"
        runbook_after_patch_json = Path(temp_dir) / "pipeline-runbook-after-patch.json"
        demo_dir = Path(temp_dir) / "phase3-demo-command-center"
        demo_dir.mkdir()
        (demo_dir / "index.html").write_text("<!doctype html><title>Phase 3 Demo</title>\n", encoding="utf-8")
        (demo_dir / "README.md").write_text("# Phase 3 Demo\n", encoding="utf-8")
        (demo_dir / "phase3-demo-evidence.md").write_text("# Phase 3 Demo Evidence\n", encoding="utf-8")
        social_dir = Path(temp_dir) / "social"
        social_dir.mkdir()
        (social_dir / "case-post.md").write_text("# Case Post\n", encoding="utf-8")
        social_visuals_dir = social_dir / "visuals"
        social_visuals_dir.mkdir()
        (social_visuals_dir / "01-cover.png").write_bytes(contact_sheet.read_bytes())
        audit_md = Path(temp_dir) / "pipeline-completion-audit.md"
        audit_json = Path(temp_dir) / "pipeline-completion-audit.json"
        audit_check = subprocess.run(
            [
                sys.executable,
                str(completion_audit_generator),
                "--run-root",
                str(temp_dir),
                "--repo-root",
                str(ROOT),
                "--project",
                "quick-check",
                "--target",
                "/dashboard",
                "--output-md",
                str(audit_md),
                "--output-json",
                str(audit_json),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "Overall status:" not in audit_check.stdout or not audit_md.exists() or not audit_json.exists():
            fail("completion audit generator did not write expected outputs")
        audit = json.loads(audit_json.read_text(encoding="utf-8"))
        if audit.get("schemaVersion") != "frontend-ui-pipeline.completion-audit.v1":
            fail("completion audit JSON schema version is wrong")
        if audit.get("phase2Manifest", {}).get("commonIconCount") != len(COMMON_ICONS):
            fail("completion audit did not verify common icon coverage")
        if audit.get("phase3PatchPlan", {}).get("duplicateCopyOperations") != 0:
            fail("completion audit did not verify deduplicated patch plan copy operations")
        audit_text = audit_md.read_text(encoding="utf-8")
        for required_audit_text in (
            "Pipeline Completion Audit",
            "phase2-foundation-kit",
            "phase2-review-decision",
            "phase1-product-design-benchmark",
            "phase3-demo-mode",
            "Phase 2 Manifest",
            "Phase 3 Patch Plan",
        ):
            if required_audit_text not in audit_text:
                fail(f"completion audit missing {required_audit_text}")
        case_pack_dir = Path(temp_dir) / "case-study-pack"
        case_pack_check = subprocess.run(
            [
                sys.executable,
                str(case_study_generator),
                "--run-root",
                str(temp_dir),
                "--project",
                "quick-check",
                "--target",
                "/dashboard",
                "--output-dir",
                str(case_pack_dir),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        case_md = case_pack_dir / "case-study.md"
        social_post_md = case_pack_dir / "social-post.zh-CN.md"
        snippet_md = case_pack_dir / "github-readme-snippet.md"
        evidence_json = case_pack_dir / "evidence-index.json"
        if "Status:" not in case_pack_check.stdout or not case_md.exists() or not social_post_md.exists() or not snippet_md.exists() or not evidence_json.exists():
            fail("case study pack generator did not write expected outputs")
        case_payload = json.loads(evidence_json.read_text(encoding="utf-8"))
        if case_payload.get("schemaVersion") != "frontend-ui-pipeline.case-study-pack.v1":
            fail("case study pack JSON schema version is wrong")
        if case_payload.get("metrics", {}).get("commonIcons") != len(COMMON_ICONS):
            fail("case study pack did not preserve common icon evidence")
        if case_payload.get("metrics", {}).get("foundationStates") != 63:
            fail("case study pack did not summarize foundation component states")
        if not case_payload.get("metrics", {}).get("visualBenchmarkPassed"):
            fail("case study pack did not preserve visual benchmark evidence")
        case_text = case_md.read_text(encoding="utf-8")
        social_post_text = social_post_md.read_text(encoding="utf-8")
        for required_case_text in (
            "Case Hook",
            "Evidence Index",
            "Completion audit",
            "Product Design benchmark",
            "Phase 2 asset review decision",
            "Asset-assembled primary screen",
        ):
            if required_case_text not in case_text:
                fail(f"case study pack missing {required_case_text}")
        for required_social_text in (
            "Frontend UI Pipeline",
            "Product Design benchmark",
            "Completion audit",
            "GitHub",
        ):
            if required_social_text not in social_post_text:
                fail(f"case study social post missing {required_social_text}")
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
        if not runbook_after_patch.get("status", {}).get("phaseReadiness", {}).get("phase2ReviewDecisionApproved"):
            fail("pipeline runbook did not detect the approved Phase 2 review decision")
        runbook_after_patch_text = runbook_after_patch_md.read_text(encoding="utf-8")
        if "Implementation patch plan" not in runbook_after_patch_text:
            fail("pipeline runbook did not index the implementation patch plan")
        if "Standalone implementation demo" not in runbook_after_patch_text:
            fail("pipeline runbook did not index the standalone Phase 3 demo")
        if "Pipeline completion audit" not in runbook_after_patch_text:
            fail("pipeline runbook did not index the completion audit")
        if "Case study pack" not in runbook_after_patch_text:
            fail("pipeline runbook did not index the case study pack")
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
