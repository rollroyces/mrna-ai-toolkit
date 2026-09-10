# `codon` — 序列分析与优化

计算每个现代 mRNA 设计模型（CodonBERT、RiboDecode、LinearDesign、mRNABERT）
都会消费的经典密码子使用特征。

## 用法

```bash
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize
```

## 输出 schema

```json
{
  "n_codons": 210,
  "cai": 0.6954,                        // Codon Adaptation Index (0–1)
  "gc_percent": 37.3,                   // overall GC%
  "rare_codon_fraction": 0.0429,        // fraction of codons below 0.10 freq
  "cpg_obs_exp": 1.1331,                // CpG O/E ratio — proxy for innate immunity
  "most_common_codons": [["GAT", 12], ...],
  "rare_codons": ["CTA", "TTA"],
  "gc_window_stddev": 4.75               // rolling GC stddev (translation speed proxy)
}
```

## `--optimize`

运行一轮贪心式的同义密码子替换，在保持 GC% 处于 45–60% 区间的条件下，
最大化逐密码子的使用频率。

在人类细胞中表达一个细菌基因时，预期 CAI 的绝对提升约为 0.2
（例如 Cas9 示例从 0.7 提升至 0.93）。

这是任何现代密码子模型都应超越的**经典基线**。它的设计刻意保持简单，
便于你把更复杂的模型（CodonBERT、RiboDecode）接入到相同的输入/输出形状中进行对比。
