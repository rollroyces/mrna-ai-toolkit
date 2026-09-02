# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-02

### Added
- Initial release of the four AI-leverage tools:
  - `codon` — codon-usage analysis (CAI, GC%, rare-codons, CpG obs/exp) + greedy optimizer
  - `neoantigen` — peptide × HLA binding + immunogenicity scoring via LLM, with A*02:01 heuristic fallback
  - `trial` — TrialGPT-style retrieve → match → rank pipeline
  - `lnp` — LNP composition recommender (clinical + ML-discovered lipids)
- Shared `llm.py` wrapper supporting `mock` and `openai` backends
- CLI dispatcher (`python -m mrna_ai_tools.cli <tool> ...`)
- Sample outputs for all four tools in `examples/sample_outputs/`
- GitHub Actions smoke-test workflow (Python 3.11–3.14)
- Local smoke-test script (`scripts/smoke.sh`)
- Dual AGPL-3.0-or-later + commercial license
