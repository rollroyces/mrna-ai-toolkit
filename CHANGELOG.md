# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] - 2026-09-11

### Added
- **RiboDecode Protocol adapters** (`mrna_ai_tools.codon_protocols` +
  `mrna_ai_tools.codon_ribodecode_adapter`). Wires the published
  RiboDecode package (Li, Wang, Yang et al., *Nat Commun* 16, 9957
  (2025)) into the toolkit via two `runtime_checkable` Protocols:
  - `TranslationPredictor` — predicts translation level per CDS,
    optionally per cellular environment (HEK293T, A549, HeLa, or
    custom RPKM CSV).
  - `CodonOptimizer` — joint translation × MFE optimization via
    the published deep generative model.
- **Two real CLI adapters** (`TranslationModelCLIAdapter`,
  `RiboDecodeCLIAdapter`) shell out to the upstream `pred-translation`
  and `ribo-decode` console scripts. Heavy deps (ViennaRNA, torch,
  CUDA) are only required on the user's machine — the toolkit itself
  remains stdlib-only.
- **Two mock backends** (`MockTranslationPredictor`,
  `MockCodonOptimizer`) that satisfy the Protocols using only stdlib
  (CAI-derived score + LinearDesign for optimization). Used by CI and
  tests; fall back automatically when the upstream binaries aren't
  installed.
- **Typed dataclass contracts**: `RiboDecodeRequest` validates
  length (multiples of 3, ≤4500 nt), mfe_weight ∈ [0,1], and
  `env='custom'` requiring a CSV path — at construction time, before
  the backend ever sees the input.
- **CLI wiring**: `mrna-ai codon --backend ribodecode-real
  [--env HEK293T|A549|HeLa|custom] [--env-csv ...] [--mfe-weight ...]
  [--optim-epoch N]`. Falls back gracefully to the mock if the
  upstream binary isn't installed.
- **Backend selector**: `select_translation_predictor()` and
  `select_codon_optimizer()` choose real-or-mock based on $PATH
  + `prefer=` override.
- **22nd backend integrity check** (`codon.ribodecode_protocols`):
  verifies dataclass validation, Protocol runtime_checkable, mock
  translation in [0, 100] range with CAI ordering, and protein
  preservation end-to-end through the mock optimizer.
- **`tests/` directory** with `test_ribodecode_adapter.py` (46
  tests): dataclass validation, Protocol conformance, mock
  translator + optimizer, CLI subprocess mock paths, backend
  selector dispatch, end-to-end protein preservation. Runs in
  ~20 s with stdlib `unittest.mock`.

### Reference
Li, Y., Wang, F., Yang, J. et al. *Deep generative optimization of
mRNA codon sequences for enhanced mRNA translation and therapeutic
efficacy.* Nat Commun 16, 9957 (2025).
DOI: 10.1038/s41467-025-64894-x

## [0.9.1] - 2026-09-10

### Performance
- **LinearDesign 2-4x faster** (no semantic change):
  - **Parent-pointer DP** replaces the full-codon-history copy: each
    state stores `(parent_key, accumulated_codons)` in an append-only
    trace dict, and the traceback walks the chain at the end. Old
    code did O(L) per-state work for O(L²) total; new code is O(L).
  - **Precomputed `_LOG_SCORE_TABLE`**: `(aa, codon) -> float`
    built once at module load. Eliminates 13M+ `dict.get` and
    `math.log` calls per Cas9 run.
  - **`_append_key(prev_key, cand, max_len)`**: faster than
    `"|".join(codons[-n:])` (no list allocation, no split).

### Benchmarks (Apple Silicon, Python 3.12)
| protein      | aa   | nt   | before | after  | speedup |
|--------------|------|------|--------|--------|---------|
| EPO          | 193  | 579  | 726ms  | 310ms  | 2.3x    |
| GFP          | 239  | 717  | 1003ms | 444ms  | 2.3x    |
| mAb heavy    | 450  | 1350 | 4459ms | 1408ms | 3.2x    |
| Luciferase   | 550  | 1650 | 3522ms | 1288ms | 2.7x    |
| **Cas9**     | 1368 | 4104 | 34040s | **8925ms** | **3.8x** |

