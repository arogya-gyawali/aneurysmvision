"""Clinical report generation via Anthropic Claude (deferred)."""

from __future__ import annotations

from backend.models import AneurysmFinding, ReportDraft, StudyMetadata


def generate_report(
    study: StudyMetadata,
    findings: list[AneurysmFinding],
    model: str = "claude-sonnet-4-20250514",
) -> ReportDraft:
    """Generate a clinical narrative draft from study metadata and findings."""
    raise NotImplementedError("Report generation not implemented (stage 4).")
