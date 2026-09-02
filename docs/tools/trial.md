# `trial` — patient-to-trial matching

End-to-end stub of the three-stage TrialGPT pipeline
(Jin et al. *Nat Commun* 15, 9074, 2024):

1. **Retrieval** — keyword overlap from the patient summary to candidate trials.
2. **Matching** — criterion-level eligibility, with explanations.
3. **Ranking** — aggregate criterion scores to a single trial-level rank.

## Usage

```bash
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl \
              --top-k 5 --backend mock
```

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
