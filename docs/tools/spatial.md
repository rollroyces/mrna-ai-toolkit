# `spatial` — spatial transcriptomics tissue modules

Closes the loop from spatial RNA-seq data to tissue-region-aware
neoantigen handoff:

1. Load a count matrix (spots × genes) and a spatial locations file
   (spot × {x, y}).
2. Pre-process with the upstream R package's
   `data_preprocessing()` (Seurat HVG selection + distance matrix).
3. Run the published `run_STModule()` Bayesian model to identify
   `num_modules` tissue modules — recurrent cellular communities
   spatially organized to exert specific biological functions.
4. Map module-associated genes back to peptide candidates via the
   toolkit's `neoantigen` pipeline.

## Reference

Wang R., Qian Y., Guo X., Song F., Xiong Z., Cai S., Bian X., Wong M.H.,
Cao Q.#, Cheng L.#, Lu G.#, and Leung K.S.#. (2025) STModule:
identifying tissue modules to uncover spatial components and
characteristics of transcriptomic landscapes. *Genome Medicine*
17(1): 18.

The R package distributes from GitHub at
[`rwang-z/STModule`](https://github.com/rwang-z/STModule) and requires
R 4.4 + Seurat v5 + torch + GPUmatrix 1.0.2 + CUDA 11.7. The toolkit
ships a small R shim (`mrna_ai_tools/scripts/stmodule_shim.R`) that
calls the published R functions and emits JSON to stdout.

## Usage

```bash
# Stdlib-only (uses synthetic spatial coordinates + mock tissue modules)
python -m mrna_ai_tools.cli spatial \
    --count-file examples/spatial/st_bc2_count_matrix.tsv \
    --locations-file examples/spatial/st_bc2_locations.tsv \
    --platform ST --num-modules 10

# Real: when R + STModule are installed (Rscript on $PATH)
python -m mrna_ai_tools.cli spatial \
    --count-file examples/spatial/st_bc2_count_matrix.tsv \
    --locations-file examples/spatial/st_bc2_locations.tsv \
    --platform ST --num-modules 10 --backend stmodule

# Slide-seqV2 (high-resolution)
python -m mrna_ai_tools.cli spatial \
    --count-file my_slideseq.tsv --locations-file my_locs.tsv \
    --platform SlideSeqV2 --num-modules 10
```

CLI flag:

- `--platform {ST,Visium,SlideSeqV2,StereoSeq,Other}` — drives
  `high_resolution=FALSE` (default) or `TRUE` in the upstream call.
- `--num-modules N` — number of tissue modules to identify (default
  10; paper recommends 10 for "major expression components").
- `--backend {auto,mock,stmodule}` — default `auto` selects STModule
  if Rscript is on $PATH, else mock.

## Python API

```python
from mrna_ai_tools.spatial_protocols import SpatialData
from mrna_ai_tools.spatial_module_adapter import select_spatial_module_backend

backend = select_spatial_module_backend()  # picks real or mock
data = SpatialData(
    count_file=Path("counts.tsv"),
    locations_file=Path("locs.tsv"),
    platform="ST",
    num_modules=10,
)
result = backend.run(data)
print(result.modules[0].top_genes)
```

The mock backend uses per-platform gene universes:

| Platform | Top genes (round-robin) |
|---|---|
| ST | GAPDH, USP4, MAPKAPK2, CPEB1, LANCL2 |
| Visium | CDH1, VIM, KRT8, KRT18, EPCAM |
| SlideSeqV2 | MOBP, MBP, PLP1, MAG, MOG |
| StereoSeq | SOX2, PAX6, NES, VIM, HES1 |
| Other | (synthetic GEN_A–E) |

## Output schema

```json
{
  "platform": "ST",
  "modules": [
    {
      "module_id": 0,
      "top_genes": ["GAPDH", "USP4", "MAPKAPK2"],
      "n_spots": 12,
      "mean_activity": 1.0
    },
    ...
  ],
  "n_spots": 12,
  "elapsed_seconds": 0.02,
  "backend": "mock",
  "notes": ["mock-backend", "platform=ST", "n_modules=10"]
}
```

The `top_genes` of each module become the candidate peptides for the
toolkit's `neoantigen` module: feed them through
`mrna-ai neoantigen --csv ... --hla ...` to score immunogenicity.

## Why a separate module (and not inside `scrna`)?

The `scrna` module handles dissociated single-cell RNA-seq — no
spatial coordinates, cells in isolation. The `spatial` module handles
**spatially resolved transcriptomics (SRT)** — coordinates preserved
so tissue architecture informs which cellular communities are
spatially co-located. The two pipelines converge at the
neoantigen-handoff step:

1. `scrna` → tumor cluster identities + mutant peptides (from
   per-cell variant expression)
2. `spatial` → tissue modules + co-located cell populations (from
   spatial architecture)
3. `neoantigen` → immunogenicity scoring on the union of candidates

For cancer mRNA-vaccine design, both modules matter: `scrna` tells
you *which* peptides are tumor-specific; `spatial` tells you *where*
the tumor cells live and what their microenvironment looks like.

## Backend matrix

| Backend | What it does | Setup |
|---|---|---|
| `mock` | Stdlib stub. Per-platform gene universe + spot/location intersection. Always available. | — |
| `stmodule` | Subprocess to `Rscript stmodule_shim.R`. Calls the upstream R functions. | `conda install r-base=4.4 r-seurat r-devtools && R -e 'devtools::install_github("rwang-z/STModule")'` |
