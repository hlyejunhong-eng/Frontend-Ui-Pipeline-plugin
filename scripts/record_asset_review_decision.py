#!/usr/bin/env python3
"""Record a Phase 2 asset review decision as Markdown and JSON evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVAL_TEXT = "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation."
DECISIONS = {
    "approve-assets": {
        "approved": True,
        "revisionRequired": False,
        "handoffAllowed": True,
        "label": "Approve assets",
        "nextPrompt": APPROVAL_TEXT,
    },
    "revise-visual-style": {
        "approved": False,
        "revisionRequired": True,
        "handoffAllowed": False,
        "label": "Revise visual style",
        "nextPrompt": "Revise visual style: update the assets, regenerate the review packet, then ask for approval again.",
    },
    "revise-naming-organization": {
        "approved": False,
        "revisionRequired": True,
        "handoffAllowed": False,
        "label": "Revise naming or organization",
        "nextPrompt": "Revise naming/organization: update filenames, folders, manifest paths, then regenerate the review packet.",
    },
    "revise-implementation-mapping": {
        "approved": False,
        "revisionRequired": True,
        "handoffAllowed": False,
        "label": "Revise implementation mapping",
        "nextPrompt": "Revise implementation mapping: update layer order, import paths, CSS selectors, or motion triggers, then regenerate the review packet.",
    },
    "review-pending": {
        "approved": False,
        "revisionRequired": False,
        "handoffAllowed": False,
        "label": "Review pending",
        "nextPrompt": "Ask the user to review the Phase 2 asset approval packet and choose approve or revise.",
    },
}

APPROVAL_MARKERS = (
    "approve",
    "approved",
    "pass",
    "passed",
    "accepted",
    "looks good",
    "go ahead",
    "通过",
    "同意",
    "确认",
    "可以",
)


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"File does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"Expected JSON object in {path}")
    return payload


def rel(path: Path | None, root: Path) -> str:
    if not path:
        return ""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def explicit_approval(text: str) -> bool:
    lowered = text.strip().lower()
    return any(marker in lowered for marker in APPROVAL_MARKERS)


def manifest_summary(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    payload = load_json(path)
    coverage = payload.get("coverage", {}) if isinstance(payload.get("coverage"), dict) else {}
    foundation = coverage.get("foundationComponents", {}) if isinstance(coverage.get("foundationComponents"), dict) else {}
    project = payload.get("project", {}) if isinstance(payload.get("project"), dict) else {}
    return {
        "path": str(path),
        "status": payload.get("status", ""),
        "project": project.get("name", payload.get("name", "")),
        "screen": project.get("screen", payload.get("screen", "")),
        "totalEntries": coverage.get("totalEntries", len(payload.get("entries", []) if isinstance(payload.get("entries"), list) else [])),
        "screenAssetSlots": coverage.get("screenAssetSlots", 0),
        "foundationStates": sum(int(value or 0) for value in foundation.values()),
        "commonIcons": coverage.get("commonIcons", 0),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    decision_info = DECISIONS[args.decision]
    message = args.message.strip()
    if args.decision == "approve-assets" and not explicit_approval(message):
        fail("approve-assets requires a message with an explicit approval/pass phrase.")
    if args.decision.startswith("revise-") and not message:
        fail("revision decisions require a non-empty message describing what to change.")

    output_dir = Path(args.output_dir).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else None
    review_packet_path = Path(args.review_packet).expanduser().resolve() if args.review_packet else None
    contact_sheet_path = Path(args.contact_sheet).expanduser().resolve() if args.contact_sheet else None
    assembly_preview_path = Path(args.assembly_preview).expanduser().resolve() if args.assembly_preview else None
    visual_diff_path = Path(args.visual_diff_report).expanduser().resolve() if args.visual_diff_report else None
    now = args.reviewed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "schemaVersion": "frontend-ui-pipeline.asset-review-decision.v1",
        "decision": args.decision,
        "label": decision_info["label"],
        "approved": decision_info["approved"],
        "revisionRequired": decision_info["revisionRequired"],
        "handoffAllowed": decision_info["handoffAllowed"],
        "reviewedBy": args.reviewed_by,
        "reviewedAt": now,
        "message": message,
        "approvalText": message if decision_info["approved"] else "",
        "nextPrompt": decision_info["nextPrompt"],
        "manifest": manifest_summary(manifest_path),
        "evidence": {
            "reviewPacket": rel(review_packet_path, output_dir),
            "contactSheet": rel(contact_sheet_path, output_dir),
            "assemblyPreview": rel(assembly_preview_path, output_dir),
            "visualDiffReport": rel(visual_diff_path, output_dir),
        },
    }


def markdown(payload: dict[str, Any]) -> str:
    manifest = payload["manifest"]
    evidence = payload["evidence"]
    return "\n".join(
        [
            "# Phase 2 Asset Review Decision",
            "",
            f"- Decision: `{payload['decision']}` / **{payload['label']}**",
            f"- Approved: `{'yes' if payload['approved'] else 'no'}`",
            f"- Revision required: `{'yes' if payload['revisionRequired'] else 'no'}`",
            f"- Handoff allowed: `{'yes' if payload['handoffAllowed'] else 'no'}`",
            f"- Reviewed by: `{payload['reviewedBy']}`",
            f"- Reviewed at: `{payload['reviewedAt']}`",
            "",
            "## Message",
            "",
            "```text",
            payload["message"],
            "```",
            "",
            "## Evidence",
            "",
            f"- Review packet: `{evidence['reviewPacket'] or 'not provided'}`",
            f"- Contact sheet: `{evidence['contactSheet'] or 'not provided'}`",
            f"- Asset assembly preview: `{evidence['assemblyPreview'] or 'not provided'}`",
            f"- Visual diff report: `{evidence['visualDiffReport'] or 'not provided'}`",
            "",
            "## Manifest Summary",
            "",
            f"- Manifest: `{manifest.get('path', 'not provided')}`",
            f"- Status: `{manifest.get('status', 'unknown')}`",
            f"- Screen asset slots: `{manifest.get('screenAssetSlots', 0)}`",
            f"- Foundation states: `{manifest.get('foundationStates', 0)}`",
            f"- Common icons: `{manifest.get('commonIcons', 0)}`",
            f"- Total entries: `{manifest.get('totalEntries', 0)}`",
            "",
            "## Next Prompt",
            "",
            "```text",
            payload["nextPrompt"],
            "```",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record Phase 2 asset review approval or revision decision.")
    parser.add_argument("--decision", choices=sorted(DECISIONS), required=True, help="Review decision.")
    parser.add_argument("--message", required=True, help="Exact user review message or pending-review note.")
    parser.add_argument("--output-dir", required=True, help="Output directory, usually the Phase 2 review folder.")
    parser.add_argument("--reviewed-by", default="user", help="Reviewer name or role.")
    parser.add_argument("--reviewed-at", default="", help="Review timestamp. Defaults to current UTC time.")
    parser.add_argument("--manifest", default="", help="Optional asset-manifest.json path.")
    parser.add_argument("--review-packet", default="", help="Optional phase2-asset-approval-packet.md/html path.")
    parser.add_argument("--contact-sheet", default="", help="Optional contact sheet path.")
    parser.add_argument("--assembly-preview", default="", help="Optional generated asset assembly preview path.")
    parser.add_argument("--visual-diff-report", default="", help="Optional visual diff report path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(args)
    output_json = output_dir / "phase2-asset-review-decision.json"
    output_md = output_dir / "phase2-asset-review-decision.md"
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(markdown(payload), encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Wrote {output_json}")
    print(f"Handoff allowed: {'yes' if payload['handoffAllowed'] else 'no'}")


if __name__ == "__main__":
    main()
