# mRNA × AI Toolkit

> Practical Python tools for the AI-leverage layers in mRNA cancer therapy.
> Stdlib-only core, seven runnable tools, eight real-model adapters behind
> Protocol contracts, three documentation locales, 167 tests, 25 backend
> integrity checks.

## What this is

Seven small, runnable tools that map 1-to-1 onto the published AI leverage
points in mRNA cancer therapeutics — plus a typed integration contract for
every published foundation model in the field. Each tool runs as a CLI
subcommand and imports cleanly as a Python module.

| Tool | What it does | AI leverage layer | Reference work integrated |
|---|---|---|---|
| `codon` | Codon analysis + LinearDesign DP + RiboDecode heuristic | Sequence design | CodonBERT, RiboDecode (Li et al., *Nat Commun* 2025), LinearDesign |
| `neoantigen` | Peptide × HLA binding + ESM2 LM immunogenicity scoring | Variant prioritization | mhcflurry, MedCPT, DeepNeo, NetMHCpan, ESM2 + Applm pattern (Wong et al., 2025) |
| `trial` | TrialGPT per-criterion LLM matching + Sim-ICL demo selection | Patient-trial matching | TrialGPT (Jin et al., *Nat Commun* 2024) + Sim-ICL (Fung et al., *Genome Biol* 2026) |
| `scrna` | scRNA-seq → tumor cluster → mutant peptides → ESM2 immunogenicity | Single-cell foundation | scGPT (Cui et al., *Nat Methods* 2024) |
| `manufacture` | mRNA manufacturability checks (poly-A, Kozak, GC, ARE, stops) | Wet-lab | Industry mRNA design guidelines |
| `lnp` | LNP composition recommender | Wet-lab | Witten 2025, Li 2024 |
| `spatial` | STModule spatial-transcriptomics tissue-module identification | Spatial transcriptomics | STModule (Wang et al., *Genome Medicine* 2025) |

**Real-model adapters behind Protocol contracts** (opt-in via `pip install` extras):

- `RiboDecode` → `pip install -e .[ribodecode]` (heavy: ViennaRNA + CUDA via subprocess)
- `STModule` → `pip install -e .[spatial-r]` (heavy: R + Seurat + torch + CUDA via subprocess)
- `ESM2 protein-LM` → `pip install -e .[protein-lm]` (heavy: torch + transformers, ~135 MB)
- `AlphaMissense` → standalone Python pickle index from user-downloaded TSV
- `scGPT` → `pip install -e .[scrna]` (heavy: torch, ~205 MB)
- `mhcflurry` → `pip install -e .[neoantigen-mhcflurry]`
- `MedCPT` → `pip install -e .[neoantigen-medcpt]` or `[trial-medcpt]` (heavy: torch + transformers, ~440 MB)
- `TrialGPT/OpenAI` → `pip install -e .[llm]`

Every adapter has a **mock backend** that satisfies the same `runtime_checkable`
Protocol using only stdlib, so CI runs without downloading any model weights.

## Quick start

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .                   # stdlib-only core

# 1. Codon analysis (CAI, GC%, rare-codon, GC-window stddev)
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta \
    --optimize --backend lineardesign

# 2. Neoantigen screen (heuristic anchor matrix + LLM immunogenicity)
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01

# 3. Patient-to-trial matching (TrialGPT-style, optionally Sim-ICL)
python -m mrna_ai_tools.cli trial \
    --patient mrna_ai_tools/examples/patient_summary.txt \
    --trials mrna_ai_tools/examples/trials.jsonl --top-k 5 \
    --matcher trialgpt-simicl

# 4. LNP composition advice
python -m mrna_ai_tools.cli lnp --target lung --cargo saRNA --intent "cancer vaccine"

# 5. scRNA-seq → neoantigen handoff
python -m mrna_ai_tools.cli scrna \
    --expression mrna_ai_tools/examples/cells.csv \
    --variants mrna_ai_tools/examples/variants_coding.csv \
    --proteins mrna_ai_tools/examples/proteins.fasta \
    --tumor-markers TP53,KRAS,BRAF

# 6. mRNA manufacturability score
python -m mrna_ai_tools.cli manufacture --cds mrna_ai_tools/examples/cds_gfp.json

# 7. Spatial transcriptomics tissue modules
python -m mrna_ai_tools.cli spatial \
    --count-file mrna_ai_tools/examples/st_bc2_count_matrix.tsv \
    --locations-file mrna_ai_tools/examples/st_bc2_locations.tsv \
    --platform ST --num-modules 10
