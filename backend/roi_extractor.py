"""Region-of-interest extraction around detected aneurysms.

Maps to ``clabtoolkit.parcellationtools`` (deferred).
"""

from __future__ import annotations

from typing import Any

from backend.models import AneurysmFinding


def run_detection(volume: Any, segmentation_path: str | None = None) -> Any:
    """Run aneurysm detection / load a pre-computed segmentation mask."""
    raise NotImplementedError("Detection model not implemented (stage 3).")


def extract_rois(
    volume: Any,
    segmentation: Any,
    min_voxels: int = 10,
) -> list[AneurysmFinding]:
    """Isolate connected components from a segmentation mask as ROIs."""
    raise NotImplementedError("ROI extraction not implemented (stage 3).")
