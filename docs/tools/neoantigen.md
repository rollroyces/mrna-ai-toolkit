# `neoantigen` — peptide × HLA screening

Scores peptide-MHC binding and immunogenicity for candidate neoantigens.

## Usage

```bash
# Default: heuristic A*02:01 anchor matrix
mrnavax neoantigen --variants mrnavax/examples/tp53_variants.csv \
                   --hla HLA-A*02:01

# Real binding-affinity prediction (mhcflurry)
pip install -e ".[neoantigen-mhcflurry]"
mrnavax neoantigen --variants mrnavax/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend mhcflurry

# OpenAI LLM for immunogenicity narrative
export OPENAI_API_KEY=...
mrnavax neoantigen --variants mrnavax/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend openai

# ESM2 protein-LM immunogenicity (frozen LM + Applm-style classifier)
pip install -e ".[protein-lm]"
python -c "
from mrnavax.neoantigen_screener import lm_immunogenicity_score
print(lm_immunogenicity_score('NLVPMVATV'))  # CMV pp65 epitope
"
```

## ESM2 protein-LM immunogenicity

For high-accuracy immunogenicity scoring, the toolkit integrates the
**ESM2 protein-language-model family** (Lin et al., *Science* 379, 2023)
via the **Applm pattern** (Wong et al., 2025, arXiv 2508.10541): use a
frozen LM to embed candidate peptides, then a lightweight downstream
classifier scores them.

The default model is `facebook/esm2_t12_35M_UR50D` (35M parameters,
12 layers, 480-dim embeddings, ~135 MB). Other supported sizes:

| Model | Params | Dim | Size |
|---|---|---|---|
| `facebook/esm2_t6_8M_UR50D` | 8M | 320 | ~30 MB |
| `facebook/esm2_t12_35M_UR50D` (default) | 35M | 480 | ~135 MB |
| `facebook/esm2_t30_150M_UR50D` | 150M | 640 | ~600 MB |
| `facebook/esm2_t33_650M_UR50D` | 650M | 1280 | ~2.5 GB |

```python
from mrnavax.neoantigen_screener import lm_immunogenicity_score
from mrnavax.protein_lm_adapter import ESM2Embedder

# Use the real ESM2-150M model for higher accuracy
result = lm_immunogenicity_score(
    "NLVPMVATV",  # CMV pp65 epitope
    embedder=ESM2Embedder(model_id="facebook/esm2_t30_150M_UR50D"),
)
# {'score': 0.0–1.0, 'dim': 640, 'model_id': '...', 'backend': 'transformers', ...}

# Mock backend (stdlib-only, no torch dep)
result = lm_immunogenicity_score("NLVPMVATV")
# {'score': 0.0–1.0, 'dim': 480, 'backend': 'mock', ...}
```

The mock uses deterministic AA-k-mer (k=3) frequency vectors L2-normalized
to match ESM2's convention. Same peptide → same score; different
peptides → different scores.

## Input CSV

```csv
variant,peptide
R175H,HMTEVVRRC
R248Q,QMNRRPGMT
```

`peptide` is the only required column. `variant` is preserved in the rationale.

## Output schema

```json
{
  "hla": ["HLA-A*02:01"],
  "candidates": [
    {
      "peptide": "HMTEVVRRC",
      "hla": "HLA-A*02:01",
      "binding_affinity_nM": 3298.8,
      "binder": false,
      "immunogenicity_score": 0.05,
      "rationale": "R175H: heuristic HLA-A*02:01 anchor matrix",
      "source": "heuristic"
    }
  ]
}
```

The `source` field records which backend produced the call: `heuristic`,
`mhcflurry`, `openai`, or `mock`.

## Backends

| Backend | What it does | Setup |
|---|---|---|
| `heuristic` (default) | A*02:01 anchor matrix — fast, no deps | — |
| `mhcflurry` | Real pan-allele MHC-I binding affinity | `pip install -e ".[neoantigen-mhcflurry]"` |
| `openai` | LLM-as-judge for immunogenicity narrative | `OPENAI_API_KEY=...` |
| `mock` | Deterministic stdlib stub | always available |
| ESM2 (via `lm_immunogenicity_score`) | Frozen LM embeddings + Applm classifier | `pip install -e ".[protein-lm]"` |

## References

- TrambaHLApan: <https://link.springer.com/article/10.1007/s12539-025-00777-5>
- DeepNeo: <https://pmc.ncbi.nlm.nih.gov/articles/PMC10320182/>
- DeepHLApan: Wu et al. Front Immunol 2019
- ESM-2: Lin, Z., Akin, H., Rao, R., et al. (2023). Evolutionary-scale prediction
  of atomic-level protein structure with a language model. *Science*
  379(6637): 1123-1130.
- Applm pattern: Wong B.S.H., Kim J.M., Fung S.H., et al. (2025). Driving
  Accurate Allergen Prediction with Protein Language Models and
  Generalization-Focused Evaluation. arXiv 2508.10541.
