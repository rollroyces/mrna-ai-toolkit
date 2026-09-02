# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-02

### Added
- **Backend integrity check module** — `python -m mrna_ai_tools.backends --check-all`
  runs 13 checks across all five tools. Used by CI; also useful as a
  post-install verification.
- **`codon --backend ribodecode`** — RiboDecode-style context-aware codon
  optimizer with optional `--ribo-weights` JSON. Reference: Fu et al.
  *Nat Commun* 16, 9957 (2025). CAI 0.78 → 1.00 on test CDS; 0 rare-pair
  remnants; smoother GC window stddev.
- **`scrna --variant-filter-top-fraction`** — AlphaMissense-style variant
  pre-filter using BLOSUM62 + driver-gene boost + Δhydrophobicity. Ranks
  BRAF.V600E (0.91) and KRAS.G12V (0.87) at the top of the standard
  test set.
- **`scrna --embedding-model`** — foundation-model cell embedder (stdlib
  TF-IDF + truncated SVD by default; scGPT plug point when installed).
  Produces 2.8–4.0× inter/intra cluster separation on synthetic data.
- **`trial --retriever dense`** — MedCPT-style dense retriever with
  biomedical synonym expansion ("skin cancer" → "melanoma", "shot" →
  "vaccine"). Correctly ranks INTerpath-001 melanoma trial on top for
  lay-terms patient summaries. Reference: Jin et al. *Nat Commun* 2024.
- `MRNA_AI_FORCE_MOCK=1` env var for CI / sandbox runs.
- Example ribosome-profiling weights file
  (`mrna_ai_tools/examples/ribo_weights_example.json`).

### Changed
- Bumped to v0.3.0.
- `scrna` accepts `--embedding-model`, `--embedding-dim`,
  `--variant-filter-top-fraction`, `--variant-filter-min-score`.
- `trial` accepts `--retriever {keyword,dense,auto}`.
- `codon` accepts `--backend {basic,ribodecode}` and `--ribo-weights`.

### Fixed
- Lint cleanup: removed unused imports/variables across the package.
- Trial-matcher CLI: explicit `import os` for the `MRNA_AI_FORCE_MOCK` guard.
- `medcpt_retriever`: defensive `_safe_text` so list-valued fields don't crash.
- `sc_rna_pipeline.embed_with_foundation_model`: returns a real stdlib embedder.

## [0.2.0] - 2026-09-02

### Added
- New `scrna` tool — scRNA-seq → tumor-cluster → mutant peptide → neoantigen handoff pipeline.
- `mhcflurry` backend for `neoantigen` — real pan-allele binding prediction.
- `pyproject.toml` with extras.
- MkDocs Material site + GitHub Pages workflow.
- Dual AGPL-3.0-or-later + commercial license.

## [0.1.0] - 2026-09-02

### Added
- Initial release: `codon`, `neoantigen`, `trial`, `lnp`.
- Dual license.