```

After `pip install -e .`, the same CLI is also installed as the console
script `mrna-ai`.

Sample outputs for every tool are committed under `examples/sample_outputs/`.

## Optional extras

```bash
pip install -e ".[llm]"                       # OpenAI-compatible LLM client (TrialGPT)
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry binding-affinity backend
pip install -e ".[neoantigen-medcpt]"          # MedCPT query/article encoders (~440 MB)
pip install -e ".[protein-lm]"                # ESM2 protein language model (~135 MB)
pip install -e ".[trial-medcpt]"               # MedCPT for trial retrieval
pip install -e ".[scrna]"                     # scanpy + anndata + scGPT plug point
pip install -e ".[docs]"                      # mkdocs-material + mkdocs-static-i18n
pip install -e ".[dev]"                       # ruff + pytest
pip install -e ".[all]"                       # everything above
```

Then activate the real backend:

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini               # default
python -m mrna_ai_tools.cli trial \
    --patient mrna_ai_tools/examples/patient_summary.txt \
    --trials mrna_ai_tools/examples/trials.jsonl --backend openai
```

Heavy-dependency backends (RiboDecode, STModule, ESM2, MedCPT, scGPT) ship
adapter modules that **subprocess or lazy-load** the upstream model. CI
runs without them; production users opt in per-extras above.

## Documentation

Full MkDocs site: <https://rollroyces.github.io/mrna-ai-toolkit/>

Available in three languages:

- 🇺🇸 English — <https://rollroyces.github.io/mrna-ai-toolkit/>
- 🇹🇼 繁體中文 — <https://rollroyces.github.io/mrna-ai-toolkit/zh-Hant/>
- 🇨🇳 简体中文 — <https://rollroyces.github.io/mrna-ai-toolkit/zh-Hans/>

Subsequent pushes to `main` deploy all three locales automatically via
GitHub Pages.

Local preview:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Real-model integrations

Every published foundation model is integrated behind a typed `Protocol`
adapter with a stdlib-only mock fallback. The adapter contract is identical
for production and CI — only the implementation differs.

### `RiboDecode` (Li et al., *Nat Commun* 16, 9957, 2025)

Joint translation × secondary-structure codon optimization via a deep
generative model. Heavy deps (ViennaRNA 2.6.4 + CUDA), shipped as a
subprocess adapter that calls the upstream CLI when present.

```bash
# Real: when ribo-decode is installed + Rscript on $PATH
mrna-ai codon --sequence gfp.fasta --optimize --backend ribodecode-real \
    --env HEK293T --env-csv custom_env.csv --mfe-weight 0.3 --optim-epoch 10

# Mock: same shape, stdlib only
mrna-ai codon --sequence gfp.fasta --optimize --backend ribodecode
```

### `STModule` (Wang et al., *Genome Medicine* 17, 2025)

Tissue-module identification from spatial-transcriptomics (SRT) data.
Heavy deps (R 4.4 + Seurat v5 + torch + GPUmatrix 1.0.2 + CUDA 11.7),
shipped via a small R shim that shells out to `Rscript stmodule_shim.R`.

```bash
# Real: when R + STModule are installed
mrna-ai spatial --count-file counts.tsv --locations-file locs.tsv \
    --platform SlideSeqV2 --num-modules 10

# Mock: same shape, stdlib only
mrna-ai spatial --count-file counts.tsv --locations-file locs.tsv \
    --platform ST --num-modules 10
```

### `ESM2` + Applm pattern (Wong et al., 2025)

Frozen protein-LM embeddings for neoantigen immunogenicity scoring.
Heavy deps (torch + transformers), shipped as a lazy-loaded adapter.

```python
from mrna_ai_tools.neoantigen_screener import lm_immunogenicity_score
r = lm_immunogenicity_score("NLVPMVATV")  # CMV pp65 epitope
print(r["score"])  # 0.0–1.0
```

### `TrialGPT` + `Sim-ICL` (Jin 2024 / Fung 2026)

Per-criterion patient-trial eligibility matching. Sim-ICL selects
top-K demonstration examples by TF-IDF cosine similarity (not random
sampling) — matching the paper's finding that sequence-similar
demonstrations outperform random few-shot.

```bash
mrna-ai trial --patient patient.txt --trials trials.jsonl \
    --matcher trialgpt-simicl --top-k 10
```

### Other real-model integrations

- **`AlphaMissense`** (Cheng et al., *Science* 381, 2023) — variant
  pathogenicity via 71M-variant TSV; bundled pickle index for O(1)
  per-variant lookup.
- **`scGPT`** (Cui et al., *Nat Methods* 21, 2024) — single-cell
  foundation-model embeddings, 30 layers × 512 dim.
