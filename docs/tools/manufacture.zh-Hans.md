# mRNA 可生产性检查器

连接计算序列设计与实际可规模化合成之间的桥梁。

## 为什么这很重要

即便算法上完美的 mRNA 序列，在生产规模上仍可能无法合成。真正的生产工艺需要
检查是否存在那些会破坏 DNA 模板稳定性、阻碍核糖体扫描或触发 mRNA 降解的
基序 —— 这些问题只有在湿实验中才会暴露。

## 八项检查

| 检查项 | 严重度阈值 | 能捕获的问题 |
|---|---|---|
| `poly_a_runs` | ≥7 个 A → error | DNA 模板中的 Poly-A 连续序列会在 IVT 过程中导致质粒不稳定 |
| `gc_5prime_hairpin` | ≥70% GC → warn，≥80% → error | 5' 端的 GC 富集茎结构会阻碍核糖体扫描 |
| `kozak_strength` | <45% 匹配 → warn | 哺乳动物翻译需要强 Kozak 一致序列（`GCCRCCATGG`） |
| `are_motif` | ≥1 个九聚体 → warn，≥2 → error | 3' UTR 中的 AU 富集元件会触发 mRNA 降解 |
| `stop_context` | 通读率 ≥0.7 → warn | TGA 是通读率最高的终止密码子；TAA-T 或 TGA-T 终止效率最高 |
| `hidden_stops` | 任何内部终止 → error | 内部框内终止密码子会破坏蛋白 |
| `gc_window_uniformity` | 标准差 >15% → warn | 极端的局部 GC 波动会损害 IVT 得率 |
| `cpg_balance` | <0.5% 或 >15% → warn | CpG 过低会沉默表达；CpG 过高则激活 TLR9 |

## 命令行

```bash
mrna-ai manufacture --cds input.fasta --utr5 GCCGCCACC --utr3 AAAAAAAAAAAAAA
```

返回一份 JSON 报告，包含逐项检查的状态、得分、严重度以及汇总。
若无任何 `error`，退出码为 0；只要存在 `error`，退出码为 2。

## Python API

```python
from mrna_ai_tools.manufacturability import score_manufacturability

report = score_manufacturability(
    cds,
    utr5="GCCGCCACC",       # optional, for Kozak scoring
    utr3="AAAAAAAAAAAAAA",  # optional, for ARE detection
)

print(f"overall: {report.overall_score:.3f}")
for c in report.checks:
    print(f"  [{c.severity}] {c.name}: {c.summary}")
```

## 参考

- Holtkamp et al. (2006) *Blood* 108.
- Kozak (1986) *Cell* 44.
- Chen & Shyu (1995) *Trends Biochem Sci* 20.
