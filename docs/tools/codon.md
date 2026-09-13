# `codon` — sequence analysis & optimization

Computes the canonical codon-usage features that every modern mRNA design model
(CodonBERT, RiboDecode, LinearDesign, mRNABERT) consumes. Ships four
optimization backends:

| Backend | Algorithm | Setup |
|---|---|---|
| `basic` (default) | Greedy per-codon frequency swap, GC% band 45–60% | — |
| `ribodecode` | Context-aware hill-climb matching RiboDecode's published algorithm (Li et al., *Nat Commun* 16, 9957, 2025) | — (stdlib) |
| `lineardesign` | Joint translation × MFE DP, no length cap | — (stdlib) |
| `ribodecode-real` | Subprocess to upstream `ribo-decode` CLI | `pip install ribodecode-1.3.0-py3-none-any.whl` + Rscript on `$PATH` |

## Usage

```bash
# Codon analysis (no optimization)
mrnavax codon --sequence mrnavax/examples/cas9.fasta

# Greedy optimization
mrnavax codon --sequence mrnavax/examples/cas9.fasta --optimize

# LinearDesign (joint translation + mRNA structure, O(L) DP)
mrnavax codon --sequence mrnavax/examples/cas9.fasta \
    --optimize --backend lineardesign

# RiboDecode heuristic (context-aware hill-climb)
mrnavax codon --sequence mrnavax/examples/cas9.fasta \
    --optimize --backend ribodecode

# Real RiboDecode CLI (requires upstream R package)
mrnavax codon --sequence mrnavax/examples/cas9.fasta \
    --optimize --backend ribodecode-real \
    --env HEK293T --mfe-weight 0.3 --optim-epoch 10

# LinearDesign works on full-length CDS (Cas9 4.1 kb in ~9 s)
mrnavax codon --sequence mrnavax/examples/cas9.fasta \
    --optimize --backend lineardesign
```

## Output schema

```json
{
  "n_codons": 210,
  "cai": 0.6954,                        // Codon Adaptation Index (0–1)
  "gc_percent": 37.3,                   // overall GC%
  "rare_codon_fraction": 0.0429,        // fraction of codons below 0.10 freq
  "cpg_obs_exp": 1.1331,                // CpG O/E ratio — proxy for innate immunity
  "most_common_codons": [["GAT", 12], ...],
  "rare_codons": ["CTA", "TTA"],
  "gc_window_stddev": 4.75               // rolling GC stddev (translation speed proxy)
}
```

## `--optimize` backends

### `basic` (default)

Greedy synonymous-codon swap that maximizes per-codon usage frequency
while keeping the GC% in the 45–60% band.

Expected CAI improvement on a bacterial gene expressed in human cells: ~0.2
absolute (e.g. 0.7 → 0.93 for the Cas9 example).

This is the **classical baseline** that any modern codon model should beat.

### `ribodecode` (heuristic)

Context-aware hill-climb: at each position, choose the synonym with the
best ribosome-profiling-weighted frequency. Stdlib-only — no upstream
dependency. Suitable for CI and offline runs.

### `lineardesign` (DP)

Joint translation × MFE dynamic programming. O(L) per step (state space
bounded by |syn|^W for window size W). **No length cap** — works on
full-length mRNA constructs up to and beyond 4 kb (Cas9 in ~9 s on
Apple Silicon). Protein sequence preserved exactly.

### `ribodecode-real`

Subprocess to the upstream `ribo-decode` R package. Requires:

```bash
# Install per the upstream vignette (R + Seurat not actually needed
# for the optimizer, just the .whl)
pip install TranslationModel-1.1.0-py3-none-any.whl
pip install ribodecode-1.3.0-py3-none-any.whl

# Optional: custom cellular environment via RPKM CSV
mrnavax codon --sequence gfp.fasta --optimize --backend ribodecode-real \
    --env HEK293T \
    --csv env_hek293t.csv \
    --mfe-weight 0.3 --optim-epoch 10
```

The adapter shells out to the upstream CLI with `--env {HEK293T,A549,HeLa,custom}`,
`--mfe-weight` (0=translation-only, 1=MFE-only), `--optim-epoch N`. When the
upstream binary isn't on `$PATH`, the adapter raises
`RiboDecodeNotInstalled` with a clear remediation message including the
Google Drive `.whl` download links.

## RiboDecode references

- Li, Y., Wang, F., Yang, J., et al. (2025). *Deep generative optimization
  of mRNA codon sequences for enhanced mRNA translation and therapeutic
  efficacy.* Nat Commun 16, 9957. DOI: 10.1038/s41467-025-64894-x
- GitHub: [wangfanfff/RiboDecode](https://github.com/wangfanfff/RiboDecode)

## LinearDesign reference

The DP algorithm follows the joint translation × structure DP from
LinearDesign (Zhang et al., 2023) — O(L) per step via suffix-state
pruning, parent-pointer backtrack, L2-normalized translation scores.
Protein preservation invariant verified across all test CDSs.
