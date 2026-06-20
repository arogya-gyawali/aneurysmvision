# AneurysmVision Backend API Contract

> **Version:** 0.1.0  
> **Transport:** In-process Python calls (`pipeline.run_pipeline`)  
> **Reference payload:** [`sample_output.json`](sample_output.json)  
> **Schema source:** [`models.py`](models.py)

---

## Overview

The Streamlit frontend invokes the backend directly:

```python
from backend.models import AnalysisRequest, BidsEntities
from backend.pipeline import run_pipeline

result = run_pipeline(
    AnalysisRequest(
        nifti_path="/data/sub-042_ses-01_acq-3d_tof_run-1_angio.nii.gz",
    )
)
```

The frontend consumes a single typed response: **`AnalysisResult`**.

---

## Request: `AnalysisRequest`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `job_id` | `string` | No | auto-generated | Client-supplied job ID. Format when auto-generated: `av-YYYYMMDD-{8 hex}`. |
| `dataset_root` | `string` | Conditional | — | Absolute path to BIDS dataset root. Mutually exclusive with `nifti_path`. |
| `nifti_path` | `string` | Conditional | — | Absolute path to a single NIfTI file. Mutually exclusive with `dataset_root`. |
| `segmentation_path` | `string` | No | `null` | Pre-computed segmentation mask. Skips detection when implemented. |
| `bids_entities` | `BidsEntities` | Conditional | — | Required when `dataset_root` is set. Must include `sub`. |
| `generate_report` | `boolean` | No | `true` | Whether to run Claude report generation. |
| `generate_mesh` | `boolean` | No | `true` | Whether to export GLB meshes to server-side paths. |
| `cache_results` | `boolean` | No | `true` | Whether to populate `cache_key` for Redis caching. |

**Validation rules**

- Exactly one of `dataset_root` or `nifti_path` must be provided.
- When `dataset_root` is set, `bids_entities` with `sub` is required.

---

## Response: `AnalysisResult`

| Field | Type | Required | Description |
|---|---|---|---|
| `job_id` | `string` | Yes | Unique identifier for this analysis run. |
| `status` | `JobStatus` | Yes | Overall job lifecycle state. |
| `created_at` | `datetime` (ISO 8601) | Yes | UTC timestamp when the job started. |
| `completed_at` | `datetime` (ISO 8601) | No | UTC timestamp when processing finished. |
| `study` | `StudyMetadata` | Yes | Consolidated study metadata. May be partial on failure. |
| `aneurysms` | `AneurysmFinding[]` | Yes | Detected aneurysms. Empty array if none found or pipeline failed early. |
| `aneurysm_count` | `integer` | Yes | Length of `aneurysms`. |
| `report` | `ReportDraft` | No | LLM clinical draft. Null if skipped or not yet implemented. |
| `stages` | `StageTiming[]` | Yes | Per-stage timing and status for progress UI. |
| `cache_key` | `string` | No | Redis cache key. Null when `cache_results=false`. |
| `errors` | `string[]` | Yes | Human-readable errors. Empty on success. |
| `metadata` | `object` | Yes | Provenance and versioning metadata. |

---

## Core Models

### `StudyMetadata`

Consolidates BIDS entities, NIfTI metadata, and QC results.

| Field | Type | Required | Description |
|---|---|---|---|
| `nifti_path` | `string` | Yes | Absolute path to the analyzed NIfTI file. |
| `bids` | `BidsEntities` | No | Parsed BIDS entities when input is BIDS-structured. |
| `shape` | `[int, int, int]` | No | Volume dimensions `[x, y, z]` in voxels. |
| `voxel_dimensions_mm` | `VoxelDimensions` | No | Physical voxel size. |
| `modality` | `ScanModality` | Yes | Imaging modality. Default: `"TOF-MRA"`. |
| `affine` | `float[4][4]` | No | NIfTI affine matrix (voxel → scanner mm). |
| `quality` | `QualityMetrics` | No | QC summary from the quality_control stage. |

### `BiomarkerSet`

