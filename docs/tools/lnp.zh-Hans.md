# `lnp` — 脂质纳米颗粒配方推荐器

针对给定（靶组织 × 载荷 × 治疗目的）组合，给出基于规则筛选的、已发表或
ML 发现的离子化脂质配方短名单。

## 用法

```bash
# 癌症疫苗，肺部递送，saRNA 载荷
mrna-ai lnp --target lung --cargo saRNA --intent "cancer vaccine"

# 肝脏基因编辑，使用 Cas9 mRNA
mrna-ai lnp --target liver --cargo Cas9 --intent "gene editing"

# 瘤内注射（TRAIL-mRNA 示例）
mrna-ai lnp --target tumor --cargo mRNA --intent "cancer vaccine"
```

## 输出 schema

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

## 精选配方预设表

| 预设 | 来源 | 最适用场景 |
|---|---|---|
| SM-102 | Moderna 临床 | 疫苗（肝/脾偏靶） |
| ALC-0315 | Pfizer/BioNTech 临床 | 疫苗（更广的组织趋向性） |
| C12-200 | Love et al. PNAS 2010 | 肝细胞基因编辑 |
| FO-32, FO-35 | Witten et al. Nat Biotech 2025 | 肺部递送（ML 设计） |
| saRNA generic | Arcturus 披露 | 自扩增 mRNA |
| tumor-it | Costa et al. IJN 2025 | 瘤内注射 TRAIL mRNA |

本推荐器是位于训练模型 Witten et al. 2025（>9,000 次实测、160 万候选虚拟筛选）
以及 Li et al. 2024（组合化学 + ML）之上的**面向人工筛选的短名单层**。
实际从业者仍需从短名单中挑选，本工具即为这一挑选过程提供接口。
