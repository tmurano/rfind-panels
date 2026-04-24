#!/usr/bin/env python3
"""Rebuild registry.json by walking all panel.yaml files in the repo.

Usage:
  python3 scripts/rebuild_registry.py

Writes registry.json at the repo root. Intended to run on merge to main so
the static catalog (tmurano.github.io/rfind-panels/) always reflects
whatever is in the tree.
"""
import datetime as dt
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "registry.json"

SORT_KEY = ("organism", "tissue", "id")


def main() -> None:
    panels = []
    for yml in sorted(ROOT.rglob("panel.yaml")):
        rel = yml.relative_to(ROOT)
        try:
            meta = yaml.safe_load(yml.read_text()) or {}
        except yaml.YAMLError as e:
            print(f"skip {rel}: YAML error: {e}")
            continue
        if not isinstance(meta, dict) or "id" not in meta:
            print(f"skip {rel}: missing id")
            continue

        panels.append({
            "id": meta["id"],
            "organism": meta.get("organism"),
            "tissue": meta.get("tissue"),
            "type": meta.get("type"),
            "n_up": meta.get("n_up", 0),
            "n_down": meta.get("n_down", 0),
            "citation": (meta.get("source") or {}).get("citation", ""),
            "path": str(rel.parent),
        })

    panels.sort(key=lambda p: tuple(p.get(k) or "" for k in SORT_KEY))

    data = {
        "schema_version": "0.1",
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "n_panels": len(panels),
        "panels": panels,
    }

    OUT.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(panels)} panel(s)")


if __name__ == "__main__":
    main()
