"""Thin response-normalization layer for the AneurysmVision frontend.

Purpose
-------
Convert the *real* ``AnalysisResult`` produced by the integrated backend into
the exact frontend-friendly shape that ``backend/sample_output.json`` uses, so
every Streamlit component can bind to one stable contract regardless of whether
the data came from the live pipeline or the bundled sample.

Design constraints
------------------
* The backend pipeline is **not** modified. This is a pure, read-only adapter.
* Detection / biomarker logic is **not** reimplemented; real values are passed
  through untouched.
* Missing or mismatched fields are mapped to **deterministic defaults**.
* The function is **idempotent**: applying it to already-normalized data (or to
  the sample file, which is already alias-shaped) is a no-op beyond defaults.

Normalized schema (frontend contract)
-------------------------------------
``normalize_result`` always returns a dict with this shape::

    {
      "job_id": str,
      "status": str,                       # queued|running|completed|failed|skipped
      "created_at": str | None,            # ISO 8601
      "completed_at": str | None,
      "study": {
        "nifti_path": str,
        "bids": {                          # BIDS *alias* keys (sub/ses/acq)
          "sub": str | None, "ses": str | None, "acq": str | None,
          "run": str | None, "suffix": str | None, "extension": str | None
        } | None,
        "shape": [int, int, int] | None,
        "voxel_dimensions_mm": {"x": float, "y": float, "z": float} | None,
        "modality": str,                   # default "TOF-MRA"
        "affine": list[list[float]] | None,
        "quality": {
          "snr": float | None, "motion_score": float | None,
          "contrast_to_noise": float | None, "passed_qc": bool, "notes": [str]
        } | None
      },
      "aneurysms": [ {
        "id": str, "label": int,
        "location": str,                   # AneurysmLocation value (may be "other")
        "location_detail": str,
        "confidence": float,               # clamped to [0, 1]
        "centroid_voxel": [float, float, float],
        "centroid_mm": [float, float, float],
        "roi_bounds_voxel": [int, int, int, int, int, int],
        "biomarkers": {
          "volume_mm3": float, "max_diameter_mm": float, "neck_width_mm": float,
          "dome_height_mm": float, "aspect_ratio": float, "size_ratio": float,
          "irregularity_index": float | None
        },
        "mesh": {"format": str, "path": str,
                 "vertex_count": int, "face_count": int} | None
      } ],
      "aneurysm_count": int,
      "report": {
        "summary": str, "findings": [str], "recommendations": [str],
        "model": str, "generated_at": str | None
      } | None,
      "stages": [ {"name": str, "status": str,
                   "duration_ms": int | None, "message": str | None,
                   "error": str | None} ],
      "cache_key": str | None,
      "errors": [str],
      "metadata": {
        "pipeline_version": str, "transport": str,
        "detection_model": str, "clabtoolkit_version": str,
        "processing_time_ms": int
      }
    }
"""

from __future__ import annotations

from typing import Any

# Honest identifier for the current intensity-threshold placeholder detector.
# (The sample file's "connectomicslab-sliding-window-v1" is aspirational.)
DEFAULT_DETECTION_MODEL = "placeholder-intensity-threshold-v0"
DEFAULT_PIPELINE_VERSION = "0.1.0"
DEFAULT_MODALITY = "TOF-MRA"
DEFAULT_LOCATION = "other"
DEFAULT_LOCATION_DETAIL = "unclassified (anatomical mapping pending)"

_VOXEL_DECIMALS = 4

_BIOMARKER_KEYS = (
    "volume_mm3",
    "max_diameter_mm",
    "neck_width_mm",
    "dome_height_mm",
    "aspect_ratio",
    "size_ratio",
)


def _clabtoolkit_version() -> str:
    try:
        from importlib.metadata import version

        return version("clabtoolkit")
    except Exception:
        return "unknown"


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: Any, ndigits: int) -> Any:
    return round(value, ndigits) if isinstance(value, (int, float)) else value


def _normalize_bids(bids: Any) -> dict[str, Any] | None:
    """Emit BIDS entities using alias keys (sub/ses/acq), accepting either form."""
    if not isinstance(bids, dict):
        return bids
    out = dict(bids)
    for alias, field in (("sub", "subject"), ("ses", "session"), ("acq", "acquisition")):
        if out.get(alias) is None and field in out:
            out[alias] = out.get(field)
    return {
        "sub": out.get("sub"),
        "ses": out.get("ses"),
        "acq": out.get("acq"),
        "run": out.get("run"),
        "suffix": out.get("suffix"),
        "extension": out.get("extension"),
    }


def _normalize_voxels(voxels: Any) -> dict[str, Any] | None:
    if not isinstance(voxels, dict):
        return voxels
    return {axis: _round(voxels.get(axis), _VOXEL_DECIMALS) for axis in ("x", "y", "z")}


