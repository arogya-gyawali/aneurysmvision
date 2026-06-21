"""Stage 0 - Patient Intake & Risk Assessment.

A pre-imaging layer that lets AneurysmVision provide value before any
MRI/MRA/CTA scan is available. It takes patient history and symptoms and
produces a deterministic, explainable risk assessment plus an imaging
recommendation.

Design principles:
  - **Deterministic, rule-based scoring** drives all clinical decisions.
  - **Explainable**: every point contributed to the score is recorded.
  - **Claude is optional and narrative-only**: it may rewrite the
    patient-friendly summary, but never changes the risk level, score, or
    imaging recommendation.

This module is fully self-contained and independent of the scan pipeline
(``pipeline.py`` and the imaging stages). It defines its own Pydantic models
so the frozen scan contract in ``models.py`` is untouched.
"""

from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class Sex(str, Enum):
    FEMALE = "female"
    MALE = "male"
    OTHER = "other"
    UNKNOWN = "unknown"


class SmokingStatus(str, Enum):
    NEVER = "never"
    FORMER = "former"
    CURRENT = "current"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ImagingRecommendation(str, Enum):
    NONE = "none"
    ROUTINE_MRA = "routine MRA"
    CTA = "CTA"
    URGENT_IMAGING = "urgent imaging"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class PatientIntake(BaseModel):
    """Patient history and symptoms collected before any imaging."""

    age: Optional[int] = Field(None, ge=0, le=120)
    sex: Sex = Sex.UNKNOWN
    smoking: SmokingStatus = SmokingStatus.UNKNOWN
    hypertension: bool = False
    family_history_aneurysm: bool = False
    prior_aneurysm: bool = False
    sudden_severe_headache: bool = False
    neurologic_symptoms: bool = False
    connective_tissue_disorder: bool = False
    clinician_notes: Optional[str] = None


class RiskFactor(BaseModel):
    """A single scored contribution to the overall risk."""

    name: str
    points: int
    detail: str


class RiskAssessment(BaseModel):
    """Deterministic risk assessment output for the intake layer."""

    risk_level: RiskLevel
    risk_score: int
    imaging_recommendation: ImagingRecommendation
    rationale: list[str]
    contributing_factors: list[RiskFactor]
    red_flag: bool
    clinician_notes: Optional[str] = None
    patient_friendly_summary: str
    narrative_model: str


# ---------------------------------------------------------------------------
# Scoring constants (explainable, deterministic)
# ---------------------------------------------------------------------------
_RULE_BASED_MODEL = "aneurysmvision-intake-rules-v1"

# Score thresholds (inclusive lower bounds).
_MODERATE_THRESHOLD = 3
_HIGH_THRESHOLD = 6


def assess_risk(intake: PatientIntake, use_claude_narrative: bool = True) -> RiskAssessment:
    """Compute a deterministic risk assessment from patient intake data."""
    factors = _score_factors(intake)
    score = sum(f.points for f in factors)

    # Red flags indicate possible acute presentation (e.g. SAH) regardless of score.
    red_flag = intake.sudden_severe_headache or intake.neurologic_symptoms

    risk_level = _risk_level(score, red_flag)
    recommendation = _imaging_recommendation(risk_level, red_flag)
    rationale = _rationale(factors, red_flag, risk_level, recommendation)

    summary, narrative_model = _patient_summary(
        risk_level, recommendation, factors, red_flag, intake, use_claude_narrative
    )

    return RiskAssessment(
        risk_level=risk_level,
        risk_score=score,
        imaging_recommendation=recommendation,
        rationale=rationale,
        contributing_factors=factors,
        red_flag=red_flag,
        clinician_notes=intake.clinician_notes,
        patient_friendly_summary=summary,
        narrative_model=narrative_model,
    )


# ---------------------------------------------------------------------------
# Deterministic scoring
# ---------------------------------------------------------------------------
def _score_factors(intake: PatientIntake) -> list[RiskFactor]:
    factors: list[RiskFactor] = []

    def add(name: str, points: int, detail: str) -> None:
        if points > 0:
            factors.append(RiskFactor(name=name, points=points, detail=detail))

    if intake.prior_aneurysm:
        add("prior_aneurysm", 3, "History of prior cerebral aneurysm.")
    if intake.family_history_aneurysm:
        add("family_history_aneurysm", 2, "Family history of cerebral aneurysm.")
    if intake.connective_tissue_disorder:
        add(
            "connective_tissue_disorder",
            2,
            "Connective tissue disorder (e.g. ADPKD, Ehlers-Danlos, Marfan).",
        )
    if intake.hypertension:
        add("hypertension", 1, "Hypertension.")

    if intake.smoking == SmokingStatus.CURRENT:
        add("smoking_current", 2, "Current smoker.")
    elif intake.smoking == SmokingStatus.FORMER:
        add("smoking_former", 1, "Former smoker.")

    if intake.sex == Sex.FEMALE:
        add("sex_female", 1, "Female sex (modestly higher prevalence).")

    if intake.age is not None and intake.age >= 40:
        add("age_over_40", 1, "Age 40 or older.")

    # Acute symptom factors (also drive the red-flag path).
    if intake.sudden_severe_headache:
        add(
            "sudden_severe_headache",
            3,
            "Sudden severe ('thunderclap') headache - possible acute presentation.",
        )
    if intake.neurologic_symptoms:
        add(
            "neurologic_symptoms",
            3,
            "Focal neurologic symptoms reported.",
        )

    return factors


