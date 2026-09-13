# mRNA × AI Toolkit

> Practical Python tools for the AI-leverage layers in mRNA cancer therapy.
> Stdlib-only core, optional integrations for mhcflurry, scGPT, and OpenAI-compatible LLMs.

Four small, runnable tools that map 1-to-1 onto the AI leverage points where
LLMs and ML models are currently transforming mRNA cancer therapeutics:

| Tool | What it does | AI leverage layer |
|---|---|---|
| `codon` | CAI, GC%, rare-codon analysis + greedy codon optimizer | Foundation models for sequence design (CodonBERT, RiboDecode, mRNABERT) |
| `neoantigen` | Peptide × HLA binding + immunogenicity scoring | TrambaHLApan, DeepNeo, DeepHLApan, NetMHCpan, mhcflurry |
| `trial` | Patient-to-trial retrieve → match → rank | TrialGPT (Jin et al. *Nat Commun* 2024) |
| `lnp` | LNP composition recommender | Witten 2025 ML-designed lipids, Li 2024 combinatorial+ML |
| `scrna` | scRNA-seq → tumor cluster → mutant peptides → handoff | scGPT / scanpy → neoantigen pipeline |

## Why these four (now five)?

The mRNA cancer therapy field has reached an inflection point:

1. **Personalized mRNA cancer vaccines work.** Intismeran autogene (mRNA-4157) +
   pembrolizumab hit both Phase 3 endpoints in INTerpath-001 (Aug 2026).
2. **Foundation models for mRNA design are mature.** CodonBERT, RiboDecode,
   mRNABERT, GEMORNA, TrambaHLApan — all published in 2024–2025.
3. **The bottleneck is no longer the algorithms — it's the integration.**
   Researchers need a clean, stdlib-only interface layer to plug these models
   into a working pipeline without a GPU cluster.

This toolkit is that integration layer.

## Quick start

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .

# codon analysis
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize

# neoantigen screen
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv --hla HLA-A*02:01

# patient → trial matching
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl --top-k 5

# LNP composition advice
mrna-ai lnp --target lung --cargo saRNA --intent "cancer vaccine"

# scRNA-seq → neoantigen handoff
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv \
              --variants mrna_ai_tools/examples/variants_coding.csv \
              --proteins mrna_ai_tools/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180
```

See the [Getting started](getting-started.md) page for full install options
and the [Backends](backends.md) page for wiring real LLMs / mhcflurry / scGPT.

## License

Dual-licensed: [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.html)
for open-source use, plus a separate commercial license for proprietary
deployments. See [License](license.md).


## Why we don't depend on heavy evaluation libraries

A surprising number of "production" bioinformatics pipelines silently
disagree on their own AUPRC scores. Chen et al. 2024 (*Genome Biology*
25(1): 118) evaluated 10 widely-used PRC-plotting + AUPRC-computing
tools across >3,000 published studies and found:

> The AUPRC values computed by the tools rank classifiers differently
> and some tools produce overly-optimistic results.

This finding is exactly why the toolkit's `backends.py` integrity
checks deliberately use **deterministic structural assertions** rather
than AUPRC / F1 / accuracy metrics computed by third-party libraries:

- Every check produces a boolean + a string message, both directly
  inspectable.
- The numbers (CAI, GC%, sequence similarity, module activity)
  are computed by **stdlib-only** code paths the toolkit owns
  end-to-end — no `sklearn.metrics.precision_recall_curve`, no
  `torchmetrics.AveragePrecision`, no silent divergences between
  local results and CI results.
- When a heavy library IS used (e.g. mhcflurry for binding affinity,
  transformers for ESM2 embeddings), the integration is **isolated
  behind a Protocol adapter** with a stdlib mock fallback — the
  integrity check never depends on the heavy library's evaluation
  semantics.

For users who need AUPRC-style evaluation, we recommend **owning
the metric**: reimplement the small formula you need (typically 10
lines of Python), commit it to your repo, and assert against your
own baseline. The Chen et al. result shows that "use scikit-learn's
average_precision_score" is not the safe default it appears to be.

### Reference

Chen W.*, Miao C.*, Zhang Z., Fung C.S.H., Wang R., Chen Y., Qian Y.,
Cheng L., Yip K.Y.#, Tsui S.K.W.#, and Cao Q.#. (2024). Commonly
used software tools produce conflicting and overly-optimistic AUPRC
values. *Genome Biology* 25(1): 118.
