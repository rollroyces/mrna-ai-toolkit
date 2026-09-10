"""Unified CLI: `python -m mrna_ai_tools.cli <tool> ...`"""

from __future__ import annotations

import argparse
import json as _json
import sys
from pathlib import Path

from .codon_optimizer import _run_cli as codon_run
from .lnp_advisor import _run_cli as lnp_run
from .manufacturability import score_manufacturability
from .neoantigen_screener import _run_cli as neo_run
from .sc_rna_pipeline import _run_cli as scrna_run
from .trial_matcher import _run_cli as trial_run


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="mrna_ai",
        description="mRNA × AI toolkit (codon / neoantigen / trial / lnp / scrna / manufacture)",
    )
    sub = p.add_subparsers(dest="tool", required=True)

    sub.add_parser("codon", help="codon-usage analysis & greedy optimization")
    sub.add_parser("neoantigen", help="peptide×HLA neoantigen screen")
    sub.add_parser("trial", help="patient-to-trial eligibility matching")
    sub.add_parser("lnp", help="LNP composition recommender")
    sub.add_parser("scrna", help="scRNA-seq → neoantigen handoff pipeline")
    sub.add_parser("manufacture", help="wet-lab manufacturability checks on a CDS")

    args, rest = p.parse_known_args(argv)
    runners = {
        "codon": codon_run,
        "neoantigen": neo_run,
        "trial": trial_run,
        "lnp": lnp_run,
        "scrna": scrna_run,
    }
    if args.tool == "manufacture":
        return _manufacture_run(rest)
    return runners[args.tool](rest)


def _manufacture_run(argv: list[str]) -> int:
    """CLI for the manufacturability checker."""
    p = argparse.ArgumentParser(prog="mrna_ai manufacture")
    p.add_argument(
        "--cds",
        required=True,
        help="FASTA file or raw CDS string (DNA, multiples of 3)",
    )
    p.add_argument(
        "--utr5",
        default="",
        help="optional 5' UTR (DNA) for Kozak scoring",
    )
    p.add_argument(
        "--utr3",
        default="",
        help="optional 3' UTR (DNA) for AU-rich element detection",
    )
    p.add_argument(
        "--out",
        default=None,
        help="output JSON file (default: stdout)",
    )
    args = p.parse_args(argv)

    cds = Path(args.cds).read_text() if Path(args.cds).exists() else args.cds
    # Strip FASTA header if present
    if cds.startswith(">"):
        cds = "".join(line for line in cds.splitlines() if not line.startswith(">"))

    report = score_manufacturability(cds, utr5=args.utr5, utr3=args.utr3)
    out_text = _json.dumps(report.to_dict(), indent=2)
    if args.out:
        Path(args.out).write_text(out_text + "\n")
    else:
        print(out_text)
    return 0 if report.n_error == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
