# `codon` — sequence analysis & optimization

Computes the canonical codon-usage features that every modern mRNA design model
(CodonBERT, RiboDecode, LinearDesign, mRNABERT) consumes.

## Usage

```bash
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize
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

## `--optimize`

Runs a greedy synonymous-codon swap that maximizes per-codon usage frequency
while keeping the GC% in the 45–60% band.

Expected CAI improvement on a bacterial gene expressed in human cells: ~0.2
absolute (e.g. 0.7 → 0.93 for the Cas9 example).

This is the **classical baseline** that any modern codon model should beat.
It's deliberately simple so you can plug a more sophisticated model
(CodonBERT, RiboDecode) into the same input/output shape and compare.
