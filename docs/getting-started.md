# Getting started

## Install

The core toolkit is **Python standard library only** — no installs required to
run `codon`, `neoantigen` (with the heuristic backend), `trial`, `lnp`, or
`scrna` (stdlib k-medoids fallback).

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .
```

This installs a single console script, `mrna-ai`, plus the `mrna_ai_tools` Python
package.

## Optional extras

Pull in extras for production-grade backends:

```bash
pip install -e ".[llm]"              # OpenAI-compatible LLM client
pip install -e ".[neoantigen-mhcflurry]"  # real binding-affinity prediction
pip install -e ".[scrna]"            # scanpy / anndata for clustering
pip install -e ".[all]"              # everything
```

## Backend resolution

For tools that can call an LLM or a model, the backend is chosen in this order:

1. `--backend <name>` CLI flag (highest priority)
2. `MRNA_AI_LLM_BACKEND` environment variable
3. Auto-detect: `mhcflurry` if installed → `openai` if `OPENAI_API_KEY` set → `mock`

See [Backends](backends.md) for the per-tool details.

## Verify

```bash
bash scripts/smoke.sh
```

This runs the four deterministic tools on the bundled example inputs and
prints sample outputs. Should complete in <2 s on a cold cache.
