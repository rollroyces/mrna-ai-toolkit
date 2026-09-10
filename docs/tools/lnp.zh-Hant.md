# `lnp` — 脂質奈米微粒（LNP）配方推薦器

針對給定（目標組織 × 貨物 × 治療意圖），提供一份以規則篩選、收錄自文獻或經機器學習發現之可離子化脂質配方的精選清單。

## 用法

```bash
# 癌症疫苗，肺部遞送，saRNA 貨物
mrna-ai lnp --target lung --cargo saRNA --intent "cancer vaccine"

# 肝臟基因編輯，Cas9 mRNA
mrna-ai lnp --target liver --cargo Cas9 --intent "gene editing"

# 瘤內注射（TRAIL-mRNA 範例）
mrna-ai lnp --target tumor --cargo mRNA --intent "cancer vaccine"
```

## 輸出 schema

```json
{
  "cargo": "sarna",
  "target": "lung",
  "intent": "cancer vaccine",
  "shortlist": [
    {
      "name": "FO-32 (pulmonary, ML-designed)",
      "ionizable_lipid": "FO-32",
      "helper_lipid": "DOPE",
      "cholesterol_pct": 24.0,
      "peg_lipid": "DMG-PEG2000",
      "peg_mol_pct": 1.0,
      "ionizable_mol_pct": 60.0,
      "helper_mol_pct": 10.0,
      "n_p_ratio": 8.0,
      "source": "Witten et al. Nat Biotech 2025",
      "notes": "Top hit from ML-guided screening (>1.6M candidates); ferret-lung delivery."
    }
  ],
  "notes": [
    "Pulmonary delivery benefits from ML-discovered biodegradable lipids (Witten 2025).",
    "saRNA prefers higher cholesterol and lower PEG for replicon stability."
  ]
}
```

## 精選預設配方表

| 預設配方 | 出處 | 最適用途 |
|---|---|---|
| SM-102 | Moderna 臨床用 | 疫苗（肝/脾傾向） |
| ALC-0315 | Pfizer/BioNTech 臨床用 | 疫苗（更廣的組織親和性） |
| C12-200 | Love et al. PNAS 2010 | 肝細胞基因編輯 |
| FO-32、FO-35 | Witten et al. Nat Biotech 2025 | 肺部遞送（ML 設計） |
| saRNA generic | Arcturus 公開資料 | 自放大 mRNA |
| tumor-it | Costa et al. IJN 2025 | 瘤內注射 TRAIL mRNA |

本推薦器是 Witten et al. 2025（>9,000 筆量測、in silico 篩選 1.6M 候選）與 Li et al. 2024（組合化學 + ML）等已訓練模型之上的**人機介面精選層**。實務工作者仍自一份短名單中挑選，本工具即是其介面。
