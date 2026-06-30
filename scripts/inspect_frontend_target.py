#!/usr/bin/env python3
"""Inspect a frontend repository before Phase 3 implementation."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


MAX_SCAN_FILES = 260
TEXT_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html", ".css", ".scss", ".json"}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def rel(path: Path, root: Path) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return str(path)


def list_existing(root: Path, candidates: list[str]) -> list[str]:
    return [candidate for candidate in candidates if (root / candidate).exists()]


def normalize_route(value: str) -> str:
    value = value.strip().replace("\\", "/")
    value = re.sub(r"^\./", "", value)
    value = re.sub(r"\.(vue|jsx|tsx|ts|js|svelte)$", "", value)
    return value.strip("/")


def collect_routes(root: Path) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    pages_json = load_json(root / "pages.json")
    for page in pages_json.get("pages", []) if isinstance(pages_json.get("pages"), list) else []:
        if isinstance(page, dict) and page.get("path"):
            routes.append(
                {
                    "path": page["path"],
                    "source": "pages.json",
                    "file": f"{page['path']}.vue",
                    "style": page.get("style", {}),
                }
            )
    for package in pages_json.get("subPackages", []) if isinstance(pages_json.get("subPackages"), list) else []:
        if not isinstance(package, dict):
            continue
        package_root = str(package.get("root", "")).strip("/")
        for page in package.get("pages", []) if isinstance(package.get("pages"), list) else []:
            if isinstance(page, dict) and page.get("path"):
                route_path = f"{package_root}/{page['path']}".strip("/")
                routes.append(
                    {
                        "path": route_path,
                        "source": "pages.json:subPackages",
                        "file": f"{route_path}.vue",
                        "style": page.get("style", {}),
                    }
                )

    conventional_roots = ["src/pages", "src/app", "app", "pages", "routes", "src/routes"]
    for route_root in conventional_roots:
        base = root / route_root
        if not base.exists() or not base.is_dir():
            continue
        for path in sorted(base.rglob("*"))[:300]:
            if path.suffix.lower() not in {".vue", ".jsx", ".tsx", ".ts", ".js", ".svelte"}:
                continue
            route = normalize_route(rel(path.with_suffix(""), base))
            if route.endswith("/index"):
                route = route[: -len("/index")] or "index"
            routes.append({"path": route, "source": route_root, "file": rel(path, root), "style": {}})

    deduped: dict[str, dict[str, Any]] = {}
    for route in routes:
        deduped.setdefault(route["path"], route)
    return list(deduped.values())


def detect_frameworks(root: Path, package_json: dict[str, Any]) -> list[str]:
    deps = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = package_json.get(key)
        if isinstance(section, dict):
            deps.update(section)
    frameworks = []
    if (root / "pages.json").exists() and (root / "manifest.json").exists():
        frameworks.append("uni-app")
    if "next" in deps or (root / "next.config.js").exists() or (root / "next.config.mjs").exists():
        frameworks.append("Next.js")
    if "nuxt" in deps or (root / "nuxt.config.ts").exists() or (root / "nuxt.config.js").exists():
        frameworks.append("Nuxt")
    if "react" in deps:
        frameworks.append("React")
    if "vue" in deps or (root / "App.vue").exists() or (root / "src" / "App.vue").exists():
        frameworks.append("Vue")
    if "svelte" in deps or "sveltekit" in deps:
        frameworks.append("Svelte")
    if "@angular/core" in deps:
        frameworks.append("Angular")
    if "vite" in deps or any(root.glob("vite.config.*")):
        frameworks.append("Vite")
    if not frameworks:
        frameworks.append("unknown")
    return frameworks


def detect_runtime(root: Path, package_json: dict[str, Any]) -> dict[str, Any]:
    scripts = package_json.get("scripts") if isinstance(package_json.get("scripts"), dict) else {}
    script_names = list(scripts.keys())
    runnable = []
    for preferred in ("dev", "start", "serve", "preview", "build", "test", "lint", "typecheck"):
        if preferred in scripts:
            runnable.append({"name": preferred, "command": f"npm run {preferred}", "script": scripts[preferred]})

    external_notes = []
    if (root / "pages.json").exists() and (root / "manifest.json").exists() and not runnable:
        external_notes.append("uni-app project without package scripts; use HBuilderX or project-specific uni-app CLI.")
    elif (root / "pages.json").exists() and (root / "manifest.json").exists():
        external_notes.append("uni-app project; HBuilderX may still be required for full device/App verification.")

    return {
        "packageScripts": scripts,
        "scriptNames": script_names,
        "recommendedCommands": runnable,
        "externalRuntimeNotes": external_notes,
    }


def text_files(root: Path) -> list[Path]:
    ignored = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "unpackage", "__pycache__"}
    candidates = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in ignored for part in path.parts):
            continue
        try:
            if path.stat().st_size > 350_000:
                continue
        except OSError:
            continue
        candidates.append(path)

    def priority(path: Path) -> tuple[int, str]:
        relative = rel(path, root).lower()
        is_api_like = bool(
            re.search(r"(^|/)(api|apis|service|services|client|clients)\.", relative)
            or re.search(r"(^|/)(api|apis|service|services|clients?)(/|$)", relative)
        )
        is_target_like = "/pages/" in f"/{relative}" or relative.startswith("pages/")
        return (0 if is_api_like else 1 if is_target_like else 2, relative)

    return sorted(candidates, key=priority)[:MAX_SCAN_FILES]


def detect_api_usage(root: Path) -> dict[str, Any]:
    patterns = {
        "apiClientImport": re.compile(r"import\s+api\s+from|from ['\"]@/common/api|from ['\"].*api", re.I),
        "apiMethodCall": re.compile(r"\bapi\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*\("),
        "fetch": re.compile(r"\bfetch\s*\("),
        "axios": re.compile(r"\baxios\.|\bfrom ['\"]axios['\"]"),
        "uniCloud": re.compile(r"\buniCloud\.callFunction\s*\("),
        "graphql": re.compile(r"\bgraphql\b|gql`", re.I),
    }
    files = text_files(root)
    hits: dict[str, list[dict[str, Any]]] = {name: [] for name in patterns}
    api_files = []

    for path in files:
        relative = rel(path, root)
        if re.search(r"(^|/)(api|apis|service|services|client|clients)\.", relative, re.I) or re.search(
            r"(^|/)(api|apis|service|services|clients?)(/|$)", relative, re.I
        ):
            api_files.append(relative)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for name, pattern in patterns.items():
            matches = list(pattern.finditer(text))
            if matches:
                hits[name].append({"file": relative, "count": len(matches)})

    return {
        "apiFiles": sorted(set(api_files))[:40],
        "signals": {name: values[:20] for name, values in hits.items() if values},
        "scannedTextFiles": len(files),
    }


def find_target(root: Path, target_route: str, routes: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_target = normalize_route(target_route)
    if not normalized_target:
        return {"requested": "", "matched": False, "reason": "No target route provided."}

    for route in routes:
        if normalize_route(str(route.get("path", ""))) == normalized_target:
            file_path = root / str(route.get("file", ""))
            return {
                "requested": target_route,
                "matched": True,
                "route": route,
                "fileExists": file_path.exists(),
                "absoluteFile": str(file_path.resolve()) if file_path.exists() else str(file_path),
            }

    direct_candidates = [
        root / normalized_target,
        root / f"{normalized_target}.vue",
        root / f"{normalized_target}.tsx",
        root / f"{normalized_target}.jsx",
        root / f"{normalized_target}.ts",
        root / f"{normalized_target}.js",
    ]
    for candidate in direct_candidates:
        if candidate.exists():
            return {
                "requested": target_route,
                "matched": True,
                "route": {"path": normalized_target, "source": "filesystem", "file": rel(candidate, root), "style": {}},
                "fileExists": True,
                "absoluteFile": str(candidate.resolve()),
            }
    return {"requested": target_route, "matched": False, "reason": "No matching route or file found."}


def recommended_asset_paths(root: Path, frameworks: list[str]) -> list[dict[str, str]]:
    if "uni-app" in frameworks:
        return [
            {"kind": "static-assets", "path": "static/frontend-ui-pipeline/"},
            {"kind": "shared-style", "path": "common/styles/frontend-ui-pipeline.css"},
            {"kind": "scoped-style", "path": "target .vue <style> block"},
        ]
    paths = []
    for candidate in ("public/frontend-ui-pipeline/", "src/assets/frontend-ui-pipeline/", "assets/frontend-ui-pipeline/"):
        parent = candidate.split("/")[0]
        if (root / parent).exists():
            paths.append({"kind": "assets", "path": candidate})
    if not paths:
        paths.append({"kind": "assets", "path": "public/frontend-ui-pipeline/"})
    return paths


def inspect(root: Path, target_route: str) -> dict[str, Any]:
    package_json = load_json(root / "package.json")
    frameworks = detect_frameworks(root, package_json)
    routes = collect_routes(root)
    runtime = detect_runtime(root, package_json)
    api_usage = detect_api_usage(root)
    target = find_target(root, target_route, routes)
    config_files = list_existing(
        root,
        [
            "package.json",
            "pages.json",
            "manifest.json",
            "App.vue",
            "main.js",
            "src/App.vue",
            "vite.config.js",
            "vite.config.ts",
            "next.config.js",
            "nuxt.config.ts",
            "uni.scss",
            "tailwind.config.js",
            "tailwind.config.ts",
        ],
    )
    return {
        "schemaVersion": "frontend-ui-pipeline.target-inspection.v1",
        "root": str(root.resolve()),
        "frameworks": frameworks,
        "configFiles": config_files,
        "runtime": runtime,
        "routes": routes[:120],
        "target": target,
        "apiUsage": api_usage,
        "assetPaths": recommended_asset_paths(root, frameworks),
        "phase3Recommendations": build_recommendations(frameworks, runtime, target, api_usage),
    }


def build_recommendations(
    frameworks: list[str], runtime: dict[str, Any], target: dict[str, Any], api_usage: dict[str, Any]
) -> list[str]:
    recommendations = []
    if not target.get("matched"):
        recommendations.append("Ask for or locate the exact target route before hot replacement.")
    if "uni-app" in frameworks:
        recommendations.append("Preserve uni-app primitives such as view, text, scroll-view, input, uni.*, uniCloud, and rpx.")
        recommendations.append("Copy approved static assets under static/frontend-ui-pipeline/ unless the app has a stronger convention.")
        if runtime.get("externalRuntimeNotes"):
            recommendations.append("Use HBuilderX or the project-specific uni-app workflow for final runtime verification.")
    if api_usage.get("apiFiles"):
        recommendations.append("Preserve existing API client files and method contracts; add mocks only when calls cannot be made.")
    if api_usage.get("signals", {}).get("uniCloud"):
        recommendations.append("Keep uniCloud.callFunction wrappers intact and match fixture shapes to cloud function results.")
    if runtime.get("recommendedCommands"):
        names = ", ".join(command["command"] for command in runtime["recommendedCommands"][:4])
        recommendations.append(f"Run available project commands during Phase 3 verification: {names}.")
    else:
        recommendations.append("No npm scripts were detected; document the external run workflow and build a standalone visual QA preview if needed.")
    return recommendations


def markdown(report: dict[str, Any]) -> str:
    route_lines = []
    for route in report.get("routes", [])[:30]:
        route_lines.append(f"- `{route.get('path')}` -> `{route.get('file')}` ({route.get('source')})")
    if not route_lines:
        route_lines.append("- No routes detected.")

    command_lines = []
    for command in report.get("runtime", {}).get("recommendedCommands", []):
        command_lines.append(f"- `{command.get('command')}` -> `{command.get('script')}`")
    if not command_lines:
        command_lines.append("- No npm run commands detected.")

    api_lines = []
    api_usage = report.get("apiUsage", {})
    for api_file in api_usage.get("apiFiles", [])[:20]:
        api_lines.append(f"- API file: `{api_file}`")
    for signal, hits in api_usage.get("signals", {}).items():
        files = ", ".join(f"`{hit.get('file')}` ({hit.get('count')})" for hit in hits[:6])
        api_lines.append(f"- {signal}: {files}")
    if not api_lines:
        api_lines.append("- No API signals detected.")
    external_note_lines = [f"- {note}" for note in report.get("runtime", {}).get("externalRuntimeNotes", [])]
    if not external_note_lines:
        external_note_lines = ["- None."]

    target = report.get("target", {})
    target_status = "matched" if target.get("matched") else "not matched"
    target_file = target.get("absoluteFile") or target.get("reason", "")
    lines = [
        "# Frontend Target Inspection",
        "",
        f"- Root: `{report.get('root')}`",
        f"- Frameworks: `{', '.join(report.get('frameworks', []))}`",
        f"- Target: `{target.get('requested', '')}` ({target_status})",
        f"- Target file/reason: `{target_file}`",
        "",
        "## Config Files",
        "",
        *[f"- `{path}`" for path in report.get("configFiles", [])],
        "",
        "## Run Commands",
        "",
        *command_lines,
        "",
        "## External Runtime Notes",
        "",
        *external_note_lines,
        "",
        "## Routes",
        "",
        *route_lines,
        "",
        "## API Signals",
        "",
        *api_lines,
        "",
        "## Recommended Asset Paths",
        "",
        *[f"- `{item.get('kind')}`: `{item.get('path')}`" for item in report.get("assetPaths", [])],
        "",
        "## Phase 3 Recommendations",
        "",
        *[f"- {item}" for item in report.get("phase3Recommendations", [])],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a frontend target repository before Phase 3.")
    parser.add_argument("repo", help="Frontend repository root.")
    parser.add_argument("--target-route", default="", help="Route, component, or file to hot-replace.")
    parser.add_argument("--output-json", default="", help="Optional JSON report path.")
    parser.add_argument("--output-md", default="", help="Optional Markdown report path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.repo).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        fail(f"Repository root does not exist: {root}")
    report = inspect(root, args.target_route)
    if args.output_json:
        Path(args.output_json).expanduser().resolve().write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.output_md:
        Path(args.output_md).expanduser().resolve().write_text(markdown(report), encoding="utf-8")
    frameworks = ", ".join(report["frameworks"])
    target = "matched" if report["target"].get("matched") else "not matched"
    print(f"[OK] inspected {root} frameworks={frameworks} target={target}")


if __name__ == "__main__":
    main()
