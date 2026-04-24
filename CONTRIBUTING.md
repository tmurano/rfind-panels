# Contributing a panel

Thank you for contributing a panel to `rfind-panels`. Follow these steps:

> **TL;DR — panels should be DEG-derived (Type A) whenever possible.**
> A panel is a pair of gene lists (UP / DOWN) from a **case-vs-control** contrast.
> This structure is what enables RFind-sc's bidirectional (four-term Running Fisher)
> scoring and makes the output score **signed** — positive = case-like, negative
> = control-like. Directionless gene sets (pathways, markers, ChIP peaks) are
> still welcome as **Type B** (UP-only) but lose the bidirectional advantage
> and become functionally equivalent to AUCell / UCell on that panel.
>
> **Quick decision**:
> - Have `log2FC` + direction from a DEG analysis? → **Type A** (recommended)
> - Just a gene list with no case/control meaning? → **Type B**
> - Forcing a directionless list into Type A with empty `down.tsv`? → **don't**; use Type B explicitly

---

## Fast path — submit from the browser (recommended)

The static site at **[tmurano.github.io/rfind-panels](https://tmurano.github.io/rfind-panels/)**
can build `panel.yaml` + `up.tsv` (+ `down.tsv`) from a raw DEG table, fork this
repo under your account, create a branch, commit the three files, and open a
pull request — all from a single form. No git or R required.

### What you need

1. **A DEG CSV/TSV** with at least two columns:
   - `Symbol` (or `gene`, `gene_symbol`)
   - `log2FC` (or `fold change`, `fc`, `logfc`, `diff`)
2. **A GitHub Personal Access Token (PAT)** with the `public_repo` scope.
   Create one at
   [github.com/settings/tokens/new?scopes=public_repo&description=rfind-panels%20submission](https://github.com/settings/tokens/new?scopes=public_repo&description=rfind-panels%20submission)
   (the scope is pre-filled via the link). The token stays in your browser's
   `localStorage` and is sent only to `api.github.com`.

### Steps

1. Open [tmurano.github.io/rfind-panels](https://tmurano.github.io/rfind-panels/)
   and click **+ Contribute a panel**.
2. **Drop your CSV/TSV** onto the upload area. The form previews how many
   UP/DOWN genes survived parsing (capped at 1,000 per direction, sorted by
   `|log2FC|`) and auto-fills `organism` (from gene-symbol casing) and `type`
   (from presence of DOWN genes).
3. **Fill in the metadata** — `id` (lowercase snake_case), `name`, `tissue`
   (e.g. `microglia`, `t_cell`), `case_condition`, `control_condition`,
   `citation`, `DOI`, `description`.
4. **Paste your PAT** and click **Submit pull request**. The page:
   - forks `tmurano/rfind-panels` to your account (if not already forked)
   - creates branch `submit/<id>-<timestamp>`
   - commits `panel.yaml`, `up.tsv`, and `down.tsv` (for `deg`)
   - opens a PR against `tmurano/rfind-panels:main` with your metadata summary
5. The **CI validator** (`.github/workflows/validate-panel.yml`) runs
   automatically and posts a comment on your PR with the schema check
   result. Fix any errors by pushing new commits to the same branch
   (or re-submitting from the browser — a new timestamped branch will
   open a fresh PR).
6. Once merged, `registry.json` is auto-rebuilt and your panel appears in
   the catalog on the next Pages deploy.

### What CI checks (see `scripts/validate_panel.py`)

- `panel.yaml` parses and contains every required field from `schema.yaml`
- `id` matches `^[a-z0-9_]+$` and is **not** already present in `registry.json`
- Directory layout matches `<organism>/<tissue>/<id>/` and agrees with the
  `organism` / `tissue` / `id` declared in `panel.yaml`
- `up.tsv` (and `down.tsv` for `deg`) header is literally `gene\tdiff\trank`
- `n_up` / `n_down` in panel.yaml match the TSV row count
- Each gene list has **20 ≤ N ≤ 5,000** rows
- Gene-symbol casing is consistent with declared organism
  (mouse = mixed case, human = ALL CAPS) — warning only

If any check fails, the PR gets a comment listing the specific issues and
the workflow turns red. Passing all checks does not auto-merge; a maintainer
still reviews scientific quality.

---

## Manual path — submit via git

Prefer git/R over the web form? Follow sections 1–5 below.

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

## 1b. Choose panel type (Type A or Type B)

`rfind-panels` accepts two panel types. Both are valid contributions; choose based on your source data:

### Type A — `type: deg` (case-vs-control DEG, **recommended**)

- Source: differential expression between two conditions (case vs control, treatment vs untreated, disease vs healthy, etc.)
- Structure: paired UP gene list (genes higher in case) + DOWN gene list (genes lower in case)
- Score interpretation in RFind-sc: **signed** — positive score = case-like cell, negative = control-like
- **Why preferred**: enables RFind-sc's bidirectional advantage (UP+DOWN four-term Running Fisher); the score sign carries biological direction; multi-axis composition (LDA, scatter) becomes interpretable
- Examples: aging signature (old vs young), drug response (treated vs vehicle), disease state (AD vs control)

### Type B — `type: gene_set` (single-direction marker / pathway list)

- Source: marker gene list, pathway gene set, ChIP-seq peak-associated genes, GO term, etc. — anything that doesn't have a natural case-vs-control direction
- Structure: only `up.tsv` (no `down.tsv`)
- Score interpretation in RFind-sc: **non-negative** — high score = cells highly expressing the gene set
- **When to use**: when your gene list is directionless (Hallmark pathways, cell-type markers, ChIP-seq peaks). RFind-sc with Type B panels is functionally similar to AUCell/UCell on that panel — bidirectional advantage is not available, but inclusion in the registry remains valuable for cross-panel composition and standardized scoring.
- Examples: MSigDB Hallmark pathway, microglia-specific marker set, H3K27ac peak-associated genes

### Recommendation
- If your data **has a case-vs-control structure** (most published DEG analyses): contribute as **Type A** to enable RFind-sc's bidirectional advantage
- If your data **is a directionless marker/pathway list**: contribute as **Type B** — still welcome, with explicit `type: gene_set` in `panel.yaml`
- Avoid the antipattern of forcing a directionless gene list into Type A by leaving `down.tsv` empty — declare it as Type B explicitly

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
Same format as `up.tsv`. **Required for `type: deg`** (Type A), **absent for `type: gene_set`** (Type B).

## 3. Panel quality guidelines

- **UP/DOWN length**: typically 50-1000 genes. Avoid extremes (< 20 or > 2000).
- **Gene symbols**: use current HGNC / MGI standard. No Ensembl IDs, no RefSeq.
- **Cross-species panels**: convert to target organism's case (e.g. MGI convention for mouse: `Tnf` not `TNF`).
- **Signal proxy for ChIP/CUT&Tag**: peak width works well when peak score is uninformative (`score_method: signal_width`).
- **Duplicate genes**: deduplicate before submission.

## 3b. Building a Type A panel from your DEG table (RFindsc R pkg)

The companion R package [RFindsc](https://github.com/tmurano/RFindsc) provides
`build_panel_from_deg()` which turns a DEG data frame into a registry-ready
panel:

```r
# install.packages("devtools")
devtools::install_github("tmurano/RFindsc")
library(RFindsc)

deg <- read.csv("my_deg.csv")   # cols: gene, log2FC, padj
p <- build_panel_from_deg(
  deg,
  gene_col    = "gene",
  log2fc_col  = "log2FC",
  padj_col    = "padj",
  padj_thresh = 0.05,
  top_n       = 1000,
  label       = "my_condition"
)

# Write out up.tsv / down.tsv in registry format
write.table(p$up,   "up.tsv",   sep = "\t", quote = FALSE, row.names = FALSE)
write.table(p$down, "down.tsv", sep = "\t", quote = FALSE, row.names = FALSE)
```

Fill `panel.yaml` manually (source, case/control conditions, etc.) and submit.
Self-check by scoring your panel against the bundled Hammond demo before
submitting:

```r
mg <- readRDS("seurat_mg_small.rds")   # or any small Seurat you have
out <- run_pipeline(mg, biosets = list(my_condition = p))
# Should produce a signed score matrix; positive = case-aligned cells
summary(out$scores[, "my_condition"])
```

If scores are all clipped to the `+/- 300` bound or uniformly near zero,
investigate your DEG filter (padj threshold, log2FC magnitude, duplicate genes).

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
