# 贡献指南

欢迎提交 Pull Request。

## 限制

- **纯标准库核心。** 在默认安装（`pip install -e .`）中随附的
  工具必须仅依赖 Python 标准库。新依赖须置于 `pyproject.toml`
  的 `optional-dependencies` extra 之后。
- **确定性。** 工具对相同输入必须产生相同输出（默认输出不含时间戳）。
  Mock 后端永远是确定性的。
- **结构验证。** 由 LLM 支持的工具必须验证响应形状，若 LLM 返回
  格式错误的 JSON 则退回启发式方法。
- **精简 CLI 界面。** 每个工具的 `_run_cli` 应接受 `--out`，未设置时
  输出至 stdout。
- **基于 Protocol 的可插拔性。** 重型模型集成（RiboDecode、STModule、
  ESM2、scGPT、mhcflurry）必须置于 `runtime_checkable` Protocol 或抽象
  适配器类之后，通过可选 extras 安装（例如
  `pip install mrnavax[sota]`）。参考
  `mrnavax/codon_ribodecode_adapter.py`、
  `mrnavax/spatial_module_adapter.py`、
  `mrnavax/protein_lm_adapter.py`。
- **新功能采用 TDD。** 每个新的公开函数必须在实现前先写测试
  （见下方 *开发* 段落）。

## 开发

```bash
git clone https://github.com/rollroyces/mrnavax.git
cd mrnavax
pip install -e ".[dev,llm]"

# 运行 25 项后端完整性检查
python -m mrnavax.backends --check-all

# 运行单元测试套件（167 个测试）
python -m unittest discover tests

# 烟雾测试
bash scripts/smoke.sh

# 本地文档
pip install -e ".[docs]"
mkdocs serve
```

## Pull Request 流程

1. 非显而易见的修改请先开 issue。
2. 新功能遵循 **TDD 循环**（依 `test-driven-development` 技能）：
   - **RED**：编写一个失败的测试，练习期望的 API。运行它并确认
     因正确的原因失败。
   - **GREEN**：编写最小实现使其通过。
   - **REFACTOR**：清理重复、命名、辅助函数。
3. 包装第三方模型时遵循 **api-integration-verify** 纪律：先探查
   上游文档／GitHub，从真实 URL 验证参数名称与返回形状，再设计
   Protocol 适配器。
4. 在 `backends.py` 中为任何新后端新增 `register()` 条目。
5. CI 必须在 Python 3.11–3.14 上保持绿灯才能合并。
6. 当 `bash scripts/smoke.sh` +
   `python -m mrnavax.backends --check-all` +
   `python -m unittest discover tests` 全部通过后，使用 `[verified]`
   commit 信息进行 squash-merge。

## 新增工具

每个新工具应随附：

1. 输入与输出的具类型 `dataclass`（frozen，于构造时验证）。
2. 后端接口的 `runtime_checkable` Protocol。
3. 通过 subprocess / 延迟加载接入上游模型的真实适配器。
4. 满足相同 Protocol 的纯标准库 mock。
5. `backends.py` 中的 `register()` 条目供 CI 完整性使用。
6. `tests/` 中遵循严格 TDD 的测试。
7. 一份 `docs/tools/<name>.{md,zh-Hant.md,zh-Hans.md}` 页面，描述
   工具、CLI 用法、后端矩阵与参考论文。
