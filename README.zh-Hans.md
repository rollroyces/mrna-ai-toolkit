# mRNA × AI 工具包

> 面向 mRNA 癌症治疗中 AI 加杠杆层的实用 Python 工具集。
> 仅依赖 Python 标准库，开箱即用，约 500 行代码。

## 概览

四个独立可运行的小工具，1:1 对应当前 LLM 与 ML 模型正在变革 mRNA
癌症治疗的关键 AI 加杠杆层：

| 工具 | AI 加杠杆层 | 集成参考 |
|---|---|---|
| `codon` | 密码子使用分析 + 贪心式优化器 | CodonBERT、RiboDecode、LinearDesign、mRNABERT |
| `neoantigen` | 肽 × HLA 结合与免疫原性评分（LLM） | TrambaHLApan、DeepNeo、DeepHLApan、NetMHCpan |
| `trial` | TrialGPT 式 检索 → 匹配 → 排序 流程 | Jin et al. *Nat Commun* 15, 9074 (2024) |
| `lnp` | LNP 配方推荐（已发表 + ML 发现） | Witten et al. *Nat Biotech* 43, 1790 (2025)，Li et al. *Nat Mater* 23, 1002 (2024) |

每个工具既可作为 CLI 子命令运行，也可作为 Python 模块直接导入。

## 快速开始

```bash
git clone https://github.com/rollroyces/mrna-ai-toolkit.git
cd mrna-ai-toolkit
pip install -e .                   # 仅依赖 Python 标准库的核心模块

# 1. 密码子分析
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta
python -m mrna_ai_tools.cli codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize

# 2. 新抗原筛选（默认使用 A*02:01 启发式锚点矩阵）
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01

# 3. 患者到临床试验的匹配（TrialGPT 式）
python -m mrna_ai_tools.cli trial \
    --patient mrna_ai_tools/examples/patient_summary.txt \
    --trials mrna_ai_tools/examples/trials.jsonl --top-k 5

# 4. LNP 配方建议
python -m mrna_ai_tools.cli lnp --target lung --cargo saRNA --intent "cancer vaccine"
python -m mrna_ai_tools.cli lnp --target liver --cargo Cas9 --intent "gene editing"

# 5. scRNA-seq → 新抗原交接
python -m mrna_ai_tools.cli scrna \
    --expression mrna_ai_tools/examples/cells.csv \
    --variants mrna_ai_tools/examples/variants_coding.csv \
    --proteins mrna_ai_tools/examples/proteins.fasta \
    --tumor-markers TP53,KRAS,BRAF
```

执行 `pip install -e .` 后，相同的 CLI 同时也会以控制台脚本 `mrna-ai`
的形式安装：

```bash
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta
mrna-ai neoantigen --variants mrna_ai_tools/examples/tp53_variants.csv --hla HLA-A*02:01
mrna-ai trial --patient mrna_ai_tools/examples/patient_summary.txt --trials mrna_ai_tools/examples/trials.jsonl
mrna-ai lnp --target lung --cargo saRNA
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv --variants mrna_ai_tools/examples/variants_coding.csv --proteins mrna_ai_tools/examples/proteins.fasta --tumor-markers TP53,KRAS,BRAF
```

五个工具的示例输出都已提交至仓库的 `examples/sample_outputs/` 目录。

## 可选扩展

```bash
pip install -e ".[llm]"                       # 兼容 OpenAI 协议的 LLM 客户端
pip install -e ".[neoantigen-mhcflurry]"       # mhcflurry>=2.0 与 pandas
pip install -e ".[scrna]"                     # scanpy / anndata，用于聚类
pip install -e ".[all]"                       # 安装全部可选依赖
```

