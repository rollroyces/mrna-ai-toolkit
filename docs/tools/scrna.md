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
mrnavax scrna --expression mrnavax/examples/cells.csv \
              --variants mrnavax/examples/variants_coding.csv \
              --proteins mrnavax/examples/proteins.fasta \
              --tumor-markers GENE_170,GENE_180

# With scanpy (real Leiden clustering)
pip install -e ".[scrna]"
mrnavax scrna --expression path/to/cells.h5ad ...
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
from mrnavax.sc_rna_pipeline import (
    cluster_with_scanpy, embed_with_foundation_model
)
import scgpt  # your installed version

embeddings = scgpt.embed(my_adata)  # whatever the current API is
labels = cluster_with_scanpy(embeddings, cell_ids, gene_names)
```

The `embed_with_foundation_model` function in this package is a thin wrapper
that documents the integration but does not depend on scgpt itself.

## Real-world biology: a gastric-cancer case study

A representative wet-lab workflow that this pipeline is designed to
serve is described in **Qian et al. 2022** (*International Journal of
Cancer* 151(8): 1367-1381):

> Single-cell RNA-seq dissecting heterogeneity of tumor cells and
> comprehensive dynamics in tumor microenvironment during lymph nodes
> metastasis in gastric cancer.

The paper profiles scRNA-seq of primary tumor + lymph node metastases
in gastric cancer, identifies tumor cell clusters, and characterizes
the tumor microenvironment (TME) — including T-cell exhaustion
phenotypes that drive immune escape. The downstream mRNA cancer
vaccine design question is: *which tumor-cluster-specific mutant
peptides are spatially co-localized with exhausted T cells, and could
serve as vaccine targets?*

The toolkit's `scrna` module closes exactly this loop:

```bash
# 1. Cluster the scRNA-seq counts
mrnavax scrna \
  --expression gastric_primary.h5ad \
  --proteins gastric_peptides.fasta \
  --variants patient_variants.csv \
  --output-dir results/

# 2. Hand off the tumor-cluster peptide list to neoantigen screening
mrnavax neoantigen \
  --csv results/tumor_peptides.csv \
  --hla "HLA-A*02:01,HLA-A*24:02" \
  --backend mock
```

The same peptide list can then be processed through:

```bash
# 3. ESM2 protein-LM immunogenicity scoring (frozen LM + classifier)
python -c "
from mrnavax.neoantigen_screener import lm_immunogenicity_score
import pandas as pd
df = pd.read_csv('results/tumor_peptides.csv')
df['lm_score'] = df['peptide'].apply(
    lambda p: lm_immunogenicity_score(p)['score']
)
df.to_csv('results/tumor_peptides_lm_scored.csv', index=False)
"
```

The full Qian-style workflow runs end-to-end on the toolkit's
stdlib-only baseline; users with GPU access can swap in scGPT for
the foundation-model step, ESM2-150M for the immunogenicity scoring,
and the per-peptide Tumor-Microenvironment interaction analysis
remains identical to the published pipeline.

## Reference

Qian Y., Zhai E., Chen S., Liu Y., Ma Y., Chen J., Liu J., Qin C.,
Cao Q.#, Chen J.#, and Cai S.#. (2022). Single-cell RNA-seq
dissecting heterogeneity of tumor cells and comprehensive dynamics
in tumor microenvironment during lymph nodes metastasis in gastric
cancer. *International Journal of Cancer* 151(8): 1367-1381.


## Bulk-data alternative: transcript isoform prediction

The `scrna` module above handles **single-cell** RNA-seq. For
researchers with **bulk RNA-seq + epigenomic tracks** (the more
common clinical setting — tumor biopsies are profiled in bulk, not
dissociated), the toolkit recommends the **universal transcript
isoform model** from Chow et al. 2025 (bioRxiv
[https://doi.org/10.1101/2025.07.21.665977](https://doi.org/10.1101/2025.07.21.665977)):

> A holy grail in computational biology is accurate modeling of
> transcript expression levels using epigenetic features … we
> computationally modeled the expression levels of individual
> transcript isoforms in 324 samples from 29 tissue types, using
> graph-based methods that integrate both location-specific
> epigenomic features and multiple types of gene-gene relationships.

The paper's key empirical finding:

> A model that integrates information from many samples of other
> tissue types **consistently outperforms** a model trained on data
> from this sample itself, providing strong support that it is
> possible to construct a "universal" model that can accurately
> infer transcript isoform expression levels across tissue types.

### Recommended workflow

1. **Bulk RNA-seq + epigenomic tracks** (ATAC-seq, H3K4me3, H3K27ac)
   from the patient's tumor biopsy + matched normal.
2. Apply the Chow et al. universal model (paper-released) to infer
   **per-isoform expression** for every coding gene.
3. For tumor-specifically overexpressed isoforms with novel
   junctions, enumerate 9-11-mer peptides spanning the
   junction-spanning regions.
4. Hand off to the `neoantigen` module (same flow as the scRNA
   pipeline above).

```bash
# Conceptual pipeline — actual Chow et al. model is paper-released;
# the toolkit provides the downstream handoff via neoantigen.
mrnavax neoantigen \
  --csv junction_peptides.csv \
  --hla "HLA-A*02:01,HLA-B*07:02" \
  --backend mock
```

### Why we don't bundle the model yet

The Chow et al. model is currently in **bioRxiv preprint** status and
the trained weights aren't yet released via a stable channel. Once a
PyPI / HuggingFace checkpoint is available, the toolkit will ship
an :class:`IsoformExpressionPredictor` Protocol adapter mirroring the
ESM2 / scGPT pattern (real + mock, deterministic stdlib fallback for
tests). Until then, this documentation serves as the integration
target.

### Reference

Chow S.H.C., Shi C.H., Deshpande A., Cao Q., and Yip K.Y. (2025).
*Towards Universal Modeling of Transcript Isoform Expression Levels.*
bioRxiv [doi:10.1101/2025.07.21.665977](https://doi.org/10.1101/2025.07.21.665977).
