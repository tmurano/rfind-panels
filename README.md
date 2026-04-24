# rfind-panels

Community panel registry for **RFind-sc** (Running Fisher for single-cell).

Each "panel" is a curated gene list (UP + optionally DOWN) that defines an
axis for scRNA-seq gene-set scoring. This registry holds panels in a
standardized, machine-readable format so they can be shared, scored,
and plugged into the [`RFindsc`](https://github.com/tmurano/RFindsc) R
package.

## Three ways to use this registry

### 1. Browse and try panels in the browser

[**tmurano.github.io/rfind-panels**](https://tmurano.github.io/rfind-panels/)
is a static catalog of every panel in the registry. Pick any panel and
click **Try on Hammond** to score it against 5,998 Hammond 2019 mouse
microglia cells directly in your browser (bidirectional Running Fisher,
~5 s, no install). You get a score histogram, a tSNE colored by score,
and a per-group violin without writing a line of code.

### 2. Submit your own panel (web form, no git)

Click **+ Contribute a panel** at the top of the catalog page. Drop a DEG
CSV/TSV (Symbol + log2FC), fill in a short metadata form, paste a GitHub
Personal Access Token, and the page will fork this repo on your account,
commit the three files, and open a pull request for you. CI validates
the schema and posts a comment with the result. See
[CONTRIBUTING.md](./CONTRIBUTING.md) for the step-by-step walkthrough.

### 3. Load panels from R

```r
# RFindsc (https://github.com/tmurano/RFindsc) is the scoring engine
install.packages("remotes")
remotes::install_github("tmurano/RFindsc")

# Install a panel by its registry path
biosets <- RFindsc::install_panel("mouse/microglia/aging_hammond2019")

# Install multiple at once
biosets <- RFindsc::install_panels(c(
  "mouse/microglia/aging_hammond2019",
  "mouse/microglia/lpc_hammond2019",
  "mouse/microglia/dam_kerenshaul2017"
))

# Score a counts matrix (or a Seurat object)
scores <- RFindsc::run_pipeline(counts, biosets)
```

Or read a panel directly from the raw GitHub URL without any package:

```r
read_panel <- function(path) {
  base <- file.path("https://raw.githubusercontent.com/tmurano/rfind-panels/main", path)
  up <- read.delim(file.path(base, "up.tsv"))
  down_path <- file.path(base, "down.tsv")
  down <- tryCatch(read.delim(down_path), error = function(e) NULL)
  list(up = up, down = down)
}
aging <- read_panel("mouse/microglia/aging_hammond2019")
```

## Directory layout

```
<organism>/<tissue>/<panel_id>/
  ├── panel.yaml   # metadata (see schema.yaml)
  ├── up.tsv       # UP genes (gene/diff/rank)
  └── down.tsv     # DOWN genes (same format, absent for type=gene_set)
```

Index of all panels: [registry.json](./registry.json)
Schema spec: [schema.yaml](./schema.yaml)

## Currently available panels

| Panel ID | Organism | Tissue | Type | UP | DOWN | Source |
|---|---|---|---|---|---|---|
| aging_hammond2019 | mouse | microglia | deg | 1000 | 1000 | Hammond 2019 Immunity |
| lpc_hammond2019 | mouse | microglia | deg | 1000 | 1000 | Hammond 2019 Immunity |
| development_hammond2019 | mouse | microglia | deg | 1000 | 1000 | Hammond 2019 Immunity |
| dam_kerenshaul2017 | mouse | microglia | deg | 1000 | 1000 | Keren-Shaul 2017 Cell |
| ldam_marschallinger2020 | mouse | microglia | deg | 377 | 319 | Marschallinger 2020 Nat Neurosci |
| aging_marschallinger2020 | mouse | microglia | deg | 50 | 49 | Marschallinger 2020 (curated from Holtman 2015) |
| ad_marschallinger2020 | mouse | microglia | deg | 75 | 54 | Marschallinger 2020 (curated from Wang 2015) |
| h3k27ac_gosselin2017 | mouse | microglia | gene_set | 1000 | 0 | Gosselin 2017 Science (ChIP) |
| h3k4me2_gosselin2017 | mouse | microglia | gene_set | 1000 | 0 | Gosselin 2017 Science (ChIP) |
| h3k4me1_wendeln2018 | mouse | microglia | gene_set | 779 | 0 | Wendeln 2018 Nature (ChIP, HOMER) |

## Panel type

- **deg**: Differentially-expressed gene signature, bidirectional (UP + DOWN), Running Fisher 4-term
- **gene_set**: Single-condition gene set, UP-only (DOWN empty), Running Fisher 2-term reduction

## Contributing a panel

We welcome panels for any organism, tissue, or biological condition.
The **fastest path is the web form** at
[tmurano.github.io/rfind-panels](https://tmurano.github.io/rfind-panels/)
— drop a CSV, fill a form, paste a PAT, and a PR is opened for you.
See [CONTRIBUTING.md](./CONTRIBUTING.md) for the walkthrough and the
manual git-based alternative.

Key rules (enforced by CI via `scripts/validate_panel.py`):

- **Source must be publicly accessible** (GEO / ArrayExpress /
  supplementary tables). No Synapse / dbGaP / EGA / account-gated data.
- Directory layout **must match** `<organism>/<tissue>/<id>/` and agree
  with the `organism` / `tissue` / `id` inside `panel.yaml`.
- `up.tsv` (and `down.tsv` for `type: deg`) header is literally
  `gene\tdiff\trank`.
- `n_up` / `n_down` in `panel.yaml` must equal the TSV row counts.
- Each gene list must have **20 ≤ N ≤ 5,000** rows.
- `id` must be unique across the registry (not already present in
  `registry.json`).

CI posts a PR comment listing any violations; turns red until resolved.
A maintainer reviews scientific quality before merging. On merge,
`registry.json` is auto-rebuilt and the catalog page updates on the
next Pages deploy.

## License

Panel metadata and curation scripts: [MIT](./LICENSE).
Individual gene lists retain the copyright/license of their original source (cited in `panel.yaml`).

## Citation

If you use panels from this registry in a publication, please cite:

1. The original source paper (listed in each panel's `panel.yaml`).
2. The RFind-sc methods paper (manuscript in preparation, 2026).
