##' STModule shim: thin CLI wrapper around the published R package
##'
##' This shim converts a SpatialData input (count matrix TSV + spatial
##' locations TSV) into a SpatialModuleResult JSON document on stdout,
##' suitable for consumption by the Python adapter
##' (`mrna_ai_tools.spatial_module_adapter.STModuleCLIAdapter`).
##'
##' Reference: Wang et al., Genome Medicine 17, 18 (2025).
##' Upstream package: https://github.com/rwang-z/STModule
##'
##' Usage:
##'   Rscript stmodule_shim.R \
##'     --count-file path/to/counts.tsv \
##'     --locations-file path/to/locs.tsv \
##'     --platform ST \
##'     --num-modules 10
##'
##' Optional flags:
##'   --high-resolution   : enable for SlideSeqV2 / StereoSeq data
##'   --max-iter N        : max STModule iterations (default 2000)
##'   --gene-mode MODE    : HVG | selected | combined (default HVG)
##'   --top-hvg N         : top N HVGs to use (default 2000)
##'   --gene-filtering F  : gene filtering threshold (default 0.1)
##'
##' Output: a single JSON object on stdout, matching
##' mrna_ai_tools.spatial_protocols.SpatialModuleResult.to_dict() shape.
##'
##' Exit codes:
##'   0  : success
##'   1  : invalid CLI arguments
##'   2  : missing R package dependency
##'   3  : STModule run failed
##'   4  : result serialization failed

suppressWarnings(suppressMessages({
  if (!requireNamespace("optparse", quietly = TRUE)) {
    message("ERROR: R package 'optparse' not installed. Install with: install.packages('optparse')")
    quit(status = 2)
  }
  if (!requireNamespace("STModule", quietly = TRUE)) {
    message("ERROR: R package 'STModule' not installed. Install per upstream vignette: devtools::install_github('rwang-z/STModule')")
    quit(status = 2)
  }
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    message("ERROR: R package 'jsonlite' not installed. Install with: install.packages('jsonlite')")
    quit(status = 2)
  }
}))

library(optparse)
library(STModule)
library(jsonlite)

option_list <- list(
  make_option("--count-file", type = "character", default = NULL,
              help = "TSV count matrix (spots x genes)"),
  make_option("--locations-file", type = "character", default = NULL,
              help = "TSV spatial coordinates (spot_id, x, y)"),
  make_option("--platform", type = "character", default = "ST",
              help = "SRT platform [ST, Visium, SlideSeqV2, StereoSeq, Other]"),
  make_option("--num-modules", type = "integer", default = 10,
              help = "Number of tissue modules to identify"),
  make_option("--high-resolution", action = "store_true", default = FALSE,
              help = "Enable for SlideSeqV2 / StereoSeq data"),
  make_option("--max-iter", type = "integer", default = 2000,
              help = "Max STModule iterations"),
  make_option("--gene-mode", type = "character", default = "HVG",
              help = "Gene selection: HVG | selected | combined"),
  make_option("--top-hvg", type = "integer", default = 2000,
              help = "Top N HVGs to use"),
  make_option("--gene-filtering", type = "double", default = 0.1,
              help = "Gene filtering threshold")
)

opt <- parse_args(OptionParser(option_list = option_list))

# --- Validation ---
if (is.null(opt$`count-file`) || is.null(opt$`locations-file`)) {
  message("ERROR: --count-file and --locations-file are required")
  quit(status = 1)
}
if (!file.exists(opt$`count-file`)) {
  message(sprintf("ERROR: count file not found: %s", opt$`count-file`))
  quit(status = 1)
}
if (!file.exists(opt$`locations-file`)) {
  message(sprintf("ERROR: locations file not found: %s", opt$`locations-file`))
  quit(status = 1)
}

t0 <- Sys.time()

# --- Run the STModule pipeline ---
# Note: STModule expects a GPU by default for SlideSeqV2/StereoSeq.
# We use the CPU version for portability; users on GPU hardware can
# edit this shim to set version="gpu".
version_mode <- "cpu"

tryCatch({
  data_preproc <- data_preprocessing(
    count_file = opt$`count-file`,
    loc_file = opt$`locations-file`,
    high_resolution = opt$`high-resolution`,
    gene_mode = opt$`gene-mode`,
    top_hvg = opt$`top-hvg`,
    gene_filtering = opt$`gene-filtering`
  )
}, error = function(e) {
  message(sprintf("ERROR: data_preprocessing failed: %s", conditionMessage(e)))
  quit(status = 3)
})

tryCatch({
  res <- run_STModule(
    data = data_preproc,
    num_modules = opt$`num-modules`,
    high_resolution = opt$`high-resolution`,
    max_iter = opt$`max-iter`,
    version = version_mode
  )
}, error = function(e) {
  message(sprintf("ERROR: run_STModule failed: %s", conditionMessage(e)))
  quit(status = 3)
})

# --- Extract module-associated genes ---
# Upstream function name has a typo: get_assocaited_genes (sic)
tryCatch({
  module_genes <- get_assocaited_genes(res)
}, error = function(e) {
  message(sprintf("ERROR: get_assocaited_genes failed: %s", conditionMessage(e)))
  quit(status = 3)
})

# --- Build the JSON payload matching SpatialModuleResult.to_dict() shape ---
# Collapse each module to its top 3 genes by activity for compact output.
modules_list <- split(module_genes, module_genes$module)
modules_out <- lapply(seq_along(modules_list), function(i) {
  mg <- modules_list[[i]]
  mg <- mg[order(-mg$activity), ]
  list(
    module_id    = as.integer(i - 1L),
    top_genes    = as.character(head(mg$gene, 3)),
    n_spots      = as.integer(nrow(data_preproc$loc)),
    mean_activity = as.numeric(mean(head(mg$activity, 3)))
  )
})

elapsed_sec <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

payload <- list(
  platform        = opt$platform,
  modules         = modules_out,
  n_spots         = as.integer(nrow(data_preproc$loc)),
  elapsed_seconds = elapsed_sec,
  backend         = "stmodule",
  notes           = character(0)
)

tryCatch({
  cat(toJSON(payload, auto_unbox = TRUE, pretty = FALSE))
}, error = function(e) {
  message(sprintf("ERROR: JSON serialization failed: %s", conditionMessage(e)))
  quit(status = 4)
})

quit(status = 0)