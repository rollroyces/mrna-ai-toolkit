"""Protocol interfaces for spatial-transcriptomics backends.

This module defines the typed contracts that any spatial-module
backend must satisfy to plug into the toolkit. Implementations live
in ``spatial_module_adapter.py``:

- :class:`STModuleCLIAdapter`: shells out to the published STModule
  R package (Wang et al., *Genome Medicine* 17, 18 (2025)) when
  installed. Heavy deps (R 4.4+, Seurat v5, torch, GPUmatrix 1.0.2,
  CUDA 11.7).
- :class:`MockSpatialModuleBackend`: deterministic stdlib stub used
  in CI and offline runs.

One protocol is defined:

- :class:`SpatialModuleBackend`: takes a :class:`SpatialData` and
  returns a :class:`SpatialModuleResult` of identified tissue modules
  + associated genes.

Why a Protocol rather than ABC: the toolkit ships without R / Seurat
/ CUDA installed. The Protocol lets users who do install the official
STModule package plug it in via a 2-line adapter without inheritance
contracts. The type checker can verify conformance.

Data contracts
--------------
- :class:`SpatialData`: typed input (count matrix path, locations path,
  platform enum, num_modules).
- :class:`SpatialModule`: one identified tissue module with top genes.
- :class:`SpatialModuleResult`: aggregate result with all modules,
  spot count, timing, backend name, notes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SpatialPlatform(str, Enum):
    """SRT technology platform — drives preprocessing params in STModule.

    Values map to the ``high_resolution`` parameter in the published
    R API (Wang et al., Genome Medicine 2025):
      - ST / Visium = ``high_resolution=FALSE`` (default)
      - SlideSeqV2 / StereoSeq = ``high_resolution=TRUE``
    """

    ST = "ST"
    Visium = "Visium"
    SlideSeqV2 = "SlideSeqV2"
    StereoSeq = "StereoSeq"
    Other = "Other"

    @classmethod
    def from_string(cls, s: str) -> "SpatialPlatform":
        """Parse a string into a SpatialPlatform, case-sensitive.

        Mirrors the published R package which is also case-sensitive
        on platform names.
        """
        for p in cls:
            if p.value == s:
                return p
        valid = ", ".join(p.value for p in cls)
        raise ValueError(f"unknown platform {s!r}; valid options: {valid}")

    @property
    def is_high_resolution(self) -> bool:
        """True iff the platform requires ``high_resolution=TRUE``.

        Mirrors STModule's recommendation: ST / Visium are coarse,
        SlideSeqV2 / StereoSeq are sub-cellular.
        """
        return self in (SpatialPlatform.SlideSeqV2, SpatialPlatform.StereoSeq)


# ---------------------------------------------------------------------------
# Input dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpatialData:
    """Typed input for spatial-module identification.

    Mirrors the two TSV inputs the published STModule R package
    expects (count matrix + spatial locations). We intentionally do
    NOT bundle the package's preprocessing (Seurat-based HVG
    selection) — callers pre-filter their data with their tool of
    choice and feed the toolkit already-cleaned TSVs.

    Attributes
    ----------
    count_file
        Path to a TSV count matrix (spots × genes). Header row with
        gene names; spot IDs in the first unnamed column.
    locations_file
        Path to a TSV with two numeric columns ``x`` and ``y`` (spot
        coordinates in tissue space). Header row; spot IDs in the
        first unnamed column. Spot IDs must match the count matrix
        exactly (or be a subset — see MockSpatialModuleBackend).
    platform
        SRT technology. Drives preprocessing + max_iter defaults in
        the upstream package.
    num_modules
        Number of tissue modules to identify. STModule's tutorial
        recommends 10 for "major expression components"; larger
        values yield finer-grained decomposition.
    """

    count_file: Path
    locations_file: Path
    platform: str = "ST"
    num_modules: int = 10

    def __post_init__(self) -> None:
        # Platform enum coercion (raises if invalid)
        SpatialPlatform.from_string(self.platform)
        # Path existence check
        if not self.count_file.exists():
            raise FileNotFoundError(f"count_file does not exist: {self.count_file}")
        if not self.locations_file.exists():
            raise FileNotFoundError(f"locations_file does not exist: {self.locations_file}")
        # num_modules sanity
        if self.num_modules < 1:
            raise ValueError(f"num_modules must be >= 1, got {self.num_modules}")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["count_file"] = str(self.count_file)
        d["locations_file"] = str(self.locations_file)
        return d

    @property
    def is_high_resolution(self) -> bool:
        """Shortcut for ``SpatialPlatform.from_string(platform).is_high_resolution``."""
        return SpatialPlatform.from_string(self.platform).is_high_resolution


# ---------------------------------------------------------------------------
# Output dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpatialModule:
    """One identified tissue module with its top associated genes.

    Mirrors the output of the published R function
    ``get_assocaited_genes()`` (sic, typo in upstream) — collapsed to
    the top-N genes per module for the toolkit's handoff to the
    neoantigen pipeline.
    """

    module_id: int
    top_genes: tuple[str, ...]
    n_spots: int
    mean_activity: float

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "top_genes": list(self.top_genes),
            "n_spots": self.n_spots,
            "mean_activity": round(self.mean_activity, 4),
        }


@dataclass(frozen=True)
class SpatialModuleResult:
    """Aggregate result for one tissue section.

    Returned by ``SpatialModuleBackend.run()``. JSON-serializable
    via :meth:`to_dict` — the real backend (R subprocess) emits
    exactly this shape on stdout.
    """

    platform: str
    modules: tuple[SpatialModule, ...]
    n_spots: int
    elapsed_seconds: float
    backend: str  # "stmodule" | "mock"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "modules": [m.to_dict() for m in self.modules],
            "n_spots": self.n_spots,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "backend": self.backend,
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class SpatialModuleBackend(Protocol):
    """Identify tissue modules from spatial-transcriptomics data.

    Implementations:
        - ``MockSpatialModuleBackend``: deterministic stdlib stub
          used by tests + offline runs.
        - ``STModuleCLIAdapter``: shells out to the published R
          package via a small shim. Heavy: R 4.4+, Seurat v5, torch,
          GPUmatrix, CUDA 11.7.

    Contract: ``run()`` must never raise on input that passes
    :class:`SpatialData` validation (file existence, num_modules>=1).
    Bad gene IDs, empty count matrices, or spot/location mismatches
    should be surfaced as ``notes`` on the result rather than as
    exceptions — the toolkit's downstream neoantigen pipeline
    tolerates partial results.
    """

    def run(self, data: SpatialData) -> SpatialModuleResult: ...
