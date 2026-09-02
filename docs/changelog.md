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
  *Nat Commun* 16, 9957 (2025).
- **`scrna --variant-filter-top-fraction`** — AlphaMissense-style variant
  pre-filter using BLOSUM62 + driver-gene boost + Δhydrophobicity.
- **`scrna --embedding-model`** — foundation-model cell embedder (stdlib
  TF-IDF + truncated SVD by default; scGPT plug point when installed).
- **`trial --retriever dense`** — MedCPT-style dense retriever with
  biomedical synonym expansion.
- `MRNA_AI_FORCE_MOCK=1` env var for CI / sandbox runs.

### Changed
- Bumped to v0.3.0.

## [0.2.0] - 2026-09-02

### Added
- New `scrna` tool.
- `mhcflurry` backend for `neoantigen`.
- `pyproject.toml` with extras.
- MkDocs Material site + GitHub Pages workflow.
- Dual AGPL-3.0-or-later + commercial license.

## [0.1.0] - 2026-09-02

### Added
- Initial release: `codon`, `neoantigen`, `trial`, `lnp`.