def _normalize_quality(quality: Any) -> dict[str, Any] | None:
    if not isinstance(quality, dict):
        return quality
    return {
        "snr": quality.get("snr"),
        "motion_score": quality.get("motion_score"),
        "contrast_to_noise": quality.get("contrast_to_noise"),
        "passed_qc": bool(quality.get("passed_qc", False)),
        "notes": list(quality.get("notes") or []),
    }


def _normalize_study(study: Any) -> dict[str, Any]:
    study = dict(study or {})
    return {
        "nifti_path": study.get("nifti_path", ""),
        "bids": _normalize_bids(study.get("bids")),
        "shape": study.get("shape"),
        "voxel_dimensions_mm": _normalize_voxels(study.get("voxel_dimensions_mm")),
        "modality": study.get("modality") or DEFAULT_MODALITY,
        "affine": study.get("affine"),
        "quality": _normalize_quality(study.get("quality")),
    }


def _normalize_biomarkers(bio: Any) -> dict[str, Any]:
    bio = dict(bio or {})
    out: dict[str, Any] = {key: _as_float(bio.get(key, 0.0)) for key in _BIOMARKER_KEYS}
    irr = bio.get("irregularity_index")
    out["irregularity_index"] = _as_float(irr) if irr is not None else None
    return out


def _normalize_mesh(mesh: Any) -> dict[str, Any] | None:
    if not isinstance(mesh, dict):
        return None
    return {
        "format": mesh.get("format", "glb"),
        "path": mesh.get("path", ""),
        "vertex_count": int(mesh.get("vertex_count", 0) or 0),
        "face_count": int(mesh.get("face_count", 0) or 0),
    }


def _normalize_finding(finding: dict[str, Any], index: int) -> dict[str, Any]:
    conf = _as_float(finding.get("confidence", 0.0))
    conf = min(max(conf, 0.0), 1.0)
    return {
        "id": finding.get("id") or f"aneurysm-{index:03d}",
        "label": int(finding.get("label", index) or index),
        "location": finding.get("location") or DEFAULT_LOCATION,
        "location_detail": finding.get("location_detail") or DEFAULT_LOCATION_DETAIL,
        "confidence": conf,
        "centroid_voxel": list(finding.get("centroid_voxel") or [0.0, 0.0, 0.0]),
        "centroid_mm": list(finding.get("centroid_mm") or [0.0, 0.0, 0.0]),
        "roi_bounds_voxel": list(finding.get("roi_bounds_voxel") or [0, 0, 0, 0, 0, 0]),
        "biomarkers": _normalize_biomarkers(finding.get("biomarkers")),
        "mesh": _normalize_mesh(finding.get("mesh")),
    }


def _normalize_report(report: Any) -> dict[str, Any] | None:
    if not isinstance(report, dict):
        return None
    return {
        "summary": report.get("summary", ""),
        "findings": list(report.get("findings") or []),
        "recommendations": list(report.get("recommendations") or []),
        "model": report.get("model", "—"),
        "generated_at": report.get("generated_at"),
    }


def _normalize_stage(stage: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": stage.get("name", "stage"),
        "status": stage.get("status", ""),
        "duration_ms": stage.get("duration_ms"),
        "message": stage.get("message"),
        "error": stage.get("error"),
    }


def _normalize_metadata(metadata: Any) -> dict[str, Any]:
    metadata = dict(metadata or {})
    metadata.setdefault("pipeline_version", DEFAULT_PIPELINE_VERSION)
    metadata.setdefault("transport", "in_process")
    metadata.setdefault("detection_model", DEFAULT_DETECTION_MODEL)
    metadata.setdefault("clabtoolkit_version", _clabtoolkit_version())
    metadata.setdefault("processing_time_ms", 0)
    return metadata


def normalize_result(raw: dict[str, Any]) -> dict[str, Any]:
    """Map a raw ``AnalysisResult`` dict into the frontend-friendly contract.

    Real backend values are preserved; only missing/mismatched fields are
    bridged to deterministic defaults. Any non-contract keys present on the
    input (e.g. the ``_source`` demo flag) are carried through unchanged.
    """
    raw = dict(raw or {})
    aneurysms = raw.get("aneurysms") or []
    normalized_aneurysms = [
        _normalize_finding(dict(f), idx) for idx, f in enumerate(aneurysms, start=1)
    ]

    result: dict[str, Any] = {
        "job_id": raw.get("job_id", ""),
        "status": raw.get("status", "unknown"),
        "created_at": raw.get("created_at"),
        "completed_at": raw.get("completed_at"),
        "study": _normalize_study(raw.get("study")),
        "aneurysms": normalized_aneurysms,
        "aneurysm_count": int(raw.get("aneurysm_count", len(normalized_aneurysms)) or 0),
        "report": _normalize_report(raw.get("report")),
        "stages": [_normalize_stage(dict(s)) for s in (raw.get("stages") or [])],
        "cache_key": raw.get("cache_key"),
        "errors": list(raw.get("errors") or []),
        "metadata": _normalize_metadata(raw.get("metadata")),
    }

    # Carry through any extra (non-contract) keys, e.g. the _source demo flag.
    for key, value in raw.items():
        if key not in result:
            result[key] = value
    return result
