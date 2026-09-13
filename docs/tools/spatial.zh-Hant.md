# `spatial` — 空間轉錄組學組織模組

從空間 RNA-seq 資料串接至組織區域感知的新抗原交接：

1. 載入計數矩陣（spots × genes）與空間位置檔（spot × {x, y}）。
2. 透過上游 R 套件的 `data_preprocessing()` 進行前處理（Seurat HVG
   選擇 + 距離矩陣）。
3. 執行已發表的 `run_STModule()` 貝氏模型以識別 `num_modules` 個
   組織模組——在空間上組織以執行特定生物功能的反覆出現細胞群落。
4. 透過本工具組的 `neoantigen` 流程將模組相關基因映射回胜肽候選。

## 參考文獻

Wang R., Qian Y., Guo X., Song F., Xiong Z., Cai S., Bian X., Wong M.H.,
Cao Q.#, Cheng L.#, Lu G.#, and Leung K.S.#. (2025) STModule:
identifying tissue modules to uncover spatial components and
characteristics of transcriptomic landscapes. *Genome Medicine*
17(1): 18.

R 套件由 GitHub 的 [`rwang-z/STModule`](https://github.com/rwang-z/STModule)
發布，需要 R 4.4 + Seurat v5 + torch + GPUmatrix 1.0.2 + CUDA 11.7。
本工具組提供小型 R 殼層（`mrna_ai_tools/scripts/stmodule_shim.R`），
呼叫已發表的 R 函式並將 JSON 輸出至 stdout。

## 用法

```bash
# 純標準函式庫（使用合成空間座標 + mock 組織模組）
python -m mrna_ai_tools.cli spatial \
    --count-file examples/spatial/st_bc2_count_matrix.tsv \
    --locations-file examples/spatial/st_bc2_locations.tsv \
    --platform ST --num-modules 10

# 真實：已安裝 R + STModule（Rscript 在 $PATH）
python -m mrna_ai_tools.cli spatial \
    --count-file examples/spatial/st_bc2_count_matrix.tsv \
    --locations-file examples/spatial/st_bc2_locations.tsv \
    --platform ST --num-modules 10 --backend stmodule

# Slide-seqV2（高解析度）
python -m mrna_ai_tools.cli spatial \
    --count-file my_slideseq.tsv --locations-file my_locs.tsv \
    --platform SlideSeqV2 --num-modules 10
```

CLI 旗標：

- `--platform {ST,Visium,SlideSeqV2,StereoSeq,Other}` — 在上游呼叫
  中驅動 `high_resolution=FALSE`（預設）或 `TRUE`。
- `--num-modules N` — 要識別的組織模組數（預設 10；論文建議 10
  作為「主要表現分量」）。
- `--backend {auto,mock,stmodule}` — 預設 `auto`，若 Rscript 在 $PATH
  則選擇 STModule，否則選擇 mock。

## Python API

```python
from mrna_ai_tools.spatial_protocols import SpatialData
from mrna_ai_tools.spatial_module_adapter import select_spatial_module_backend

backend = select_spatial_module_backend()  # 挑選真實或 mock
data = SpatialData(
    count_file=Path("counts.tsv"),
    locations_file=Path("locs.tsv"),
    platform="ST",
    num_modules=10,
)
result = backend.run(data)
print(result.modules[0].top_genes)
```

Mock 後端使用各平台對應的基因宇宙：

| Platform | 頂端基因（循環） |
|---|---|
| ST | GAPDH, USP4, MAPKAPK2, CPEB1, LANCL2 |
| Visium | CDH1, VIM, KRT8, KRT18, EPCAM |
| SlideSeqV2 | MOBP, MBP, PLP1, MAG, MOG |
| StereoSeq | SOX2, PAX6, NES, VIM, HES1 |
| Other | （合成 GEN_A–E） |

## 輸出結構

```json
{
  "platform": "ST",
  "modules": [
    {
      "module_id": 0,
      "top_genes": ["GAPDH", "USP4", "MAPKAPK2"],
      "n_spots": 12,
      "mean_activity": 1.0
    },
    ...
  ],
  "n_spots": 12,
  "elapsed_seconds": 0.02,
  "backend": "mock",
  "notes": ["mock-backend", "platform=ST", "n_modules=10"]
}
```

每個模組的 `top_genes` 成為本工具組 `neoantigen` 模組的候選胜肽：
透過 `mrna-ai neoantigen --csv ... --hla ...` 餵入以評分免疫原性。

## 為何是獨立模組（而非併入 `scrna`）？

`scrna` 模組處理分離的單細胞 RNA-seq——無空間座標、細胞獨立。
`spatial` 模組處理**空間解析轉錄組學（SRT）**——保留座標，使組織
架構得以告知哪些細胞群落在空間上共定位。兩個流程在新抗原交接
步驟合流：

1. `scrna` → 腫瘤群聚身分 + 突變胜肽（來自每細胞變異表現）
2. `spatial` → 組織模組 + 共定位細胞群體（來自空間架構）
3. `neoantigen` → 對候選聯集進行免疫原性評分

對癌症 mRNA 疫苗設計而言，兩個模組皆重要：`scrna` 告訴你
*哪些*胜肽具有腫瘤特異性；`spatial` 告訴你腫瘤細胞*在哪裡*
及其微環境的樣貌。

## 後端矩陣

| Backend | 功能 | 安裝 |
|---|---|---|
| `mock` | 純標準函式庫樁。各平台基因宇宙 + spot/location 交集。永遠可用。 | — |
| `stmodule` | 子行程至 `Rscript stmodule_shim.R`。呼叫上游 R 函式。 | `conda install r-base=4.4 r-seurat r-devtools && R -e 'devtools::install_github("rwang-z/STModule")'` |
