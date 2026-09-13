# 快速开始

## 安装

工具包核心为**纯 Python 标准库**——无需任何安装即可运行
`codon`、`neoantigen`（含启发式后端）、`trial`、`manufacture`、
`lnp`、`scrna`（标准库 k-medoids 后备）或 `spatial`（mock 后端）。

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .
```

这会安装单一控制台脚本 `mrna-ai`，以及 `mrna_ai_tools` Python 包。

## 可选扩展包

为生产级别的后端安装扩展包：

```bash
pip install -e ".[llm]"                       # OpenAI 兼容 LLM 客户端（TrialGPT）
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry 结合亲和力
pip install -e ".[neoantigen-medcpt]"          # 用于新抗原检索的 MedCPT
pip install -e ".[protein-lm]"                # ESM2 蛋白质语言模型（免疫原性）
pip install -e ".[trial-medcpt]"               # 用于试验检索的 MedCPT
pip install -e ".[scrna]"                     # scanpy / anndata / scGPT 接入点
pip install -e ".[docs]"                      # mkdocs-material + mkdocs-static-i18n
pip install -e ".[dev]"                       # ruff + pytest
pip install -e ".[all]"                       # 上述全部
```

## 后端解析

对于会调用 LLM 或重型模型的工具，后端依下列顺序选择：

1. `--backend <name>` CLI 标志（最高优先）
2. 工具专用环境变量（如 `MRNA_AI_LLM_BACKEND`、`MRNA_AI_SIMICL_TOPK`）
3. 自动检测：上游二进制在 `$PATH`（例如 STModule 用 `Rscript`、
   RiboDecode 用 `pred-translation`）→ 已安装的 Python 依赖
   （ESM2 用 transformers、结合亲和力用 mhcflurry、LLM 用 OpenAI）
   → mock

各工具的详细说明请见 [Backends](backends.md)。

## 验证

```bash
# 运行 25 项后端完整性检查
python -m mrna_ai_tools.backends --check-all

# 运行单元测试套件（167 个测试）
python -m unittest discover tests

# 运行随附示例脚本（见 scripts/smoke.sh）
bash scripts/smoke.sh
```

smoke 脚本会在随附示例输入上运行每个确定性工具并打印示例输出。
冷启动缓存下应于 2 秒内完成。
