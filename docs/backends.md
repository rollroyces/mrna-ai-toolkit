# Backends

The `neoantigen` and `trial` tools can call an LLM (or a trained model) for
inference. The `codon` and `lnp` tools are deterministic and never call a
model.

## Backend matrix

| Backend | What it does | Setup |
|---|---|---|
| `mock` | Heuristic / offline stub — fast, no deps | always available |
| `openai` | Calls OpenAI Chat Completions (or any OpenAI-compatible endpoint) | `OPENAI_API_KEY=...` |
| `mhcflurry` | Real pan-allele binding-affinity prediction | `pip install mhcflurry pandas` |

## `mock`

Default. Uses a hand-coded A*02:01 anchor matrix for `neoantigen` and keyword
overlap for `trial`. Useful for tests, CI, and offline experimentation.

## `openai`

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini        # default
export OPENAI_BASE_URL=https://api.openai.com/v1  # any compatible endpoint

mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend openai
```

The LLM is prompted to return a strict JSON object — the tool validates the
shape and falls back to the heuristic if the LLM doesn't follow it.

## `mhcflurry`

The mhcflurry backend uses the
[`Class1PresentationPredictor`](https://github.com/openvax/mhcflurry), a
pan-allele MHC-I binding + presentation model trained on mass-spec
eluted-ligand data.

```bash
pip install -e ".[neoantigen-mhcflurry]"

# First use downloads ~600 MB of model weights to ~/.mhcflurry/
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend mhcflurry
```

Output format is identical to the mock backend, but `binding_affinity_nM` and
`immunogenicity_score` come from the trained model rather than the anchor
heuristic. The `source` field reads `mhcflurry` to make this clear.

## Auto-detection

When `--backend auto` (the default), the tool picks the strongest available
backend in this order:

1. `mhcflurry` (if installed) — best for neoantigen scoring
2. `openai` (if `OPENAI_API_KEY` set) — needed for the trial matcher
3. `mock` — always works, deterministic, ~0 ms

This makes local dev painless and lets production deployments override via env
var or CLI flag.