Same outputs: protein sequences preserved on every test, CAI
deltas identical, codon-change counts identical.

## [0.9.0] - 2026-09-03

### Added
- **TrialGPT-style per-criterion LLM matching** (`mrna_ai_tools.trial_llm`)
  - Implements the TrialGPT-Matching approach from Jin et al.
    (*Nature Communications* 2024): per-criterion LLM reasoning,
    each inclusion/exclusion criterion judged independently as
    ``"met" | "unmet" | "uncertain"`` with a short evidence snippet
  - `score_trial_with_llm(patient_text, nct_id, title, inclusion,
    exclusion, *, backend=None)` returns a `TrialMatchResult` with
    per-criterion verdicts and aggregate 0–1 score
  - Aggregate score = (n_met_inclusion / n_total_inclusion) ×
    (n_unmet_exclusion / n_total_exclusion) — both axes required
    for eligibility
  - Schema-validated JSON parsing with case-insensitive dedup and
    backfill of criteria the LLM omitted
  - `MATCH_PROMPT_TEMPLATE` is the canonical TrialGPT prompt
- `trial_matcher.match(..., matcher="trialgpt"|"keyword"|"auto")`:
  - `matcher="trialgpt"` forces per-criterion LLM matching
  - `matcher="auto"` (default) uses TrialGPT when `OPENAI_API_KEY`
    is set, otherwise keyword fallback
  - On TrialGPT failure, automatically falls back to keyword with
    `"trialgpt-fallback"` note
- CLI: `mrna-ai trial --matcher {auto,trialgpt,keyword}`
- 21st backend integrity check (`trial.trialgpt_llm`):
  - Skips when `MRNA_AI_FORCE_MOCK=1` (CI without LLM)
  - Skips when `MRNA_AI_SKIP_LLM_CHECK=1` (CI escape hatch)
  - Otherwise verifies per-criterion verdicts and that a matching
    trial outranks an unrelated one

