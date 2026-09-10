# `trial` — 患者到临床试验的匹配

TrialGPT 三阶段流程（Jin et al. *Nat Commun* 15, 9074, 2024）的端到端桩实现：

1. **检索（Retrieval）** —— 基于关键词重叠，从患者摘要中匹配候选临床试验。
2. **匹配（Matching）** —— 按入排标准逐条评估，并给出解释。
3. **排序（Ranking）** —— 将逐条标准得分聚合为单个试验级别的排序分。

## 用法

```bash
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl \
              --top-k 5 --backend mock
```

## 输入

- **患者摘要（Patient summary）** —— 自由文本。纯英文临床记录效果最佳。
- **临床试验（Trials）** —— JSONL，每行一条试验记录：

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

## 输出 schema

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

`score` = `eligibility_pct / 100 − 0.2 × (met exclusion criteria)`。
得分最高的试验即为推荐匹配项。
