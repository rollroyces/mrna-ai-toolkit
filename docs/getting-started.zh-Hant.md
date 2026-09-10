# Getting started

## 安裝

核心工具組**僅使用 Python 標準函式庫**——執行 `codon`、`neoantigen`（啟發式後端）、`trial`、`lnp` 或 `scrna`（標準函式庫的 k-medoids 後備方案）皆無需額外安裝。

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .
```

此指令會安裝單一主控台指令 `mrna-ai`，以及 `mrna_ai_tools` Python 套件。

## 選用 extras

若需用於正式環境等級的後端，可額外安裝擴充套件：

```bash
pip install -e ".[llm]"              # 相容 OpenAI API 的 LLM 用戶端
pip install -e ".[neoantigen-mhcflurry]"  # 真實的結合親和性預測
pip install -e ".[scrna]"            # scanpy / anndata 用於分群
pip install -e ".[all]"              # 全部
```

## 後端解析

對於會呼叫 LLM 或模型工具，後端依下列優先順序選定：

1. 命令列旗標 `--backend <name>`（最高優先）
2. 環境變數 `MRNA_AI_LLM_BACKEND`
3. 自動偵測：已安裝 `mhcflurry` → 已設定 `OPENAI_API_KEY` 時用 `openai` → 否則 `mock`

各工具的後端細節請見 [Backends](backends.md)。

## 驗證

```bash
bash scripts/smoke.sh
```

此腳本會以內建的範例輸入執行四個確定性工具，並印出範例輸出。在冷快取下應於 2 秒內完成。
