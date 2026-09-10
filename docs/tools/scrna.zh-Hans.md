# `scrna` — scRNA-seq → 新抗原交接流程

打通从组织样本到疫苗设计之间的完整闭环：

1. 加载 AnnData（h5ad）或 CSV/TSV（细胞 × 基因）表达矩阵。
2. 对细胞进行聚类 —— 若已安装 scanpy 则使用 Leiden 算法，否则使用标准库的 k-medoids。
3. 识别肿瘤聚类（按提供的标记基因，或默认取最大的聚类）。
4. 对位于肿瘤聚类表达基因上的每个编码区 SNV 变异：
   - 枚举覆盖该变体的 9–11 肽。
5. 将肽列表交接给新抗原筛选器。

## 用法

```bash
# 仅依赖标准库（使用合成表达数据 + k-medoids）
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv \
              --variants mrna_ai_tools/examples/variants_coding.csv \
              --proteins mrna_ai_tools/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180

# 使用 scanpy（真正的 Leiden 聚类）
pip install -e ".[scrna]"
mrna-ai scrna --expression path/to/cells.h5ad ...
```

## 输入文件

- **表达矩阵（Expression）** —— 细胞 × 基因的 CSV/TSV。若文件不存在，则使用一组
  确定性的 50 细胞 × 200 基因合成数据集，以便流程其余环节仍可运行。
- **变异（Variants）** —— CSV，包含列 `gene,position,wt_aa,mut_aa`。
- **蛋白（Proteins）** —— 多记录 FASTA，每个基因符号对应一条蛋白序列。

## 输出 schema

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

## 与 scGPT 的集成

`sc_rna_pipeline.py` 中的 `embed_with_foundation_model` 函数是接入 scGPT、
Geneformer 或 UNI-RNA 嵌入的显式扩展点。在两者均未安装的情况下，流程会回退到
恒等嵌入（每个细胞的平均表达），足以支撑 k-medoids 聚类，但不足以精确识别细胞类型。

接入 scGPT 的示例：

```python
# 在自定义集成脚本中：
from mrna_ai_tools.sc_rna_pipeline import (
    cluster_with_scanpy, embed_with_foundation_model
)
import scgpt  # 你安装的版本

embeddings = scgpt.embed(my_adata)  # 视当前 API 而定
labels = cluster_with_scanpy(embeddings, cell_ids, gene_names)
```

本包中的 `embed_with_foundation_model` 函数是一个轻量包装层，用于文档化集成方式，
但本身并不依赖于 scgpt。
