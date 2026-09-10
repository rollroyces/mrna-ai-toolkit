# `codon` — 序列分析與優化

計算所有現代 mRNA 設計模型（CodonBERT、RiboDecode、LinearDesign、mRNABERT）所共同仰賴的標準密碼子使用特徵。

## 用法

```bash
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta
mrna-ai codon --sequence mrna_ai_tools/examples/cas9.fasta --optimize
```

## 輸出 schema

```json
{
  "n_codons": 210,
  "cai": 0.6954,                        // Codon Adaptation Index (0–1)
  "gc_percent": 37.3,                   // 整體 GC%
  "rare_codon_fraction": 0.0429,        // 使用頻率低於 0.10 的密碼子比例
  "cpg_obs_exp": 1.1331,                // CpG O/E 比值——先天免疫之代理指標
  "most_common_codons": [["GAT", 12], ...],
  "rare_codons": ["CTA", "TTA"],
  "gc_window_stddev": 4.75               // 滑動 GC 標準差（轉譯速度之代理指標）
}
```

## `--optimize`

執行一輪貪婪式的同義密碼子替換，在維持 GC% 於 45–60% 區間的前提下，極大化各密碼子的使用頻率。

對一條在人類細胞表現的細菌基因，預期 CAI 約可提升 0.2（例如 Cas9 範例由 0.7 → 0.93）。

這是任何現代密碼子模型都應該超越的**經典基準**。刻意保持簡單，以便您能將更精密的模型（CodonBERT、RiboDecode）以相同的輸入輸出形狀接入並進行比較。
