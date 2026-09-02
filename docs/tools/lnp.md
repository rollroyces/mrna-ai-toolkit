# `lnp` — lipid nanoparticle composition recommender

A rule-based shortlist of published or ML-discovered ionizable-lipid
formulations for a given (target tissue × cargo × therapeutic intent).

## Usage

```bash
# Cancer vaccine, lung delivery, saRNA cargo
mrna-ai lnp --target lung --cargo saRNA --intent "cancer vaccine"

# Hepatic gene editing with Cas9 mRNA
mrna-ai lnp --target liver --cargo Cas9 --intent "gene editing"

# Intratumoral injection (TRAIL-mRNA example)
mrna-ai lnp --target tumor --cargo mRNA --intent "cancer vaccine"
```

## Output schema

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

## Curated preset table

| Preset | Source | Best for |
|---|---|---|
| SM-102 | Moderna clinical | vaccines (liver/spleen bias) |
| ALC-0315 | Pfizer/BioNTech clinical | vaccines (broader tropism) |
| C12-200 | Love et al. PNAS 2010 | hepatocyte gene editing |
| FO-32, FO-35 | Witten et al. Nat Biotech 2025 | lung delivery (ML-designed) |
| saRNA generic | Arcturus disclosures | self-amplifying mRNA |
| tumor-it | Costa et al. IJN 2025 | intratumoral TRAIL mRNA |

The recommender is the **human-facing shortlist layer** above the trained
models in Witten et al. 2025 (>9,000 measurements, 1.6M candidates screened
in silico) and Li et al. 2024 (combinatorial chemistry + ML). Practitioners
still pick from a shortlist, and this tool is the interface.
