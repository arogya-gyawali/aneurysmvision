"""End-to-end aneurysm analysis pipeline orchestrator.

Transport: in-process Python calls from the Streamlit frontend.
Heavy processing stages delegate to module stubs and raise
``NotImplementedError`` until later implementation stages.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeVar

from backend import (
    bids_parser,
    biomarkers,
    mesh_generator,
    nifti_loader,
    report_generator,
    roi_extractor,
)
from backend.exceptions import PipelineError, StageNotImplementedError, ValidationError
from backend.models import (
    AnalysisRequest,
    AnalysisResult,
    AneurysmFinding,
    JobStatus,
    ReportDraft,
    StageTiming,
    StudyMetadata,
)

logger = logging.getLogger(__name__)

PIPELINE_VERSION = "0.1.0"

T = TypeVar("T")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure minimal structured logging for the backend."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _run_stage(
    name: str,
    stages: list[StageTiming],
    fn: Callable[[], T],
    *,
    skip: bool = False,
    skip_message: str = "",
) -> T | None:
    """Execute a pipeline stage with timing, logging, and error capture."""
    if skip:
        stages.append(
            StageTiming(name=name, status=JobStatus.SKIPPED, message=skip_message or None)
        )
        logger.info("Stage '%s' skipped: %s", name, skip_message)
        return None

    stage = StageTiming(name=name, status=JobStatus.RUNNING)
    stages.append(stage)
    start = time.perf_counter()

    try:
        result = fn()
        stage.status = JobStatus.COMPLETED
        stage.duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info("Stage '%s' completed in %dms", name, stage.duration_ms)
        return result
    except NotImplementedError as exc:
        stage.status = JobStatus.FAILED
        stage.duration_ms = int((time.perf_counter() - start) * 1000)
        stage.error = str(exc)
        logger.warning("Stage '%s' not implemented: %s", name, exc)
        raise StageNotImplementedError(name, str(exc)) from exc
    except Exception as exc:
        stage.status = JobStatus.FAILED
        stage.duration_ms = int((time.perf_counter() - start) * 1000)
        stage.error = str(exc)
        logger.exception("Stage '%s' failed", name)
        raise


def run_pipeline(request: AnalysisRequest) -> AnalysisResult:
    """Execute the aneurysm analysis pipeline for a single study."""
    configure_logging()

    job_id = request.resolved_job_id()
    created_at = datetime.now(timezone.utc)
    stages: list[StageTiming] = []
    errors: list[str] = []
    study = StudyMetadata(nifti_path="")
    findings: list[AneurysmFinding] = []
    report: ReportDraft | None = None
    status = JobStatus.RUNNING
    volume: Any = None
    segmentation: Any = None
    pipeline_start = time.perf_counter()

    logger.info("Pipeline started job_id=%s", job_id)

    try:
        def bids_stage() -> list[str]:
            nonlocal study
            path, entities = bids_parser.resolve_nifti_path(request)
            study = StudyMetadata(nifti_path=str(path), bids=entities)
            if request.dataset_root:
                return bids_parser.validate_bids_dataset(Path(request.dataset_root))
            return []

        warnings = _run_stage("bids_parse", stages, bids_stage)
        if warnings and stages:
            stages[-1].message = "; ".join(warnings)

        loaded = _run_stage(
            "nifti_load",
            stages,
            lambda: nifti_loader.load_nifti(Path(study.nifti_path)),
        )
        assert loaded is not None
        volume, study = loaded

        quality = _run_stage(
            "quality_control",
            stages,
            lambda: nifti_loader.run_quality_checks(volume, study),
        )
        assert quality is not None
        study = study.model_copy(update={"quality": quality})

        segmentation = _run_stage(
            "detection",
            stages,
            lambda: roi_extractor.run_detection(volume, request.segmentation_path),
        )

        extracted = _run_stage(
            "roi_extraction",
            stages,
            lambda: roi_extractor.extract_rois(volume, segmentation),
        )
        assert extracted is not None
        findings = extracted

        if study.voxel_dimensions_mm is not None:
            enriched = _run_stage(
                "biomarkers",
                stages,
                lambda: biomarkers.enrich_findings_with_biomarkers(
                    findings,
                    study.voxel_dimensions_mm,
                ),
            )
            if enriched is not None:
                findings = enriched
        else:
            _run_stage(
                "biomarkers",
                stages,
                lambda: None,
                skip=True,
                skip_message="Voxel dimensions unavailable",
            )

        if request.generate_mesh:
            meshed = _run_stage(
                "mesh_generation",
                stages,
                lambda: mesh_generator.generate_meshes(
                    findings,
                    roi_volumes={},
                    output_dir=Path(f"/artifacts/{job_id}/meshes"),
                ),
            )
            if meshed is not None:
                findings = meshed
        else:
            _run_stage(
                "mesh_generation",
                stages,
                lambda: None,
                skip=True,
                skip_message="generate_mesh=false",
            )

        if request.generate_report:
            report = _run_stage(
                "report_generation",
                stages,
                lambda: report_generator.generate_report(study, findings),
            )
        else:
            _run_stage(
                "report_generation",
                stages,
                lambda: None,
                skip=True,
                skip_message="generate_report=false",
            )

        status = JobStatus.COMPLETED

    except StageNotImplementedError as exc:
        errors.append(str(exc))
        status = JobStatus.FAILED
    except ValidationError as exc:
        errors.append(str(exc))
        status = JobStatus.FAILED
    except PipelineError as exc:
        errors.append(str(exc))
        status = JobStatus.FAILED
    except Exception as exc:
        errors.append(f"Unexpected error: {exc}")
        status = JobStatus.FAILED
        logger.exception("Pipeline job_id=%s failed unexpectedly", job_id)

    completed_at = datetime.now(timezone.utc)
    processing_ms = int((time.perf_counter() - pipeline_start) * 1000)

    result = AnalysisResult(
        job_id=job_id,
        status=status,
        created_at=created_at,
        completed_at=completed_at,
        study=study,
        aneurysms=findings,
        aneurysm_count=len(findings),
        report=report,
        stages=stages,
        cache_key=_cache_key(request) if request.cache_results else None,
        errors=errors,
        metadata={
            "pipeline_version": PIPELINE_VERSION,
            "transport": "in_process",
            "processing_time_ms": processing_ms,
        },
    )

    logger.info(
        "Pipeline finished job_id=%s status=%s stages=%d errors=%d",
        job_id,
        status.value,
        len(stages),
        len(errors),
    )
    return result


def _cache_key(request: AnalysisRequest) -> str | None:
    """Build a deterministic Redis cache key placeholder."""
    if request.nifti_path:
        return f"av:path:{Path(request.nifti_path).name}"
    if request.bids_entities:
        parts = [f"sub-{request.bids_entities.subject}"]
        if request.bids_entities.session:
            parts.append(f"ses-{request.bids_entities.session}")
        return f"av:{':'.join(parts)}"
    return None
