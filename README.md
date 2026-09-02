# mRNA × AI Toolkit

> Practical Python tools for the AI-leverage layers in mRNA cancer therapy.
> Stdlib-only, no installs, ~500 LOC.

## What this is

Four small, runnable tools that map 1-to-1 onto the AI leverage points where
LLMs and ML models are currently transforming mRNA cancer therapeutics:

| Tool | AI leverage layer | Reference work it integrates |
|---|---|---|
| `codon` | Codon-usage analysis + greedy optimizer | CodonBERT, RiboDecode, LinearDesign, mRNABERT |
| `neoantigen` | Peptide × HLA binding + immunogenicity scoring (LLM) | TrambaHLApan, DeepNeo, DeepHLApan, NetMHCpan |
| `trial` | TrialGPT-style retrieve → match → rank pipeline | Jin et al. *Nat Commun* 15, 9074 (2024) |
| `lnp` | LNP composition recommender (published + ML-discovered) | Witten et al. *Nat Biotech* 43, 1790 (2025), Li et al. *Nat Mater* 23, 1002 (2024) |

Each tool runs as a CLI subcommand and also imports cleanly as a Python module.

## Quick start

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .                   # stdlib-only core

# 1. Codon analysis
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize

# 2. Neoantigen screen (heuristic A*02:01 anchor matrix by default)
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01

# 3. Patient-to-trial matching (TrialGPT-style)
python -m mrna_ai_tools.cli trial \
    --patient mrna_ai_tools/examples/patient_summary.txt \
    --trials mrna_ai_tools/examples/trials.jsonl --top-k 5

# 4. LNP composition advice
python -m mrna_ai_tools.cli lnp --target lung --cargo saRNA --intent "cancer vaccine"
python -m mrna_ai_tools.cli lnp --target liver --cargo Cas9 --intent "gene editing"

# 5. scRNA-seq → neoantigen handoff
python -m mrna_ai_tools.cli scrna \
    --expression mrna_ai_tools/examples/cells.csv \
    --variants mrna_ai_tools/examples/variants_coding.csv \
    --proteins mrna_ai_tools/examples/proteins.fasta \
    --tumor-markers TP53,KRAS,BRAF
```

After `pip install -e .`, the same CLI is also installed as the console
script `mrna-ai`:

```bash
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv --hla HLA-A*02:01
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt --trials mrna_ai_tools/examples/trials.jsonl
mrna-ai lnp --target lung --cargo saRNA
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv --variants mrna_ai_tools/examples/variants_coding.csv --proteins mrna_ai_tools/examples/proteins.fasta --tumor-markers TP53,KRAS,BRAF
```

Sample outputs for all five tools are committed under `examples/sample_outputs/`.

## Optional extras

```bash
pip install -e ".[llm]"                       # OpenAI-compatible LLM client
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry>=2.0 pandas
pip install -e ".[scrna]"                     # scanpy / anndata for clustering
pip install -e ".[all]"                       # everything
```

Then activate the real backend:

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini               # default
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend openai
```

Auto-detection order: `mhcflurry` (if installed) → `openai` (if `OPENAI_API_KEY` set) → `mock`.

## Documentation

Full MkDocs site: <https://rollroyces.github.io/mrna-ai-toolkit/>

Local preview:

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Wiring a real LLM

The `neoantigen` and `trial` tools call an LLM by default. To plug in a real
model, export your API key:

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini            # or any OpenAI-compatible model
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend openai
```

The `codon` and `lnp` tools are deterministic and don't call any LLM.

## Why these four layers?

The mRNA cancer therapy research identified four AI-leverage layers where
**either no foundation model exists yet, or where the existing models can
be plugged into a clean deterministic interface** — which is exactly what
this toolkit provides.

1. **Sequence design** (codon): CodonBERT / RiboDecode / LinearDesign / mRNABERT
   take per-codon and per-region statistics as inputs. The codon analyzer
   here emits exactly those features (CAI, GC%, rare-codon fraction, CpG
   obs/exp, GC window stddev). Drop it in as a feature provider.

2. **Neoantigen prediction**: TrambaHLApan (2025), DeepNeo (2023), DeepHLApan
   (2019), NetMHCpan (4.1) are the field's standards. The LLM-prompt
   interface here replaces them when you don't have a GPU handy, and the
   heuristic A*02:01 fallback is a useful sanity baseline.

3. **Trial matching**: TrialGPT itself is an LLM pipeline (retrieval →
   matching → ranking). The published benchmark reports 87.3% accuracy on
   criterion-level matching and 42.6% reduction in screening time. A clean
   open-source stub is genuinely useful.

4. **LNP composition**: Witten et al. 2025 trained a directed message-passing
   neural network on >9,000 LNP measurements and screened 1.6M candidates in
   silico. Li et al. 2024 used combinatorial chemistry + ML. The recommender
   here is the human-facing shortlist layer above those models.

## Development

```bash
# Run the full smoke test (matches CI):
for tool in codon neoantigen trial lnp; do
  python -m mrna_ai_tools.cli $tool --help
done

# Run on the bundled examples (see scripts/smoke.sh):
bash scripts/smoke.sh
```

## License

Dual-licensed. See `LICENSE` for the dual-license summary and `LICENSE-AGPL`
for the AGPL-3.0-or-later terms. A commercial license is available on
request — open an issue on the GitHub repo.

## Publishing to PyPI

The wheel and sdist are pre-built and attached to every GitHub release.

To publish a new version:

```bash
# 1. Bump version in mrna_ai_tools/__init__.py
# 2. Build
python -m pip install --upgrade build twine
python -m build --sdist --wheel
# 3. Upload (Test PyPI first, then real)
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

You'll need a PyPI token — generate one at
<https://pypi.org/manage/account/token/> and either pass it via
`TWINE_PASSWORD` (with `TWINE_USERNAME=__token__`) or store it in `~/.pypirc`.

## Contributing

Pull requests welcome. Please keep the dependency surface at zero (Python
stdlib only). External model integrations should plug into the backend
abstraction in `mrna_ai_tools/llm.py`.
