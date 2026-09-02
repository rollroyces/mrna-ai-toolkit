# `scrna` — scRNA-seq → neoantigen handoff pipeline

Closes the loop from tissue to vaccine design:

1. Load an AnnData (h5ad) or CSV/TSV (cells × genes) expression matrix.
2. Cluster cells — uses scanpy Leiden if installed, otherwise a stdlib k-medoids.
3. Identify the tumor cluster (by supplied marker genes, or largest cluster by default).
4. For each coding-region SNV in the supplied variant CSV that is in a tumor-cluster-expressed gene:
   - Enumerate 9-11-mer peptides overlapping the variant.
5. Hand off the peptide list to the neoantigen screener.

## Usage

```bash
# Stdlib-only (uses synthetic expression data + k-medoids)
mrna-ai scrna --expression mrna_ai_tools/examples/cells.csv \
              --variants mrna_ai_tools/examples/variants_coding.csv \
              --proteins mrna_ai_tools/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180

# With scanpy (real Leiden clustering)
pip install -e ".[scrna]"
mrna-ai scrna --expression path/to/cells.h5ad ...
```

## Input files

- **Expression** — cells × genes CSV/TSV. If the file doesn't exist, a deterministic 50-cell × 200-gene synthetic dataset is used so the rest of the pipeline runs.
- **Variants** — CSV with columns `gene,position,wt_aa,mut_aa`.
- **Proteins** — multi-record FASTA, one protein sequence per gene symbol.

## Output schema

```json
{
  "n_cells": 50,
  "n_genes": 200,
  "cluster_labels": [0, 0, ...],
  "cluster_marker_scores": {"0": 0.34, "1": 0.41, "2": 2.87},
  "tumor_cluster": 2,
  "n_variants_input": 7,
  "n_candidate_peptides": 24,
  "peptides": [
    {
      "cell_cluster": 2,
      "gene": "TP53",
      "position": 175,
      "wt_aa": "R",
      "mut_aa": "H",
      "peptide": "HMTEVVRRC",
      "length": 9,
      "cluster_marker_score": 2.87
    }
  ]
}
```

## Integration with scGPT

The `embed_with_foundation_model` function in `sc_rna_pipeline.py` is the
explicit plug point for scGPT, Geneformer, or UNI-RNA embeddings. With
neither installed, the pipeline falls back to identity embeddings (per-cell
mean expression), which is sufficient for k-medoids clustering but
insufficient for fine-grained cell-type identification.

To wire scGPT:

```python
# In a custom integration script:
from mrna_ai_tools.sc_rna_pipeline import (
    cluster_with_scanpy, embed_with_foundation_model
)
import scgpt  # your installed version

embeddings = scgpt.embed(my_adata)  # whatever the current API is
labels = cluster_with_scanpy(embeddings, cell_ids, gene_names)
```

The `embed_with_foundation_model` function in this package is a thin wrapper
that documents the integration but does not depend on scgpt itself.
