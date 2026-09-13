# Getting started

## Install

The core toolkit is **Python standard library only** — no installs required
to run `codon`, `neoantigen` (with the heuristic backend), `trial`,
`manufacture`, `lnp`, `scrna` (stdlib k-medoids fallback), or `spatial`
(mock backend).

```bash
git clone https://github.com/rollroyces/mrnavax.git
cd mrnavax
pip install -e .
```

This installs a single console script, `mrnavax`, plus the `mrnavax`
Python package.

## Optional extras

Pull in extras for production-grade backends:

```bash
pip install -e ".[llm]"                       # OpenAI-compatible LLM client (TrialGPT)
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry binding-affinity
pip install -e ".[neoantigen-medcpt]"          # MedCPT for neoantigen retrieval
pip install -e ".[protein-lm]"                # ESM2 protein-LM for immunogenicity
pip install -e ".[trial-medcpt]"               # MedCPT for trial retrieval
pip install -e ".[scrna]"                     # scanpy / anndata / scGPT plug point
pip install -e ".[docs]"                      # mkdocs-material + mkdocs-static-i18n
pip install -e ".[dev]"                       # ruff + pytest
pip install -e ".[all]"                       # everything
```

## Backend resolution

For tools that can call an LLM or a heavy model, the backend is chosen
in this order:

1. `--backend <name>` CLI flag (highest priority)
2. Tool-specific env var (e.g. `MRNA_AI_LLM_BACKEND`, `MRNA_AI_SIMICL_TOPK`)
3. Auto-detect: upstream binary on `$PATH` (e.g. `Rscript` for STModule,
   `pred-translation` for RiboDecode) → installed Python deps
   (transformers for ESM2, mhcflurry for binding, OpenAI for LLM) → mock

See [Backends](backends.md) for the per-tool details.

## Verify

```bash
# Run the 25 backend integrity checks
python -m mrnavax.backends --check-all

# Run the unit test suite (167 tests)
python -m unittest discover tests

# Run the bundled example scripts (see scripts/smoke.sh)
bash scripts/smoke.sh
```

The smoke script runs every deterministic tool on the bundled example
inputs and prints sample outputs. Should complete in <2 s on a cold cache.
