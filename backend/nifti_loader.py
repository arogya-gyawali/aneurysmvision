"""NIfTI volume loading, metadata extraction, and quality control.

This module is a thin **adapter** over established neuroimaging tooling. It is
*not* a reimplementation of clabtoolkit:

  - I/O follows clabtoolkit's own convention: load with ``nibabel``.
  - ``clabtoolkit.imagetools.get_voxel_size`` provides voxel spacing from the
    affine (with a header-based fallback if clabtoolkit is unavailable).
  - ``clabtoolkit.qcqatools.get_valid_slices`` provides a structural QC check
    (does the volume actually contain signal?).

Aneurysm-specific QC metrics (SNR, contrast-to-noise, motion proxy) are *not*
provided by clabtoolkit and are intentionally computed here in the
AneurysmVision application layer.

Scope: Stage 2 only. No ROI extraction, mesh generation, biomarkers, or
reporting is performed here.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import nibabel as nib
import numpy as np

from backend import bids_parser
from backend.exceptions import ValidationError
from backend.models import QualityMetrics, ScanModality, StudyMetadata, VoxelDimensions

logger = logging.getLogger(__name__)

# QC thresholds (AneurysmVision domain rules, not clabtoolkit).
SNR_MIN_PASS = 5.0
MOTION_MAX_PASS = 0.6

# Suffix → modality hints used when no JSON sidecar is available.
_SUFFIX_MODALITY = {
    "angio": ScanModality.TOF_MRA,
    "mra": ScanModality.MRA,
    "tof": ScanModality.TOF_MRA,
    "ct": ScanModality.CTA,
    "cta": ScanModality.CTA,
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_nifti(path: Path) -> tuple[np.ndarray, StudyMetadata]:
    """Load a NIfTI volume and return ``(volume_array, StudyMetadata)``.

    The returned ``StudyMetadata`` is enriched with ``shape``, ``affine``,
    ``voxel_dimensions_mm`` and ``modality``. The ``bids`` field is re-parsed
    from the filename when the path follows BIDS naming, preserving the entity
    information established during the ``bids_parse`` stage.

    The QC summary (``quality``) is intentionally left ``None`` here; it is
    populated by :func:`run_quality_checks` in the ``quality_control`` stage.
    """
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"NIfTI file not found: {path}")

    try:
        nii = nib.load(str(path))
    except Exception as exc:  # nibabel raises a variety of error types
        raise ValidationError(f"Failed to load NIfTI '{path}': {exc}") from exc

    try:
        data = np.asanyarray(nii.dataobj)
    except Exception as exc:
        raise ValidationError(f"Failed to read NIfTI array data '{path}': {exc}") from exc

    affine = np.asarray(nii.affine, dtype=float)
    shape = _spatial_shape(data.shape)
    voxel_dims = _voxel_dimensions(affine, nii.header)
    bids = _safe_parse_bids(path)
    modality = infer_modality(path)

    study = StudyMetadata(
        nifti_path=str(path),
        bids=bids,
        shape=shape,
        voxel_dimensions_mm=voxel_dims,
        modality=modality,
        affine=affine.tolist(),
    )

    logger.info(
        "Loaded NIfTI %s shape=%s voxel=(%.3f, %.3f, %.3f)mm modality=%s",
        path.name,
        shape,
        voxel_dims.x,
        voxel_dims.y,
        voxel_dims.z,
        modality.value,
    )
    return data, study


def infer_modality(path: Path) -> ScanModality:
    """Infer scan modality from a BIDS JSON sidecar, then filename suffix.

    Resolution order:
      1. JSON sidecar fields (``MRAcquisitionType``, ``ScanningSequence``,
         ``SeriesDescription``, ``Modality``).
      2. BIDS suffix from the filename (e.g. ``angio`` → TOF-MRA).
      3. Default: TOF-MRA (the platform's primary modality).
    """
    sidecar = _read_sidecar(path)
    if sidecar:
        haystack = " ".join(
            str(sidecar.get(key, ""))
            for key in ("ScanningSequence", "SequenceName", "SeriesDescription", "MRAcquisitionType")
        ).lower()
        if "tof" in haystack:
            return ScanModality.TOF_MRA
        modality_field = str(sidecar.get("Modality", "")).lower()
        if "ct" in modality_field or "ct" in haystack:
            return ScanModality.CTA
        if "angio" in haystack or "mra" in haystack:
            return ScanModality.MRA

    suffix = _safe_suffix(path)
    if suffix:
        hint = _SUFFIX_MODALITY.get(suffix.lower())
        if hint is not None:
            return hint

    return ScanModality.TOF_MRA


# ---------------------------------------------------------------------------
# Quality control
# ---------------------------------------------------------------------------
def run_quality_checks(volume: Any, study: StudyMetadata) -> QualityMetrics:
    """Compute QC metrics for a loaded volume.

    Structural QC (signal presence) uses ``clabtoolkit.qcqatools.get_valid_slices``.
    Signal-quality metrics (SNR / contrast-to-noise / motion proxy) are computed
    in the AneurysmVision layer because clabtoolkit does not provide them.
    """
    data = np.asanyarray(volume).astype(np.float64, copy=False)
    notes: list[str] = []

    has_signal = _has_valid_slices(data, notes)

    if not np.any(np.isfinite(data)) or not np.any(data != 0):
        notes.append("Volume contains no non-zero signal; QC failed.")
        return QualityMetrics(passed_qc=False, notes=notes)

    snr, cnr, motion = _signal_metrics(data, notes)

    passed = has_signal
    if snr is not None and snr < SNR_MIN_PASS:
        passed = False
        notes.append(f"SNR {snr:.1f} below minimum {SNR_MIN_PASS:.1f}.")
    if motion is not None and motion > MOTION_MAX_PASS:
        passed = False
        notes.append(f"Motion proxy {motion:.2f} above threshold {MOTION_MAX_PASS:.2f}.")
    if passed and not notes:
        notes.append("All QC checks passed.")

    return QualityMetrics(
        snr=snr,
        motion_score=motion,
        contrast_to_noise=cnr,
        passed_qc=passed,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _spatial_shape(shape: tuple[int, ...]) -> tuple[int, int, int]:
    """Coerce an N-D shape to a 3-tuple of spatial dimensions."""
    dims = [int(d) for d in shape[:3]]
    while len(dims) < 3:
        dims.append(1)
    return (dims[0], dims[1], dims[2])


def _voxel_dimensions(affine: np.ndarray, header: Any) -> VoxelDimensions:
    """Voxel spacing via clabtoolkit, falling back to the NIfTI header zooms."""
    try:
        import clabtoolkit.imagetools as imagetools

        vx, vy, vz = imagetools.get_voxel_size(affine)
        return VoxelDimensions(x=float(vx), y=float(vy), z=float(vz))
    except Exception as exc:  # pragma: no cover - exercised only without clabtoolkit
        logger.warning("clabtoolkit.get_voxel_size unavailable (%s); using header zooms.", exc)
        try:
            zooms = header.get_zooms()
            vx, vy, vz = (float(z) for z in list(zooms[:3]) + [1.0, 1.0, 1.0][: max(0, 3 - len(zooms))])
            return VoxelDimensions(x=vx, y=vy, z=vz)
        except Exception:
            norm = np.linalg.norm(affine[:3, :3], axis=0)
            return VoxelDimensions(x=float(norm[0]), y=float(norm[1]), z=float(norm[2]))


def _has_valid_slices(data: np.ndarray, notes: list[str]) -> bool:
    """Use clabtoolkit's slice validity check to confirm the volume has signal."""
    spatial = data
    if spatial.ndim > 3:
        spatial = spatial[..., 0]
    try:
        import clabtoolkit.qcqatools as qcqatools

        sag, cor, ax = qcqatools.get_valid_slices(spatial, ignore_value=0)
        if sag and cor and ax:
            return True
        notes.append("clabtoolkit.get_valid_slices found no signal-bearing slices.")
        return False
    except Exception as exc:  # pragma: no cover - exercised only without clabtoolkit
        logger.warning("clabtoolkit.get_valid_slices unavailable (%s); using fallback.", exc)
        if np.any(spatial != 0):
            return True
        notes.append("Fallback QC: volume is empty.")
        return False


def _signal_metrics(
    data: np.ndarray,
    notes: list[str],
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Compute (SNR, contrast-to-noise, motion proxy) heuristics.

    Background noise is estimated from the volume corners (a standard simple
    QC heuristic); signal is estimated from voxels well above the noise floor.
    These are preliminary indicators, not calibrated clinical measures.
    """
    spatial = data
    if spatial.ndim > 3:
        spatial = spatial[..., 0]

    bg = _corner_background(spatial)
    mean_bg = float(np.mean(bg)) if bg.size else 0.0
    std_bg = float(np.std(bg)) if bg.size else 0.0

    nonzero = spatial[spatial != 0]
    if nonzero.size == 0:
        return None, None, None

    if std_bg <= 1e-6:
        notes.append("Background noise ~0 (masked volume); SNR/CNR not computed.")
        snr = None
        cnr = None
    else:
        threshold = mean_bg + 2.0 * std_bg
        signal = spatial[spatial > threshold]
        if signal.size == 0:
            signal = nonzero
        mean_signal = float(np.mean(signal))
        snr = round(mean_signal / std_bg, 2)
        cnr = round((mean_signal - mean_bg) / std_bg, 2)

    motion = _motion_proxy(spatial)
    return snr, cnr, motion


def _corner_background(spatial: np.ndarray) -> np.ndarray:
    """Sample small cubes from the 8 corners as a background-noise estimate."""
    if spatial.ndim != 3:
        return spatial[spatial == spatial]  # degenerate fallback: all voxels
    sizes = [max(1, min(8, dim // 8)) for dim in spatial.shape]
    sx, sy, sz = sizes
    patches = []
    for ix in (slice(0, sx), slice(-sx, None)):
        for iy in (slice(0, sy), slice(-sy, None)):
            for iz in (slice(0, sz), slice(-sz, None)):
                patches.append(spatial[ix, iy, iz].ravel())
    return np.concatenate(patches) if patches else np.empty(0)


def _motion_proxy(spatial: np.ndarray) -> Optional[float]:
    """Rough motion/inhomogeneity proxy from axial slice-mean variation.

    Returns the coefficient of variation of per-slice mean intensity, clamped
    to [0, 1]. Higher values suggest greater inter-slice inconsistency.
    """
    if spatial.ndim != 3 or spatial.shape[2] < 2:
        return None
    slice_means = np.array([
        spatial[:, :, z][spatial[:, :, z] != 0].mean() if np.any(spatial[:, :, z] != 0) else 0.0
        for z in range(spatial.shape[2])
    ])
    overall = float(np.mean(slice_means))
    if overall <= 1e-6:
        return None
    cov = float(np.std(slice_means) / overall)
    return round(min(max(cov, 0.0), 1.0), 3)


def _safe_parse_bids(path: Path):
    """Re-parse BIDS entities from the filename, returning None if not BIDS."""
    name = path.name
    if not bids_parser._looks_like_bids(name):  # noqa: SLF001 - intentional reuse
        return None
    try:
        return bids_parser.parse_bids_filename(name)
    except ValidationError:
        return None


def _safe_suffix(path: Path) -> Optional[str]:
    entities = _safe_parse_bids(path)
    return entities.suffix if entities is not None else None


def _read_sidecar(path: Path) -> dict:
    """Load the BIDS JSON sidecar next to a NIfTI file, if present."""
    name = path.name
    for ext in (".nii.gz", ".nii"):
        if name.endswith(ext):
            sidecar = path.with_name(name[: -len(ext)] + ".json")
            break
    else:
        sidecar = path.with_suffix(".json")

    if not sidecar.is_file():
        return {}
    try:
        with sidecar.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning("Failed to read JSON sidecar %s: %s", sidecar, exc)
        return {}
