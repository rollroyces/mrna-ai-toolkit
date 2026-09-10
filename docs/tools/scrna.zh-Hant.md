# `scrna` — scRNA-seq → 新抗原銜接流程

從組織到疫苗設計的閉環：

1. 載入 AnnData（h5ad）或 CSV/TSV（細胞 × 基因）表現量矩陣。
2. 對細胞進行分群——若已安裝 scanpy，採 Leiden 演算法，否則使用標準函式庫的 k-medoids。
3. 鑑別腫瘤集群（依使用者提供的標記基因，預設為細胞數最多的集群）。
4. 對位於腫瘤集群表現基因上、且屬於編碼區 SNV 的每筆變異：
   - 列舉覆蓋變異位點的 9–11 個胺基酸長之胜肽。
5. 將胜肽清單交棒給新抗原篩選器。

## 用法

```bash
# 僅使用標準函式庫（以合成表現量資料 + k-medoids）
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv \
              --variants mrna_ai_tools/examples/variants_coding.csv \
              --proteins mrna_ai_tools/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180

# 使用 scanpy（真正的 Leiden 分群）
pip install -e ".[scrna]"
mrna-ai scrna --expression path/to/cells.h5ad ...
```

## 輸入檔案

- **Expression（表現量）** — 細胞 × 基因 的 CSV/TSV。若檔案不存在，則使用確定性的 50 細胞 × 200 基因合成資料集，使流程仍可繼續執行。
- **Variants（變異）** — CSV，欄位為 `gene,position,wt_aa,mut_aa`。
- **Proteins（蛋白質）** — 多序列 FASTA，每個基因符號對應一條蛋白質序列。

## 輸出 schema

```json
{
  "n_cells": 50,
  "n_genes": 200,
  "cluster_labels": [0, 0, ...],
  "cluster_marker_scores": {"0": 0.34, "1": 0.41, "2": 2.87},
  "tumor_cluster": 2,
  "n_variants_input": 7,
  "n_candidate_peptides": 24,
  "peptides": [
    {
      "cell_cluster": 2,
      "gene": "TP53",
      "position": 175,
      "wt_aa": "R",
      "mut_aa": "H",
      "peptide": "HMTEVVRRC",
      "length": 9,
      "cluster_marker_score": 2.87
    }
  ]
}
```

## 與 scGPT 的整合

`sc_rna_pipeline.py` 中的 `embed_with_foundation_model` 函式，是 scGPT、Geneformer 或 UNI-RNA 嵌入的明確接入點。兩者皆未安裝時，流程會退而採用恆等嵌入（每細胞的平均表現量），此方式足以應付 k-medoids 分群，但不足以做精細的細胞類型鑑定。

接入 scGPT 的方式：

```python
# 於自訂的整合腳本中：
from mrna_ai_tools.sc_rna_pipeline import (
    cluster_with_scanpy, embed_with_foundation_model
)
import scgpt  # 請使用您已安裝的版本

embeddings = scgpt.embed(my_adata)  # 視當前 API 而定
labels = cluster_with_scanpy(embeddings, cell_ids, gene_names)
```

本套件中的 `embed_with_foundation_model` 是一個薄包裝，僅用於記載整合方式，本身並不依賴 scgpt。
