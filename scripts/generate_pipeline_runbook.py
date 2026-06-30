#!/usr/bin/env python3
"""Generate a bilingual runbook from a frontend-ui-pipeline run folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


APPROVAL_TEXT = "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation."


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def find_all(root: Path, patterns: list[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        found.extend(path for path in root.glob(pattern) if path.is_file())
    return sorted(set(found), key=lambda item: item.as_posix())


def first(paths: list[Path]) -> Path | None:
    return paths[0] if paths else None


def artifact(path: Path, root: Path, phase: str, label: str, kind: str) -> dict[str, str]:
    return {
        "phase": phase,
        "label": label,
        "kind": kind,
        "path": rel(path, root),
    }


def collect_artifacts(root: Path) -> dict[str, list[Path]]:
    return {
        "phase1Briefs": find_all(root, ["**/phase1-ui-brief.md"]),
        "phase1Previews": find_all(root, ["**/phase1-preview*.png", "**/phase1-flow-preview*.png"]),
        "phase2Manifests": find_all(root, ["**/asset-manifest.json", "**/foundation-asset-manifest*.json"]),
        "phase2PromptPacks": find_all(root, ["**/phase2-asset-prompt-pack.md"]),
        "phase2ContactSheets": find_all(root, ["**/phase2-contact-sheet.png", "**/component-contact-sheet.html"]),
        "phase2ReviewPackets": find_all(root, ["**/phase2-asset-approval-packet.md", "**/phase2-asset-approval-packet.html"]),
        "phase2Handoffs": find_all(root, ["**/phase2-asset-handoff.md"]),
        "phase3Inspections": find_all(root, ["**/phase3-target-inspection.md", "**/phase3-target-inspection.json"]),
        "phase3ScreenshotPlans": find_all(root, ["**/phase3-screenshot-qa-plan.md", "**/phase3-screenshot-qa-plan.json"]),
        "phase3CaptureScripts": find_all(root, ["**/capture-screenshots.mjs"]),
        "phase3Screenshots": find_all(root, ["**/screenshots/*.png", "**/phase3-*screenshot*.png", "**/implementation-screenshot*.png"]),
        "visualReports": find_all(root, ["**/visual-diff*.md", "**/visual-diff*.json"]),
        "issueLogs": find_all(root, ["**/plugin-run-issues.md", "**/issues.md"]),
        "socialDrafts": find_all(root, ["**/social/*.md", "**/*case-post.md"]),
    }


def status_from(artifacts: dict[str, list[Path]]) -> dict[str, Any]:
    phase1_ready = bool(artifacts["phase1Briefs"] and artifacts["phase1Previews"])
    phase2_review_ready = bool(
        artifacts["phase2Manifests"]
        and artifacts["phase2PromptPacks"]
        and artifacts["phase2ReviewPackets"]
    )
    phase2_approved = bool(artifacts["phase2Handoffs"])
    phase3_inspected = bool(artifacts["phase3Inspections"])
    phase3_planned = bool(artifacts["phase3ScreenshotPlans"] and artifacts["phase3CaptureScripts"])
    phase3_screenshots = bool(artifacts["phase3Screenshots"])

    if not phase1_ready:
        key = "phase1-needed"
        title_cn = "需要先完成阶段一"
        title_en = "Phase 1 needed"
        next_skill = "$frontend-ui-ideation"
        next_prompt = (
            "Use $frontend-ui-ideation to redesign this existing app screen into a premium UI brief "
            "and preview. Use production mode unless I ask for demo mode."
        )
    elif not phase2_review_ready:
        key = "phase2-needed"
        title_cn = "阶段一已就绪，下一步生成阶段二资产"
        title_en = "Phase 1 ready; generate Phase 2 assets"
        next_skill = "$frontend-asset-production"
        next_prompt = (
            "Use $frontend-asset-production with the phase1-ui-brief.md and preview images in this "
            "run folder. Generate the complete foundation asset kit, review packet, and stop for my asset approval."
        )
    elif not phase2_approved:
        key = "asset-approval-required"
        title_cn = "阶段二资产等待用户审核"
        title_en = "Phase 2 asset approval required"
        next_skill = "$frontend-asset-production"
        next_prompt = APPROVAL_TEXT
    elif not phase3_inspected:
        key = "phase3-inspection-needed"
        title_cn = "资产已通过，下一步检查目标前端"
        title_en = "Assets approved; inspect the target frontend"
        next_skill = "$frontend-implementation"
        next_prompt = (
            "Use $frontend-implementation with the approved phase2-asset-handoff.md. Inspect the target "
            "frontend first, then hot-replace the requested route with the approved assets."
        )
    elif not phase3_planned:
        key = "phase3-qa-plan-needed"
        title_cn = "目标项目已检查，下一步生成截图 QA 计划"
        title_en = "Target inspected; create the screenshot QA plan"
        next_skill = "$frontend-implementation"
        next_prompt = (
            "Continue $frontend-implementation. Generate the Phase 3 screenshot QA plan, then capture "
            "desktop and mobile screenshots when the app runtime is available."
        )
    elif not phase3_screenshots:
        key = "phase3-screenshot-capture-needed"
        title_cn = "截图 QA 计划已就绪，下一步捕获实现截图"
        title_en = "Screenshot QA plan ready; capture implementation screenshots"
        next_skill = "$frontend-implementation"
        next_prompt = (
            "Continue $frontend-implementation. Run the target app, execute the generated capture-screenshots.mjs "
            "script or capture equivalent external-runtime screenshots, then run visual checks and diffs."
        )
    else:
        key = "implementation-evidence-ready"
        title_cn = "三阶段证据基本齐全，检查最终验收"
        title_en = "Pipeline evidence ready; verify final acceptance"
        next_skill = "$frontend-implementation"
        next_prompt = (
            "Review the final implementation evidence, visual checks, screenshot diffs, and remaining risks. "
            "Confirm whether the frontend can be treated as production-ready."
        )

    return {
        "key": key,
        "titleCn": title_cn,
        "titleEn": title_en,
        "nextSkill": next_skill,
        "nextPrompt": next_prompt,
        "phaseReadiness": {
            "phase1Ready": phase1_ready,
            "phase2ReviewReady": phase2_review_ready,
            "phase2Approved": phase2_approved,
            "phase3Inspected": phase3_inspected,
            "phase3QaPlanned": phase3_planned,
            "phase3ScreenshotsCaptured": phase3_screenshots,
        },
    }


def build_runbook(root: Path, project: str, target: str) -> dict[str, Any]:
    artifacts = collect_artifacts(root)
    status = status_from(artifacts)
    display_artifacts: list[dict[str, str]] = []
    groups = [
        ("phase1Briefs", "Phase 1", "UI brief", "spec"),
        ("phase1Previews", "Phase 1", "Preview image", "visual"),
        ("phase2Manifests", "Phase 2", "Asset manifest", "manifest"),
        ("phase2PromptPacks", "Phase 2", "Asset prompt pack", "prompt-pack"),
        ("phase2ContactSheets", "Phase 2", "Contact sheet", "review"),
        ("phase2ReviewPackets", "Phase 2", "Approval packet", "approval"),
        ("phase2Handoffs", "Phase 2", "Final asset handoff", "handoff"),
        ("phase3Inspections", "Phase 3", "Target inspection", "inspection"),
        ("phase3ScreenshotPlans", "Phase 3", "Screenshot QA plan", "qa-plan"),
        ("phase3CaptureScripts", "Phase 3", "Capture script", "script"),
        ("phase3Screenshots", "Phase 3", "Implementation screenshot", "visual"),
        ("visualReports", "QA", "Visual report", "qa"),
        ("issueLogs", "Ops", "Issue log", "log"),
        ("socialDrafts", "Social", "Social draft", "content"),
    ]
    for key, phase, label, kind in groups:
        for path in artifacts[key]:
            display_artifacts.append(artifact(path, root, phase, label, kind))

    return {
        "schemaVersion": "frontend-ui-pipeline.runbook.v1",
        "runRoot": str(root),
        "project": project or root.name,
        "target": target,
        "status": status,
        "artifacts": display_artifacts,
        "approvalGate": {
            "requiredBeforePhase3Production": True,
            "passed": status["phaseReadiness"]["phase2Approved"],
            "approvalText": APPROVAL_TEXT,
        },
        "recommendedCommands": {
            "phase2ApprovalPacket": "Open phase2-asset-approval-packet.html or .md, then reply with the approval text if it passes.",
            "phase3Capture": "Run phase3-screenshot-qa/capture-screenshots.mjs after the target app has a browser URL.",
        },
    }


def artifact_table(runbook: dict[str, Any]) -> list[str]:
    rows = ["| Phase | Artifact | Kind | Path |", "| --- | --- | --- | --- |"]
    for item in runbook["artifacts"]:
        rows.append(f"| {item['phase']} | {item['label']} | `{item['kind']}` | `{item['path']}` |")
    if len(rows) == 2:
        rows.append("| - | No artifacts found | - | - |")
    return rows


def markdown(runbook: dict[str, Any]) -> str:
    status = runbook["status"]
    readiness = status["phaseReadiness"]
    readiness_rows = [
        ("Phase 1 brief + preview", readiness["phase1Ready"]),
        ("Phase 2 review package", readiness["phase2ReviewReady"]),
        ("Phase 2 approved handoff", readiness["phase2Approved"]),
        ("Phase 3 target inspection", readiness["phase3Inspected"]),
        ("Phase 3 screenshot QA plan", readiness["phase3QaPlanned"]),
        ("Phase 3 implementation screenshots", readiness["phase3ScreenshotsCaptured"]),
    ]
    readiness_lines = [f"- {name}: `{'yes' if value else 'no'}`" for name, value in readiness_rows]
    return "\n".join(
        [
            "# Frontend UI Pipeline Runbook",
            "",
            "## Status / 状态",
            "",
            f"- Project / 项目: `{runbook['project']}`",
            f"- Target / 目标: `{runbook['target'] or 'not specified'}`",
            f"- Current status / 当前状态: `{status['key']}`",
            f"- 中文: {status['titleCn']}",
            f"- English: {status['titleEn']}",
            f"- Next skill / 下一步 Skill: `{status['nextSkill']}`",
            "",
            "## Next Prompt / 下一句直接发送",
            "",
            "```text",
            status["nextPrompt"],
            "```",
            "",
            "## Approval Gate / 审核门禁",
            "",
            f"- Required before production Phase 3 / 生产阶段三前必须审核: `yes`",
            f"- Passed / 是否已通过: `{'yes' if runbook['approvalGate']['passed'] else 'no'}`",
            "- Approval text / 通过时直接回复:",
            "",
            "```text",
            runbook["approvalGate"]["approvalText"],
            "```",
            "",
            "## Readiness / 完成度",
            "",
            *readiness_lines,
            "",
            "## Artifact Index / 产物索引",
            "",
            *artifact_table(runbook),
            "",
            "## Notes / 备注",
            "",
            "- This runbook is generated from files on disk; if a phase looks incomplete, generate or move the missing artifact into the run folder.",
            "- 这份索引只读取当前目录里的真实文件；如果某阶段显示未完成，请先补齐对应产物或确认路径。",
            "- Do not hot-replace a production app until Phase 2 approval is explicit.",
            "- 阶段二没有明确通过前，不要热更替换正式应用。",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a frontend-ui-pipeline runbook from a run folder.")
    parser.add_argument("--run-root", required=True, help="Pipeline run folder to scan.")
    parser.add_argument("--project", default="", help="Project name for the runbook.")
    parser.add_argument("--target", default="", help="Target route, screen, or flow.")
    parser.add_argument("--output-md", default="", help="Markdown output path. Defaults to <run-root>/pipeline-runbook.md.")
    parser.add_argument("--output-json", default="", help="JSON output path. Defaults to <run-root>/pipeline-runbook.json.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.run_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"Run root must be an existing directory: {root}")
    runbook = build_runbook(root, args.project, args.target)
    output_md = Path(args.output_md).expanduser().resolve() if args.output_md else root / "pipeline-runbook.md"
    output_json = Path(args.output_json).expanduser().resolve() if args.output_json else root / "pipeline-runbook.json"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown(runbook), encoding="utf-8")
    output_json.write_text(json.dumps(runbook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print(f"Status {runbook['status']['key']}")


if __name__ == "__main__":
    main()