### Mock backend improvements
The `_mock_complete` LLM mock backend now produces real per-criterion
JSON output for trial-matching prompts:
- Parses inclusion/exclusion bullets from the prompt
- Splits patient summary out by marker
- Judges inclusion criteria by keyword overlap (>=50% hit → "met")
- Judges exclusion criteria with negation awareness ("no prior
  therapy" + criterion "Prior therapy" → "unmet")

### Reference
Jin, Qiao, et al. "Matching patients to clinical trials with large
language models." *Nature Communications* 15 (2024): 9074.
DOI: 10.1038/s41467-024-53081-z
Reported: 87.3% accuracy on 1,015 patient-criterion pairs.

## [0.8.0] - 2026-09-03

### Added
- **Real scGPT foundation model integration** (`mrna_ai_tools.scgpt_integration`)
  - Loads the `perturblab/scgpt-human` checkpoint (whole-human, 33M
    cells, 60,697-gene vocab, 205 MB)
  - Reimplements scGPT's `FlashTransformerEncoderLayer` in pure PyTorch
    (12 layers, 8 heads, 512 dim, fused `Wqkv` projection split into
    Q/K/V, post-norm) — no `flash-attn` dependency
  - `embed_with_scgpt(matrix, gene_names=...)` produces CLS-token
    cell embeddings. Real TF-IDF baseline: silhouette -0.114 on
    tumor-vs-normal; real scGPT: **+0.214** (+0.328 improvement)
  - `scgpt_available()` check; weights expected at
    `~/.cache/mrna_ai_tools/{best_model.pt,vocab.json,args.json}`
  - `bin_expression()` rank-bins raw values into 51 categories per
    scGPT preprocessing
  - `ScGPTConfig.from_json()` mirrors the upstream args.json layout
- `sc_rna_pipeline.embed_with_foundation_model(...)` extended with
  `gene_names` parameter — when set, real scGPT can use the names
  to look up token IDs in its 60,697-gene vocabulary
- 20th backend integrity check (`scrna.scgpt_integration`):
  - Skips when `MRNA_AI_FORCE_MOCK=1` (CI without scGPT weights)
  - Skips when `MRNA_AI_SKIP_SCGPT_CHECK=1` (CI escape hatch)
  - Skips when weights not present (first-run)
  - Otherwise embeds 30 named-gene cells and verifies 30×512 output

### Reference
Cui et al., scGPT: toward building a foundation model for single-cell
multi-omics. *Nat Methods* 21, 1480–1491 (2024).

## [0.7.0] - 2026-09-03

### Added
- **mRNA manufacturability checker** — the wet-lab bridge between
  computational sequence design and what's actually synthesizable.
  Eight checks:
  1. `poly_a_runs` — runs of ≥5 As destabilize the DNA template
  2. `gc_5prime_hairpin` — GC-rich stems (≥70% GC, 30+ nt) at the 5'
     end block ribosome scanning
  3. `kozak_strength` — match to mammalian Kozak consensus
     `GCCRCCATGG`
  4. `are_motif` — AU-rich elements (`UUAUUUAUU` nonamers) in the
     3' UTR trigger mRNA decay
  5. `stop_context` — termination efficiency depends on stop codon
     identity + +4 base (TGA-T and TAA-T are strongest)
  6. `hidden_stops` — internal in-frame stops (must be zero)
  7. `gc_window_uniformity` — local GC stddev > 15% flags IVT yield
     problems and ribosomal stalling
  8. `cpg_balance` — extreme CpG density (suppressed <0.5% or
     excessive >15%) signals silencing or immune activation
- New CLI: `mrna-ai manufacture --cds input.fasta [--utr5 ...] [--utr3 ...]`
  returns a JSON report with per-check status, score, severity, and
  summary. Exit code 0 if no errors, 2 if any check is `error`.
- 19th backend integrity check (`manufacture.score_manufacturability`)
  verifies that the checker correctly distinguishes clean vs
  pathological sequences.

### Reference
- Holtkamp et al. (2006) *Blood* 108.
- Kozak (1986) *Cell* 44.
- Chen & Shyu (1995) *Trends Biochem Sci* 20.

## [0.6.0] - 2026-09-03

### Added
- **Full-length LinearDesign** (Do & Woods, *Nature* 2024): the
  600-nt CLI cap is gone. Real LinearDesign uses a **linear-time
  per-step DP** where the state space is bounded by `|Σ|^(W/3)` —
  independent of CDS length. This implementation now does the same:
  state key = the last `W/3` codons (default 7 codons / 21 nt).
  Pareto-prune keeps the highest-translation-score path per key, so
  two paths arriving at the same suffix collapse to one state.
  Full-length Cas9 (4,104 nt) optimizes in **37.6 s** via the CLI
  with protein preservation verified.
- New `LinearDesignResult` fields: `elapsed_seconds`, `n_states_evaluated`
  — useful for benchmarking and reporting.
- 18th backend integrity check (`codon.lineardesign_full_length`) that
  verifies LinearDesign works on a 603-nt synthetic CDS end-to-end and
  preserves the protein sequence. Runs in ~100 ms.

### Changed
- Default `gc_window_size` lowered from 30 → 21 (must be a multiple of
  3 so the codon-suffix state grouping is exact). Window 21 keeps the
  state space at `|Σ|^7 ≈ 64K max` for sub-second typical runs while
  still capturing the same class of local stem structures.
- `optimize_lineardesign` accepts a new `verbose` flag that prints
  progress every 50 codons — useful for full-length runs.
- Codon CLI `--backend lineardesign` now accepts CDS of any length
  (was previously hard-capped at 600 nt).

### Reference
- Do, C. & Woods, D. LinearDesign: a Toolkit for Full-length Stable
  mRNA Design. *Nature* (2024).

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
