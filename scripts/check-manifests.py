#!/usr/bin/env python3
"""Check that the marketplace manifest and every plugin manifest agree.

Dependency-free on purpose so it runs anywhere (CI included) without auth.
`claude plugin validate . --strict` is the richer check — run that locally too;
this script is the part that can be enforced unattended.

Exit: 0 clean, 1 problems found.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = ROOT / "plugins"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+].+)?$")

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        fail(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def main() -> int:
    market = load(MARKETPLACE)
    if market is None:
        return report()

    for field in ("name", "description", "owner"):
        if not market.get(field):
            fail(f"marketplace.json: missing '{field}'")

    entries = market.get("plugins")
    if not isinstance(entries, list):
        fail("marketplace.json: 'plugins' must be a list")
        return report()

    seen: set[str] = set()
    listed: set[str] = set()

    for i, entry in enumerate(entries):
        where = f"marketplace.json plugins[{i}]"
        name = entry.get("name")
        if not name:
            fail(f"{where}: missing 'name'")
            continue
        if name in seen:
            fail(f"{where}: duplicate plugin name '{name}'")
        seen.add(name)

        if not entry.get("description"):
            fail(f"{where} ({name}): missing 'description'")

        version = entry.get("version")
        if not version:
            fail(f"{where} ({name}): missing 'version'")
        elif not SEMVER.match(str(version)):
            fail(f"{where} ({name}): version '{version}' is not semver")

        source = entry.get("source")
        if not source:
            fail(f"{where} ({name}): missing 'source'")
            continue
        if not isinstance(source, str) or not source.startswith("./plugins/"):
            fail(f"{where} ({name}): source should be './plugins/<dir>', got {source!r}")
            continue

        plugin_dir = (ROOT / source).resolve()
        listed.add(plugin_dir.name)
        if not plugin_dir.is_dir():
            fail(f"{where} ({name}): source directory does not exist: {source}")
            continue
        if plugin_dir.name != name:
            fail(f"{where}: plugin name '{name}' does not match directory '{plugin_dir.name}'")

        manifest = load(plugin_dir / ".claude-plugin" / "plugin.json")
        if manifest is None:
            continue
        rel = f"plugins/{plugin_dir.name}/.claude-plugin/plugin.json"
        if manifest.get("name") != name:
            fail(f"{rel}: name '{manifest.get('name')}' != marketplace entry '{name}'")
        if not manifest.get("description"):
            fail(f"{rel}: missing 'description'")
        if not manifest.get("version"):
            fail(f"{rel}: missing 'version' (keep it in sync with the marketplace entry)")
        elif version and str(manifest["version"]) != str(version):
            fail(f"{rel}: version '{manifest['version']}' != marketplace entry '{version}'")

        if not (plugin_dir / "README.md").is_file():
            fail(f"plugins/{plugin_dir.name}: missing README.md")

        components = ["skills", "commands", "hooks", "agents"]
        if not any((plugin_dir / c).exists() for c in components):
            fail(
                f"plugins/{plugin_dir.name}: no {'/'.join(components)} directory "
                "— plugin ships nothing"
            )

    if PLUGINS_DIR.is_dir():
        for child in sorted(PLUGINS_DIR.iterdir()):
            if child.is_dir() and child.name not in listed:
                fail(f"plugins/{child.name}: directory exists but is not listed in marketplace.json")

    return report()


def report() -> int:
    if problems:
        print(f"\033[31m✘ {len(problems)} manifest problem(s)\033[0m")
        for p in problems:
            print(f"    {p}")
        return 1
    print("\033[32m✔ manifests consistent\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
