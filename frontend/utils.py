"""Frontend utilities for risk scoring and display helpers.

Computes risk level from BiomarkerSet fields since the backend schema
does not include risk_level / risk_score directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskAssessment:
    score: int          # 0-100
    level: str          # "Low" | "Moderate" | "High" | "Critical"
    color: str          # CSS/Plotly colour
    rationale: list[str]


_LOCATION_LABELS: dict[str, str] = {
    "middle_cerebral_artery": "Middle Cerebral Artery (MCA)",
    "anterior_cerebral_artery": "Anterior Cerebral Artery (ACA)",
    "internal_carotid_artery": "Internal Carotid Artery (ICA)",
    "basilar_artery": "Basilar Artery (BA)",
    "posterior_cerebral_artery": "Posterior Cerebral Artery (PCA)",
    "anterior_communicating_artery": "Anterior Communicating Artery (AComA)",
    "posterior_communicating_artery": "Posterior Communicating Artery (PComA)",
    "other": "Other",
}


def compute_risk(biomarkers: dict[str, Any]) -> RiskAssessment:
    """Derive a risk assessment from BiomarkerSet fields."""
    score = 0
    rationale: list[str] = []

    aspect_ratio = biomarkers.get("aspect_ratio", 0.0)
    volume = biomarkers.get("volume_mm3", 0.0)
    diameter = biomarkers.get("max_diameter_mm", 0.0)
    irr = biomarkers.get("irregularity_index") or 1.0

    if aspect_ratio >= 1.6:
        pts = 35
        score += pts
        rationale.append(f"Aspect ratio {aspect_ratio:.2f} >= 1.6 (+{pts} pts)")
    elif aspect_ratio >= 1.2:
        pts = 15
        score += pts
        rationale.append(f"Aspect ratio {aspect_ratio:.2f} >= 1.2 (+{pts} pts)")

    if volume >= 500:
        pts = 30
        score += pts
        rationale.append(f"Volume {volume:.1f} mm³ >= 500 mm³ (+{pts} pts)")
    elif volume >= 100:
        pts = 15
        score += pts
        rationale.append(f"Volume {volume:.1f} mm³ >= 100 mm³ (+{pts} pts)")

    if diameter >= 10:
        pts = 20
        score += pts
        rationale.append(f"Max diameter {diameter:.1f} mm >= 10 mm (+{pts} pts)")
    elif diameter >= 5:
        pts = 10
        score += pts
        rationale.append(f"Max diameter {diameter:.1f} mm >= 5 mm (+{pts} pts)")

    if irr >= 1.3:
        pts = 15
        score += pts
        rationale.append(f"Irregularity index {irr:.2f} >= 1.3 (+{pts} pts)")

    score = min(score, 100)

    if score >= 70:
        level, color = "Critical", "#ef4444"
    elif score >= 45:
        level, color = "High", "#f97316"
    elif score >= 20:
        level, color = "Moderate", "#eab308"
    else:
        level, color = "Low", "#22c55e"

    return RiskAssessment(score=score, level=level, color=color, rationale=rationale)


def location_label(location_value: str) -> str:
    return _LOCATION_LABELS.get(location_value, location_value.replace("_", " ").title())


def finding_label(finding: dict[str, Any]) -> str:
    idx = finding.get("label", "?")
    loc = location_label(finding.get("location", ""))
    dia = finding.get("biomarkers", {}).get("max_diameter_mm", 0.0)
    return f"#{idx} — {loc} ({dia:.1f} mm)"


def format_stage_status(stage: dict[str, Any]) -> tuple[str, str]:
    """Return (icon, colour) for a pipeline stage status."""
    status = stage.get("status", "")
    if status == "completed":
        return "✓", "#22c55e"
    if status == "failed":
        return "✗", "#ef4444"
    if status == "skipped":
        return "—", "#6b7280"
    return "●", "#3b82f6"
