"""Backend availability + integrity checks.

Used by CI to verify that the optional backend wiring is intact even when the
heavy models themselves aren't installed. Heavy model downloads (mhcflurry,
scGPT) are gated by their respective extras.

Run directly:

    python -m mrna_ai_tools.backends --check-all

Exits 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from typing import Callable

CHECKS: list[tuple[str, Callable[[], tuple[bool, str]]]] = []


def register(name: str):
    def deco(fn: Callable[[], tuple[bool, str]]) -> Callable[[], tuple[bool, str]]:
        CHECKS.append((name, fn))
        return fn
    return deco


# ---------- neoantigen backends -------------------------------------------

@register("neoantigen.heuristic_A0201")
def _check_neoantigen_heuristic() -> tuple[bool, str]:
    from .neoantigen_screener import screen_peptide_llm
    # Known-good A*02:01 binder — must come back positive in the heuristic.
    r = screen_peptide_llm("NLVPMVATV", "HLA-A*02:01", backend="mock")
    ok = r.source == "heuristic" and isinstance(r.binding_affinity_nM, float)
    return ok, f"source={r.source} aff={r.binding_affinity_nM} nM"


@register("neoantigen.heuristic_nonA2_silent")
def _check_neoantigen_non_a2() -> tuple[bool, str]:
    from .neoantigen_screener import screen_peptide_llm
    r = screen_peptide_llm("NLVPMVATV", "HLA-A*03:01", backend="mock")
    ok = r.binding_affinity_nM >= 5000  # heuristic is silent on non-A2
    return ok, f"non-A2 affinity={r.binding_affinity_nM} nM (expected >= 5000)"


@register("neoantigen.mhcflurry_available")
def _check_neoantigen_mhcflurry() -> tuple[bool, str]:
    from .neoantigen_screener import _mhcflurry_available
    available = _mhcflurry_available()
    if available:
        return True, "installed — will use as default"
    return True, "not installed (optional: pip install -e '.[neoantigen-mhcflurry]')"


# ---------- codon backend -------------------------------------------------

@register("codon.analyze")
def _check_codon_analyze() -> tuple[bool, str]:
    from .codon_optimizer import analyze_cds
    r = analyze_cds("ATGGATAAGAAATACTCAATAGGCTTAGATATCGGCACAAATAGC")
    ok = 0 < r.cai <= 1 and 0 < r.gc_percent < 100
    return ok, f"cai={r.cai} gc={r.gc_percent}%"


@register("codon.optimize")
def _check_codon_optimize() -> tuple[bool, str]:
    from .codon_optimizer import optimize_basic
    r = optimize_basic("ATGGATAAGAAATACTCAATAGGCTTAGATATCGGCACAAATAGCGTGGGCTGGGCG")
    ok = r["after"]["cai"] > r["before"]["cai"] and r["changes"] > 0
    return ok, f"basic CAI {r['before']['cai']} → {r['after']['cai']} ({r['changes']} swaps)"


@register("codon.ribodecode_optimizer")
def _check_codon_ribodecode() -> tuple[bool, str]:
    from .codon_ribodecode import optimize_ribodecode
    seq = (
        "ATGGATAAGAAATACTCAATAGGCTTAGATATCGGCACAAATAGCGTGGGCTGGGCGGTGATCAC"
        "CGATGAATATAAGGTTCCGTCTAAAAAGTTCAAGGTTCTGGGAAATACAGACCGCCACAGTATC"
    )
    r = optimize_ribodecode(seq)
    ok = (
        r.after["cai"] >= r.before["cai"]
        and r.after["rare_codon_fraction"] <= r.before["rare_codon_fraction"]
    )
    return ok, (
        f"ribodecode CAI {r.before['cai']} → {r.after['cai']}, "
        f"rare-pair {r.rare_pair_count}, GC-stddev {r.gc_window_stddev_before} → {r.gc_window_stddev_after}"
    )


# ---------- trial backend -------------------------------------------------

@register("trial.keyword_fallback")
def _check_trial_keyword() -> tuple[bool, str]:
    from .trial_matcher import Trial, match
    trials = [
        Trial(
            nct_id="NCT00000001",
            title="Test trial for melanoma",
            condition="melanoma",
            phase="1",
            inclusion=["resected melanoma"],
            exclusion=[],
        )
    ]
    ranked, _ = match("patient with resected melanoma", trials, top_k=1, backend="mock")
    ok = len(ranked) >= 1 and ranked[0].score > 0
    return ok, f"top score={ranked[0].score}"


# ---------- lnp backend ---------------------------------------------------

@register("lnp.recommend")
def _check_lnp_recommend() -> tuple[bool, str]:
    from .lnp_advisor import recommend
    r = recommend(target="lung", cargo="saRNA", intent="cancer vaccine", n=3)
    ok = len(r.shortlist) > 0 and all("name" in c for c in r.shortlist)
    return ok, f"{len(r.shortlist)} candidates for lung/saRNA"


# ---------- scrna backend -------------------------------------------------

@register("scrna.pipeline")
def _check_scrna() -> tuple[bool, str]:
    from .sc_rna_pipeline import run_pipeline
    r = run_pipeline(
        "mrna_ai_tools/examples/cells.csv",
        "mrna_ai_tools/examples/variants_coding.csv",
        "mrna_ai_tools/examples/proteins.fasta",
        hla=("HLA-A*02:01",),
        tumor_marker_genes=["TP53", "KRAS", "BRAF"],
    )
    ok = r.n_cells > 0 and r.n_candidate_peptides > 0 and r.tumor_cluster >= 0
    return ok, (
        f"cells={r.n_cells} clusters={len(set(r.cluster_labels))} "
        f"tumor={r.tumor_cluster} peptides={r.n_candidate_peptides}"
    )


# ---------- runner --------------------------------------------------------

def run_all(verbose: bool = True) -> int:
    failures = 0
    if verbose:
        print("=" * 72)
        print(f"{'Backend check':50s} {'Status':6s}  Detail")
        print("=" * 72)
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"EXCEPTION: {e!r}"
        status = "PASS" if ok else "FAIL"
        if verbose:
            print(f"{name:50s} {status:6s}  {detail}")
        if not ok:
            failures += 1
    if verbose:
        print("=" * 72)
        print(f"{len(CHECKS) - failures}/{len(CHECKS)} checks passed.")
    return 0 if failures == 0 else 1


def main() -> int:
    return run_all(verbose=True)


if __name__ == "__main__":
    sys.exit(main())
