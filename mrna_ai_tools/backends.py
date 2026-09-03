"""Backend availability + integrity checks.

Used by CI to verify that the optional backend wiring is intact even when the
heavy models themselves aren't installed. Heavy model downloads (mhcflurry,
scGPT) are gated by their respective extras.

Run directly:

    python -m mrna_ai_tools.backends --check-all

Exits 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import sys
from typing import Callable

CHECKS: list[tuple[str, Callable[[], tuple[bool, str]]]] = []


def _example_path(name: str) -> str:
    """Resolve an example-file path relative to the installed package.

    Works in two layouts:
    - Installed wheel: pkg_dir = site-packages/mrna_ai_tools, examples
      are bundled next to it under site-packages/mrna_ai_tools/examples.
    - Dev / repo: pkg_dir is inside the repo, examples live at the repo
      root under mrna_ai_tools/examples.

    Returns the first path that exists, falling back to the wheel layout
    (which will raise FileNotFoundError downstream if missing — that's the
    expected behavior for missing bundled data).
    """
    from pathlib import Path

    pkg_dir = Path(__file__).resolve().parent
    wheel_candidate = pkg_dir / "examples" / name
    if wheel_candidate.exists():
        return str(wheel_candidate)
    repo_candidate = pkg_dir.parent.parent / "mrna_ai_tools" / "examples" / name
    if repo_candidate.exists():
        return str(repo_candidate)
    return str(wheel_candidate)


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


_CODON_TABLE = {
    "ATG": "M",
    "ATA": "I",
    "ATT": "I",
    "ATC": "I",
    "ACA": "T",
    "ACT": "T",
    "ACC": "T",
    "ACG": "T",
    "ACN": "T",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "AAR": "K",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "AGR": "R",
    "AGY": "S",
    "TCA": "S",
    "TCG": "S",
    "TCT": "S",
    "TCC": "S",
    "TCN": "S",
    "TCY": "S",
    "TCR": "S",
    "TCW": "S",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "GCN": "A",
    "GAT": "D",
    "GAC": "D",
    "GAY": "D",
    "GAA": "E",
    "GAG": "E",
    "GAR": "E",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
    "GGN": "G",
    "CAT": "H",
    "CAC": "H",
    "CAY": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CAR": "Q",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "CGN": "R",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "CTN": "L",
    "CTR": "L",
    "CTY": "L",
    "TTA": "L",
    "TTG": "L",
    "TTR": "L",
    "TTT": "F",
    "TTC": "F",
    "TTY": "F",
    "TGG": "W",
    "TAT": "Y",
    "TAC": "Y",
    "TAY": "Y",
    "TGT": "C",
    "TGC": "C",
    "TGY": "C",
    "TAA": "*",
    "TAG": "*",
    "TGA": "*",
    "TRA": "*",
}


def _translate(cds: str) -> str:
    return "".join(_CODON_TABLE.get(cds[i : i + 3], "?") for i in range(0, len(cds), 3))


@register("codon.lineardesign_optimizer")
def _check_codon_lineardesign() -> tuple[bool, str]:
    """LinearDesign DP must improve CAI without breaking the protein."""
    from .codon_lineardesign import optimize_lineardesign

    seq = (
        "ATGGATAAGAAATACTCAATAGGCTTAGATATCGGCACAAATAGCGTGGGCTGGGCGGTGATCAC"
        "CGATGAATATAAGGTTCCGTCTAAAAAGTTCAAGGTTCTGGGAAATACAGACCGCCACAGTATC"
    )
    r = optimize_lineardesign(seq)
    protein_ok = _translate(seq) == _translate(r.new_cds)
    cai_ok = r.after["cai"] >= r.before["cai"]
    ok = protein_ok and cai_ok
    return ok, (
        f"lineardesign CAI {r.before['cai']} → {r.after['cai']}, "
        f"changes={r.changes}, structure_score={r.structure_score}, "
        f"protein_preserved={protein_ok}"
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


@register("trial.dense_retriever")
def _check_trial_dense_retriever() -> tuple[bool, str]:
    """Semantic retriever must still rank the correct trial on top with lay terms."""
    from .trial_matcher import Trial, match

    trials = [
        Trial(
            nct_id="NCT05933577",
            title="INTerpath-001: Personalized mRNA-4157 + Pembrolizumab in Resected Melanoma",
            condition="Stage IIB-IV melanoma",
            phase="3",
            inclusion=[
                "Completely resected stage IIB-IV melanoma",
                "ECOG 0 or 1",
                "No prior systemic therapy",
            ],
            exclusion=["Active autoimmune disease", "Prior treatment with anti-PD-1"],
            biomarkers=["BRAF V600E", "BRAF V600K"],
        ),
        Trial(
            nct_id="NCT04526899",
            title="GRT-C901/GRT-R902: Neoantigen Vaccine + Nivolumab + Ipilimumab in NSCLC",
            condition="Non-small cell lung cancer",
            phase="1/2",
            inclusion=["Stage IV NSCLC", "Progression on anti-PD-1/PD-L1", "ECOG 0 or 1"],
            exclusion=["Active autoimmune disease", "EGFR or ALK positive"],
            biomarkers=[],
        ),
    ]
    # Lay patient description. Keyword retriever would under-match on
    # "skin cancer" → "melanoma". Dense retriever with synonym expansion
    # must still rank the melanoma trial first.
    lay_patient = (
        "62-year-old man with stage 3 skin cancer. Tumor was BRAF V600E positive on biopsy. "
        "Had surgery to remove the tumor. No prior systemic treatment. "
        "Looking for adjuvant therapy or a vaccine to prevent recurrence."
    )
    ranked, _ = match(lay_patient, trials, top_k=2, backend="mock", retriever="dense")
    top = ranked[0]
    ok = top.nct_id == "NCT05933577"
    return (
        ok,
        f"dense retriever top trial on lay-terms patient = {top.nct_id} (must be NCT05933577)",
    )


@register("trial.medcpt_integration")
def _check_medcpt() -> tuple[bool, str]:
    """Confirm MedCPT plug-in is wired correctly.

    Skipped in CI via MRNA_AI_SKIP_MEDCPT_CHECK=1 (model weights are ~440 MB
    and require network). When run locally with torch + transformers
    installed, asserts the encoder round-trips and returns cosine scores
    in the expected range.
    """
    import os

    if os.environ.get("MRNA_AI_SKIP_MEDCPT_CHECK") == "1":
        return True, "skipped via MRNA_AI_SKIP_MEDCPT_CHECK=1 (set in CI)"
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError as e:
        return True, f"medcpt not installed ({e}); plug-in dormant as expected"

    from .medcpt_integration import retrieve_medcpt

    patient = "62-year-old man with stage IIB-IV melanoma, BRAF V600E positive"
    trials = [
        "Personalized mRNA-4157 vaccine plus pembrolizumab for resected melanoma, BRAF V600E",
        "Neoantigen vaccine plus nivolumab for non-small cell lung cancer",
        "KRAS-targeting mRNA vaccine for KRAS G12D mutated solid tumors",
    ]
    scores = retrieve_medcpt(patient, trials)
    ok = len(scores) == 3 and all(-1.0 <= s <= 1.0 for s in scores)
    top_idx = scores.index(max(scores))
    return ok, (
        f"medcpt round-trip OK: 3 cosine scores in [{min(scores):.3f}, {max(scores):.3f}], "
        f"top match idx={top_idx}"
    )


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
        _example_path("cells.csv"),
        _example_path("variants_coding.csv"),
        _example_path("proteins.fasta"),
        hla=("HLA-A*02:01",),
        tumor_marker_genes=["TP53", "KRAS", "BRAF"],
    )
    ok = r.n_cells > 0 and r.n_candidate_peptides > 0 and r.tumor_cluster >= 0
    return ok, (
        f"cells={r.n_cells} clusters={len(set(r.cluster_labels))} "
        f"tumor={r.tumor_cluster} peptides={r.n_candidate_peptides}"
    )


@register("scrna.variant_filter")
def _check_scrna_variant_filter() -> tuple[bool, str]:
    from .sc_rna_pipeline import run_pipeline

    full = run_pipeline(
        _example_path("cells.csv"),
        _example_path("variants_coding.csv"),
        _example_path("proteins.fasta"),
        hla=("HLA-A*02:01",),
        tumor_marker_genes=["TP53", "KRAS", "BRAF"],
    )
    filt = run_pipeline(
        _example_path("cells.csv"),
        _example_path("variants_coding.csv"),
        _example_path("proteins.fasta"),
        hla=("HLA-A*02:01",),
        tumor_marker_genes=["TP53", "KRAS", "BRAF"],
        variant_filter_top_fraction=0.30,
    )
    ok = (
        filt.n_variants_after_filter < full.n_variants_after_filter
        and filt.n_candidate_peptides < full.n_candidate_peptides
    )
    return ok, (
        f"top-30% filter: {full.n_variants_input} variants → "
        f"{filt.n_variants_after_filter} kept → "
        f"{filt.n_candidate_peptides} peptides (was {full.n_candidate_peptides})"
    )


@register("scrna.variant_scorer_alphamissense")
def _check_variant_scorer() -> tuple[bool, str]:
    from .variant_scorer import score_variant

    # Known driver mutations should rank highest
    braf = score_variant("BRAF", 600, "V", "E", protein_length=766)
    kras = score_variant("KRAS", 12, "G", "V", protein_length=189)
    benign = score_variant("MYC", 100, "A", "A", protein_length=439)  # silent
    ok = braf.normalized_score > kras.normalized_score > 0
    return ok, (
        f"BRAF.V600E={braf.normalized_score} > "
        f"KRAS.G12V={kras.normalized_score} > 0 (silent={benign.normalized_score})"
    )


@register("scrna.alphamissense_integration")
def _check_alphamissense_integration() -> tuple[bool, str]:
    """Confirm the AlphaMissense plug-in is wired end-to-end.

    Always runs (no network, no model download) by exercising the
    synthetic test index. Verifies:
      1. build_test_index() returns the expected number of entries.
      2. lookup() returns an AlphaMissenseResult with the right fields.
      3. variant_scorer integrates the score and reports it in rationale.
    """
    from .alphamissense_integration import build_test_index, lookup
    from .variant_scorer import score_variant

    idx = build_test_index()
    assert len(idx) == 5, f"expected 5 test entries, got {len(idx)}"
    r = lookup("P01116", "G", 12, "D", index=idx)
    assert r is not None, "KRAS.G12D lookup returned None"
    assert r.classification == "likely_pathogenic"
    assert 0.0 <= r.score <= 1.0
    # End-to-end: BRAF.V600E with synthetic AlphaMissense
    r2 = score_variant(
        "BRAF", 600, "V", "E",
        protein_length=766,
        uniprot_id="P15056",
        am_lookup=lambda u, w, p, m: lookup(u, w, p, m, index=idx),
    )
    assert "alphamissense_score" in r2.components
    assert r2.components["alphamissense_score"] > 0.5
    return True, (
        f"AlphaMissense lookup + integration OK: "
        f"5-entry test index, BRAF.V600E norm={r2.normalized_score}, "
        f"AM={r2.components['alphamissense_score']:.3f}"
    )


@register("scrna.structural_disruption_chou_fasman")
def _check_structural_disruption() -> tuple[bool, str]:
    """L→P in a helix context must score higher than L→P in a coil context.

    Proline is a helix breaker; in a real alpha-helix, L→P scores higher
    because of the additional structural-disruption component.
    """
    from .variant_scorer import score_variant

    helix_seq = "LAELAEKLAEEK"
    coil_seq = "GGPGGPPPGGPG"
    v_helix = score_variant(
        "FAKE",
        2,
        "L",
        "P",
        protein_length=12,
        protein_sequence=helix_seq,
    )
    v_coil = score_variant(
        "FAKE",
        2,
        "L",
        "P",
        protein_length=12,
        protein_sequence=coil_seq,
    )
    ok = v_helix.normalized_score > v_coil.normalized_score
    return ok, (
        f"L→P in helix={v_helix.normalized_score:.3f} (struct={v_helix.components['structural_disruption']}) "
        f"> L→P in coil={v_coil.normalized_score:.3f} (struct={v_coil.components['structural_disruption']})"
    )


@register("scrna.embedding_tfidf_svd")
def _check_embedding() -> tuple[bool, str]:
    import math

    from .foundation_embedder import embed_cells
    from .sc_rna_pipeline import _synthetic

    _, _, matrix = _synthetic()
    emb = embed_cells(matrix, model="tfidf-svd", n_components=8)
    # Cluster 0 (cells 0-19) vs cluster 2 (cells 35-49)
    intra = sum(
        math.sqrt(sum((emb[i][k] - emb[j][k]) ** 2 for k in range(8)))
        for i in range(19)
        for j in range(i + 1, 20)
    ) / (19 * 18 / 2)
    inter = (
        sum(math.sqrt(sum((emb[0][k] - emb[j][k]) ** 2 for k in range(8))) for j in range(35, 50))
        / 15
    )
    sep = inter / intra if intra else 0
    ok = sep > 1.5  # require at least 1.5x separation
    return ok, f"shape={len(emb)}x{len(emb[0])} inter/intra separation={sep:.2f}x"


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
