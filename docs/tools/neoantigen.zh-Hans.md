# `neoantigen` — 肽 × HLA 筛选

对候选新抗原进行肽–MHC 结合与免疫原性打分。

## 用法

```bash
# 默认：启发式 A*02:01 锚定位矩阵
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01

# 真实的结合亲和力预测（mhcflurry）
pip install -e ".[neoantigen-mhcflurry]"
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend mhcflurry

# OpenAI LLM
export OPENAI_API_KEY=...
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend openai
```

## 输入 CSV

```csv
variant,peptide
R175H,HMTEVVRRC
R248Q,QMNRRPGMT
```

`peptide` 是唯一必填列。`variant` 会保留在 `rationale` 中。

## 输出 schema

```json
{
  "hla": ["HLA-A*02:01"],
  "candidates": [
    {
      "peptide": "HMTEVVRRC",
      "hla": "HLA-A*02:01",
      "binding_affinity_nM": 3298.8,
      "binder": false,
      "immunogenicity_score": 0.05,
      "rationale": "R175H: heuristic HLA-A*02:01 anchor matrix",
      "source": "heuristic"
    }
  ]
}
```

`source` 字段记录产生该结果的后端：`heuristic`、`mhcflurry`、`openai` 或 `mock`。