Morphometric biomarkers attached to each aneurysm finding.

| Field | Type | Required | Unit | Description |
|---|---|---|---|---|
| `volume_mm3` | `float` | Yes | mm³ | Aneurysm sac volume. |
| `max_diameter_mm` | `float` | Yes | mm | Maximum dome diameter. |
| `neck_width_mm` | `float` | Yes | mm | Neck width at parent vessel junction. |
| `dome_height_mm` | `float` | Yes | mm | Height from neck plane to dome apex. |
| `aspect_ratio` | `float` | Yes | — | `dome_height / neck_width`. Values > 1.6 suggest elevated rupture risk. |
| `size_ratio` | `float` | Yes | — | Aneurysm size relative to parent vessel diameter. |
| `irregularity_index` | `float` | No | — | Surface irregularity score. Values > 1.0 suggest lobulation. |

### `MeshData`

Server-side mesh artifact for frontend 3D rendering.

| Field | Type | Required | Description |
|---|---|---|---|
| `format` | `string` | Yes | Mesh format. Currently `"glb"`. |
| `path` | `string` | Yes | **Server-side absolute path** to the mesh file on the backend host. |
| `vertex_count` | `integer` | Yes | Number of mesh vertices. |
| `face_count` | `integer` | Yes | Number of triangular faces. |

### `ReportDraft`

LLM-generated clinical narrative.

| Field | Type | Required | Description |
|---|---|---|---|
| `summary` | `string` | Yes | One-paragraph executive summary. |
| `findings` | `string[]` | Yes | Bulleted clinical findings. |
| `recommendations` | `string[]` | Yes | Bulleted management recommendations. |
| `model` | `string` | Yes | Claude model identifier. |
| `generated_at` | `datetime` (ISO 8601) | Yes | UTC timestamp of report generation. |

### `StageTiming`

Per-stage progress record.

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | Yes | Stage identifier (see Pipeline Stages below). |
| `status` | `JobStatus` | Yes | Stage lifecycle state. Includes `"skipped"`. |
| `duration_ms` | `integer` | No | Wall-clock duration in milliseconds. |
| `message` | `string` | No | Optional human-readable note. |
| `error` | `string` | No | Error message when `status` is `"failed"`. |

---

## Supporting Types

### `BidsEntities`

| Field | JSON key | Type | Required | Description |
|---|---|---|---|---|
| Subject | `sub` | `string` | Yes | BIDS subject ID without prefix. Example: `"042"`. |
| Session | `ses` | `string` | No | Session label. Example: `"01"`. |
| Acquisition | `acq` | `string` | No | Acquisition group. Example: `"3d_tof"`. |
| Run | `run` | `string` | No | Run index. Example: `"1"`. |
| Suffix | `suffix` | `string` | Yes | BIDS suffix. Primary: `"angio"`. |
| Extension | `extension` | `string` | Yes | File extension. Example: `"nii.gz"`. |

**BIDS suffix resolution** (implemented in `bids_parser.py`):

1. Primary: `angio` (TOF-MRA)
2. Fallbacks (in order): `MRA`, `swi`, `T1w`

### `VoxelDimensions`

| Field | Type | Description |
|---|---|---|
| `x` | `float` | Voxel size along x-axis (mm). |
| `y` | `float` | Voxel size along y-axis (mm). |
| `z` | `float` | Voxel size along z-axis (mm). |

### `QualityMetrics`

| Field | Type | Description |
|---|---|---|
| `snr` | `float` | Signal-to-noise ratio. Typical range: 10–30. |
| `motion_score` | `float` | Normalized motion artifact score in `[0, 1]`. Lower is better. |
| `contrast_to_noise` | `float` | Vessel contrast-to-noise ratio. |
| `passed_qc` | `boolean` | Whether scan meets minimum quality thresholds. |
| `notes` | `string[]` | Human-readable QC observations. |

