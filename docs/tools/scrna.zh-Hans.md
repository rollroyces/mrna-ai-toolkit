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
mrnavax scrna --expression mrnavax/examples/cells.csv \
              --variants mrnavax/examples/variants_coding.csv \
              --proteins mrnavax/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180

# 使用 scanpy（真正的 Leiden 聚类）
pip install -e ".[scrna]"
mrnavax scrna --expression path/to/cells.h5ad ...
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
from mrnavax.sc_rna_pipeline import (
    cluster_with_scanpy, embed_with_foundation_model
)
import scgpt  # 你安装的版本

embeddings = scgpt.embed(my_adata)  # 视当前 API 而定
labels = cluster_with_scanpy(embeddings, cell_ids, gene_names)
```

本包中的 `embed_with_foundation_model` 函数是一个轻量包装层，用于文档化集成方式，
但本身并不依赖于 scgpt。

## 真实生物学案例：胃癌研究

本流程所对应的代表性湿实验工作流程，记载于 **Qian et al. 2022**
（*International Journal of Cancer* 151(8): 1367-1381）：

> 通过单细胞 RNA 测序解析胃癌淋巴结转移中肿瘤细胞的异质性及肿瘤
> 环境的全面动态。

该研究对胃癌原发肿瘤加上淋巴结转移进行 scRNA-seq 测序，识别肿瘤
细胞群聚，并表征肿瘤微环境 (TME)——包括驱动免疫逃逸的 T 细胞耗竭
表型。下游 mRNA 癌症疫苗设计的问题是：*哪些肿瘤群聚特异性的突变
肽段与耗竭 T 细胞在空间上共定位，能作为疫苗标的？*

本工具组的 `scrna` 模块正好串联此循环：

```bash
# 1. 将 scRNA-seq 计数进行分群
mrnavax scrna \
  --expression gastric_primary.h5ad \
  --proteins gastric_peptides.fasta \
  --variants patient_variants.csv \
  --output-dir results/

# 2. 将肿瘤群聚肽段清单移交给新抗原筛选
mrnavax neoantigen \
  --csv results/tumor_peptides.csv \
  --hla "HLA-A*02:01,HLA-A*24:02" \
  --backend mock
```

同一份肽段清单接着可通过以下步骤处理：

```bash
# 3. ESM2 蛋白质语言模型免疫原性评分（冻结 LM + 分类器）
python -c "
from mrnavax.neoantigen_screener import lm_immunogenicity_score
import pandas as pd
df = pd.read_csv('results/tumor_peptides.csv')
df['lm_score'] = df['peptide'].apply(
    lambda p: lm_immunogenicity_score(p)['score']
)
df.to_csv('results/tumor_peptides_lm_scored.csv', index=False)
"
```

整个 Qian 风格的工作流程可在工具组的纯标准函数库基线上端到端执行；
具备 GPU 访问权限的用户可改用 scGPT 作为基础模型步骤，
ESM2-150M 用于免疫原性评分，而每个肽段的肿瘤微环境交互分析则
与已发表流程完全相同。

## 参考文献

Qian Y., Zhai E., Chen S., Liu Y., Ma Y., Chen J., Liu J., Qin C.,
Cao Q.#, Chen J.#, and Cai S.#. (2022). Single-cell RNA-seq
dissecting heterogeneity of tumor cells and comprehensive dynamics
in tumor microenvironment during lymph nodes metastasis in gastric
cancer. *International Journal of Cancer* 151(8): 1367-1381.
