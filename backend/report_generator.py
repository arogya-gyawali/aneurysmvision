"""Clinical report generation for cerebral aneurysm analysis.

Thin **application-layer adapter** that turns Stage 1-5 outputs (study
metadata, findings, biomarkers, mesh references) into a structured
:class:`ReportDraft`.

Anthropic Claude is used as the narrative engine **when available and
configured** (``ANTHROPIC_API_KEY``). Otherwise a deterministic, rule-based
draft is produced from the same structured data so the pipeline remains
fully functional and reproducible offline.

Scope: Stage 6 only. No frontend, caching, or contract changes.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

from backend.models import AneurysmFinding, ReportDraft, StudyMetadata

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-20250514"
_RULE_BASED_MODEL = "aneurysmvision-rule-based-v1"

# Aspect ratio above which rupture risk is commonly flagged in the literature.
_HIGH_ASPECT_RATIO = 1.6
_LARGE_DIAMETER_MM = 7.0


def generate_report(
    study: StudyMetadata,
    findings: list[AneurysmFinding],
    model: str = DEFAULT_MODEL,
) -> ReportDraft:
    """Generate a clinical narrative draft from study metadata and findings."""
    generated_at = _report_timestamp(study)
    context = _build_context(study, findings)

    claude_draft = _try_generate_with_claude(context, model)
    if claude_draft is not None:
        summary, narrative_findings, recommendations, used_model = claude_draft
    else:
        summary, narrative_findings, recommendations = _rule_based_report(study, findings)
        used_model = _RULE_BASED_MODEL

    return ReportDraft(
        summary=summary,
        findings=narrative_findings,
        recommendations=recommendations,
        model=used_model,
        generated_at=generated_at,
    )


# ---------------------------------------------------------------------------
# Structured context
# ---------------------------------------------------------------------------
def _build_context(study: StudyMetadata, findings: list[AneurysmFinding]) -> dict:
    """Assemble a deterministic, serializable summary of the analysis inputs."""
    return {
        "modality": study.modality.value,
        "subject": study.bids.subject if study.bids else None,
        "session": study.bids.session if study.bids else None,
        "shape": list(study.shape) if study.shape else None,
        "voxel_dimensions_mm": (
            [study.voxel_dimensions_mm.x, study.voxel_dimensions_mm.y, study.voxel_dimensions_mm.z]
            if study.voxel_dimensions_mm
            else None
        ),
        "quality": (
            {
                "snr": study.quality.snr,
                "contrast_to_noise": study.quality.contrast_to_noise,
                "motion_score": study.quality.motion_score,
                "passed_qc": study.quality.passed_qc,
            }
            if study.quality
            else None
        ),
        "aneurysm_count": len(findings),
        "aneurysms": [
            {
                "id": f.id,
                "location": f.location.value,
                "location_detail": f.location_detail,
                "confidence": f.confidence,
                "centroid_mm": list(f.centroid_mm),
                "biomarkers": {
                    "volume_mm3": f.biomarkers.volume_mm3,
                    "max_diameter_mm": f.biomarkers.max_diameter_mm,
                    "neck_width_mm": f.biomarkers.neck_width_mm,
                    "dome_height_mm": f.biomarkers.dome_height_mm,
                    "aspect_ratio": f.biomarkers.aspect_ratio,
                    "size_ratio": f.biomarkers.size_ratio,
                    "irregularity_index": f.biomarkers.irregularity_index,
                },
                "mesh": (
                    {"path": f.mesh.path, "format": f.mesh.format} if f.mesh else None
                ),
            }
            for f in findings
        ],
    }


# ---------------------------------------------------------------------------
# Claude engine (optional)
# ---------------------------------------------------------------------------
def _try_generate_with_claude(context: dict, model: str):
    """Attempt Claude-based generation; return None to trigger the fallback."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("ANTHROPIC_API_KEY not set; using rule-based report fallback.")
        return None

    try:
        import anthropic
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("anthropic SDK unavailable (%s); using rule-based fallback.", exc)
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=0.0,  # deterministic
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": _USER_PROMPT_TEMPLATE.format(
                        context=json.dumps(context, indent=2, sort_keys=True)
                    ),
                }
            ],
        )
        text = "".join(block.text for block in message.content if getattr(block, "type", None) == "text")
        parsed = json.loads(text)
        return (
            str(parsed["summary"]),
            [str(x) for x in parsed["findings"]],
            [str(x) for x in parsed["recommendations"]],
            model,
        )
    except Exception as exc:
        logger.warning("Claude report generation failed (%s); using rule-based fallback.", exc)
        return None


