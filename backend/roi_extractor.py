"""Region-of-interest extraction for cerebral aneurysm candidates.

This module is a thin **adapter** over ``clabtoolkit.parcellationtools``. The
``Parcellation`` class is used as the primary engine to ingest the segmentation
label volume, enumerate regions, and compute per-ROI centroids/volumes. A pure
``numpy`` path is used as a fallback when clabtoolkit is unavailable.

Two pipeline stages are served here:

  - ``detection``      → :func:`run_detection` produces a labeled segmentation
                          (loads a provided mask, or derives a placeholder
                          candidate mask from the volume intensities).
  - ``roi_extraction`` → :func:`extract_rois` converts that segmentation into a
                          list of :class:`AneurysmFinding` ROI descriptors
                          (centroid, bounding box, voxel count) for downstream
                          mesh generation.

Scope: Stage 3 only. This module deliberately does **not** compute clinical
biomarkers (left as neutral placeholders, filled by Stage 4 ``biomarkers.py``),
nor does it perform mesh generation or reporting. The intensity threshold used
when no mask is supplied is a placeholder, **not** the production detection
model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from backend.models import AneurysmFinding, AneurysmLocation, BiomarkerSet

logger = logging.getLogger(__name__)

# Percentile threshold for the placeholder candidate mask (bright structures
# dominate in TOF-MRA). Replaced by the real detection model in a later stage.
CANDIDATE_PERCENTILE = 99.5


@dataclass
class _Segmentation:
    """Internal container passed from ``run_detection`` to ``extract_rois``.

    Holds the integer label volume plus the affine (when known) and, when
    available, the backing ``clabtoolkit`` ``Parcellation`` engine.
    """

    data: np.ndarray
    affine: np.ndarray = field(default_factory=lambda: np.eye(4))
    parcellation: Any = None
    source: str = "derived"


# ---------------------------------------------------------------------------
# Stage: detection
# ---------------------------------------------------------------------------
def run_detection(volume: Any, segmentation_path: str | None = None) -> _Segmentation:
    """Produce a labeled segmentation for the study.

    If ``segmentation_path`` is provided, the precomputed mask is loaded
    (preserving its affine). Otherwise a placeholder candidate mask is derived
    from the volume intensities and connected components are labeled. The label
    volume is wrapped in a ``clabtoolkit`` ``Parcellation`` engine when
    available.
    """
    if segmentation_path:
        labels, affine, source = _load_segmentation(segmentation_path)
    else:
        data = np.asanyarray(volume)
        labels = _label_components(_candidate_mask(data))
        affine = np.eye(4)
        source = "derived"

    parcellation = _build_parcellation(labels, affine)
    n_regions = int(labels.max())
    logger.info(
        "Detection produced %d candidate region(s) (source=%s, engine=%s)",
        n_regions,
        source,
        "clabtoolkit" if parcellation is not None else "numpy",
    )
    return _Segmentation(data=labels, affine=affine, parcellation=parcellation, source=source)


# ---------------------------------------------------------------------------
# Stage: roi_extraction
# ---------------------------------------------------------------------------
def extract_rois(
    volume: Any,
    segmentation: Any,
    min_voxels: int = 10,
) -> list[AneurysmFinding]:
    """Convert a labeled segmentation into ROI findings for downstream stages.

    Each connected region with at least ``min_voxels`` voxels becomes an
    :class:`AneurysmFinding` carrying its label, centroid (voxel and world mm),
    bounding box, and a confidence proxy. Clinical biomarkers are left as
    neutral placeholders for Stage 4.
    """
    seg = _coerce_segmentation(segmentation)
    volume_arr = np.asanyarray(volume) if volume is not None else None

    regions = _region_table(seg)
    findings: list[AneurysmFinding] = []

    for entry in regions:
        if entry["nvoxels"] < min_voxels:
            continue
        label = entry["label"]
        mask = seg.data == label
        bounds = _bounding_box(mask)
        if bounds is None:
            continue

        findings.append(
            AneurysmFinding(
                id="",  # assigned after sorting
                label=label,
                location=AneurysmLocation.OTHER,
                location_detail="unclassified (anatomical mapping pending)",
                confidence=_confidence(volume_arr, mask),
                centroid_voxel=entry["centroid_voxel"],
                centroid_mm=entry["centroid_mm"],
                roi_bounds_voxel=bounds,
                biomarkers=_placeholder_biomarkers(),
                mesh=None,
            )
        )

    # Largest ROIs first; assign stable, human-readable ids.
    findings.sort(key=lambda f: _roi_size(f.roi_bounds_voxel), reverse=True)
    for idx, finding in enumerate(findings, start=1):
        finding.id = f"aneurysm-{idx:03d}"

    logger.info(
        "ROI extraction kept %d region(s) with >= %d voxels.",
        len(findings),
        min_voxels,
    )
    return findings


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------
def _candidate_mask(volume: np.ndarray, percentile: float = CANDIDATE_PERCENTILE) -> np.ndarray:
    """Threshold bright structures as a placeholder candidate mask."""
    data = np.asarray(volume, dtype=np.float64)
    if data.ndim > 3:
        data = data[..., 0]
    nonzero = data[data != 0]
    if nonzero.size == 0:
        return np.zeros(data.shape, dtype=bool)
    threshold = float(np.percentile(nonzero, percentile))
    # No morphological opening here: it can erode small aneurysms. Isolated
    # noise voxels are removed downstream by the ``min_voxels`` filter.
    return data > threshold


def _label_components(mask: np.ndarray) -> np.ndarray:
    """Label connected components in a binary mask (26-connectivity)."""
    if not np.any(mask):
        return np.zeros(mask.shape, dtype=np.int32)
    try:
        from scipy.ndimage import label

        structure = np.ones((3, 3, 3), dtype=int) if mask.ndim == 3 else None
        labels, _ = label(mask, structure=structure)
        return labels.astype(np.int32)
    except Exception as exc:  # pragma: no cover
        logger.warning("scipy labeling unavailable (%s); treating mask as single ROI.", exc)
        return mask.astype(np.int32)


def _load_segmentation(segmentation_path: str) -> tuple[np.ndarray, np.ndarray, str]:
    """Load a precomputed segmentation NIfTI as an integer label volume."""
    path = Path(segmentation_path)
    if not path.is_file():
        raise FileNotFoundError(f"Segmentation file not found: {path}")
    import nibabel as nib

    nii = nib.load(str(path))
    labels = np.asanyarray(nii.dataobj)
    labels = np.rint(labels).astype(np.int32)
    return labels, np.asarray(nii.affine, dtype=float), "provided"


def _build_parcellation(labels: np.ndarray, affine: np.ndarray) -> Any:
    """Wrap the label volume in a clabtoolkit Parcellation engine if possible."""
    if not np.any(labels):
        return None
    try:
        from clabtoolkit.parcellationtools import Parcellation

        return Parcellation(parc_file=labels.astype(np.int32), affine=affine)
    except Exception as exc:  # pragma: no cover - exercised only without clabtoolkit
        logger.warning("clabtoolkit.Parcellation unavailable (%s); using numpy fallback.", exc)
        return None


# ---------------------------------------------------------------------------
# ROI extraction helpers
# ---------------------------------------------------------------------------
def _coerce_segmentation(segmentation: Any) -> _Segmentation:
    """Accept either a ``_Segmentation`` or a raw label array."""
    if isinstance(segmentation, _Segmentation):
        return segmentation
    data = np.rint(np.asanyarray(segmentation)).astype(np.int32)
    return _Segmentation(data=data, affine=np.eye(4), parcellation=_build_parcellation(data, np.eye(4)))


def _region_table(seg: _Segmentation) -> list[dict]:
    """Per-region centroid/volume table via Parcellation, with numpy fallback."""
    if seg.parcellation is not None:
        try:
            df = seg.parcellation.compute_centroids(gaussian_smooth=False, closing_iterations=0)
            return [
                {
                    "label": int(row["index"]),
                    "nvoxels": int(row["nvoxels"]),
                    "centroid_voxel": (
                        float(row["x_vox"]),
                        float(row["y_vox"]),
                        float(row["z_vox"]),
                    ),
                    "centroid_mm": (
                        float(row["x_mm"]),
                        float(row["y_mm"]),
                        float(row["z_mm"]),
                    ),
                }
                for _, row in df.iterrows()
            ]
        except Exception as exc:
            logger.warning("Parcellation.compute_centroids failed (%s); using numpy.", exc)

    return _region_table_numpy(seg)


def _region_table_numpy(seg: _Segmentation) -> list[dict]:
    """Compute per-region centroids and counts directly from the label array."""
    data = seg.data
    affine = seg.affine
    table: list[dict] = []
    for label in (int(v) for v in np.unique(data) if v != 0):
        coords = np.argwhere(data == label)
        if coords.size == 0:
            continue
        centroid_vox = coords.mean(axis=0)
        centroid_mm = affine[:3, :3] @ centroid_vox + affine[:3, 3]
        table.append(
            {
                "label": label,
                "nvoxels": int(coords.shape[0]),
                "centroid_voxel": tuple(float(c) for c in centroid_vox[:3]),
                "centroid_mm": tuple(float(c) for c in centroid_mm[:3]),
            }
        )
    return table


def _bounding_box(mask: np.ndarray) -> Optional[tuple[int, int, int, int, int, int]]:
    """Axis-aligned voxel bounding box ``(i0, i1, j0, j1, k0, k1)``."""
    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    return (
        int(mins[0]),
        int(maxs[0]),
        int(mins[1]),
        int(maxs[1]),
        int(mins[2]),
        int(maxs[2]),
    )


def _confidence(volume: Optional[np.ndarray], mask: np.ndarray) -> float:
    """Intensity-based confidence proxy in [0, 1] (placeholder for the model)."""
    if volume is None or volume.shape != mask.shape:
        return 0.5
    roi_vals = volume[mask]
    if roi_vals.size == 0:
        return 0.5
    denom = float(np.percentile(volume[volume != 0], 99)) if np.any(volume != 0) else 0.0
    if denom <= 0:
        return 0.5
    return round(float(min(max(np.mean(roi_vals) / denom, 0.0), 1.0)), 2)


def _roi_size(bounds: tuple[int, int, int, int, int, int]) -> int:
    i0, i1, j0, j1, k0, k1 = bounds
    return (i1 - i0 + 1) * (j1 - j0 + 1) * (k1 - k0 + 1)


def _placeholder_biomarkers() -> BiomarkerSet:
    """Neutral biomarker placeholder; real values are computed in Stage 4."""
    return BiomarkerSet(
        volume_mm3=0.0,
        max_diameter_mm=0.0,
        neck_width_mm=0.0,
        dome_height_mm=0.0,
        aspect_ratio=0.0,
        size_ratio=0.0,
        irregularity_index=None,
    )
