"""Protocol interfaces for protein-language-model embedders.

This module defines the typed contracts that any protein-LM embedder
must satisfy to plug into the toolkit. Implementations live in
``protein_lm_adapter.py``:

- :class:`ESM2Embedder`: real adapter via transformers.AutoModel.
  Heavy: torch, transformers, ~135 MB download.
- :class:`MockProteinLMEmbedder`: deterministic stdlib stub using
  AA k-mer frequencies. Used in CI and offline runs.

One protocol is defined:

- :class:`ProteinLMEmbedder`: takes a list of AA sequences and returns
  fixed-dim embedding vectors.

Why a Protocol rather than ABC: the toolkit ships without torch /
transformers installed. The Protocol lets users who do install
HuggingFace stack plug in ESM2 / ESMFold / ProtT5 / etc. via a 2-line
adapter. The type checker verifies conformance via runtime_checkable.

Data contracts
--------------
- :class:`EmbeddingRequest`: typed input (sequences, model_id, pooling,
  batch_size). Validates AA alphabet at construction.
- :class:`EmbeddingResult`: typed output (embeddings, dim, model_id,
  backend, elapsed_seconds, notes).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Protocol, runtime_checkable

# Standard 20 amino acid alphabet (ESM2 expects uppercase)
_STANDARD_AA = frozenset("ACDEFGHIKLMNPQRSTVWY")
_VALID_POOLING = ("mean", "cls", "sum")
_DEFAULT_MODEL = "facebook/esm2_t12_35M_UR50D"


@dataclass(frozen=True)
class EmbeddingRequest:
    """Typed input for protein-LM embedding.

    Attributes
    ----------
    sequences
        Tuple of amino-acid sequences (uppercase, standard 20 AA only).
        Lowercase input is normalized to uppercase before validation.
    model_id
        HuggingFace model identifier (e.g.
        ``facebook/esm2_t12_35M_UR50D``). Default: ESM2-35M (12 layers,
        480-dim). Other options: ``facebook/esm2_t6_8M_UR50D`` (8M,
        320-dim, faster), ``facebook/esm2_t30_150M_UR50D`` (150M,
        640-dim, more accurate).
    pooling
        How to reduce residue-level embeddings to one vector per
        sequence:
          - ``"mean"``: mean-pool over residue positions (default,
            matches ESM2 paper convention).
          - ``"cls"``: take the first token's embedding (CLS-style).
          - ``"sum"``: sum over residue positions (preserves length
            signal).
    batch_size
        Number of sequences per forward-pass batch. Default 8.
    """

    sequences: tuple[str, ...]
    model_id: str = _DEFAULT_MODEL
    pooling: str = "mean"
    batch_size: int = 8

    def __post_init__(self) -> None:
        if not self.sequences:
            raise ValueError("sequences must be non-empty")
        if self.pooling not in _VALID_POOLING:
            raise ValueError(
                f"pooling {self.pooling!r} not in {list(_VALID_POOLING)}; "
                f"valid options: mean, cls, sum"
            )
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self.batch_size}")
        # Normalize to uppercase + validate AA alphabet
        normalized: list[str] = []
        for i, seq in enumerate(self.sequences):
            if not seq:
                raise ValueError(f"sequence[{i}] is empty")
            upper = seq.upper()
            invalid = sorted(set(upper) - _STANDARD_AA)
            if invalid:
                raise ValueError(
                    f"sequence[{i}] contains non-standard amino acids: "
                    f"{invalid}; ESM2 only supports the 20 standard AAs"
                )
            normalized.append(upper)
        # Frozen dataclass: bypass __setattr__ via object.__setattr__
        object.__setattr__(self, "sequences", tuple(normalized))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EmbeddingResult:
    """Typed output of a protein-LM embedding run.

    Attributes
    ----------
    embeddings
        Tuple of tuples — ``embeddings[i]`` is the embedding for
        ``request.sequences[i]``. Each inner tuple has length ``dim``.
    dim
        Embedding dimension. Must match the length of each embedding
        vector (validated at construction).
    model_id
        The model identifier that produced these embeddings.
    backend
        ``"transformers"`` for real ESM2, ``"mock"`` for the stdlib
        stub. Used for audit + routing in the toolkit.
    elapsed_seconds
        Wall-clock time for the full batch.
    notes
        Free-form debug notes (e.g., ``"transformers-not-installed-fallback"``).
    """

    embeddings: tuple[tuple[float, ...], ...]
    dim: int
    model_id: str
    backend: str
    elapsed_seconds: float
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.embeddings:
            raise ValueError("embeddings must be non-empty")
        for i, emb in enumerate(self.embeddings):
            if len(emb) != self.dim:
                raise ValueError(f"embeddings[{i}] has dim {len(emb)}, expected {self.dim}")

    def to_dict(self) -> dict:
        return {
            "embeddings": [list(e) for e in self.embeddings],
            "dim": self.dim,
            "model_id": self.model_id,
            "backend": self.backend,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
            "notes": list(self.notes),
        }


@runtime_checkable
class ProteinLMEmbedder(Protocol):
    """Compute protein-language-model embeddings for AA sequences.

    Implementations:
        - ``MockProteinLMEmbedder``: deterministic stdlib stub used by
          tests + offline runs.
        - ``ESM2Embedder``: real adapter via transformers.AutoModel +
          AutoTokenizer. Heavy: torch, transformers, ~135 MB download
          for the default ESM2-35M model.

    Contract: ``embed()`` must never raise on input that passes
    :class:`EmbeddingRequest` validation. Unknown sequences (none in
    current implementation), tokenizer errors, or runtime errors
    should be surfaced as ``notes`` on the result rather than as
    exceptions — the toolkit's downstream neoantigen pipeline
    tolerates partial results.
    """

    def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...
