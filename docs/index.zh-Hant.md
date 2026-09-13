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


## 為何我們不依賴重型評估函式庫

令人驚訝的是，許多「生產級」生物資訊流程會在內部對自己的 AUPRC
分數產生分歧。Chen et al. 2024（*Genome Biology* 25(1): 118）在超過
3,000 項已發表研究中評估了 10 個廣泛使用的 PRC 繪圖與 AUPRC 計算
工具，並發現：

> 這些工具計算出的 AUPRC 值會以不同方式對分類器進行排名，且部分
> 工具會產生過於樂觀的結果。

此發現正說明為何本工具組的 `backends.py` 完整性檢查刻意採用
**確定性的結構性斷言**，而非由第三方函式庫計算的 AUPRC / F1 /
準確率：

- 每項檢查都產生一個布林值與字串訊息，皆可直接檢視。
- 所有數字（CAI、GC%、序列相似度、模組活性）皆透過本工具組端到端
  擁有的**純標準函式庫**程式碼路徑計算——沒有 `sklearn.metrics.
  precision_recall_curve`、沒有 `torchmetrics.AveragePrecision`、
  也沒有本機結果與 CI 結果之間的隱性分歧。
- 當確實使用重型函式庫時（例如 mhcflurry 用於結合親和力、
  transformers 用於 ESM2 嵌入），該整合會**隔離在 Protocol 配接器
  之後**，並提供純標準函式庫的 mock 後備——完整性檢查絕不依賴
  重型函式庫的評估語意。

對於需要 AUPRC 類型評估的使用者，我們建議**自己擁有該指標**：
重新實作所需的小型公式（通常 10 行 Python），提交至你的儲存庫，
並以自己的基線作為斷言依據。Chen et al. 的結果顯示，
「使用 scikit-learn 的 average_precision_score」並非表面上安全的預設。

### 參考文獻

Chen W.*, Miao C.*, Zhang Z., Fung C.S.H., Wang R., Chen Y., Qian Y.,
Cheng L., Yip K.Y.#, Tsui S.K.W.#, and Cao Q.#. (2024). Commonly
used software tools produce conflicting and overly-optimistic AUPRC
values. *Genome Biology* 25(1): 118.
