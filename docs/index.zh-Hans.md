# mRNA × AI 工具包

> 面向 mRNA 癌症治疗中 AI 加杠杆层的实用 Python 工具集。
> 仅依赖 Python 标准库的核心模块，并可选集成 mhcflurry、scGPT 以及兼容 OpenAI 协议的 LLM。

四个独立可运行的小工具，1:1 对应当前 LLM 与 ML 模型正在变革 mRNA
癌症治疗的关键 AI 加杠杆层：

| 工具 | 功能 | AI 加杠杆层 |
|---|---|---|
| `codon` | CAI、GC%、稀有密码子分析 + 贪心式密码子优化 | 面向序列设计的基座模型（CodonBERT、RiboDecode、mRNABERT） |
| `neoantigen` | 肽 × HLA 结合与免疫原性评分 | TrambaHLApan、DeepNeo、DeepHLApan、NetMHCpan、mhcflurry |
| `trial` | 患者→临床试验 检索→匹配→排序 | TrialGPT（Jin et al. *Nat Commun* 2024） |
| `lnp` | LNP 配方推荐 | Witten 2025 ML 设计脂质、Li 2024 组合化学 + ML |
| `scrna` | scRNA-seq → 肿瘤聚类 → 突变肽 → 交接 | scGPT / scanpy → 新抗原流程 |

## 为什么是这四个（现在其实是五个）？

mRNA 癌症治疗领域已经来到拐点：

1. **个性化 mRNA 癌症疫苗已被证实有效。** Intismeran autogene（mRNA-4157）
   联合 pembrolizumab 在 INTerpath-001（2026 年 8 月）两项 III 期终点均获阳性结果。
2. **面向 mRNA 设计的基座模型已经成熟。** CodonBERT、RiboDecode、mRNABERT、
   GEMORNA、TrambaHLApan —— 均发表于 2024–2025 年。
3. **瓶颈已不再是算法本身，而是集成。** 研究人员需要一套干净、仅依赖标准库的
   接口层，从而无需 GPU 集群就能把这些模型拼装到可运行的流程中。

本工具包正是这一集成层。

## 快速开始

```bash
git clone https://github.com/rollroyces/mrnavax.git
cd mrnavax
pip install -e .

# 密码子分析
mrnavax codon --sequence mrnavax/examples/cas9.fasta --optimize

# 新抗原筛选
mrnavax neoantigen --variants mrnavax/examples/tp53_variants.csv --hla HLA-A*02:01

# 患者 → 临床试验匹配
mrnavax trial --patient mrnavax/examples/patient_summary.txt \
              --trials mrnavax/examples/trials.jsonl --top-k 5

# LNP 配方建议
mrnavax lnp --target lung --cargo saRNA --intent "cancer vaccine"

# scRNA-seq → 新抗原交接
mrnavax scrna --expression mrnavax/examples/cells.csv \
              --variants mrnavax/examples/variants_coding.csv \
              --proteins mrnavax/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180
```

完整的安装选项见 [快速开始](getting-started.md) 页面；接入真实的 LLM / mhcflurry /
scGPT 的方法见 [后端](backends.md) 页面。

## 授权许可

双重许可：开源使用采用 [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.html)；
商业专有部署另需独立商业许可。详见 [License](license.md)。


## 为何我们不依赖重型评估函数库

令人惊讶的是，许多"生产级"生物信息流程会在内部对自己的 AUPRC
分数产生分歧。Chen et al. 2024（*Genome Biology* 25(1): 118）在超过
3,000 项已发表研究中评估了 10 个广泛使用的 PRC 绘图与 AUPRC 计算
工具，并发现：

> 这些工具计算出的 AUPRC 值会以不同方式对分类器进行排名，且部分
> 工具会产生过于乐观的结果。

此发现正说明为何本工具组的 `backends.py` 完整性检查刻意采用
**确定性的结构性断言**，而非由第三方函数库计算的 AUPRC / F1 /
准确率：

- 每项检查都产生一个布尔值与字符串消息，皆可直接查看。
- 所有数字（CAI、GC%、序列相似度、模块活性）皆通过本工具组端到端
  拥有的**纯标准函数库**代码路径计算——没有 `sklearn.metrics.
  precision_recall_curve`、没有 `torchmetrics.AveragePrecision`、
  也没有本地结果与 CI 结果之间的隐性分歧。
- 当确实使用重型函数库时（例如 mhcflurry 用于结合亲和力、
  transformers 用于 ESM2 嵌入），该整合会**隔离在 Protocol 适配器
  之后**，并提供纯标准函数库的 mock 后备——完整性检查绝不依赖
  重型函数库的评估语义。

对于需要 AUPRC 类型评估的用户，我们建议**自己拥有该指标**：
重新实现所需的小型公式（通常 10 行 Python），提交至你的代码仓库，
并以自己的基线作为断言依据。Chen et al. 的结果显示，
"使用 scikit-learn 的 average_precision_score"并非表面安全的默认。

### 参考文献

Chen W.*, Miao C.*, Zhang Z., Fung C.S.H., Wang R., Chen Y., Qian Y.,
Cheng L., Yip K.Y.#, Tsui S.K.W.#, and Cao Q.#. (2024). Commonly
used software tools produce conflicting and overly-optimistic AUPRC
values. *Genome Biology* 25(1): 118.
