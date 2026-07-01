#!/usr/bin/env python3
"""Generate an evidence audit for a frontend-ui-pipeline run folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


COMMON_ICONS = {
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
}

FOUNDATION_COMPONENTS = {
    "button",
    "numeric-badge",
    "card",
    "combobox",
    "navigation",
    "notice-bar",
    "search-bar",
    "section-title",
    "modal",
    "transition",
}


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
    return sorted(set(found), key=lambda path: path.as_posix())


def read_text(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def first(paths: list[Path]) -> Path | None:
    return paths[0] if paths else None


def collect(root: Path) -> dict[str, list[Path]]:
    return {
        "phase1Briefs": find_all(root, ["**/phase1-ui-brief.md"]),
        "phase1Previews": find_all(root, ["**/phase1-preview*.png", "**/phase1-option*.png"]),
        "phase1Gates": find_all(root, ["**/phase1-visual-excellence-gate.md", "**/phase1-visual-excellence-gate.json"]),
        "phase1Benchmarks": find_all(root, ["**/phase1-visual-benchmark.md", "**/phase1-visual-benchmark.json"]),
        "phase2Manifests": find_all(root, ["**/asset-manifest.json", "**/foundation-asset-manifest*.json"]),
        "phase2PromptPacks": find_all(root, ["**/phase2-asset-prompt-pack.md"]),
        "phase2ReviewPackets": find_all(root, ["**/phase2-asset-approval-packet.md", "**/phase2-asset-approval-packet.html"]),
        "phase2ReviewDecisions": find_all(root, ["**/phase2-asset-review-decision.md", "**/phase2-asset-review-decision.json"]),
        "phase2Assemblies": find_all(root, ["**/primary-screen-asset-assembly*.png", "**/primary-screen-asset-assembly*.html"]),
        "phase2Handoffs": find_all(root, ["**/phase2-asset-handoff.md"]),
        "phase3Inspections": find_all(root, ["**/phase3-target-inspection.md", "**/phase3-target-inspection.json"]),
        "phase3QaPlans": find_all(root, ["**/phase3-screenshot-qa-plan.md", "**/phase3-screenshot-qa-plan.json"]),
        "phase3PatchPlans": find_all(root, ["**/phase3-implementation-patch-plan.md", "**/phase3-implementation-patch-plan.json"]),
        "phase3Demos": find_all(root, ["**/phase3-demo*/index.html", "**/phase3-demo*/README.md", "**/phase3-demo*/phase3-demo-evidence.md"]),
        "phase3Screenshots": find_all(root, ["**/screenshots/*.png", "**/phase3-*screenshot*.png", "**/implementation-screenshot*.png"]),
        "phase3DesignQa": find_all(root, ["**/design-qa.md", "**/design-qa.json"]),
        "social": find_all(root, ["**/social/*.md", "**/social/visuals/*.png", "**/*case-post.md", "**/case-study-pack/*.md", "**/case-study-pack/*.json"]),
        "runbooks": find_all(root, ["**/pipeline-runbook.md", "**/pipeline-runbook.json"]),
    }


def visual_gate_passed(paths: list[Path]) -> bool:
    for path in paths:
        payload = load_json(path) if path.suffix == ".json" else {}
        if payload.get("passed") is True and payload.get("phase2Allowed") is True:
            return True
        text = read_text(path).lower()
        if "phase 2 allowed: `yes`" in text or "phase2allowed" in text and "true" in text:
            return True
    return False


def visual_benchmark_passed(paths: list[Path]) -> bool:
    for path in paths:
        payload = load_json(path) if path.suffix == ".json" else {}
        if payload.get("passed") is True and payload.get("phase2Allowed") is True:
            return True
        text = read_text(path).lower()
        if "benchmark passed: `yes`" in text and "phase 2 allowed: `yes`" in text:
            return True
    return False


def design_qa_passed(paths: list[Path]) -> bool:
    for path in paths:
        payload = load_json(path) if path.suffix == ".json" else {}
        if payload.get("finalResult") == "passed":
            return True
        if "final result: passed" in read_text(path).lower():
            return True
    return False


def approved_review_decision(paths: list[Path]) -> bool:
    for path in paths:
        payload = load_json(path) if path.suffix == ".json" else {}
        if (
            payload.get("schemaVersion") == "frontend-ui-pipeline.asset-review-decision.v1"
            and payload.get("approved") is True
            and payload.get("handoffAllowed") is True
        ):
            return True
        text = read_text(path).lower()
        if "approved: `yes`" in text and "handoff allowed: `yes`" in text:
            return True
    return False


def manifest_summary(path: Path | None) -> dict[str, Any]:
    payload = load_json(path)
    coverage = payload.get("coverage", {}) if isinstance(payload.get("coverage"), dict) else {}
    foundation = coverage.get("foundationComponents", {}) if isinstance(coverage.get("foundationComponents"), dict) else {}
    entries = payload.get("entries", []) if isinstance(payload.get("entries"), list) else []
    icons = {
        str(item.get("state", "")).strip().lower()
        for item in entries
        if isinstance(item, dict) and str(item.get("component", "")).strip().lower() == "common-icon"
    }
    return {
        "status": payload.get("status", ""),
        "totalEntries": coverage.get("totalEntries", len(entries)),
        "commonIconCount": coverage.get("commonIcons", len(icons)),
        "foundationComponents": sorted(foundation.keys()),
        "icons": sorted(icons),
        "missingComponents": sorted(FOUNDATION_COMPONENTS - set(foundation.keys())),
        "missingIcons": sorted(COMMON_ICONS - icons) if icons else [],
    }


def patch_plan_summary(path: Path | None) -> dict[str, Any]:
    payload = load_json(path)
    operations = payload.get("copyOperations", []) if isinstance(payload.get("copyOperations"), list) else []
    keys = {
        json.dumps([item.get("kind"), item.get("source"), item.get("destination")], sort_keys=True)
        for item in operations
        if isinstance(item, dict)
    }
    return {
        "blockedBeforeEditing": payload.get("blockedBeforeEditing"),
        "approvalReady": payload.get("approvalReady"),
        "targetMatched": payload.get("targetMatched"),
        "copyOperations": len(operations),
        "duplicateCopyOperations": len(operations) - len(keys),
        "blockers": payload.get("blockers", []),
    }


def status(passed: bool, missing: list[str] | None = None, blocked: bool = False) -> str:
    if passed:
        return "passed"
    if blocked:
        return "blocked"
    if missing:
        return "missing"
    return "incomplete"


def item(identifier: str, requirement: str, state: str, evidence: list[Path], root: Path, notes: list[str] | None = None, missing: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": identifier,
        "requirement": requirement,
        "status": state,
        "evidence": [rel(path, root) for path in evidence],
        "missing": missing or [],
        "notes": notes or [],
    }


def plugin_evidence(repo_root: Path | None) -> tuple[str, list[str], list[str]]:
    if not repo_root:
        return "not-checked", [], ["No --repo-root was provided."]
    required = [
        repo_root / ".codex-plugin" / "plugin.json",
        repo_root / "README.md",
        repo_root / "scripts" / "install_local_marketplace.py",
        repo_root / "scripts" / "diagnose_install.py",
        repo_root / "scripts" / "quick_check.py",
        repo_root / "scripts" / "start_pipeline.py",
        repo_root / "scripts" / "generate_pipeline_runbook.py",
        repo_root / "scripts" / "generate_pipeline_completion_audit.py",
        repo_root / "scripts" / "generate_case_study_pack.py",
        repo_root / "scripts" / "record_asset_review_decision.py",
        repo_root / "scripts" / "generate_visual_benchmark_report.py",
        repo_root / "skills" / "frontend-ui-ideation" / "SKILL.md",
        repo_root / "skills" / "frontend-asset-production" / "SKILL.md",
        repo_root / "skills" / "frontend-implementation" / "SKILL.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    readme = read_text(repo_root / "README.md")
    readme_markers = [
        "codex plugin add frontend-ui-pipeline@personal",
        "Install Doctor",
        "Start Wizard",
        "Full Pipeline Prompt",
        "Case Study Pack Generator",
        "Product Design Benchmark",
        "Asset Review Decision",
        "Demo Mode",
        "Phase Output Standards",
    ]
    missing_markers = [marker for marker in readme_markers if marker not in readme]
    return ("passed" if not missing and not missing_markers else "missing", missing, missing_markers)


def build_audit(root: Path, repo_root: Path | None, project: str, target: str) -> dict[str, Any]:
    artifacts = collect(root)
    brief = first(artifacts["phase1Briefs"])
    brief_text = read_text(brief)
    manifest = first(artifacts["phase2Manifests"])
    manifest_info = manifest_summary(manifest)
    patch_plan = first([path for path in artifacts["phase3PatchPlans"] if path.suffix == ".json"]) or first(artifacts["phase3PatchPlans"])
    patch_info = patch_plan_summary(patch_plan)
    phase2_review_decision_approved = approved_review_decision(artifacts["phase2ReviewDecisions"])
    phase2_approved = bool(artifacts["phase2Handoffs"])
    phase3_screenshots = bool(artifacts["phase3Screenshots"])
    phase3_design_passed = design_qa_passed(artifacts["phase3DesignQa"])
    plugin_state, plugin_missing, plugin_missing_markers = plugin_evidence(repo_root)

    items = [
        item(
            "installable-plugin",
            "GitHub users can install and operate the plugin with clear non-expert instructions.",
            plugin_state,
            [] if not repo_root else [path for path in [repo_root / ".codex-plugin" / "plugin.json", repo_root / "README.md"] if path.exists()],
            root,
            missing=[*plugin_missing, *plugin_missing_markers],
        ),
        item(
            "phase1-premium-brief",
            "Phase 1 produces a premium UI brief, visual previews, and a passing visual excellence gate.",
            status(bool(brief and artifacts["phase1Previews"] and visual_gate_passed(artifacts["phase1Gates"]))),
            [path for path in [brief, *artifacts["phase1Previews"][:4], *artifacts["phase1Gates"][:2]] if path],
            root,
            missing=[] if brief else ["phase1-ui-brief.md"],
        ),
        item(
            "phase1-product-design-benchmark",
            "Phase 1 proves the selected direction beats the Product Design baseline before Phase 2 starts.",
            status(bool(artifacts["phase1Benchmarks"] and visual_benchmark_passed(artifacts["phase1Benchmarks"]))),
            artifacts["phase1Benchmarks"][:2],
            root,
            missing=[] if artifacts["phase1Benchmarks"] else ["phase1-visual-benchmark.md/json"],
        ),
        item(
            "phase1-phase2-guide",
            "Phase 1 includes a Phase 2 generation guide with layer order, naming/export rules, responsive crop rules, and adjustable parameters.",
            status(all(marker in brief_text for marker in ("Phase 2 Generation Guide", "Layer Map", "Adjustable Parameters", "Asset Naming Rules", "Export Rules", "Responsive Crop Rules"))),
            [brief] if brief else [],
            root,
            missing=[marker for marker in ("Phase 2 Generation Guide", "Layer Map", "Adjustable Parameters", "Asset Naming Rules", "Export Rules", "Responsive Crop Rules") if marker not in brief_text],
        ),
        item(
            "phase2-foundation-kit",
            "Phase 2 generates the complete foundation kit: backgrounds/illustrations plus required components, transitions, and 20 common icons.",
            status(
                bool(manifest)
                and not manifest_info["missingComponents"]
                and manifest_info["commonIconCount"] >= 20
                and int(manifest_info["totalEntries"] or 0) >= 89
            ),
            [manifest] if manifest else [],
            root,
            notes=[f"totalEntries={manifest_info['totalEntries']}", f"commonIcons={manifest_info['commonIconCount']}"],
            missing=[*manifest_info["missingComponents"], *manifest_info["missingIcons"]],
        ),
        item(
            "phase2-review-and-assembly",
            "Phase 2 provides review packet and asset-assembled primary screen proof before asking for approval.",
            status(bool(artifacts["phase2ReviewPackets"] and artifacts["phase2Assemblies"])),
            [*artifacts["phase2ReviewPackets"][:2], *artifacts["phase2Assemblies"][:2]],
            root,
            missing=[
                *([] if artifacts["phase2ReviewPackets"] else ["phase2-asset-approval-packet"]),
                *([] if artifacts["phase2Assemblies"] else ["primary-screen-asset-assembly"]),
            ],
        ),
        item(
            "phase2-review-decision",
            "Phase 2 records the user's approval, pending review, or revision decision before final handoff.",
            status(
                phase2_review_decision_approved,
                missing=[] if artifacts["phase2ReviewDecisions"] else ["phase2-asset-review-decision.md/json"],
                blocked=bool(artifacts["phase2ReviewDecisions"]) and not phase2_review_decision_approved,
            ),
            artifacts["phase2ReviewDecisions"] or artifacts["phase2ReviewPackets"][:1],
            root,
            notes=["Approved review decision is required before phase2-asset-handoff.md is generated."],
            missing=[] if artifacts["phase2ReviewDecisions"] else ["phase2-asset-review-decision.md/json"],
        ),
        item(
            "phase2-approval-gate",
            "Production Phase 3 is blocked until the user explicitly approves Phase 2 assets.",
            status(phase2_approved, blocked=not phase2_approved),
            artifacts["phase2Handoffs"] or artifacts["phase2ReviewDecisions"] or artifacts["phase2ReviewPackets"][:1],
            root,
            notes=["Approval text: Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation."],
            missing=[] if phase2_approved else ["phase2-asset-handoff.md"],
        ),
        item(
            "phase3-demo-mode",
            "Phase 3 demo mode provides a runnable standalone implementation without editing the production app.",
            status(bool(artifacts["phase3Demos"] and artifacts["phase3Inspections"] and artifacts["phase3QaPlans"] and artifacts["phase3PatchPlans"])),
            [*artifacts["phase3Demos"], *artifacts["phase3Inspections"][:2], *artifacts["phase3QaPlans"][:1], *artifacts["phase3PatchPlans"][:1]],
            root,
            notes=[f"patchPlanBlockedBeforeEditing={patch_info['blockedBeforeEditing']}", f"duplicateCopyOperations={patch_info['duplicateCopyOperations']}"],
        ),
        item(
            "phase3-production-verification",
            "Production Phase 3 has real implementation screenshots, visual diff evidence, and a passing design QA gate.",
            status(phase2_approved and phase3_screenshots and phase3_design_passed, blocked=not phase2_approved),
            [*artifacts["phase3Screenshots"][:4], *artifacts["phase3DesignQa"][:2]],
            root,
            missing=[
                *([] if phase2_approved else ["phase2-asset-handoff.md"]),
                *([] if phase3_screenshots else ["phase3 implementation screenshots"]),
                *([] if phase3_design_passed else ["passing design-qa.md/json"]),
            ],
        ),
        item(
            "social-proof",
            "The run includes self-media/GitHub-star case material with visuals and copy.",
            status(bool(artifacts["social"])),
            artifacts["social"][:12],
            root,
        ),
    ]

    if phase2_approved and phase3_screenshots and phase3_design_passed and all(entry["status"] == "passed" for entry in items if entry["id"] != "phase2-approval-gate"):
        overall = "complete"
    elif not phase2_approved and artifacts["phase2ReviewPackets"]:
        overall = "blocked-on-asset-approval"
    elif any(entry["status"] == "missing" for entry in items):
        overall = "incomplete"
    else:
        overall = "in-progress"

    return {
        "schemaVersion": "frontend-ui-pipeline.completion-audit.v1",
        "project": project or root.name,
        "target": target,
        "runRoot": str(root),
        "repoRoot": str(repo_root) if repo_root else "",
        "overallStatus": overall,
        "summary": {
            "passed": sum(1 for entry in items if entry["status"] == "passed"),
            "blocked": sum(1 for entry in items if entry["status"] == "blocked"),
            "missing": sum(1 for entry in items if entry["status"] == "missing"),
            "incomplete": sum(1 for entry in items if entry["status"] == "incomplete"),
        },
        "phase2Manifest": manifest_info,
        "phase3PatchPlan": patch_info,
        "items": items,
    }


def markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Pipeline Completion Audit",
        "",
        f"- Project: `{audit['project']}`",
        f"- Target: `{audit['target'] or 'not specified'}`",
        f"- Overall status: `{audit['overallStatus']}`",
        f"- Run root: `{audit['runRoot']}`",
        "",
        "## Summary",
        "",
        f"- Passed: `{audit['summary']['passed']}`",
        f"- Blocked: `{audit['summary']['blocked']}`",
        f"- Missing: `{audit['summary']['missing']}`",
        f"- Incomplete: `{audit['summary']['incomplete']}`",
        "",
        "## Requirement Evidence",
        "",
        "| ID | Status | Requirement | Evidence | Missing / Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in audit["items"]:
        evidence = "<br>".join(f"`{path}`" for path in entry["evidence"]) or "-"
        missing = ", ".join(entry["missing"]) if entry["missing"] else ""
        notes = ", ".join(entry["notes"]) if entry["notes"] else ""
        detail = "<br>".join(part for part in (missing, notes) if part) or "-"
        lines.append(f"| `{entry['id']}` | `{entry['status']}` | {entry['requirement']} | {evidence} | {detail} |")
    lines.extend(
        [
            "",
            "## Phase 2 Manifest",
            "",
            f"- Status: `{audit['phase2Manifest']['status'] or 'unknown'}`",
            f"- Total entries: `{audit['phase2Manifest']['totalEntries']}`",
            f"- Common icons: `{audit['phase2Manifest']['commonIconCount']}`",
            f"- Missing components: `{', '.join(audit['phase2Manifest']['missingComponents']) or 'none'}`",
            f"- Missing icons: `{', '.join(audit['phase2Manifest']['missingIcons']) or 'none'}`",
            "",
            "## Phase 3 Patch Plan",
            "",
            f"- Blocked before editing: `{audit['phase3PatchPlan']['blockedBeforeEditing']}`",
            f"- Approval ready: `{audit['phase3PatchPlan']['approvalReady']}`",
            f"- Target matched: `{audit['phase3PatchPlan']['targetMatched']}`",
            f"- Copy operations: `{audit['phase3PatchPlan']['copyOperations']}`",
            f"- Duplicate copy operations: `{audit['phase3PatchPlan']['duplicateCopyOperations']}`",
            "",
            "## Next Gate",
            "",
            "If the overall status is `blocked-on-asset-approval`, the next user action is:",
            "",
            "```text",
            "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation.",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an evidence audit for a frontend-ui-pipeline run folder.")
    parser.add_argument("--run-root", required=True, help="Pipeline run folder to audit.")
    parser.add_argument("--repo-root", default="", help="Optional plugin repository root for installability evidence.")
    parser.add_argument("--project", default="", help="Project name.")
    parser.add_argument("--target", default="", help="Target route, screen, or flow.")
    parser.add_argument("--output-md", default="", help="Markdown output path. Defaults to <run-root>/pipeline-completion-audit.md.")
    parser.add_argument("--output-json", default="", help="JSON output path. Defaults to <run-root>/pipeline-completion-audit.json.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.run_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"Run root must be an existing directory: {root}")
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
    audit = build_audit(root, repo_root, args.project, args.target)
    output_md = Path(args.output_md).expanduser().resolve() if args.output_md else root / "pipeline-completion-audit.md"
    output_json = Path(args.output_json).expanduser().resolve() if args.output_json else root / "pipeline-completion-audit.json"
    output_md.write_text(markdown(audit), encoding="utf-8")
    output_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print(f"Overall status: {audit['overallStatus']}")


if __name__ == "__main__":
    main()