然后激活真实后端：

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini               # 默认模型
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend openai
```

自动检测顺序：`mhcflurry`（若已安装）→ `openai`（若设置了 `OPENAI_API_KEY`）→ `mock`。

## 文档

完整的 MkDocs 站点：<https://rollroyces.github.io/mrna-ai-toolkit/>

提供三种语言版本：

- 🇺🇸 英文 — <https://rollroyces.github.io/mrna-ai-toolkit/>
- 🇹🇼 繁體中文 — <https://rollroyces.github.io/mrna-ai-toolkit/zh-Hant/>
- 🇨🇳 简体中文 — <https://rollroyces.github.io/mrna-ai-toolkit/zh-Hans/>

之后每次推送至 `main` 分支，都会通过 GitHub Pages 自动部署全部
三种语言版本。

本地预览：

```bash
pip install -e ".[docs]"
mkdocs serve
```

## 接入真实 LLM

`neoantigen` 与 `trial` 工具默认会调用 LLM。如需接入真实模型，请导出
你的 API 密钥：

```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini            # 或任意兼容 OpenAI 协议的模型
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend openai
```

`codon` 与 `lnp` 工具是确定性的，不会调用任何 LLM。

## 为什么是这四个层？

mRNA 癌症治疗研究识别出四个 AI 加杠杆层，**它们要么目前尚无基座
模型，要么现有模型可被接入到一套干净的确定性接口中**——而这正是本
工具包所提供的。

1. **序列设计**（codon）：CodonBERT / RiboDecode / LinearDesign /
   mRNABERT 以每个密码子与每个区段的统计量作为输入。本工具中的密码子
   分析器正好输出这些特征（CAI、GC%、稀有密码子比例、CpG 观测值/期望值、
   GC 窗口标准差），可直接作为特征提供方接入。

2. **新抗原预测**：TrambaHLApan（2025）、DeepNeo（2023）、DeepHLApan
   （2019）、NetMHCpan（4.1）是该领域的标杆。本工具提供的 LLM 提示接口
   在没有 GPU 时可作为替代，启发式的 A*02:01 兜底也是一个有用的合理性基线。

3. **临床试验匹配**：TrialGPT 本身就是一条 LLM 流水线（检索 → 匹配 →
   排序）。其已发表的基准报告显示，标准层面的匹配准确率达 87.3%，筛选
   时间缩短 42.6%。一套干净的开源桩实现非常实用。

4. **LNP 配方**：Witten 等 2025 年用 >9,000 条 LNP 测量数据训练了一个
   有向消息传递神经网络，并在计算机中筛选了 160 万个候选分子。Li 等
   2024 年则采用组合化学 + 机器学习的方法。本工具中的推荐器是上述模型
   之上、面向人类的候选短名单层。

## 开发

```bash
# 运行完整冒烟测试（与 CI 一致）：
for tool in codon neoantigen trial lnp; do
  python -m mrna_ai_tools.cli $tool --help
done

# 使用随仓库分发的示例运行（见 scripts/smoke.sh）：
bash scripts/smoke.sh
```

## 授权许可

采用双重许可。双重许可的概要见 `LICENSE`，AGPL-3.0-or-later 的条款见
`LICENSE-AGPL`。如需商业许可，请通过 GitHub 仓库提交 issue 申请。

## 发布到 PyPI

wheel 与 sdist 已预构建，并随每次 GitHub release 一同发布。

发布新版本的步骤：

```bash
# 1. 在 mrna_ai_tools/__init__.py 中更新版本号
# 2. 构建
python -m pip install --upgrade build twine
python -m build --sdist --wheel
# 3. 上传（先上传到 Test PyPI，再上传到正式仓库）
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

你需要一个 PyPI 令牌——可在 <https://pypi.org/manage/account/token/>
申请，并通过 `TWINE_PASSWORD`（同时设置 `TWINE_USERNAME=__token__`）
传入，或直接保存到 `~/.pypirc` 中。

## 贡献指南

欢迎提交 Pull Request。请保持依赖面为零（仅依赖 Python 标准库）。外部
模型集成应接入到 `mrna_ai_tools/llm.py` 中的后端抽象层。
