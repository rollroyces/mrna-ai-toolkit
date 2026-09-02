# Contributing

Pull requests welcome.

## Constraints

- **Stdlib-only core.** Tools that ship in the default install (`pip install -e .`) must depend only on the Python standard library. New deps go behind an `optional-dependencies` extra in `pyproject.toml`.
- **Determinism.** Tools must produce the same output for the same input (no timestamps in default outputs). Mock backends are always deterministic.
- **Schema validation.** LLM-backed tools must validate the response shape and fall back to the heuristic if the LLM returns malformed JSON.
- **Small CLI surface.** Each tool's `_run_cli` should accept `--out` and print to stdout if unset.

## Development

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e ".[dev,llm]"

# smoke test
bash scripts/smoke.sh

# docs locally
pip install -e ".[docs]"
mkdocs serve
```

## Pull request process

1. Open an issue first for non-trivial changes.
2. Fork, branch, commit with `[verified]` prefix once `bash scripts/smoke.sh` passes.
3. CI must be green on Python 3.11–3.14 before merge.
4. Squash-merge.
