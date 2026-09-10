# 快速开始

## 安装

核心工具包**仅依赖 Python 标准库** —— 要运行 `codon`、`neoantigen`（使用启发式后端）、
`trial`、`lnp`，以及 `scrna`（使用标准库 k-medoids 兜底实现），无需任何额外安装。

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .
```

该命令会同时安装一个控制台脚本 `mrna-ai` 以及 Python 包 `mrna_ai_tools`。

## 可选扩展

如需使用生产级后端，请安装相应的可选依赖：

```bash
pip install -e ".[llm]"              # 兼容 OpenAI 协议的 LLM 客户端
pip install -e ".[neoantigen-mhcflurry]"  # 真实的结合亲和力预测
pip install -e ".[scrna]"            # 用于聚类的 scanpy / anndata
pip install -e ".[all]"              # 安装全部可选依赖
```

## 后端解析顺序

对于会调用 LLM 或 ML 模型的工具，按以下顺序选择后端：

1. `--backend <name>` 命令行参数（最高优先级）
2. 环境变量 `MRNA_AI_LLM_BACKEND`
3. 自动检测：已安装 `mhcflurry` → 已设置 `OPENAI_API_KEY` 时的 `openai` → `mock`

各工具后端的详细说明见 [后端](backends.md)。

## 验证

```bash
bash scripts/smoke.sh
```

该脚本会使用随仓库分发的示例输入运行四个确定性工具，并打印示例输出。
冷缓存下应在 2 秒内完成。
