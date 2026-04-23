# export_panels.R
# ----------------------------------------------------------------------------
# biosets.rds + (axis meta) → panel registry format の自動変換 script
#
# Input : ~/Miyakawa Lab Dropbox/Murano Tomoyuki/RFind-sc_260423/processed/biosets.rds
# Output: ./mouse/microglia/<panel_id>/{panel.yaml, up.tsv, (down.tsv)}
#         ./registry.json (全 panel の index)
# ----------------------------------------------------------------------------

BIOSETS_RDS <- "~/Miyakawa Lab Dropbox/Murano Tomoyuki/RFind-sc_260423/processed/biosets.rds"
REGISTRY_ROOT <- "~/Desktop/rfind-panels"

# -- Panel 命名 / メタデータ map ------------------------------------------------
# key = biosets.rds 上の panel 名 ("Aging" 等)
# value = registry 上の metadata (path, yaml 用)
PANEL_DEFS <- list(
  Aging = list(
    id = "aging_hammond2019", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "P540 (aged)",
    control_condition = "P100_brain (adult)",
    citation = "Hammond et al. 2019 Immunity 50(1):253-271.e6",
    doi = "10.1016/j.immuni.2018.11.004",
    geo_accession = "GSE121654",
    description = "Aging signature (aged P540 vs adult P100) from mouse microglia scRNA-seq.",
    score_method = "log2fc"
  ),
  LPC = list(
    id = "lpc_hammond2019", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "P100_LPC (demyelination)",
    control_condition = "P100_saline",
    citation = "Hammond et al. 2019 Immunity 50(1):253-271.e6",
    doi = "10.1016/j.immuni.2018.11.004", geo_accession = "GSE121654",
    description = "LPC-induced demyelination response signature (P100 LPC vs saline) from mouse microglia.",
    score_method = "log2fc"
  ),
  Development = list(
    id = "development_hammond2019", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "E14.5 (embryonic)",
    control_condition = "P100_brain (adult)",
    citation = "Hammond et al. 2019 Immunity 50(1):253-271.e6",
    doi = "10.1016/j.immuni.2018.11.004", geo_accession = "GSE121654",
    description = "Developmental signature (E14.5 embryonic vs P100 adult) from mouse microglia.",
    score_method = "log2fc"
  ),
  KS_DAM = list(
    id = "dam_kerenshaul2017", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "5xFAD (AD model)",
    control_condition = "WT",
    citation = "Keren-Shaul et al. 2017 Cell 169(7):1276-1290.e17",
    doi = "10.1016/j.cell.2017.05.018", geo_accession = "GSE98969",
    description = "Disease-Associated Microglia (DAM) signature from 5xFAD AD model (Supplementary Table mmc3).",
    score_method = "log2fc"
  ),
  LDAM = list(
    id = "ldam_marschallinger2020", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "BODIPY-high (lipid-accumulating)",
    control_condition = "BODIPY-low",
    citation = "Marschallinger et al. 2020 Nat Neurosci 23(2):194-208",
    doi = "10.1038/s41593-019-0566-1",
    geo_accession = NULL,
    description = "Lipid Droplet-Accumulating Microglia (LDAM) signature from BODIPY-sorted aged mouse microglia (Suppl Table 2, sheet T2-1).",
    score_method = "log2fc"
  ),
  Aging_Marsch = list(
    id = "aging_marschallinger2020", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "aged",
    control_condition = "young",
    citation = "Marschallinger et al. 2020 Nat Neurosci 23(2):194-208 (curated from Holtman 2015)",
    doi = "10.1038/s41593-019-0566-1",
    geo_accession = NULL,
    description = "Curated aging signature from Marschallinger 2020 Suppl Table 12, originally from Holtman et al. 2015 (binary UP/DOWN).",
    score_method = "binary"
  ),
  AD_Marsch = list(
    id = "ad_marschallinger2020", organism = "mouse", tissue = "microglia",
    type = "deg", case_condition = "AD (5xFAD/APP)",
    control_condition = "WT",
    citation = "Marschallinger et al. 2020 Nat Neurosci 23(2):194-208 (curated from Wang 2015)",
    doi = "10.1038/s41593-019-0566-1",
    geo_accession = NULL,
    description = "Curated AD signature from Marschallinger 2020 Suppl Table 12, originally from Wang et al. 2015 (binary UP/DOWN).",
    score_method = "binary"
  ),
  H3K27ac = list(
    id = "h3k27ac_gosselin2017", organism = "mouse", tissue = "microglia",
    type = "gene_set", case_condition = "H3K27ac enrichment",
    control_condition = NULL,
    citation = "Gosselin et al. 2017 Science 356(6344):eaal3222",
    doi = "10.1126/science.aal3222", geo_accession = "GSE89960",
    description = "Active enhancer mark (H3K27ac) ChIP-seq peak-annotated gene list from ex vivo mouse microglia; signal = peak width.",
    score_method = "signal_width"
  ),
  H3K4me2 = list(
    id = "h3k4me2_gosselin2017", organism = "mouse", tissue = "microglia",
    type = "gene_set", case_condition = "H3K4me2 enrichment",
    control_condition = NULL,
    citation = "Gosselin et al. 2017 Science 356(6344):eaal3222",
    doi = "10.1126/science.aal3222", geo_accession = "GSE89960",
    description = "Active chromatin mark (H3K4me2) ChIP-seq peak-annotated gene list from ex vivo mouse microglia; signal = peak width (no_intergenic filter).",
    score_method = "signal_width"
  ),
  H3K4me1 = list(
    id = "h3k4me1_wendeln2018", organism = "mouse", tissue = "microglia",
    type = "gene_set", case_condition = "H3K4me1 primed enhancer",
    control_condition = NULL,
    citation = "Wendeln et al. 2018 Nature 556(7701):332-338",
    doi = "10.1038/s41586-018-0023-4", geo_accession = NULL,
    description = "Primed enhancer mark (H3K4me1) gene list from AD-LPS primed enhancers (Suppl MOESM3, HOMER xlsx) — APP_4xLPS vs APP_PBS.",
    score_method = "signal_width"
  )
)

