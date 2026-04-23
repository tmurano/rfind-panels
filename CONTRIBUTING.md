# Contributing a panel

Thank you for contributing a panel to `rfind-panels`. Follow these steps:

## 1. Check source data eligibility

Your panel's underlying data **must be publicly accessible**. Acceptable sources:

- ✅ GEO (Gene Expression Omnibus)
- ✅ ArrayExpress / ENA / SRA
- ✅ Published paper supplementary tables (Excel, CSV, PDF)
- ✅ Curated gene set databases (MSigDB, Reactome, GO, WikiPathways)
- ✅ DEG tables from published papers

Not acceptable:

- ❌ Synapse (account-gated)
- ❌ dbGaP / EGA (controlled access)
- ❌ Unpublished / preprint-only data without clear licensing
- ❌ Anything requiring registration, MTA, or request-based access

## 2. Prepare the panel files

Create directory `<organism>/<tissue>/<panel_id>/` with three files:

### `panel.yaml`
Metadata following [schema.yaml](./schema.yaml). Copy an existing panel as a template:

```bash
cp -r mouse/microglia/aging_hammond2019 mouse/<your_tissue>/<your_panel_id>
# then edit panel.yaml
```

Required fields:
- `id`: lowercase snake_case, unique across registry (typically `<condition>_<firstauthor><year>`)
- `organism`, `tissue`, `type` (deg | gene_set)
- `case_condition`, `control_condition` (null for gene_set)
- `source`: citation, doi, geo_accession
- `description`: 1-2 sentence summary
- `score_method`: log2fc | binary | signal_width | other
- `n_up`, `n_down`

### `up.tsv`
Tab-separated, header `gene<TAB>diff<TAB>rank`:
- `gene`: gene symbol in organism-native case (mouse = mixed case like "Apoe", human = ALL CAPS like "APOE")
- `diff`: numeric value (see `score_method`)
- `rank`: integer starting at 1, sorted by |diff| descending within UP

### `down.tsv`
Same format as `up.tsv`. Required for `type: deg`, absent for `type: gene_set`.

## 3. Panel quality guidelines

- **UP/DOWN length**: typically 50-1000 genes. Avoid extremes (< 20 or > 2000).
- **Gene symbols**: use current HGNC / MGI standard. No Ensembl IDs, no RefSeq.
- **Cross-species panels**: convert to target organism's case (e.g. MGI convention for mouse: `Tnf` not `TNF`).
- **Signal proxy for ChIP/CUT&Tag**: peak width works well when peak score is uninformative (`score_method: signal_width`).
- **Duplicate genes**: deduplicate before submission.

## 4. Submit a PR

```bash
git checkout -b add-panel-<your_panel_id>
git add <organism>/<tissue>/<panel_id>/
git commit -m "Add panel: <your_panel_id> (<one-line description>)"
git push origin add-panel-<your_panel_id>
```

Open a PR with title `Add panel: <panel_id>`. In the PR description, include:

- [ ] Source paper citation + DOI
- [ ] Link to supplementary data or GEO accession
- [ ] Brief description of how DEG / gene set was derived (e.g. "DESeq2 padj < 0.05 from GSE... case vs ctrl")
- [ ] Confirmation that source is publicly accessible without account

## 5. PR review

Maintainers will:

1. Verify source accessibility
2. Check `panel.yaml` schema compliance
3. Spot-check gene symbols (standard nomenclature)
4. Confirm UP/DOWN lengths are reasonable
5. Regenerate `registry.json` (maintainer task)

## Regenerating registry.json

Maintainer-only: after merging a panel, regenerate the index:

```bash
Rscript scripts/export_panels.R  # re-scans biosets.rds (if working from internal)
# OR
Rscript scripts/rebuild_registry.R  # (TODO: standalone scan of all panel.yaml)
```

## Questions

Open an issue on GitHub.
