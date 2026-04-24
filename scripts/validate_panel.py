#!/usr/bin/env python3
"""Validate one or more panel directories against the rfind-panels schema.

Usage:
  python3 scripts/validate_panel.py <panel_dir> [<panel_dir> ...]

Exit code 0 = all valid, 1 = at least one invalid. A markdown summary is
printed to stdout for use in PR comments.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "registry.json"

REQUIRED_FIELDS = [
    "id", "name", "organism", "tissue", "type",
    "case_condition", "control_condition",
    "source", "description", "score_method",
    "n_up", "n_down", "files", "contributor", "created",
]
ORGANISM_ENUM = {"mouse", "human", "rat", "zebrafish", "other"}
TYPE_ENUM = {"deg", "gene_set"}
SCORE_METHOD_ENUM = {"log2fc", "binary", "signal_width", "other"}
MIN_GENES = 20
MAX_GENES = 5000
ID_RE = re.compile(r"^[a-z0-9_]+$")


def _existing_ids() -> set[str]:
    if not REGISTRY_PATH.exists():
        return set()
    data = json.loads(REGISTRY_PATH.read_text())
    return {p["id"] for p in data.get("panels", [])}


def _read_tsv(path: Path) -> tuple[list[dict], list[str]]:
    errs: list[str] = []
    rows: list[dict] = []
    if not path.exists():
        errs.append(f"{path.relative_to(ROOT)}: missing file")
        return rows, errs
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    if not lines:
        errs.append(f"{path.relative_to(ROOT)}: empty file")
        return rows, errs
    header = lines[0].split("\t")
    if header[:3] != ["gene", "diff", "rank"]:
        errs.append(
            f"{path.relative_to(ROOT)}: header must be 'gene\\tdiff\\trank', got {header!r}"
        )
        return rows, errs
    for i, line in enumerate(lines[1:], start=2):
        parts = line.split("\t")
        if len(parts) < 3:
            errs.append(f"{path.relative_to(ROOT)}:{i}: expected 3 columns, got {len(parts)}")
            continue
        try:
            diff = float(parts[1])
            rank = int(parts[2])
        except ValueError:
            errs.append(f"{path.relative_to(ROOT)}:{i}: non-numeric diff/rank")
            continue
        rows.append({"gene": parts[0], "diff": diff, "rank": rank})
    return rows, errs


def _check_gene_casing(genes: list[str], declared_organism: str) -> list[str]:
    if not genes or declared_organism not in {"mouse", "human"}:
        return []
    all_caps = sum(1 for g in genes if g == g.upper() and any(c.isalpha() for c in g))
    frac = all_caps / len(genes)
    warns: list[str] = []
    if declared_organism == "mouse" and frac > 0.5:
        warns.append(
            f"{frac*100:.0f}% of gene symbols are ALL CAPS but organism=mouse "
            f"(expected mixed case)"
        )
    if declared_organism == "human" and frac < 0.5:
        warns.append(
            f"only {frac*100:.0f}% of gene symbols are ALL CAPS but organism=human "
            f"(expected ALL CAPS)"
        )
    return warns


def validate_panel(panel_dir: Path, existing_ids: set[str]) -> tuple[list[str], list[str]]:
    errs: list[str] = []
    warns: list[str] = []
    rel = panel_dir.relative_to(ROOT)

    yaml_path = panel_dir / "panel.yaml"
    if not yaml_path.exists():
        errs.append(f"{rel}: panel.yaml missing")
        return errs, warns

    try:
        meta = yaml.safe_load(yaml_path.read_text())
    except yaml.YAMLError as e:
        errs.append(f"{rel}/panel.yaml: YAML parse error: {e}")
        return errs, warns
    if not isinstance(meta, dict):
        errs.append(f"{rel}/panel.yaml: top level must be a mapping")
        return errs, warns

    for fld in REQUIRED_FIELDS:
        if fld not in meta:
            errs.append(f"{rel}/panel.yaml: missing required field `{fld}`")

    pid = meta.get("id", "")
    if not ID_RE.match(str(pid)):
        errs.append(f"{rel}/panel.yaml: id {pid!r} must match ^[a-z0-9_]+$")
    if pid in existing_ids:
        errs.append(f"{rel}/panel.yaml: id {pid!r} already exists in registry.json")

    path_parts = rel.parts
    if len(path_parts) == 3:
        exp_org, exp_tissue, exp_id = path_parts
        if meta.get("organism") != exp_org:
            errs.append(
                f"{rel}/panel.yaml: organism={meta.get('organism')!r} but path says {exp_org!r}"
            )
        if meta.get("tissue") != exp_tissue:
            errs.append(
                f"{rel}/panel.yaml: tissue={meta.get('tissue')!r} but path says {exp_tissue!r}"
            )
        if pid != exp_id:
            errs.append(f"{rel}/panel.yaml: id={pid!r} but path says {exp_id!r}")
    else:
        errs.append(
            f"{rel}: path must be <organism>/<tissue>/<id>/ (got {len(path_parts)} parts)"
        )

    if meta.get("organism") not in ORGANISM_ENUM:
        errs.append(f"{rel}/panel.yaml: organism must be one of {sorted(ORGANISM_ENUM)}")
    if meta.get("type") not in TYPE_ENUM:
        errs.append(f"{rel}/panel.yaml: type must be one of {sorted(TYPE_ENUM)}")
    if meta.get("score_method") not in SCORE_METHOD_ENUM:
        errs.append(f"{rel}/panel.yaml: score_method must be one of {sorted(SCORE_METHOD_ENUM)}")

    src = meta.get("source")
    if not isinstance(src, dict) or not src.get("citation"):
        errs.append(f"{rel}/panel.yaml: source.citation is required")

    up_rows, e1 = _read_tsv(panel_dir / "up.tsv")
    errs.extend(e1)
    if up_rows:
        if len(up_rows) < MIN_GENES:
            errs.append(f"{rel}/up.tsv: {len(up_rows)} genes < {MIN_GENES}")
        if len(up_rows) > MAX_GENES:
            errs.append(f"{rel}/up.tsv: {len(up_rows)} genes > {MAX_GENES}")
        if meta.get("n_up") != len(up_rows):
            errs.append(f"{rel}: n_up={meta.get('n_up')} but up.tsv has {len(up_rows)} rows")

    if meta.get("type") == "deg":
        dn_rows, e2 = _read_tsv(panel_dir / "down.tsv")
        errs.extend(e2)
        if dn_rows:
            if len(dn_rows) < MIN_GENES:
                errs.append(f"{rel}/down.tsv: {len(dn_rows)} genes < {MIN_GENES}")
            if len(dn_rows) > MAX_GENES:
                errs.append(f"{rel}/down.tsv: {len(dn_rows)} genes > {MAX_GENES}")
            if meta.get("n_down") != len(dn_rows):
                errs.append(
                    f"{rel}: n_down={meta.get('n_down')} but down.tsv has {len(dn_rows)} rows"
                )
    else:
        if (panel_dir / "down.tsv").exists():
            warns.append(f"{rel}: type=gene_set but down.tsv exists (will be ignored)")

    all_genes = [r["gene"] for r in up_rows]
    if meta.get("type") == "deg" and up_rows and (panel_dir / "down.tsv").exists():
        dn_rows_only, _ = _read_tsv(panel_dir / "down.tsv")
        all_genes.extend(r["gene"] for r in dn_rows_only)
    warns.extend(_check_gene_casing(all_genes, meta.get("organism", "")))

    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("panels", nargs="+", help="panel directories to validate")
    ap.add_argument("--md", action="store_true", help="emit markdown summary")
    args = ap.parse_args()

    existing = _existing_ids()

    print("# Panel validation\n")
    n_ok = n_bad = 0
    for p_str in args.panels:
        p = Path(p_str).resolve()
        errs, warns = validate_panel(p, existing)
        status = "FAIL" if errs else ("WARN" if warns else "OK")
        emoji = {"FAIL": "❌", "WARN": "⚠️", "OK": "✅"}[status]
        print(f"## {emoji} `{p.relative_to(ROOT)}` — **{status}**")
        if errs:
            print("\n**Errors**:")
            for e in errs:
                print(f"- {e}")
        if warns:
            print("\n**Warnings**:")
            for w in warns:
                print(f"- {w}")
        if not errs and not warns:
            print("\nAll checks passed.")
        print()
        if errs:
            n_bad += 1
        else:
            n_ok += 1

    print(f"---\n**Summary**: {n_ok} panel(s) passed, {n_bad} failed.")
    sys.exit(0 if n_bad == 0 else 1)


if __name__ == "__main__":
    main()