# -- YAML writer (no dependency) ----------------------------------------------
yaml_scalar <- function(v) {
  if (is.null(v) || (is.character(v) && length(v) == 0)) return("null")
  if (is.logical(v)) return(tolower(as.character(v)))
  if (is.numeric(v)) return(as.character(v))
  # String: always quote to be safe with special chars
  escaped <- gsub("\"", "\\\\\"", as.character(v))
  sprintf("\"%s\"", escaped)
}

write_panel_yaml <- function(path, meta, n_up, n_down, contributor = "tmurano") {
  lines <- c(
    sprintf("id: %s",   yaml_scalar(meta$id)),
    sprintf("name: %s", yaml_scalar(meta$id)),
    sprintf("organism: %s", yaml_scalar(meta$organism)),
    sprintf("tissue: %s",   yaml_scalar(meta$tissue)),
    sprintf("type: %s",     yaml_scalar(meta$type)),
    sprintf("case_condition: %s",    yaml_scalar(meta$case_condition)),
    sprintf("control_condition: %s", yaml_scalar(meta$control_condition)),
    "source:",
    sprintf("  citation: %s",      yaml_scalar(meta$citation)),
    sprintf("  doi: %s",           yaml_scalar(meta$doi)),
    sprintf("  geo_accession: %s", yaml_scalar(meta$geo_accession)),
    sprintf("description: %s", yaml_scalar(meta$description)),
    sprintf("score_method: %s", yaml_scalar(meta$score_method)),
    sprintf("n_up: %d",   n_up),
    sprintf("n_down: %d", n_down),
    "files:",
    sprintf("  up: %s", "up.tsv"),
    if (n_down > 0) sprintf("  down: %s", "down.tsv") else "  down: null",
    sprintf("contributor: %s", yaml_scalar(contributor)),
    sprintf("created: %s", yaml_scalar(format(Sys.Date())))
  )
  writeLines(lines, path)
}

# -- Main ---------------------------------------------------------------------
b <- readRDS(BIOSETS_RDS)
registry <- list()

for (orig_name in setdiff(names(b), "meta")) {
  if (!orig_name %in% names(PANEL_DEFS)) {
    cat(sprintf("  [skip] %s (no PANEL_DEFS entry)\n", orig_name))
    next
  }
  def <- PANEL_DEFS[[orig_name]]
  panel_dir <- file.path(REGISTRY_ROOT, def$organism, def$tissue, def$id)
  dir.create(panel_dir, recursive = TRUE, showWarnings = FALSE)

  up_df  <- b[[orig_name]]$up
  dn_df  <- b[[orig_name]]$down
  n_up   <- nrow(up_df)
  n_down <- if (is.null(dn_df)) 0L else nrow(dn_df)

  write.table(up_df, file.path(panel_dir, "up.tsv"),
              sep = "\t", quote = FALSE, row.names = FALSE)
  if (n_down > 0) {
    write.table(dn_df, file.path(panel_dir, "down.tsv"),
                sep = "\t", quote = FALSE, row.names = FALSE)
  }
  write_panel_yaml(file.path(panel_dir, "panel.yaml"), def, n_up, n_down)

  registry[[def$id]] <- list(
    id = def$id, organism = def$organism, tissue = def$tissue,
    type = def$type, n_up = n_up, n_down = n_down,
    citation = def$citation,
    path = sprintf("%s/%s/%s", def$organism, def$tissue, def$id)
  )

  cat(sprintf("  ✓ %s/%s/%-30s  UP=%4d  DOWN=%4d\n",
              def$organism, def$tissue, def$id, n_up, n_down))
}

# registry.json (minimal, no jsonlite dependency)
json_escape <- function(s) gsub("\"", "\\\\\"", s)
json_panel <- function(p) {
  fields <- c(
    sprintf("\"id\":\"%s\"",        json_escape(p$id)),
    sprintf("\"organism\":\"%s\"",  json_escape(p$organism)),
    sprintf("\"tissue\":\"%s\"",    json_escape(p$tissue)),
    sprintf("\"type\":\"%s\"",      json_escape(p$type)),
    sprintf("\"n_up\":%d",          p$n_up),
    sprintf("\"n_down\":%d",        p$n_down),
    sprintf("\"citation\":\"%s\"",  json_escape(p$citation)),
    sprintf("\"path\":\"%s\"",      json_escape(p$path))
  )
  sprintf("    {%s}", paste(fields, collapse = ","))
}

lines_json <- c(
  "{",
  sprintf("  \"schema_version\": \"0.1\","),
  sprintf("  \"generated_at\": \"%s\",", format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z")),
  sprintf("  \"n_panels\": %d,", length(registry)),
  "  \"panels\": [",
  paste(sapply(registry, json_panel), collapse = ",\n"),
  "  ]",
  "}"
)
writeLines(lines_json, file.path(REGISTRY_ROOT, "registry.json"))

cat(sprintf("\n✓ Exported %d panels to %s\n", length(registry), REGISTRY_ROOT))
cat(sprintf("✓ Registry index: %s\n", file.path(REGISTRY_ROOT, "registry.json")))
