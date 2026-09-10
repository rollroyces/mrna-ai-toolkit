# `trial` — 病人對臨床試驗配對

TrialGPT 三階段流程的端到端簡化實作（Jin et al. *Nat Commun* 15, 9074, 2024）：

1. **Retrieval（檢索）** — 自病人摘要對候選試驗進行關鍵字比對。
2. **Matching（配對）** — 逐條條件評估收錄與否，並附理由說明。
3. **Ranking（排名）** — 將各條件分數彙整為單一的試驗等級排名。

## 用法

```bash
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl \
              --top-k 5 --backend mock
```

## 輸入

- **病人摘要** — 自由文字，英文臨床筆記效果最佳。
- **臨床試驗** — JSONL，每行一筆試驗：

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

## 輸出 schema

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

`score` = `eligibility_pct / 100 − 0.2 × (符合的排除條件數)`。分數最高的試驗即為建議配對。
