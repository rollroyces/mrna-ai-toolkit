# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-02

### Added
- **New `scrna` tool** — scRNA-seq → tumor-cluster → mutant peptide → neoantigen handoff pipeline. Stdlib k-medoids fallback; upgrades to scanpy Leiden when `[scrna]` extra is installed.
- **`mhcflurry` backend for `neoantigen`** — real pan-allele binding-affinity prediction via `Class1PresentationPredictor`. Activates automatically when `mhcflurry` is installed.
- **`pyproject.toml`** with proper extras (`[llm]`, `[neoantigen-mhcflurry]`, `[scrna]`, `[docs]`, `[all]`, `[dev]`) and a `mrna-ai` console script.
- **MkDocs Material site** under `docs/`, deployed to GitHub Pages on push to `main`.
- **GitHub Pages deploy workflow** (`.github/workflows/docs.yml`).

### Changed
- Bumped `__version__` to `0.2.0`.
- CLI dispatcher now lists `scrna` alongside the original four tools.
- `neoantigen --backend` choices extended with `mhcflurry` (and `mock`).
- Backend auto-detection now picks `mhcflurry` over `openai` over `mock`.

## [0.1.0] - 2026-09-02

### Added
- Initial release of the four AI-leverage tools: `codon`, `neoantigen`, `trial`, `lnp`.
- Shared `llm.py` wrapper supporting `mock` and `openai` backends.
- CLI dispatcher.
- Sample outputs for all four tools in `examples/sample_outputs/`.
- GitHub Actions smoke-test workflow (Python 3.11–3.14).
- Local smoke-test script (`scripts/smoke.sh`).
- Dual AGPL-3.0-or-later + commercial license.
