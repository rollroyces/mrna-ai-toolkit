# mRNA Manufacturability Checker

The bridge between computational sequence design and what's actually
synthesizable at production scale.

## Why this matters

A mRNA sequence that's algorithmically perfect can still be impossible
to manufacture. Real production requires checking for motifs that
destabilize the DNA template, block ribosome scanning, or trigger
mRNA decay — issues that show up only in the wet lab.

## Eight checks

| Check | Severity threshold | What it catches |
|---|---|---|
| `poly_a_runs` | ≥7 As → error | Poly-A runs in the DNA template destabilize the plasmid during IVT |
| `gc_5prime_hairpin` | ≥70% GC → warn, ≥80% → error | GC-rich stems at the 5' end block ribosome scanning |
| `kozak_strength` | <45% match → warn | Strong Kozak consensus (`GCCRCCATGG`) is required for mammalian translation |
| `are_motif` | ≥1 nonamer → warn, ≥2 → error | AU-rich elements in the 3' UTR trigger mRNA decay |
| `stop_context` | leakiness ≥0.7 → warn | TGA is the leakiest stop codon; TAA-T or TGA-T is strongest |
| `hidden_stops` | any internal stop → error | Internal in-frame stops break the protein |
| `gc_window_uniformity` | stddev >15% → warn | Extreme local GC variation hurts IVT yield |
| `cpg_balance` | <0.5% or >15% → warn | Suppressed CpG silences; excessive CpG activates TLR9 |

## CLI

```bash
mrna-ai manufacture --cds input.fasta --utr5 GCCGCCACC --utr3 AAAAAAAAAAAAAA
```

Returns a JSON report with per-check status, score, severity, and
summary. Exit code 0 if no errors, 2 if any check returns `error`.

## Python API

```python
from mrna_ai_tools.manufacturability import score_manufacturability

report = score_manufacturability(
    cds,
    utr5="GCCGCCACC",       # optional, for Kozak scoring
    utr3="AAAAAAAAAAAAAA",  # optional, for ARE detection
)

print(f"overall: {report.overall_score:.3f}")
for c in report.checks:
    print(f"  [{c.severity}] {c.name}: {c.summary}")
```

## Reference

- Holtkamp et al. (2006) *Blood* 108.
- Kozak (1986) *Cell* 44.
- Chen & Shyu (1995) *Trends Biochem Sci* 20.
