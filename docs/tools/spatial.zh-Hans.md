# `spatial` — 空间转录组学组织模块

从空间 RNA-seq 数据串联至组织区域感知的新抗原交接：

1. 加载计数矩阵（spots × genes）与空间位置文件（spot × {x, y}）。
2. 通过上游 R 包的 `data_preprocessing()` 进行预处理（Seurat HVG
   选择 + 距离矩阵）。
3. 运行已发表的 `run_STModule()` 贝叶斯模型以识别 `num_modules` 个
   组织模块——在空间上组织以执行特定生物功能的反复出现的细胞群落。
4. 通过本工具包的 `neoantigen` 流程将模块相关基因映射回肽段候选。

## 参考文献

Wang R., Qian Y., Guo X., Song F., Xiong Z., Cai S., Bian X., Wong M.H.,
Cao Q.#, Cheng L.#, Lu G.#, and Leung K.S.#. (2025) STModule:
identifying tissue modules to uncover spatial components and
characteristics of transcriptomic landscapes. *Genome Medicine*
17(1): 18.

R 包由 GitHub 的 [`rwang-z/STModule`](https://github.com/rwang-z/STModule)
发布，需要 R 4.4 + Seurat v5 + torch + GPUmatrix 1.0.2 + CUDA 11.7。
本工具包提供小型 R 壳层（`mrnavax/scripts/stmodule_shim.R`），
调用已发表的 R 函数并将 JSON 输出至 stdout。

## 用法

```bash
# 纯标准库（使用合成空间坐标 + mock 组织模块）
python -m mrnavax.cli spatial \
    --count-file examples/spatial/st_bc2_count_matrix.tsv \
    --locations-file examples/spatial/st_bc2_locations.tsv \
    --platform ST --num-modules 10

# 真实：已安装 R + STModule（Rscript 在 $PATH）
python -m mrnavax.cli spatial \
    --count-file examples/spatial/st_bc2_count_matrix.tsv \
    --locations-file examples/spatial/st_bc2_locations.tsv \
    --platform ST --num-modules 10 --backend stmodule

# Slide-seqV2（高分辨率）
python -m mrnavax.cli spatial \
    --count-file my_slideseq.tsv --locations-file my_locs.tsv \
    --platform SlideSeqV2 --num-modules 10
```

CLI 标志：

- `--platform {ST,Visium,SlideSeqV2,StereoSeq,Other}` — 在上游调用
  中驱动 `high_resolution=FALSE`（默认）或 `TRUE`。
- `--num-modules N` — 要识别的组织模块数（默认 10；论文建议 10
  作为"主要表达分量"）。
- `--backend {auto,mock,stmodule}` — 默认 `auto`，若 Rscript 在 $PATH
  则选择 STModule，否则选择 mock。

## Python API

```python
from mrnavax.spatial_protocols import SpatialData
from mrnavax.spatial_module_adapter import select_spatial_module_backend

backend = select_spatial_module_backend()  # 挑选真实或 mock
data = SpatialData(
    count_file=Path("counts.tsv"),
    locations_file=Path("locs.tsv"),
    platform="ST",
    num_modules=10,
)
result = backend.run(data)
print(result.modules[0].top_genes)
```

Mock 后端使用各平台对应的基因宇宙：

| Platform | 顶端基因（循环） |
|---|---|
| ST | GAPDH, USP4, MAPKAPK2, CPEB1, LANCL2 |
| Visium | CDH1, VIM, KRT8, KRT18, EPCAM |
| SlideSeqV2 | MOBP, MBP, PLP1, MAG, MOG |
| StereoSeq | SOX2, PAX6, NES, VIM, HES1 |
| Other | （合成 GEN_A–E） |

## 输出结构

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

每个模块的 `top_genes` 成为本工具包 `neoantigen` 模块的候选肽段：
通过 `mrnavax neoantigen --csv ... --hla ...` 馈入以评分免疫原性。

## 为何是独立模块（而非并入 `scrna`）？

`scrna` 模块处理分离的单细胞 RNA-seq——无空间坐标、细胞独立。
`spatial` 模块处理**空间分辨转录组学（SRT）**——保留坐标，使组织
架构得以告知哪些细胞群落在空间上共定位。两个流程在新抗原交接
步骤合流：

1. `scrna` → 肿瘤群聚身份 + 突变肽段（来自每细胞变异表达）
2. `spatial` → 组织模块 + 共定位细胞群落（来自空间架构）
3. `neoantigen` → 对候选并集进行免疫原性评分

对癌症 mRNA 疫苗设计而言，两个模块皆重要：`scrna` 告诉你
*哪些*肽段具有肿瘤特异性；`spatial` 告诉你肿瘤细胞*在哪里*
及其微环境的样貌。

## 后端矩阵

| Backend | 功能 | 安装 |
|---|---|---|
| `mock` | 纯标准库桩。各平台基因宇宙 + spot/location 交集。永远可用。 | — |
| `stmodule` | 子进程至 `Rscript stmodule_shim.R`。调用上游 R 函数。 | `conda install r-base=4.4 r-seurat r-devtools && R -e 'devtools::install_github("rwang-z/STModule")'` |
