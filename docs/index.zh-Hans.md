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
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .

# 密码子分析
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize

# 新抗原筛选
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv --hla HLA-A*02:01

# 患者 → 临床试验匹配
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl --top-k 5

# LNP 配方建议
mrna-ai lnp --target lung --cargo saRNA --intent "cancer vaccine"

# scRNA-seq → 新抗原交接
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv \
              --variants mrna_ai_tools/examples/variants_coding.csv \
              --proteins mrna_ai_tools/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180
```

完整的安装选项见 [快速开始](getting-started.md) 页面；接入真实的 LLM / mhcflurry /
scGPT 的方法见 [后端](backends.md) 页面。

## 授权许可

双重许可：开源使用采用 [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.html)；
商业专有部署另需独立商业许可。详见 [License](license.md)。
