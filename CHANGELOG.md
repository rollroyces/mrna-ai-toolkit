# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-09-02

### Added
- **LinearDesign-style codon optimizer** (`--backend lineardesign`) — DP
  over codon choices jointly optimizing translation efficiency and mRNA
  secondary-structure stability. Captures the operational idea of
  Do & Woods, *Nature* (2024). Reference sequence preserved; CAI 0.78 →
  0.998 with measurable structure improvement. Optional on the CLI
  (limited to ≤600 nt to keep DP runtime acceptable); full-length CDS use
  the Python API.
- **Chou-Fasman helix/strand disruption penalty** in variant scoring —
  variants in structured regions (predicted from protein sequence)
  rank higher than the same substitution in a coil. L→P in helix:
  score 0.43 (struct_penalty 0.8). L→P in coil: score 0.27
  (struct_penalty 0.0). Reference: Chou & Fasman (1978).
- **MedCPT integration module** (`mrna_ai_tools.medcpt_integration`) —
  real semantic trial retrieval via `ncbi/MedCPT-Query-Encoder` and
  `ncbi/MedCPT-Article-Encoder` from HuggingFace. Verified end-to-end
  on the bundled melanoma test patient: INTerpath-001 ranks #1 with
  cosine similarity 0.601, NSCLC #2 (0.498), pancreatic #3 (0.488).
  Auto-activates when `torch` + `transformers` are installed and the
  model weights are cached. Skipped in CI via
  `MRNA_AI_SKIP_MEDCPT_CHECK=1`. Reference: Jin et al., *Nat Commun*
  15, 1785 (2024).
- New `[neoantigen-medcpt]` and `[trial-medcpt]` extras for one-line
  installs.
- 16th backend integrity check (`trial.medcpt_integration`).

### Changed
- Bumped to v0.4.0.
- `trial --retriever {keyword,dense,auto}` auto-picks MedCPT when
  available, then falls back to TF-IDF dense, then keyword.
- `filter_variants` accepts `protein_sequences: dict[str, str]` for
  per-gene protein context (enables the Chou-Fasman component).

### Fixed
- Codon optimizer now raises `ValueError` on internal stop codons
  instead of silently producing a truncated protein.
- Removed unused `seed` parameter from `optimize_ribodecode` (was
  accepted but ignored — deterministic hill-climb).
- `variant_scorer.score_variant` returns `None` (or raises in `strict`
  mode) for unknown amino acids instead of silently maxing the BLOSUM
  penalty and inflating the score.
- LinearDesign DP bug: Pareto-pruning now tracks the protein sequence
  so codon swaps preserve the amino-acid sequence (verified by
  translation check).
- Test codon table missing `TCA → S` and several IUPAC-degenerate
  entries; expanded to 64 entries including stop codons.

## [0.3.0] - 2026-09-02

### Added
- Backend integrity check module (`mrna_ai_tools.backends --check-all`,
  13 checks). CI runs without network access.
- RiboDecode-style codon optimizer (`--backend ribodecode`) with
  optional `--ribo-weights` JSON.
- AlphaMissense-style variant pre-filter (BLOSUM62 + driver genes +
  Δhydrophobicity).
- TF-IDF + truncated SVD cell embedder (scGPT plug point).
- MedCPT-style dense retriever with biomedical synonym expansion.
- `MRNA_AI_FORCE_MOCK=1` env var for CI / sandbox.

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
