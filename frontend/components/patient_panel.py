"""Patient & study metadata panel.

Renders a horizontal clinical header strip from `AnalysisResult.study`
plus job-level fields (job_id, status, created_at).
"""

from __future__ import annotations

from typing import Any

import streamlit as st

_STATUS_COLORS = {
    "completed": "#16a34a",
    "running": "#2563eb",
    "queued": "#6b7280",
    "failed": "#dc2626",
    "skipped": "#6b7280",
}


def _metric_card(label: str, value: str, sub: str = "", accent: str | None = None) -> str:
    border = f"border-top:3px solid {accent};" if accent else ""
    return (
        f"<div class='av-card' style='{border}padding:0.7rem 1rem;'>"
        f"<div class='av-card-label'>{label}</div>"
        f"<div class='av-card-value' style='font-size:1.15rem;'>{value}</div>"
        + (f"<div class='av-card-sub'>{sub}</div>" if sub else "")
        + "</div>"
    )


def render(result: dict[str, Any]) -> None:
    study = result.get("study", {}) or {}
    bids = study.get("bids") or {}
    quality = study.get("quality") or {}
    voxels = study.get("voxel_dimensions_mm") or {}
    shape = study.get("shape")

    status = result.get("status", "unknown")
    status_color = _STATUS_COLORS.get(status, "#6b7280")

    qc_passed = quality.get("passed_qc")
    qc_color = "#16a34a" if qc_passed else ("#dc2626" if qc_passed is False else "#6b7280")
    qc_label = "Passed" if qc_passed else ("Failed" if qc_passed is False else "—")

    voxel_str = (
        f"{voxels.get('x', '—')} × {voxels.get('y', '—')} × {voxels.get('z', '—')} mm"
        if voxels
        else "—"
    )
    shape_str = f"{shape[0]} × {shape[1]} × {shape[2]} vox" if shape else "—"

    cols = st.columns(6)
    cards = [
        _metric_card("Subject", f"sub-{bids.get('sub', '—')}", f"ses-{bids.get('ses')}" if bids.get("ses") else "no session"),
        _metric_card("Modality", study.get("modality", "TOF-MRA"), shape_str),
        _metric_card("Voxel size", voxel_str),
        _metric_card("Quality control", qc_label, f"SNR {quality.get('snr', '—')}", accent=qc_color),
        _metric_card("Job status", status.upper(), result.get("job_id", "—"), accent=status_color),
        _metric_card(
            "Aneurysms found",
            str(result.get("aneurysm_count", len(result.get("aneurysms", [])))),
            accent="#2563eb",
        ),
    ]
    for col, card_html in zip(cols, cards):
        with col:
            st.markdown(card_html, unsafe_allow_html=True)

    notes = quality.get("notes") or []
    if notes:
        st.caption(" · ".join(notes))