- **`mhcflurry`** (O'Donnell et al.) — Class I MHC binding affinity,
  IC50 in nM.
- **`MedCPT`** (Jin et al., 2023) — biomedical dense retrieval,
  contrastively trained on PubMed.

## Architecture rationale

The toolkit's `backends.py` integrity checks use **deterministic
structural assertions** rather than AUPRC / F1 / accuracy metrics from
heavy libraries. Chen et al. 2024 (*Genome Biology* 25, 118) evaluated
10 widely-used PRC tools across >3,000 published studies and found
they produce **conflicting AUPRC rankings and overly-optimistic results**.
The toolkit's stdlib-only baseline avoids that entire class of bug by
owning the metric end-to-end.

See `docs/index.md` for the full rationale.

## Real-world case studies (grounded in published biology)

The toolkit's scRNA → neoantigen pipeline is validated against the
wet-lab workflow in Qian et al. 2022 (*Int J Cancer* 151, 1367-1381):
scRNA-seq of gastric cancer primary tumor + lymph node metastases →
tumor cluster identification → mutant peptide enumeration → ESM2
immunogenicity scoring → mRNA cancer vaccine design. See
`docs/tools/scrna.md` for the full walkthrough.

## Why seven layers (and not four or five)?

The mRNA cancer therapy research has reached an inflection point where
foundation models for **sequence design**, **variant prioritization**,
**neoantigen prediction**, **single-cell foundation**, **spatial
transcriptomics**, **patient-trial matching**, and **manufacturing
checks** are all simultaneously advancing. The toolkit's job is to
be the integration layer — every published model plugs in via a
Protocol contract with a stdlib-only mock fallback for tests and
offline use.

1. **Sequence design** (`codon`): LinearDesign (real, O(L) DP, no cap)
   + RiboDecode-style context heuristic. Powers any mRNA construct.
2. **Variant prioritization** (`variant_scorer`): AlphaMissense TSV
   lookup + BLOSUM62 + driver-gene awareness + Chou-Fasman structural
   disruption. AM weighted at 45%.
3. **Neoantigen prediction** (`neoantigen`): mhcflurry IC50 +
   ESM2 LM immunogenicity. Frozen-LM-then-classifier pattern.
4. **Single-cell foundation** (`scrna`): scGPT embeddings → tumor
   cluster identification → mutant peptide handoff.
5. **Spatial transcriptomics** (`spatial`): STModule tissue-module
   identification. Spatial coordinates reveal where the tumor
   cluster lives.
6. **Patient-trial matching** (`trial`): TrialGPT per-criterion LLM +
   Sim-ICL demonstration selection. Real + keyword fallback.
7. **Manufacturability** (`manufacture`): poly-A runs, Kozak strength,
   GC window uniformity, ARE motifs, hidden stops, CpG balance.
8. **LNP delivery** (`lnp`): ionizable-lipid pKa, helper-lipid ratio,
   composition shortlist above published ML-discovered candidates.

## Development

```bash
# Run all backend integrity checks (matches CI)
python -m mrna_ai_tools.backends --check-all

# Run the unit test suite
python -m unittest discover tests

# Run on the bundled examples (see scripts/smoke.sh)
bash scripts/smoke.sh

# Build docs locally
pip install -e ".[docs]"
mkdocs serve
```

## License

Dual-licensed. See `LICENSE` for the dual-license summary and `LICENSE-AGPL`
for the AGPL-3.0-or-later terms. A commercial license is available on
request — open an issue on the GitHub repo.

## Publishing to PyPI

The toolkit ships **trusted publishing** via GitHub Actions OIDC —
no long-lived PyPI tokens to manage. The workflow lives in
`.github/workflows/publish.yml`.

### One-time setup

1. Register a pending trusted publisher at
   <https://pypi.org/manage/account/publishing/>:
   - Owner: `rollroyces`
   - Repository: `mrna-ai-toolkit`
   - Workflow file: `publish.yml`
   - Environment: `pypi`
2. In GitHub repo **Settings → Environments**, create the `pypi`
   environment — require reviewer approval before deploy
   (recommended for production deploys).

### Release flow

```bash
# 1. Bump version in mrna_ai_tools/__init__.py + pyproject.toml
# 2. Commit + tag
git commit -am "release: v0.14.0"
git tag v0.14.0
git push --follow-tags

# 3. CI does the rest:
#    a. build job  → builds sdist + wheel, verifies version matches tag
#    b. publish-to-pypi → uploads to PyPI (after manual approval of
#                          the 'pypi' environment)
```

PEP 740 attestations are auto-generated by `pypa/gh-action-pypi-publish@release/v1`.

### Manual fallback (no trusted publisher configured)

If you haven't registered a trusted publisher yet, you can fall back
to a long-lived API token:

```bash
# Generate a token at https://pypi.org/manage/account/token/
python -m pip install --upgrade build twine
python -m build --sdist --wheel
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-... \
    python -m twine upload dist/mrna_ai_toolkit-*
```

You'll need a PyPI token — generate one at
<https://pypi.org/manage/account/token/> and either pass it via
`TWINE_PASSWORD` (with `TWINE_USERNAME=__token__`) or store it in `~/.pypirc`.

## Contributing

Pull requests welcome. The default dependency surface is **Python stdlib
only** — heavy model integrations must plug into a backend selector via
the existing Protocol-based adapter pattern (see `mrna_ai_tools/codon_ribodecode_adapter.py`,
`mrna_ai_tools/spatial_module_adapter.py`, `mrna_ai_tools/protein_lm_adapter.py`
for reference).

Every new tool should ship with:

1. A typed dataclass for input + output (frozen, validated at construction).
2. A `runtime_checkable` Protocol for the backend interface.
3. A real adapter that shells out / lazy-loads the upstream model.
4. A stdlib-only mock that satisfies the same Protocol.
5. A `register()` entry in `backends.py` for CI integrity.
6. Tests in `tests/` following strict TDD.
