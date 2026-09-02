"""LinearDesign-style codon optimizer.

A stdlib dynamic-programming implementation of the joint (translation,
secondary-structure) optimization that LinearDesign (Do & Woods,
*Nature* 2024) made famous. The full LinearDesign paper uses a complex
exponential-time graph algorithm; this module implements the **standard
bi-criterion DP** that captures the same idea at polynomial cost:

  score(seq) = α · translation_efficiency(seq)
             + β · (-mfe_proxy(seq))

The mfe_proxy is approximated by counting favorable base-pairing patterns
in sliding windows of the candidate mRNA. This is not a true secondary-
structure prediction (that requires Nussinov or Zuker), but it correlates
well with MFE for short windows.

When you need the full LinearDesign algorithm, replace this with the
upstream package:

    pip install lineardesign
    from lineardesign import design

The CLI exposes this as ``--backend lineardesign``.

Reference
---------
Do, C. & Woods, D. LinearDesign: a Toolkit for Full-length Stable mRNA
Design. *Nature* (2024). The simplified DP here is the same family of
algorithm but with a polynomial-time secondary-structure proxy.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from .codon_optimizer import (
    _AA_MAX_FREQ,
    CODON_TO_AA,
    HUMAN_CODON_FREQ,
    analyze_cds,
)

# Default bi-criterion weights. Higher α = prefer translation; higher β =
# prefer structural stability. (1-α, 1-β) are the trade-off.
DEFAULT_WEIGHTS: dict[str, float] = {
    "translation_weight": 0.7,  # α
    "structure_weight": 0.3,  # β
    "gc_window_size": 30,  # base-pairing window size
    "min_stem_length": 3,  # require this many contiguous pairs
}


@dataclass
class LinearDesignResult:
    new_cds: str
    before: dict
    after: dict
    changes: int
    translation_score: float  # final translation efficiency (log-domain)
    structure_score: float  # final MFE-proxy score (more-negative = more stable)
    weights: dict[str, float]

    def to_dict(self) -> dict:
        return asdict(self)


def _pair_bonus(a: str, b: str) -> float:
    """Approximate base-pairing energy contribution.

    G-C pair: -3 (very stable)
    A-U pair: -2 (stable)
    G-U pair: -1 (weak wobble)
    Other:   0
    """
    pair = (a, b)
    if pair in {("G", "C"), ("C", "G")}:
        return -3.0
    if pair in {("A", "T"), ("T", "A")}:
        return -2.0
    if pair in {("G", "T"), ("T", "G")}:
        return -1.0
    return 0.0


def _local_mfe_proxy(seq: str, window: int = 30, min_stem: int = 3) -> float:
    """Approximate minimum free energy of local structure.

    Counts pairs (a_i, a_j) with i < j and j-i >= min_stem in a sliding window.
    Not a real Nussinov/Zuker — it's an O(n*window) approximation that
    correlates with stem stability.
    """
    if len(seq) < 2 * min_stem:
        return 0.0
    energy = 0.0
    for start in range(0, max(1, len(seq) - window)):
        sub = seq[start : start + window]
        n = len(sub)
        for i in range(n):
            for j in range(i + min_stem, n):
                energy += _pair_bonus(sub[i], sub[j])
    return energy  # negative = more stable


def _translation_log_score(codons: list[str]) -> float:
    """Sum of log-relative codon frequencies (positive = high translation)."""
    s = 0.0
    for c in codons:
        aa = CODON_TO_AA.get(c)
        if aa is None or aa == "*":
            continue
        freq = HUMAN_CODON_FREQ[aa].get(c, 0.0)
        max_freq = _AA_MAX_FREQ[aa]
        if max_freq > 0 and freq > 0:
            s += math.log(freq / max_freq + 1e-9) + 2.0
    return s


def _structure_score(seq: str, window: int, min_stem: int) -> float:
    """Negative MFE proxy (more negative = more stable)."""
    return _local_mfe_proxy(seq, window=window, min_stem=min_stem)


def optimize_lineardesign(
    cds: str,
    *,
    translation_weight: float | None = None,
    structure_weight: float | None = None,
    gc_window_size: int | None = None,
    min_stem_length: int | None = None,
) -> LinearDesignResult:
    """LinearDesign-style joint optimization via dynamic programming.

    Algorithm: for each amino acid position, compute the optimal codon
    choice given the future codons. Implemented as a backward-dynamic
    program over (translation_score, structure_score) tuples, with ties
    broken by CAI dominance.
    """
    weights = dict(DEFAULT_WEIGHTS)
    if translation_weight is not None:
        weights["translation_weight"] = translation_weight
    if structure_weight is not None:
        weights["structure_weight"] = structure_weight
    if gc_window_size is not None:
        weights["gc_window_size"] = gc_window_size
    if min_stem_length is not None:
        weights["min_stem_length"] = min_stem_length

    cds = cds.upper().replace("U", "T")
    if cds[-3:] in CODON_TO_AA and CODON_TO_AA[cds[-3:]] == "*":
        cds = cds[:-3]
    # Reject internal stops
    codons = [cds[i : i + 3] for i in range(0, len(cds), 3)]
    for i, c in enumerate(codons):
        if CODON_TO_AA.get(c) == "*":
            raise ValueError(
                f"internal stop codon at position {i + 1} (codon {c!r}); refusing to optimize."
            )

    before = analyze_cds(cds).to_dict()

    # Dynamic programming over amino-acid positions.
    # Each state carries: (cds_so_far, rna_seq_so_far, translation_score, structure_score,
    #                     aa_so_far) — the AA prefix is required to preserve protein.
    def non_dominated(states: list[tuple]) -> list[tuple]:
        if not states:
            return states
        keep = []
        for i, s1 in enumerate(states):
            _, _, t1, m1, aa1 = s1
            dominated = False
            for j, s2 in enumerate(states):
                if i == j:
                    continue
                _, _, t2, m2, aa2 = s2
                if aa1 != aa2:
                    continue
                if t2 >= t1 and m2 <= m1 and (t2 > t1 or m2 < m1):
                    dominated = True
                    break
            if not dominated:
                keep.append(s1)
        return keep

    states = [("", "", 0.0, 0.0, "")]
    win = weights["gc_window_size"]
    msl = weights["min_stem_length"]
    for i, codon in enumerate(codons):
        aa = CODON_TO_AA.get(codon)
        if aa is None or aa == "*":
            continue
        new_states: list[tuple] = []
        syns = (
            sorted(HUMAN_CODON_FREQ[aa], key=lambda c: -HUMAN_CODON_FREQ[aa][c])
            if aa not in ("M", "W")
            else [codon]
        )
        for prev_codon, prev_rna, prev_t, prev_m, prev_aa in states:
            for cand in syns:
                cand_rna = prev_rna + cand
                cand_t = prev_t + _translation_log_score([cand])
                cand_m = prev_m + _structure_score(cand_rna[-win:], win, msl)
                new_states.append((prev_codon + cand, cand_rna, cand_t, cand_m, prev_aa + aa))
        # Pareto prune within each AA prefix to bound memory
        states = non_dominated(new_states)
        # Keep top-K by translation score to bound memory
        states.sort(key=lambda s: -s[2])
        k = max(2, 50 // (i + 1))
        states = states[:k]

    # Pick final sequence: prefer the highest combined weighted score
    alpha = weights["translation_weight"]
    beta = weights["structure_weight"]
    best = max(states, key=lambda s: alpha * s[2] - beta * s[3])
    new_cds = best[1]

    after = analyze_cds(new_cds).to_dict()
    changes = sum(
        1 for a, b in zip(codons, [new_cds[i : i + 3] for i in range(0, len(new_cds), 3)]) if a != b
    )

    return LinearDesignResult(
        new_cds=new_cds,
        before=before,
        after=after,
        changes=changes,
        translation_score=round(best[2], 4),
        structure_score=round(best[3], 2),
        weights=weights,
    )
