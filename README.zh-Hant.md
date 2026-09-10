# mRNA × AI 工具組

> 為 mRNA 癌症治療中 AI 加值層所設計的實用 Python 工具。
> 僅依賴標準函式庫，無需安裝，約 500 行程式碼。

## 這是什麼

四個小而可執行的工具，一對一對應到當前 LLM 與 ML 模型正在改變 mRNA 癌症療法的 AI 加值環節：

| 工具 | AI 加值層 | 整合的參考文獻 |
|---|---|---|
| `codon` | 密碼子使用分析 + 貪婪式優化器 | CodonBERT、RiboDecode、LinearDesign、mRNABERT |
| `neoantigen` | 胜肽 × HLA 結合 + 免疫原性評分（LLM） | TrambaHLApan、DeepNeo、DeepHLApan、NetMHCpan |
| `trial` | TrialGPT 風格的 檢索 → 配對 → 排名 流程 | Jin et al. *Nat Commun* 15, 9074 (2024) |
| `lnp` | LNP 配方推薦器（已發表 + ML 發現） | Witten et al. *Nat Biotech* 43, 1790 (2025)、Li et al. *Nat Mater* 23, 1002 (2024) |

每個工具皆可作為 CLI 子命令執行，亦可作為 Python 模組直接匯入。

## 快速開始

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .                   # 僅依賴標準函式庫的核心

# 1. 密碼子分析
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize

# 2. 新抗原篩選（預設為啟發式 A*02:01 錨定矩陣）
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01

# 3. 病人對臨床試驗配對（TrialGPT 風格）
python -m mrna_ai_tools.cli trial \
    --patient mrna_ai_tools/examples/patient_summary.txt \
    --trials mrna_ai_tools/examples/trials.jsonl --top-k 5

# 4. LNP 配方建議
python -m mrna_ai_tools.cli lnp --target lung --cargo saRNA --intent "cancer vaccine"
python -m mrna_ai_tools.cli lnp --target liver --cargo Cas9 --intent "gene editing"

# 5. scRNA-seq → 新抗原銜接
python -m mrna_ai_tools.cli scrna \
    --expression mrna_ai_tools/examples/cells.csv \
    --variants mrna_ai_tools/examples/variants_coding.csv \
    --proteins mrna_ai_tools/examples/proteins.fasta \
    --tumor-markers TP53,KRAS,BRAF
```

完成 `pip install -e .` 後，相同的 CLI 亦會以 `mrna-ai` 主控台指令的形式安裝：

```bash
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv --hla HLA-A*02:01
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt --trials mrna_ai_tools/examples/trials.jsonl
mrna-ai lnp --target lung --cargo saRNA
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv --variants mrna_ai_tools/examples/variants_coding.csv --proteins mrna_ai_tools/examples/proteins.fasta --tumor-markers TP53,KRAS,BRAF
```

五個工具的範例輸出皆已提交至 `examples/sample_outputs/`。

## 選用擴充套件

```bash
pip install -e ".[llm]"                       # 相容 OpenAI API 的 LLM 用戶端
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry>=2.0 pandas
pip install -e ".[scrna]"                     # scanpy / anndata 用於分群
pip install -e ".[all]"                       # 全部
```

接著啟用真實的後端：

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini               # 預設值
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend openai
```

自動偵測順序：`mhcflurry`（若已安裝）→ `openai`（若已設定 `OPENAI_API_KEY`）→ `mock`。

## 說明文件

完整 MkDocs 網站：<https://rollroyces.github.io/mrna-ai-toolkit/>

提供三種語言版本：

- 🇺🇸 English — <https://rollroyces.github.io/mrna-ai-toolkit/>
- 🇹🇼 繁體中文 — <https://rollroyces.github.io/mrna-ai-toolkit/zh-Hant/>
- 🇨🇳 简体中文 — <https://rollroyces.github.io/mrna-ai-toolkit/zh-Hans/>

之後每次推送至 `main` 分支時，將透過 GitHub Pages 自動部署三種語系版本。

本機預覽：

```bash
pip install -e ".[docs]"
mkdocs serve
```

## 接入真實的 LLM

`neoantigen` 與 `trial` 工具預設會呼叫 LLM。如欲接入真實模型，請匯出您的 API 金鑰：

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini            # 或任何相容 OpenAI API 的模型
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend openai
```

`codon` 與 `lnp` 為確定性工具，不會呼叫任何 LLM。

## 為何是這四個層次？

mRNA 癌症治療研究已找出四個 AI 加值層，這些層次**目前或尚無基礎模型，或現有模型可被接入一套乾淨的確定性介面**——這正是本工具組所提供的。

1. **序列設計**（codon）：CodonBERT / RiboDecode / LinearDesign / mRNABERT
   皆以「逐密碼子」與「逐區段」的統計資料作為輸入。本工具組的密碼子
   分析器正好輸出這些特徵（CAI、GC%、罕見密碼子比例、CpG obs/exp、
   GC 滑動窗口標準差）。可直接作為特徵提供者接入。

2. **新抗原預測**：TrambaHLApan（2025）、DeepNeo（2023）、DeepHLApan
   （2019）、NetMHCpan（4.1）為本領域的標準方法。此處的 LLM prompt 介面
   可在您手邊沒有 GPU 時作為替代方案，而啟發式 A*02:01 後備方案則是
   一個實用的健全性基準。

3. **臨床試驗配對**：TrialGPT 本身就是一個 LLM 流程（檢索 →
   配對 → 排名）。其已發表的基準測試在條件層級的配對上報告了 87.3%
   的準確率，並縮短了 42.6% 的篩選時間。一套乾淨的開源精簡版實作確實
   具有價值。

4. **LNP 配方**：Witten 等人於 2025 年以超過 9,000 筆 LNP 量測資料
   訓練了一個導向訊息傳遞神經網路，並以 in silico 方式篩選了 160 萬
   個候選配方。Li 等人於 2024 年則使用組合化學加上機器學習。本工具組中
   的推薦器是這些模型之上、面向使用者的精選層。

## 開發

```bash
# 執行完整的冒煙測試（與 CI 一致）：
for tool in codon neoantigen trial lnp; do
  python -m mrna_ai_tools.cli $tool --help
done

# 以內建範例執行（請見 scripts/smoke.sh）：
bash scripts/smoke.sh
```

## 授權

採雙重授權。雙授權摘要詳見 `LICENSE`，AGPL-3.0-or-later 條款請見
`LICENSE-AGPL`。商用授權可來信洽詢——於 GitHub 儲存庫開立 issue 即可。

## 發布至 PyPI

wheel 與 sdist 已預先建置，並隨每次 GitHub release 一同附加。

發布新版本的步驟：

```bash
# 1. 在 mrna_ai_tools/__init__.py 中調整版本號
# 2. 建置
python -m pip install --upgrade build twine
python -m build --sdist --wheel
# 3. 上傳（先上傳至 Test PyPI，再上傳至正式環境）
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

您需要一組 PyPI token——請至
<https://pypi.org/manage/account/token/> 產生，並透過
`TWINE_PASSWORD`（搭配 `TWINE_USERNAME=__token__`）傳入，或儲存於 `~/.pypirc`。

## 貢獻指南

歡迎提交 Pull Request。請維持零相依性（僅使用 Python 標準函式庫）。
外部模型整合應接入 `mrna_ai_tools/llm.py` 中的後端抽象層。
