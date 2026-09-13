# `trial` — patient-to-trial matching

End-to-end implementation of the three-stage TrialGPT pipeline
(Jin et al. *Nat Commun* 15, 9074, 2024):

1. **Retrieval** — keyword overlap from the patient summary to candidate trials.
2. **Matching** — criterion-level eligibility, with explanations.
3. **Ranking** — aggregate criterion scores to a single trial-level rank.

Two matcher backends ship: plain TrialGPT (zero-shot per-criterion LLM
judging) and **Sim-ICL** (similarity-ranked few-shot demonstration
selection).

## Usage

```bash
# Plain TrialGPT (zero-shot per-criterion LLM)
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl \
              --top-k 5 --matcher trialgpt --backend openai

# Sim-ICL: similarity-ranked few-shot demos (Fung et al. 2026)
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl \
              --top-k 5 --matcher trialgpt-simicl --backend openai

# Mock backend (no API key needed; uses heuristic per-criterion judge)
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl \
              --top-k 5 --matcher trialgpt --backend mock
```

## Sim-ICL demonstration selection

For low-shot regimes (e.g. you have <100 labelled patient-trial pairs),
**selecting demonstrations by similarity to the query** outperforms
random sampling. This is the Sim-ICL finding from Fung et al. 2026
(*Genome Biology*, in press).

The toolkit's `trial_similar.py`:

1. Stores 12+ demonstration triples (`{patient, trial, ground_truth_verdicts}`)
   in `examples/simicl_demos.json` (overridable via
   `$MRNA_AI_SIMICL_DEMOS`).
2. On each new query, ranks all stored demos by **TF-IDF cosine
   similarity** of `(patient + trial)` text.
3. Prepends the top-K demos (default `K=32`, `$MRNA_AI_SIMICL_TOPK`)
   to the prompt before asking the LLM for verdicts.

For a **BRAF V600E melanoma** patient query, the ranker correctly
returns all 3 BRAF-melanoma trials in the top 3 — perfect biological
relevance.

```python
from mrna_ai_tools.trial_llm import score_trial_with_llm
from mrna_ai_tools.trial_similar import load_default_demo_store

result = score_trial_with_llm(
    patient_text="55yo BRAF V600E melanoma patient",
    nct_id="NCT_TEST",
    title="BRAF melanoma trial",
    inclusion=["metastatic melanoma", "BRAF V600E"],
    exclusion=["prior systemic therapy"],
    backend="openai",
    demo_store=load_default_demo_store(),
    use_simicl=True,
)
# result.notes contains "simicl-k12" and the demo IDs used
```

**Env-var knobs:**

- `MRNA_AI_SIMICL_TOPK` — number of demos to inject (default 32).
- `MRNA_AI_SIMICL_ENABLED` — set to `0` to disable even when a demo
  store is loaded.
- `MRNA_AI_SIMICL_DEMOS` — path to a JSON file of the canonical shape.

## Input

- **Patient summary** — free text. Plain English clinical notes work best.
- **Trials** — JSONL with one trial per line:

```json
{
  "nct_id": "NCT05933577",
  "title": "INTerpath-001: Personalized mRNA-4157 + Pembrolizumab",
  "condition": "Stage IIB-IV melanoma",
  "phase": "3",
  "inclusion": ["Completely resected melanoma", "ECOG 0 or 1"],
  "exclusion": ["Active autoimmune disease"],
  "biomarkers": ["BRAF V600E", "BRAF V600K"]
}
```

## Output schema

```json
{
  "ranked": [
    {
      "nct_id": "NCT05933577",
      "title": "INTerpath-001: ...",
      "score": 1.0,
      "eligibility_pct": 100.0,
      "n_met": 4,
      "n_total": 4,
      "reasons": ["Completely resected melanoma", "ECOG 0 or 1"]
    }
  ],
  "n_candidates_screened": 5
}
```

`score` = `eligibility_pct / 100 − 0.2 × (met exclusion criteria)`. The
trial with the highest score is the recommended match.

## Matchers

| Matcher | What it does |
|---|---|
| `trialgpt` (default) | Per-criterion LLM matching. Zero-shot prompting. |
| `trialgpt-simicl` | Per-criterion LLM matching with similarity-ranked few-shot demos (Sim-ICL). |
| `keyword` | Heuristic keyword-overlap scoring — fast, no LLM. |
| `auto` | Uses `trialgpt` if `OPENAI_API_KEY` is set, else falls back to `keyword`. |

## References

- Jin Q., et al. (2024). Matching patients to clinical trials with
  large language models. *Nature Communications* 15: 9074.
- Fung S.H., Zhang Z., Wang R., Miao C., Wong B.S.H., Li K.Y., Hong C.,
  Zhou J., Yip K.Y.#, Tsui S.K.W.#, and Cao Q.#. (2026). A Systematic
  Evaluation of In-Context Learning in Large Language Models for
  Antibody Characterization. *Genome Biology* (in press).
