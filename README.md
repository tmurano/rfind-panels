# rfind-panels

Community panel registry for **RFind-sc** (Running Fisher for individuals, single-cell version).

Each "panel" is a curated gene list (UP and optionally DOWN) that defines an axis for scRNA-seq gene-set scoring. This registry holds panels in a standardized, machine-readable format so they can be easily shared, reused, and installed into the `RFindsc` R package (coming soon).

## Quick usage (once RFindsc R package is released)

```r
# Install a panel by path
biosets <- RFindsc::install_panel("mouse/microglia/aging_hammond2019")

# Install multiple
biosets <- RFindsc::install_panels(c(
  "mouse/microglia/aging_hammond2019",
  "mouse/microglia/lpc_hammond2019",
  "mouse/microglia/dam_kerenshaul2017"
))

# Score a Seurat object
scores <- RFindsc::run_pipeline(seurat, biosets)
```

Until then, panels can be loaded directly:

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

We welcome panels for any organism, tissue, or biological condition. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the submission checklist and PR workflow.

Key rules:
- **Source must be publicly accessible** (GEO / ArrayExpress / supplementary tables). No Synapse / dbGaP / EGA / account-gated data.
- Follow the directory layout and `panel.yaml` schema ([schema.yaml](./schema.yaml)).
- One panel per PR for easy review.

## License

Panel metadata and curation scripts: [MIT](./LICENSE).
Individual gene lists retain the copyright/license of their original source (cited in `panel.yaml`).

## Citation

If you use panels from this registry in a publication, please cite:

1. The original source paper (listed in each panel's `panel.yaml`).
2. The RFind-sc methods paper (manuscript in preparation, 2026).
