"""Morphometric biomarker computation for cerebral aneurysms.

This module is a thin **application-layer adapter**. It converts Stage 3 ROI
findings (bounding boxes, centroids, optional binary masks) into
:class:`BiomarkerSet` values defined by the frontend contract.

Optional read-only helpers from ``clabtoolkit.imagetools`` (e.g.
``get_voxel_volume``) may be used for unit conversions; clinical biomarker
logic lives here in AneurysmVision, not in clabtoolkit.

Scope: Stage 4 only. No mesh generation, reporting, or detection logic.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Optional

import numpy as np

from backend.exceptions import ValidationError
from backend.models import AneurysmFinding, BiomarkerSet, VoxelDimensions

logger = logging.getLogger(__name__)

# Typical parent-vessel diameter (mm) when vessel calibre is unknown.
_DEFAULT_PARENT_VESSEL_MM = 3.0
_MIN_LINEAR_MM = 1e-3


def compute_biomarkers(
    roi_mask: Any,
    voxel_dimensions_mm: VoxelDimensions,
) -> BiomarkerSet:
    """Compute morphometric biomarkers from a binary ROI mask."""
    mask = np.asarray(roi_mask).astype(bool)
    if mask.ndim > 3:
        mask = mask[..., 0]

    if not np.any(mask):
        raise ValidationError("Cannot compute biomarkers from an empty ROI mask.")

    voxel_dims = _resolve_voxel_dimensions(voxel_dimensions_mm)
    coords = np.argwhere(mask)
    voxel_volume = _voxel_volume_mm3(voxel_dims)
    volume_mm3 = float(coords.shape[0]) * voxel_volume

    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    extents_mm = _voxel_extents_to_mm(mins, maxs, voxel_dims)

    return _biomarkers_from_geometry(
        volume_mm3=volume_mm3,
        extents_mm=extents_mm,
        parent_vessel_mm=_DEFAULT_PARENT_VESSEL_MM,
    )


def enrich_findings_with_biomarkers(
    findings: list[AneurysmFinding],
    voxel_dimensions_mm: VoxelDimensions,
) -> list[AneurysmFinding]:
    """Attach computed biomarkers to each finding from its ROI bounding box."""
    if not findings:
        return []

    voxel_dims = _resolve_voxel_dimensions(voxel_dimensions_mm)
    enriched: list[AneurysmFinding] = []

    for finding in findings:
        biomarkers = _biomarkers_from_bounds(finding.roi_bounds_voxel, voxel_dims)
        enriched.append(finding.model_copy(update={"biomarkers": biomarkers}))
        logger.debug(
            "Computed biomarkers for %s: volume=%.2f mm³ max_diameter=%.2f mm",
            finding.id,
            biomarkers.volume_mm3,
            biomarkers.max_diameter_mm,
        )

    logger.info("Enriched %d finding(s) with biomarker sets.", len(enriched))
    return enriched


# ---------------------------------------------------------------------------
# Internal geometry helpers
# ---------------------------------------------------------------------------
def _resolve_voxel_dimensions(voxel_dimensions_mm: Optional[VoxelDimensions]) -> VoxelDimensions:
    if voxel_dimensions_mm is not None:
        return voxel_dimensions_mm
    logger.warning("Voxel dimensions missing; using 1.0 mm isotropic fallback.")
    return VoxelDimensions(x=1.0, y=1.0, z=1.0)


def _voxel_volume_mm3(voxel_dims: VoxelDimensions) -> float:
    """Single-voxel volume (mm³) via clabtoolkit helper when available."""
    try:
        import clabtoolkit.imagetools as imagetools

        affine = np.diag([voxel_dims.x, voxel_dims.y, voxel_dims.z, 1.0])
        return float(imagetools.get_voxel_volume(affine))
    except Exception:  # pragma: no cover - fallback when clabtoolkit unavailable
        return float(voxel_dims.x * voxel_dims.y * voxel_dims.z)


def _bounds_to_voxel_counts(
    bounds: tuple[int, int, int, int, int, int],
) -> tuple[int, int, int]:
    i0, i1, j0, j1, k0, k1 = bounds
    return (i1 - i0 + 1, j1 - j0 + 1, k1 - k0 + 1)


def _voxel_extents_to_mm(
    mins: np.ndarray,
    maxs: np.ndarray,
    voxel_dims: VoxelDimensions,
) -> tuple[float, float, float]:
    counts = (maxs - mins + 1).astype(float)
    return (
        float(counts[0] * voxel_dims.x),
        float(counts[1] * voxel_dims.y),
        float(counts[2] * voxel_dims.z),
    )


def _extents_mm_from_bounds(
    bounds: tuple[int, int, int, int, int, int],
    voxel_dims: VoxelDimensions,
) -> tuple[float, float, float]:
    nx, ny, nz = _bounds_to_voxel_counts(bounds)
    return (
        float(nx * voxel_dims.x),
        float(ny * voxel_dims.y),
        float(nz * voxel_dims.z),
    )


def _ellipsoid_volume_mm3(extents_mm: tuple[float, float, float]) -> float:
    """Approximate ROI volume as an ellipsoid from axis-aligned extents."""
    a, b, c = (max(e, _MIN_LINEAR_MM) for e in extents_mm)
    return (4.0 / 3.0) * math.pi * (a / 2.0) * (b / 2.0) * (c / 2.0)


def _biomarkers_from_bounds(
    bounds: tuple[int, int, int, int, int, int],
    voxel_dims: VoxelDimensions,
) -> BiomarkerSet:
    extents_mm = _extents_mm_from_bounds(bounds, voxel_dims)
    volume_mm3 = _ellipsoid_volume_mm3(extents_mm)
    return _biomarkers_from_geometry(
        volume_mm3=volume_mm3,
        extents_mm=extents_mm,
        parent_vessel_mm=_DEFAULT_PARENT_VESSEL_MM,
    )


def _biomarkers_from_geometry(
    volume_mm3: float,
    extents_mm: tuple[float, float, float],
    parent_vessel_mm: float,
) -> BiomarkerSet:
    """Derive contract biomarkers from volume and sorted axis extents (mm)."""
    sorted_extents = sorted((max(e, _MIN_LINEAR_MM) for e in extents_mm), reverse=True)
    max_diameter_mm = sorted_extents[0]
    dome_height_mm = sorted_extents[1]
    neck_width_mm = max(sorted_extents[2], _MIN_LINEAR_MM)

    aspect_ratio = _safe_ratio(dome_height_mm, neck_width_mm)
    size_ratio = _safe_ratio(max_diameter_mm, max(parent_vessel_mm, _MIN_LINEAR_MM))

    sphere_volume = (4.0 / 3.0) * math.pi * (max_diameter_mm / 2.0) ** 3
    irregularity_index: Optional[float] = None
    if sphere_volume > _MIN_LINEAR_MM:
        irregularity_index = _round(max(volume_mm3 / sphere_volume, 0.0))

    return BiomarkerSet(
        volume_mm3=_round(max(volume_mm3, 0.0)),
        max_diameter_mm=_round(max_diameter_mm),
        neck_width_mm=_round(neck_width_mm),
        dome_height_mm=_round(dome_height_mm),
        aspect_ratio=_round(aspect_ratio),
        size_ratio=_round(size_ratio),
        irregularity_index=irregularity_index,
    )


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= _MIN_LINEAR_MM:
        return 0.0
    return numerator / denominator


def _round(value: float, places: int = 2) -> float:
    return round(float(value), places)
