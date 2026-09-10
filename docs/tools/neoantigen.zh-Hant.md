# `neoantigen` — 胜肽 × HLA 篩選

為候選新抗原（neoantigen）評估胜肽–MHC 結合與免疫原性分數。

## 用法

```bash
# 預設：啟發式 A*02:01 錨定矩陣
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01

# 真實的結合親和性預測（mhcflurry）
pip install -e ".[neoantigen-mhcflurry]"
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend mhcflurry

# OpenAI LLM
export OPENAI_API_KEY=...
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv \
                   --hla HLA-A*02:01 --backend openai
```

## 輸入 CSV

```csv
variant,peptide
R175H,HMTEVVRRC
R248Q,QMNRRPGMT
```

`peptide` 是唯一必要欄位；`variant` 會原樣保留於評估理由中。

## 輸出 schema

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

`source` 欄位記錄產生此次評估的後端：`heuristic`、`mhcflurry`、`openai` 或 `mock`。
