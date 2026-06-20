"""Morphometric biomarker computation for cerebral aneurysms.

Maps to ``clabtoolkit.imagetools`` and ``clabtoolkit.parcellationtools`` (deferred).
"""

from __future__ import annotations

from typing import Any

from backend.models import AneurysmFinding, BiomarkerSet, VoxelDimensions


def compute_biomarkers(
    roi_mask: Any,
    voxel_dimensions_mm: VoxelDimensions,
) -> BiomarkerSet:
    """Compute standard aneurysm morphometric biomarkers from a binary ROI."""
    raise NotImplementedError("Biomarker computation not implemented (stage 3).")


def enrich_findings_with_biomarkers(
    findings: list[AneurysmFinding],
    voxel_dimensions_mm: VoxelDimensions,
) -> list[AneurysmFinding]:
    """Attach computed biomarkers to each finding."""
    raise NotImplementedError("Biomarker enrichment not implemented (stage 3).")
