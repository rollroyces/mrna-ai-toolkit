#!/usr/bin/env bash
# Local smoke test — mirrors CI. Run from repo root.
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p /tmp/mrna_ai_smoke

echo "[1/4] codon analyze + optimize"
python -m mrna_ai_tools.cli codon \
    --sequence mrna_ai_tools/examples/cas9.fasta \
    --out /tmp/mrna_ai_smoke/cas9_analysis.json
python -m mrna_ai_tools.cli codon \
    --sequence mrna_ai_tools/examples/cas9.fasta --optimize \
    --out /tmp/mrna_ai_smoke/cas9_optimized.json

echo "[2/4] neoantigen (mock)"
python -m mrna_ai_tools.cli neoantigen \
    --variants mrna_ai_tools/examples/tp53_variants.csv \
    --hla HLA-A*02:01 --backend mock \
    --out /tmp/mrna_ai_smoke/tp53_screen.json

echo "[3/4] trial (mock)"
python -m mrna_ai_tools.cli trial \
    --patient mrna_ai_tools/examples/patient_summary.txt \
    --trials mrna_ai_tools/examples/trials.jsonl --top-k 5 --backend mock \
    --out /tmp/mrna_ai_smoke/trial_match.json

echo "[4/4] lnp (3 targets)"
python -m mrna_ai_tools.cli lnp --target liver --cargo mRNA --intent "cancer vaccine" --out /tmp/mrna_ai_smoke/lnp_liver.json
python -m mrna_ai_tools.cli lnp --target lung  --cargo mRNA --intent "cancer vaccine" --out /tmp/mrna_ai_smoke/lnp_lung.json
python -m mrna_ai_tools.cli lnp --target tumor --cargo mRNA --intent "cancer vaccine" --out /tmp/mrna_ai_smoke/lnp_tumor.json

echo "All four tools OK. Outputs in /tmp/mrna_ai_smoke/."
