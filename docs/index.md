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