### `AneurysmFinding`

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Stable ID within the job. Format: `aneurysm-{NNN}`. |
| `label` | `integer` | Segmentation mask label (1-indexed). |
| `location` | `AneurysmLocation` | Anatomical territory enum. |
| `location_detail` | `string` | Free-text anatomical description. |
| `confidence` | `float` | Detection confidence in `[0, 1]`. |
| `centroid_voxel` | `[float, float, float]` | Center of mass in voxel `[i, j, k]`. |
| `centroid_mm` | `[float, float, float]` | Center of mass in scanner mm `[x, y, z]`. |
| `roi_bounds_voxel` | `[int × 6]` | Bounding box `[i_min, i_max, j_min, j_max, k_min, k_max]`. |
| `biomarkers` | `BiomarkerSet` | Morphometric measurements. |
| `mesh` | `MeshData` | Server-side mesh path. Null when `generate_mesh=false`. |

---

## Enums

### `JobStatus`

| Value | Description |
|---|---|
| `queued` | Accepted, not yet started. |
| `running` | Actively processing. |
| `completed` | Finished successfully. |
| `failed` | Unrecoverable error; see `errors` and `stages[].error`. |
| `skipped` | Stage intentionally bypassed. |

### `ScanModality`

| Value | Description |
|---|---|
| `TOF-MRA` | Time-of-flight MR angiography (primary). |
| `MRA` | Generic MR angiography. |
| `CTA` | CT angiography. |

### `AneurysmLocation`

| Value | Description |
|---|---|
| `middle_cerebral_artery` | MCA territory. |
| `anterior_cerebral_artery` | ACA territory. |
| `internal_carotid_artery` | ICA territory. |
| `basilar_artery` | Basilar tip or trunk. |
| `posterior_cerebral_artery` | PCA territory. |
| `anterior_communicating_artery` | AComA. |
| `posterior_communicating_artery` | PComA. |
| `other` | Outside standard taxonomy. |

---

## Pipeline Stages

Executed in order by `pipeline.run_pipeline`:

| Order | `name` | Module | Stage 1 status |
|---|---|---|---|
| 1 | `bids_parse` | `bids_parser` | **Implemented** (path discovery + entity parsing) |
| 2 | `nifti_load` | `nifti_loader` | Stub (`NotImplementedError`) |
| 3 | `quality_control` | `nifti_loader` | Stub |
| 4 | `detection` | `roi_extractor` | Stub |
| 5 | `roi_extraction` | `roi_extractor` | Stub |
| 6 | `biomarkers` | `biomarkers` | Stub |
| 7 | `mesh_generation` | `mesh_generator` | Stub (skipped when `generate_mesh=false`) |
| 8 | `report_generation` | `report_generator` | Stub (skipped when `generate_report=false`) |

On failure the pipeline returns an `AnalysisResult` with `status: "failed"`, populated `stages` up to the failing stage, and `errors` describing the failure. Earlier stage outputs (e.g. `study.nifti_path` after `bids_parse`) are preserved.

---

## `metadata` Fields

| Key | Type | Description |
|---|---|---|
| `pipeline_version` | `string` | Backend semver. Current: `"0.1.0"`. |
| `transport` | `string` | Always `"in_process"` for Stage 1. |
| `processing_time_ms` | `integer` | Total wall-clock time for the pipeline call. |
| `detection_model` | `string` | Detection model ID (present in completed runs). |
| `clabtoolkit_version` | `string` | Installed clabtoolkit version (present in completed runs). |

---

## Error Handling

| Exception | When | Frontend action |
|---|---|---|
| Pydantic `ValidationError` | Invalid `AnalysisRequest` at construction | Fix request fields before calling pipeline. |
| `ValidationError` | BIDS path/entity resolution failure | Display `errors[0]` to user. |
| `StageNotImplementedError` | Stage stub not yet built | Expected in Stage 1 after `bids_parse`; show partial progress via `stages`. |
| Unexpected exception | Internal bug | Log via Sentry; show generic error message. |

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| 0.1.0 | 2025-06-20 | Stage 1: typed models, pipeline orchestrator, BIDS parser, contract docs. |
