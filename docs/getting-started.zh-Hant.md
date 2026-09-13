# 快速開始

## 安裝

工具組核心為**純 Python 標準函式庫**——無需任何安裝即可執行
`codon`、`neoantigen`（含啟發式後端）、`trial`、`manufacture`、
`lnp`、`scrna`（標準函式庫 k-medoids 後備）或 `spatial`（mock 後端）。

```bash
git clone https://github.com/rollroyces/mrnavax.git
cd mrnavax
pip install -e .
```

這會安裝單一主控台腳本 `mrnavax`，以及 `mrnavax` Python 套件。

## 選用擴充套件

為生產等級的後端安裝擴充套件：

```bash
pip install -e ".[llm]"                       # OpenAI 相容 LLM 客戶端（TrialGPT）
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry 結合親和力
pip install -e ".[neoantigen-medcpt]"          # 用於新抗原檢索的 MedCPT
pip install -e ".[protein-lm]"                # ESM2 蛋白質語言模型（免疫原性）
pip install -e ".[trial-medcpt]"               # 用於試驗檢索的 MedCPT
pip install -e ".[scrna]"                     # scanpy / anndata / scGPT 接入點
pip install -e ".[docs]"                      # mkdocs-material + mkdocs-static-i18n
pip install -e ".[dev]"                       # ruff + pytest
pip install -e ".[all]"                       # 上述全部
```

## 後端解析

對於會呼叫 LLM 或重型模型的工具，後端依下列順序選擇：

1. `--backend <name>` CLI 旗標（最高優先）
2. 工具專用環境變數（如 `MRNA_AI_LLM_BACKEND`、`MRNA_AI_SIMICL_TOPK`）
3. 自動偵測：上游二進位在 `$PATH`（例如 STModule 用 `Rscript`、
   RiboDecode 用 `pred-translation`）→ 已安裝的 Python 依賴
   （ESM2 用 transformers、結合親和力用 mhcflurry、LLM 用 OpenAI）
   → mock

各工具的詳細說明請見 [Backends](backends.md)。

## 驗證

```bash
# 執行 25 項後端完整性檢查
python -m mrnavax.backends --check-all

# 執行單元測試套件（167 個測試）
python -m unittest discover tests

# 執行隨附範例腳本（見 scripts/smoke.sh）
bash scripts/smoke.sh
```

smoke 腳本會在隨附範例輸入上執行每個確定性工具並列印範例輸出。
冷啟動快取下應於 2 秒內完成。
