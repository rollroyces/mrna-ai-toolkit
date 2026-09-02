"""Unified CLI: `python -m mrna_ai_tools.cli <tool> ...`"""
from __future__ import annotations

import argparse
import sys

from .codon_optimizer import _run_cli as codon_run
from .neoantigen_screener import _run_cli as neo_run
from .trial_matcher import _run_cli as trial_run
from .lnp_advisor import _run_cli as lnp_run


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mrna_ai",
                                description="mRNA × AI toolkit (codon / neoantigen / trial / lnp)")
    sub = p.add_subparsers(dest="tool", required=True)

    sub.add_parser("codon", help="codon-usage analysis & greedy optimization")
    sub.add_parser("neoantigen", help="peptide×HLA neoantigen screen")
    sub.add_parser("trial", help="patient-to-trial eligibility matching")
    sub.add_parser("lnp", help="LNP composition recommender")

    args, rest = p.parse_known_args(argv)
    runners = {
        "codon": codon_run,
        "neoantigen": neo_run,
        "trial": trial_run,
        "lnp": lnp_run,
    }
    return runners[args.tool](rest)


if __name__ == "__main__":
    sys.exit(main())