def _risk_level(score: int, red_flag: bool) -> RiskLevel:
    if red_flag:
        return RiskLevel.HIGH
    if score >= _HIGH_THRESHOLD:
        return RiskLevel.HIGH
    if score >= _MODERATE_THRESHOLD:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def _imaging_recommendation(risk_level: RiskLevel, red_flag: bool) -> ImagingRecommendation:
    if red_flag:
        return ImagingRecommendation.URGENT_IMAGING
    if risk_level == RiskLevel.HIGH:
        return ImagingRecommendation.CTA
    if risk_level == RiskLevel.MODERATE:
        return ImagingRecommendation.ROUTINE_MRA
    return ImagingRecommendation.NONE


def _rationale(
    factors: list[RiskFactor],
    red_flag: bool,
    risk_level: RiskLevel,
    recommendation: ImagingRecommendation,
) -> list[str]:
    rationale: list[str] = []
    if red_flag:
        rationale.append(
            "Acute red-flag symptom(s) present; urgent imaging advised to exclude "
            "rupture/subarachnoid hemorrhage."
        )
    for f in factors:
        rationale.append(f"+{f.points}: {f.detail}")
    rationale.append(
        f"Computed risk level: {risk_level.value}; recommendation: {recommendation.value}."
    )
    rationale.append("Rule-based, non-diagnostic; requires clinician review.")
    return rationale


# ---------------------------------------------------------------------------
# Patient-friendly narrative (Claude optional, narrative-only)
# ---------------------------------------------------------------------------
def _patient_summary(
    risk_level: RiskLevel,
    recommendation: ImagingRecommendation,
    factors: list[RiskFactor],
    red_flag: bool,
    intake: PatientIntake,
    use_claude_narrative: bool,
) -> tuple[str, str]:
    base_summary = _rule_based_summary(risk_level, recommendation, factors, red_flag)

    if use_claude_narrative:
        rewritten = _try_claude_rewrite(base_summary, risk_level, recommendation)
        if rewritten is not None:
            return rewritten, "claude-narrative"

    return base_summary, _RULE_BASED_MODEL


def _rule_based_summary(
    risk_level: RiskLevel,
    recommendation: ImagingRecommendation,
    factors: list[RiskFactor],
    red_flag: bool,
) -> str:
    if red_flag:
        return (
            "Based on the symptoms entered, we strongly recommend seeking medical "
            "attention promptly. Some symptoms (such as a sudden severe headache or "
            "new neurological changes) can be urgent, and imaging is advised right away. "
            "This tool does not provide a diagnosis."
        )

    factor_phrase = ""
    if factors:
        top = ", ".join(f.name.replace("_", " ") for f in factors[:3])
        factor_phrase = f" Contributing considerations include: {top}."

    rec_text = {
        ImagingRecommendation.NONE: (
            "no aneurysm-specific imaging is suggested at this time based on the "
            "information provided"
        ),
        ImagingRecommendation.ROUTINE_MRA: (
            "a routine MRA (a type of MRI scan) may be worth discussing with your doctor"
        ),
        ImagingRecommendation.CTA: (
            "a CTA scan may be worth discussing with your doctor"
        ),
        ImagingRecommendation.URGENT_IMAGING: "urgent imaging is advised",
    }[recommendation]

    return (
        f"Your estimated risk level is {risk_level.value}. Based on this, {rec_text}."
        f"{factor_phrase} This is an automated, non-diagnostic estimate - please review "
        "the results with a qualified clinician."
    )


def _try_claude_rewrite(
    base_summary: str,
    risk_level: RiskLevel,
    recommendation: ImagingRecommendation,
) -> Optional[str]:
    """Use Claude ONLY to rewrite the narrative; never to change the decision."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("anthropic SDK unavailable (%s); using rule-based summary.", exc)
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            temperature=0.0,
            system=(
                "Rewrite the given clinical risk summary in clear, compassionate, "
                "plain language for a patient. Do NOT change the risk level or the "
                "imaging recommendation. Keep it non-diagnostic. Return only the text."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Risk level: {risk_level.value}\n"
                        f"Imaging recommendation: {recommendation.value}\n"
                        f"Summary to rewrite:\n{base_summary}"
                    ),
                }
            ],
        )
        text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        ).strip()
        return text or None
    except Exception as exc:
        logger.warning("Claude narrative rewrite failed (%s); using rule-based summary.", exc)
        return None
