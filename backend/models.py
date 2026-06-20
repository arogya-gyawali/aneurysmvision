"""Pydantic schemas for AneurysmVision backend I/O.

These models define the contract between the processing pipeline and the
Streamlit frontend. See ``api_contract.md`` for field-level documentation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class JobStatus(str, Enum):
    """Lifecycle states for an analysis job or stage."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ScanModality(str, Enum):
    """Supported neuroimaging modalities."""

    TOF_MRA = "TOF-MRA"
    MRA = "MRA"
    CTA = "CTA"


class AneurysmLocation(str, Enum):
    """Common cerebral aneurysm locations."""

    MCA = "middle_cerebral_artery"
    ACA = "anterior_cerebral_artery"
    ICA = "internal_carotid_artery"
    BA = "basilar_artery"
    PCA = "posterior_cerebral_artery"
    ACOM = "anterior_communicating_artery"
    PCOM = "posterior_communicating_artery"
    OTHER = "other"


class BidsEntities(BaseModel):
    """BIDS filename entities extracted from input paths."""

    subject: str = Field(..., alias="sub")
    session: Optional[str] = Field(None, alias="ses")
    acquisition: Optional[str] = Field(None, alias="acq")
    run: Optional[str] = Field(None, alias="run")
    suffix: str
    extension: str

    model_config = {"populate_by_name": True}


class AnalysisRequest(BaseModel):
    """Input payload to start an aneurysm analysis (in-process call)."""

    job_id: Optional[str] = None
    dataset_root: Optional[str] = None
    nifti_path: Optional[str] = None
    segmentation_path: Optional[str] = None
    bids_entities: Optional[BidsEntities] = None
    generate_report: bool = True
    generate_mesh: bool = True
    cache_results: bool = True

    @model_validator(mode="after")
    def validate_input_source(self) -> AnalysisRequest:
        if not self.dataset_root and not self.nifti_path:
            raise ValueError("Exactly one of dataset_root or nifti_path must be provided.")
        if self.dataset_root and self.nifti_path:
            raise ValueError("Provide dataset_root or nifti_path, not both.")
        if self.dataset_root and self.bids_entities is None:
            raise ValueError("bids_entities with subject (sub) is required for BIDS mode.")
        return self

    def resolved_job_id(self) -> str:
        if self.job_id:
            return self.job_id
        return f"av-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:8]}"


class VoxelDimensions(BaseModel):
    """Physical voxel size in millimeters."""

    x: float
    y: float
    z: float


class QualityMetrics(BaseModel):
    """Image quality control summary."""

    snr: Optional[float] = None
    motion_score: Optional[float] = None
    contrast_to_noise: Optional[float] = None
    passed_qc: bool = False
    notes: list[str] = Field(default_factory=list)


class StudyMetadata(BaseModel):
    """Consolidated study metadata from BIDS parse, NIfTI load, and QC."""

    nifti_path: str
    bids: Optional[BidsEntities] = None
    shape: Optional[tuple[int, int, int]] = None
    voxel_dimensions_mm: Optional[VoxelDimensions] = None
    modality: ScanModality = ScanModality.TOF_MRA
    affine: Optional[list[list[float]]] = None
    quality: Optional[QualityMetrics] = None


class BiomarkerSet(BaseModel):
    """Morphometric biomarkers for a detected aneurysm."""

    volume_mm3: float
    max_diameter_mm: float
    neck_width_mm: float
    dome_height_mm: float
    aspect_ratio: float
    size_ratio: float
    irregularity_index: Optional[float] = None


class MeshData(BaseModel):
    """3D mesh output referenced by server-side file path."""

    format: str = "glb"
    path: str
    vertex_count: int
    face_count: int


class AneurysmFinding(BaseModel):
    """Single detected aneurysm with spatial and morphometric data."""

    id: str
    label: int
    location: AneurysmLocation
    location_detail: str
    confidence: float
    centroid_voxel: tuple[float, float, float]
    centroid_mm: tuple[float, float, float]
    roi_bounds_voxel: tuple[int, int, int, int, int, int]
    biomarkers: BiomarkerSet
    mesh: Optional[MeshData] = None


class ReportDraft(BaseModel):
    """LLM-generated clinical narrative draft."""

    summary: str
    findings: list[str]
    recommendations: list[str]
    model: str
    generated_at: datetime


class StageTiming(BaseModel):
    """Timing and status for a single pipeline stage."""

    name: str
    status: JobStatus
    duration_ms: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    """Complete analysis output consumed by the frontend."""

    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    study: StudyMetadata
    aneurysms: list[AneurysmFinding] = Field(default_factory=list)
    aneurysm_count: int = 0
    report: Optional[ReportDraft] = None
    stages: list[StageTiming] = Field(default_factory=list)
    cache_key: Optional[str] = None
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
