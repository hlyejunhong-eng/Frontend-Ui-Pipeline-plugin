#!/usr/bin/env python3
"""Register Frontend UI Pipeline in the default personal Codex marketplace."""

from __future__ import annotations

import json
from pathlib import Path


PLUGIN_NAME = "frontend-ui-pipeline"
EXPECTED_PLUGIN_DIR = Path.home() / "plugins" / PLUGIN_NAME
MARKETPLACE_PATH = Path.home() / ".agents" / "plugins" / "marketplace.json"


def load_marketplace() -> dict:
    if not MARKETPLACE_PATH.exists():
        return {
            "name": "personal",
            "interface": {"displayName": "Personal"},
            "plugins": [],
        }
    with MARKETPLACE_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SystemExit(f"{MARKETPLACE_PATH} must contain a JSON object.")
    payload.setdefault("name", "personal")
    payload.setdefault("interface", {"displayName": "Personal"})
    payload.setdefault("plugins", [])
    if not isinstance(payload["plugins"], list):
        raise SystemExit(f"{MARKETPLACE_PATH} field 'plugins' must be an array.")
    return payload


def main() -> None:
    plugin_dir = Path(__file__).resolve().parents[1]
    if plugin_dir != EXPECTED_PLUGIN_DIR:
        raise SystemExit(
            "This installer expects the repository at "
            f"{EXPECTED_PLUGIN_DIR}.\n"
            "Run:\n"
            "  mkdir -p ~/plugins\n"
            "  git clone https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin.git "
            f"{EXPECTED_PLUGIN_DIR}"
        )

    manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing plugin manifest: {manifest_path}")

    payload = load_marketplace()
    entry = {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Design",
    }

    plugins = payload["plugins"]
    for index, existing in enumerate(plugins):
        if isinstance(existing, dict) and existing.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            break
    else:
        plugins.append(entry)

    MARKETPLACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MARKETPLACE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    marketplace_name = payload.get("name", "personal")
    print(f"Registered {PLUGIN_NAME} in {MARKETPLACE_PATH}")
    print("")
    print("Next steps:")
    print(f"  1. Run: codex plugin add {PLUGIN_NAME}@{marketplace_name}")
    print("  2. Open Codex Desktop or Codex CLI.")
    print("  3. Start a new Codex thread so the newly installed skills are loaded.")
    print("  4. Paste a screenshot, local project path, localhost URL, Figma link, or page description.")
    print("  5. Optional check: python3 scripts/diagnose_install.py")
    print("")
    print("If the three skills do not appear, close this thread and open another new Codex thread.")


if __name__ == "__main__":
    main()
