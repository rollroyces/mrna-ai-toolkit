# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-09-03

### Added
- **AlphaMissense (DeepMind) variant pathogenicity integration** via the
  pre-computed predictions TSV (Cheng et al., *Science* 2023). When the
  predictions file is present, the variant scorer weights AlphaMissense
  at 45% of the total score — the dominant signal.
  Verified end-to-end: BRAF.V600E norm jumps from 0.73 (heuristic) to
  0.83 (AlphaMissense-augmented).
- `mrna_ai_tools.alphamissense_integration` module with:
  - `build_test_index()` — 5-entry synthetic index for unit tests
    (KRAS.G12D=0.832, KRAS.G12V=0.913, BRAF.V600E=0.954,
    TP53.R175H=0.881, TP53.R248Q=0.872)
  - `load_index()` — streams the 5.5 GB predictions TSV into a 71.7M-entry
    dict and pickles it (cached at
    `~/.cache/mrna_ai_tools/alphamissense_index.pkl`)
  - `lookup(uniprot, wt_aa, position, mut_aa)` — O(1) by `(uniprot, aa_change)`
- `UNIPROT_TO_GENE` reverse-lookup table (TP53, KRAS, BRAF, BRCA1/2, EGFR,
  PTEN, PIK3CA, AKT1/2, etc.) — bridges the UniProt-keyed AlphaMissense
  data to the gene-symbol-keyed variant CSVs.
- `load_protein_fasta_detailed()` — new FASTA loader that extracts UniProt
  accessions from standard `>sp|P01116|RASK_HUMAN ...` headers.
- Updated bundled `examples/proteins.fasta` to UniProt-style headers so
  AlphaMissense lookups work out-of-the-box.
- 17th backend integrity check (`scrna.alphamissense_integration`) that
  verifies the AlphaMissense lookup + integration end-to-end using
  synthetic data — runs in milliseconds, no network or model download.

### Caveats
- The AlphaMissense predictions TSV is licensed under **CC BY-NC-SA 4.0**
  (non-commercial, share-alike). It cannot be bundled with mrna-ai-toolkit
  (which is dual-licensed under AGPL-3.0 + commercial). Users must download
  the ~640 MB gzipped TSV separately from
  https://storage.googleapis.com/dm_alphamissense/.
- First-time index build takes ~15 min (streaming 71.7M rows + pickling
  ~5 GB dict). Subsequent loads are <1 s.

## [0.4.1] - 2026-09-03

### Fixed
- `mrna_ai_tools.backends --check-all` previously failed when run from
  outside the repo (e.g., from a fresh `pip install` of the wheel),
  because two checks used hardcoded relative paths
  (`"mrna_ai_tools/examples/..."`) instead of resolving against the
  installed package location. Now resolves via `_example_path()` and
  passes 16/16 from any CWD. Caught during independent validation.

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
