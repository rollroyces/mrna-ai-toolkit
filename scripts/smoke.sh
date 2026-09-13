#!/usr/bin/env bash
# Local smoke test — mirrors CI. Run from repo root.
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p /tmp/mrnaflow_smoke

echo "[1/4] codon analyze + optimize"
python -m mrnaflow.cli codon \
    --sequence mrnaflow/examples/cas9.fasta \
    --out /tmp/mrnaflow_smoke/cas9_analysis.json
python -m mrnaflow.cli codon \
    --sequence mrnaflow/examples/cas9.fasta --optimize \
    --out /tmp/mrnaflow_smoke/cas9_optimized.json

echo "[2/4] neoantigen (mock)"
python -m mrnaflow.cli neoantigen \
    --variants mrnaflow/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend mock \
    --out /tmp/mrnaflow_smoke/tp53_screen.json

echo "[3/4] trial (mock)"
python -m mrnaflow.cli trial \
    --patient mrnaflow/examples/patient_summary.txt \
    --trials mrnaflow/examples/trials.jsonl --top-k 5 --backend mock \
    --out /tmp/mrnaflow_smoke/trial_match.json

echo "[4/4] lnp (3 targets)"
python -m mrnaflow.cli lnp --target liver --cargo mRNA --intent "cancer vaccine" --out /tmp/mrnaflow_smoke/lnp_liver.json
python -m mrnaflow.cli lnp --target lung  --cargo mRNA --intent "cancer vaccine" --out /tmp/mrnaflow_smoke/lnp_lung.json
python -m mrnaflow.cli lnp --target tumor --cargo mRNA --intent "cancer vaccine" --out /tmp/mrnaflow_smoke/lnp_tumor.json

echo "All four tools OK. Outputs in /tmp/mrnaflow_smoke/."
