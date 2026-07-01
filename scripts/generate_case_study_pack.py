#!/usr/bin/env python3
"""Generate a shareable case-study pack from a frontend-ui-pipeline run folder."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_TEXT = "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation."
DEFAULT_GITHUB_URL = "https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin"


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
        "pipelineStarts": find_all(root, ["**/pipeline-start.md", "**/pipeline-start.json"]),
        "runbooks": find_all(root, ["**/pipeline-runbook.md", "**/pipeline-runbook.json"]),
        "audits": find_all(root, ["**/pipeline-completion-audit.md", "**/pipeline-completion-audit.json"]),
        "phase1Briefs": find_all(root, ["**/phase1-ui-brief.md"]),
        "phase1Options": find_all(root, ["**/phase1-option*.png"]),
        "phase1Previews": find_all(root, ["**/phase1-preview*.png", "**/phase1-flow-preview*.png"]),
        "phase1Gates": find_all(root, ["**/phase1-visual-excellence-gate.md", "**/phase1-visual-excellence-gate.json"]),
        "phase1Benchmarks": find_all(root, ["**/phase1-visual-benchmark.md", "**/phase1-visual-benchmark.json"]),
        "phase2Manifests": find_all(root, ["**/asset-manifest.json", "**/foundation-asset-manifest*.json"]),
        "phase2Review": find_all(root, ["**/phase2-asset-approval-packet.md", "**/phase2-asset-approval-packet.html"]),
        "phase2Assemblies": find_all(root, ["**/primary-screen-asset-assembly*.png", "**/primary-screen-asset-assembly*.html"]),
        "phase2ContactSheets": find_all(root, ["**/phase2-contact-sheet.png", "**/component-contact-sheet.html"]),
        "phase2Handoffs": find_all(root, ["**/phase2-asset-handoff.md"]),
        "phase3Demos": find_all(root, ["**/phase3-demo*/index.html", "**/phase3-demo*/phase3-demo-evidence.md", "**/phase3-demo*/README.md"]),
        "phase3PatchPlans": find_all(root, ["**/phase3-implementation-patch-plan.md", "**/phase3-implementation-patch-plan.json"]),
        "phase3Screenshots": find_all(root, ["**/screenshots/*.png", "**/phase3-*screenshot*.png", "**/implementation-screenshot*.png"]),
        "socialDrafts": find_all(root, ["**/social/*.md", "**/*case-post.md"]),
        "socialVisuals": find_all(root, ["**/social/visuals/*.png"]),
        "issueLogs": find_all(root, ["**/issues/*.md", "**/*run-issues*.md"]),
    }


def manifest_metrics(manifest: dict[str, Any]) -> dict[str, Any]:
    coverage = manifest.get("coverage", {}) if isinstance(manifest.get("coverage"), dict) else {}
    entries = manifest.get("entries", []) if isinstance(manifest.get("entries"), list) else []
    foundation_components = coverage.get("foundationComponents", {}) if isinstance(coverage.get("foundationComponents"), dict) else {}
    foundation_states = coverage.get("foundationStates")
    if foundation_states is None:
        foundation_states = sum(int(value or 0) for value in foundation_components.values())
    return {
        "status": manifest.get("status", ""),
        "totalEntries": coverage.get("totalEntries", len(entries)),
        "screenSlots": coverage.get("screenAssetSlots", 0),
        "foundationStates": foundation_states,
        "commonIcons": coverage.get("commonIcons", 0),
    }


def audit_summary(audit: dict[str, Any]) -> dict[str, Any]:
    summary = audit.get("summary", {}) if isinstance(audit.get("summary"), dict) else {}
    return {
        "overallStatus": audit.get("overallStatus", "unknown"),
        "passed": summary.get("passed", 0),
        "blocked": summary.get("blocked", 0),
        "missing": summary.get("missing", 0),
        "incomplete": summary.get("incomplete", 0),
    }


def benchmark_metrics(path: Path | None) -> dict[str, Any]:
    payload = load_json(path)
    return {
        "visualBenchmarkPassed": bool(payload.get("passed")),
        "visualBenchmarkAverageMargin": payload.get("averageMargin", 0),
        "visualBenchmarkAdvantages": payload.get("advantageCriteria", []) if isinstance(payload.get("advantageCriteria"), list) else [],
    }


def artifact(label: str, kind: str, paths: list[Path], root: Path, limit: int = 8) -> list[dict[str, str]]:
    return [
        {"label": label, "kind": kind, "path": rel(path, root)}
        for path in paths[:limit]
    ]


def build_pack(root: Path, project: str, target: str, github_url: str, title: str) -> dict[str, Any]:
    artifacts = collect(root)
    audit = load_json(first([path for path in artifacts["audits"] if path.suffix == ".json"]))
    runbook = load_json(first([path for path in artifacts["runbooks"] if path.suffix == ".json"]))
    manifest = load_json(first(artifacts["phase2Manifests"]))
    metrics = manifest_metrics(manifest)
    benchmark = benchmark_metrics(first([path for path in artifacts["phase1Benchmarks"] if path.suffix == ".json"]))
    summary = audit_summary(audit)
    phase_readiness = {}
    status = runbook.get("status") if isinstance(runbook.get("status"), dict) else {}
    if isinstance(status.get("phaseReadiness"), dict):
        phase_readiness = status["phaseReadiness"]

    actual_project = project or audit.get("project") or runbook.get("project") or root.name
    actual_target = target or audit.get("target") or runbook.get("target") or ""
    phase1_direction_count = len(artifacts["phase1Options"]) or len(artifacts["phase1Previews"])
    next_action = APPROVAL_TEXT if summary["overallStatus"] == "blocked-on-asset-approval" else "Review the runbook and completion audit before claiming production completion."

    evidence = []
    evidence.extend(artifact("Pipeline start prompt", "start", artifacts["pipelineStarts"], root))
    evidence.extend(artifact("Runbook", "runbook", artifacts["runbooks"], root))
    evidence.extend(artifact("Completion audit", "audit", artifacts["audits"], root))
    evidence.extend(artifact("Phase 1 brief", "spec", artifacts["phase1Briefs"], root))
    evidence.extend(artifact("Phase 1 visual direction", "visual", artifacts["phase1Options"] or artifacts["phase1Previews"], root, limit=6))
    evidence.extend(artifact("Phase 1 visual gate", "qa", artifacts["phase1Gates"], root))
    evidence.extend(artifact("Phase 1 Product Design benchmark", "qa", artifacts["phase1Benchmarks"], root))
    evidence.extend(artifact("Phase 2 manifest", "manifest", artifacts["phase2Manifests"], root))
    evidence.extend(artifact("Phase 2 review packet", "approval", artifacts["phase2Review"], root))
    evidence.extend(artifact("Asset-assembled primary screen", "assembly", artifacts["phase2Assemblies"], root))
    evidence.extend(artifact("Contact sheet", "review", artifacts["phase2ContactSheets"], root))
    evidence.extend(artifact("Phase 2 handoff", "handoff", artifacts["phase2Handoffs"], root))
    evidence.extend(artifact("Phase 3 demo", "demo", artifacts["phase3Demos"], root))
    evidence.extend(artifact("Phase 3 patch plan", "patch-plan", artifacts["phase3PatchPlans"], root))
    evidence.extend(artifact("Phase 3 screenshot", "visual", artifacts["phase3Screenshots"], root))
    evidence.extend(artifact("Social visual", "social-visual", artifacts["socialVisuals"], root, limit=12))
    evidence.extend(artifact("Issue log", "ops", artifacts["issueLogs"], root, limit=4))

    return {
        "schemaVersion": "frontend-ui-pipeline.case-study-pack.v1",
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project": actual_project,
        "target": actual_target,
        "title": title or f"{actual_project} Frontend UI Pipeline Case Study",
        "runRoot": str(root),
        "githubUrl": github_url,
        "summary": summary,
        "metrics": {
            **metrics,
            **benchmark,
            "phase1VisualDirections": phase1_direction_count,
            "socialVisuals": len(artifacts["socialVisuals"]),
            "phase3DemoFiles": len(artifacts["phase3Demos"]),
        },
        "phaseReadiness": phase_readiness,
        "nextAction": next_action,
        "evidence": evidence,
    }


def status_sentence(pack: dict[str, Any]) -> str:
    status = pack["summary"]["overallStatus"]
    if status == "complete":
        return "The run has complete production evidence."
    if status == "blocked-on-asset-approval":
        return "The run is deliberately blocked before production hot replacement because Phase 2 assets still need explicit approval."
    if status == "in-progress":
        return "The run is in progress; use this case pack as a progress proof, not a final production claim."
    return "The run is incomplete; use the missing evidence list before publishing strong claims."


def evidence_table(pack: dict[str, Any]) -> list[str]:
    rows = ["| Artifact | Kind | Path |", "| --- | --- | --- |"]
    for entry in pack["evidence"]:
        rows.append(f"| {entry['label']} | `{entry['kind']}` | `{entry['path']}` |")
    if len(rows) == 2:
        rows.append("| - | - | No evidence files found |")
    return rows


def case_study_md(pack: dict[str, Any]) -> str:
    metrics = pack["metrics"]
    summary = pack["summary"]
    return "\n".join(
        [
            f"# {pack['title']}",
            "",
            f"- Project: `{pack['project']}`",
            f"- Target: `{pack['target'] or 'not specified'}`",
            f"- Status: `{summary['overallStatus']}`",
            f"- GitHub: {pack['githubUrl']}",
            "",
            "## Case Hook",
            "",
            f"Old page in, {metrics['phase1VisualDirections']} premium visual directions, {metrics['totalEntries']} asset records, {metrics['commonIcons']} common icons, a runnable demo, and an evidence audit out.",
            "",
            "## What This Proves",
            "",
            f"- Phase 1 visual directions: `{metrics['phase1VisualDirections']}`",
            f"- Product Design benchmark: `{'passed' if metrics['visualBenchmarkPassed'] else 'not proven'}`",
            f"- Benchmark average margin: `{metrics['visualBenchmarkAverageMargin']}`",
            f"- Phase 2 asset manifest entries: `{metrics['totalEntries']}`",
            f"- Screen asset slots: `{metrics['screenSlots']}`",
            f"- Foundation states: `{metrics['foundationStates']}`",
            f"- Common icons: `{metrics['commonIcons']}`",
            f"- Social visuals: `{metrics['socialVisuals']}`",
            f"- Completion audit: `{summary['passed']}` passed, `{summary['blocked']}` blocked, `{summary['missing']}` missing, `{summary['incomplete']}` incomplete",
            "",
            "## Honest Status",
            "",
            status_sentence(pack),
            "",
            "## Next Gate",
            "",
            "```text",
            pack["nextAction"],
            "```",
            "",
            "## Evidence Index",
            "",
            *evidence_table(pack),
            "",
        ]
    )


def social_post_cn(pack: dict[str, Any]) -> str:
    metrics = pack["metrics"]
    summary = pack["summary"]
    status_note = "资产还没审核通过，所以它没有偷跑生产热替换。" if summary["overallStatus"] == "blocked-on-asset-approval" else "所有结论都来自 run 目录里的真实产物。"
    return "\n".join(
        [
            f"# {pack['project']} 案例发布文案",
            "",
            "我做了一个 Codex 插件：Frontend UI Pipeline。",
            "",
            "它想解决的不是“生成一张好看的 UI 图”，而是让不懂美术、不懂前端的人，也能从旧页面开始，跑出能真实落地的高端前端流水线。",
            "",
            f"这次案例跑的是：`{pack['project']}` `{pack['target'] or ''}`",
            "",
            "跑出来的证据：",
            f"- Phase 1：`{metrics['phase1VisualDirections']}` 个高端视觉方向",
            f"- Phase 2：`{metrics['totalEntries']}` 条资产 manifest 记录",
            f"- Phase 2：`{metrics['commonIcons']}` 个常用 icons",
            f"- Product Design benchmark：`{'已通过' if metrics['visualBenchmarkPassed'] else '未证明'}`，领先项：`{', '.join(metrics['visualBenchmarkAdvantages']) or '无'}`",
            f"- Phase 2：完整 foundation kit，覆盖按钮、角标、卡片、combobox、导航、通告、搜索、标题、弹窗和过渡动画",
            "- Phase 2：真实资产拼装主屏，不拿 Phase 1 截图冒充资产完成",
            f"- Phase 3：`{metrics['phase3DemoFiles']}` 个 demo/证据文件",
            f"- Completion audit：`{summary['passed']}` 项通过，`{summary['blocked']}` 项被门禁阻塞，`{summary['missing']}` 项缺失",
            "",
            status_note,
            "",
            "我觉得这才是 AI 前端工具真正该长出来的样子：",
            "",
            "旧页面 -> 视觉比稿 -> 像素级 brief -> 完整资产系统 -> 审核门禁 -> 真实前端落地。",
            "",
            "GitHub:",
            pack["githubUrl"],
            "",
        ]
    )


def readme_snippet_md(pack: dict[str, Any]) -> str:
    metrics = pack["metrics"]
    return "\n".join(
        [
            "## Case Study Snippet",
            "",
            f"- Case: `{pack['project']}`",
            f"- Target: `{pack['target'] or 'not specified'}`",
            f"- Status: `{pack['summary']['overallStatus']}`",
            f"- Phase 1 directions: `{metrics['phase1VisualDirections']}`",
            f"- Product Design benchmark: `{'passed' if metrics['visualBenchmarkPassed'] else 'not proven'}`",
            f"- Asset records: `{metrics['totalEntries']}`",
            f"- Common icons: `{metrics['commonIcons']}`",
            f"- Social visuals: `{metrics['socialVisuals']}`",
            f"- Evidence pack: `case-study-pack/case-study.md`",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a shareable case-study pack from a frontend-ui-pipeline run.")
    parser.add_argument("--run-root", required=True, help="Pipeline run folder to summarize.")
    parser.add_argument("--project", default="", help="Project name.")
    parser.add_argument("--target", default="", help="Target route, screen, or flow.")
    parser.add_argument("--github-url", default=DEFAULT_GITHUB_URL, help="GitHub URL to use in CTA copy.")
    parser.add_argument("--title", default="", help="Case study title.")
    parser.add_argument("--output-dir", default="", help="Output directory. Defaults to <run-root>/case-study-pack.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.run_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"Run root must be an existing directory: {root}")
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else root / "case-study-pack"
    output_dir.mkdir(parents=True, exist_ok=True)
    pack = build_pack(root, args.project, args.target, args.github_url, args.title)

    case_md = output_dir / "case-study.md"
    social_md = output_dir / "social-post.zh-CN.md"
    snippet_md = output_dir / "github-readme-snippet.md"
    index_json = output_dir / "evidence-index.json"
    case_md.write_text(case_study_md(pack), encoding="utf-8")
    social_md.write_text(social_post_cn(pack), encoding="utf-8")
    snippet_md.write_text(readme_snippet_md(pack), encoding="utf-8")
    index_json.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {case_md}")
    print(f"Wrote {social_md}")
    print(f"Wrote {snippet_md}")
    print(f"Wrote {index_json}")
    print(f"Status: {pack['summary']['overallStatus']}")


if __name__ == "__main__":
    main()
