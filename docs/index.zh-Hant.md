# mRNA × AI 工具組

> 為 mRNA 癌症治療中 AI 加值層所設計的實用 Python 工具。
> 核心僅依賴 Python 標準函式庫，並可選擇性整合 mhcflurry、scGPT 以及相容 OpenAI API 的 LLM。

四個小而可執行的工具，一對一對應到當前 LLM 與 ML 模型正在改變 mRNA 癌症療法的 AI 加值環節：

| 工具 | 功能 | AI 加值層 |
|---|---|---|
| `codon` | CAI、GC%、罕見密碼子分析 + 貪婪式密碼子優化 | 序列設計的基礎模型（CodonBERT、RiboDecode、mRNABERT） |
| `neoantigen` | 胜肽 × HLA 結合 + 免疫原性評分 | TrambaHLApan、DeepNeo、DeepHLApan、NetMHCpan、mhcflurry |
| `trial` | 病人對臨床試驗的「檢索 → 配對 → 排名」 | TrialGPT（Jin et al. *Nat Commun* 2024） |
| `lnp` | LNP 配方推薦 | Witten 2025 ML 設計之脂質、Li 2024 組合化學 + ML |
| `scrna` | scRNA-seq → 腫瘤集群 → 突變胜肽 → 銜接下游 | scGPT / scanpy → neoantigen 流程 |

## 為何是這四個（現在是五個）？

mRNA 癌症治療領域已到達一個轉折點：

1. **個人化 mRNA 癌症疫苗已證實有效。** Intismeran autogene（mRNA-4157）合併 pembrolizumab 在 INTerpath-001（2026 年 8 月）達成了兩個第三期主要終點。
2. **mRNA 設計的基礎模型已臻成熟。** CodonBERT、RiboDecode、mRNABERT、GEMORNA、TrambaHLApan——皆於 2024–2025 年間發表。
3. **瓶頸已不再是演算法，而是整合。** 研究人員需要一套乾淨、僅依賴標準函式庫的介面層，以便在不架設 GPU 叢集的前提下，把這些模型接進可運作的工作流程。

本工具組即是那個整合層。

## 快速開始

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .

# codon 分析
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize

# neoantigen 篩選
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv --hla HLA-A*02:01

# 病人 → 臨床試驗配對
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt \
              --trials mrna_ai_tools/examples/trials.jsonl --top-k 5

# LNP 配方建議
mrna-ai lnp --target lung --cargo saRNA --intent "cancer vaccine"

# scRNA-seq → neoantigen 銜接
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv \
              --variants mrna_ai_tools/examples/variants_coding.csv \
              --proteins mrna_ai_tools/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180
```

完整安裝選項請見 [Getting started](getting-started.md) 頁；如何接入真實的 LLM / mhcflurry / scGPT，請見 [Backends](backends.md) 頁。

## 授權

雙重授權：開源使用採 [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.html)；專屬部署另需商用授權。詳見 [License](license.md)。