_SYSTEM_PROMPT = (
    "You are a neuroradiology assistant drafting a structured, non-diagnostic "
    "summary of automated cerebral aneurysm analysis. Respond ONLY with JSON "
    "containing keys: summary (string), findings (array of strings), "
    "recommendations (array of strings). Be concise and clinically cautious."
)

_USER_PROMPT_TEMPLATE = (
    "Generate a structured clinical report draft from this analysis context. "
    "Return JSON only.\n\nContext:\n{context}"
)


# ---------------------------------------------------------------------------
# Deterministic rule-based engine (default / offline)
# ---------------------------------------------------------------------------
def _rule_based_report(
    study: StudyMetadata,
    findings: list[AneurysmFinding],
) -> tuple[str, list[str], list[str]]:
    count = len(findings)
    modality = study.modality.value
    subject = f"subject {study.bids.subject}" if study.bids else "the subject"

    if count == 0:
        summary = (
            f"Automated {modality} analysis for {subject} detected no cerebral "
            f"aneurysm candidates meeting the size threshold."
        )
        return summary, ["No aneurysm candidates were identified."], [
            "No aneurysm-specific follow-up indicated based on this automated analysis.",
            "Correlate with clinical findings and radiologist review.",
        ]

    largest = max(findings, key=lambda f: f.biomarkers.max_diameter_mm)
    summary = (
        f"Automated {modality} analysis for {subject} identified {count} cerebral "
        f"aneurysm candidate{'s' if count != 1 else ''}. The largest candidate "
        f"({largest.id}) measures {largest.biomarkers.max_diameter_mm:.1f} mm in maximum "
        f"diameter at {largest.location_detail or largest.location.value}."
    )

    narrative_findings: list[str] = []
    for f in findings:
        bm = f.biomarkers
        narrative_findings.append(
            f"{f.id}: {bm.max_diameter_mm:.1f} mm max diameter, volume "
            f"{bm.volume_mm3:.1f} mm³, neck width {bm.neck_width_mm:.1f} mm, "
            f"aspect ratio {bm.aspect_ratio:.2f} "
            f"(location: {f.location_detail or f.location.value}, "
            f"detection confidence {f.confidence:.2f})."
        )

    if study.quality is not None:
        qc_state = "passed" if study.quality.passed_qc else "did not pass"
        snr_txt = f"{study.quality.snr:.1f}" if study.quality.snr is not None else "n/a"
        narrative_findings.append(
            f"Image quality control {qc_state} (SNR {snr_txt})."
        )

    recommendations = _recommendations(findings)
    return summary, narrative_findings, recommendations


def _recommendations(findings: list[AneurysmFinding]) -> list[str]:
    recommendations: list[str] = []

    high_risk = [
        f
        for f in findings
        if f.biomarkers.aspect_ratio >= _HIGH_ASPECT_RATIO
        or f.biomarkers.max_diameter_mm >= _LARGE_DIAMETER_MM
    ]
    if high_risk:
        ids = ", ".join(f.id for f in high_risk)
        recommendations.append(
            f"Specialist (neurosurgery/interventional radiology) review recommended for "
            f"higher-risk candidate(s): {ids} (elevated aspect ratio and/or size)."
        )
    else:
        recommendations.append(
            "Consider routine imaging follow-up for the detected candidate(s); "
            "no high-risk morphology flagged by automated thresholds."
        )

    recommendations.append(
        "All automated findings require confirmation by a qualified radiologist; "
        "this draft is non-diagnostic."
    )
    return recommendations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _report_timestamp(study: StudyMetadata) -> datetime:
    """Return a UTC timestamp for the report.

    Uses the QC/processing time implicitly via the current time; kept as a
    single ``now()`` call so the narrative content (the part that must be
    deterministic) is unaffected by it.
    """
    return datetime.now(timezone.utc)
