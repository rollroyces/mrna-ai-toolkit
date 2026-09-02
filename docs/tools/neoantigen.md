# `neoantigen` — peptide × HLA screening

Scores peptide-MHC binding and immunogenicity for candidate neoantigens.

## Usage

```bash
# Default: heuristic A*02:01 anchor matrix
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01

# Real binding-affinity prediction (mhcflurry)
pip install -e ".[neoantigen-mhcflurry]"
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend mhcflurry

# OpenAI LLM
export OPENAI_API_KEY=...
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend openai
```

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
