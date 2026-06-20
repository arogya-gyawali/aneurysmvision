"""NIfTI volume loading and metadata extraction.

Maps to ``clabtoolkit.imagetools`` and ``clabtoolkit.qcqatools`` (deferred).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.models import QualityMetrics, ScanModality, StudyMetadata, VoxelDimensions


def load_nifti(path: Path) -> tuple[Any, StudyMetadata]:
    """Load a NIfTI volume and return raw array plus study metadata."""
    raise NotImplementedError("NIfTI loading not implemented (stage 2).")


def infer_modality(path: Path) -> ScanModality:
    """Infer scan modality from filename or BIDS sidecar metadata."""
    raise NotImplementedError("Modality inference not implemented (stage 2).")


def run_quality_checks(volume: Any, study: StudyMetadata) -> QualityMetrics:
    """Compute QC metrics for a loaded volume."""
    raise NotImplementedError("Quality control not implemented (stage 2).")
