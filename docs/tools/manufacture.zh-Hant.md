# mRNA 可製造性檢查器

介於「計算上的序列設計」與「實際可在量產規模合成」之間的橋樑。

## 為何重要

一條在演算法上完美無瑕的 mRNA 序列，仍可能完全無法量產。實際生產時，必須檢查會導致 DNA 模板不穩定、阻斷核糖體掃描、或觸發 mRNA 分解的各式 motifs——這些問題往往只在濕實驗中才會顯現。

## 八項檢查

| 檢查項 | 嚴重度門檻 | 攔截的問題 |
|---|---|---|
| `poly_a_runs` | A ≥ 7 → error | DNA 模板中的 Poly-A 連續片段會在 IVT 期間破壞質體穩定性 |
| `gc_5prime_hairpin` | GC ≥ 70% → warn，≥ 80% → error | 5' 端富含 GC 的幹結構會阻斷核糖體掃描 |
| `kozak_strength` | 比對 < 45% → warn | 哺乳動物轉譯需要強 Kozak 一致序列（`GCCRCCATGG`） |
| `are_motif` | 出現 ≥ 1 個 nonamer → warn，≥ 2 → error | 3' UTR 中的 AU-rich 元件會觸發 mRNA 分解 |
| `stop_context` | 滲漏性 ≥ 0.7 → warn | TGA 是滲漏性最高的終止密碼子；TAA-T 或 TGA-T 最為強勢 |
| `hidden_stops` | 出現任何內部終止密碼子 → error | 內部框內終止密碼子會截斷蛋白質 |
| `gc_window_uniformity` | 標準差 > 15% → warn | 局部 GC 過度變化會損害 IVT 產率 |
| `cpg_balance` | < 0.5% 或 > 15% → warn | CpG 過低會抑制表現；過高則會活化 TLR9 |

## CLI

```bash
mrna-ai manufacture --cds input.fasta --utr5 GCCGCCACC --utr3 AAAAAAAAAAAAAA
```

回傳一份 JSON 報告，內含每項檢查的狀態、分數、嚴重度與摘要。若無任何 error，結束代碼為 0；若有任一項檢查回傳 `error`，則結束代碼為 2。

## Python API

```python
from mrna_ai_tools.manufacturability import score_manufacturability

report = score_manufacturability(
    cds,
    utr5="GCCGCCACC",       # 選填，用於 Kozak 評分
    utr3="AAAAAAAAAAAAAA",  # 選填，用於 ARE 偵測
)

print(f"overall: {report.overall_score:.3f}")
for c in report.checks:
    print(f"  [{c.severity}] {c.name}: {c.summary}")
```

## 參考文獻

- Holtkamp et al. (2006) *Blood* 108.
- Kozak (1986) *Cell* 44.
- Chen & Shyu (1995) *Trends Biochem Sci* 20.
