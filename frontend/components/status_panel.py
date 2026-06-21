"""Pipeline status / timing panel, rendered from `StageTiming[]` + `metadata`."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.utils import format_stage_status

_STAGE_LABELS = {
    "bids_parse": "BIDS parsing",
    "nifti_load": "NIfTI loading",
    "quality_control": "Quality control",
    "detection": "Aneurysm detection",
    "roi_extraction": "ROI extraction",
    "biomarkers": "Biomarker computation",
    "mesh_generation": "Mesh generation",
    "report_generation": "Report generation",
}


def render(stages: list[dict[str, Any]], metadata: dict[str, Any] | None = None, cache_key: str | None = None) -> None:
    st.markdown("<div class='av-section-header'>Pipeline Status</div>", unsafe_allow_html=True)

    if not stages:
        st.caption("No stage timing available yet.")
        return

    total_ms = sum(s.get("duration_ms") or 0 for s in stages)
    for stage in stages:
        icon, color = format_stage_status(stage)
        name = _STAGE_LABELS.get(stage.get("name", ""), stage.get("name", "stage"))
        dur = f"{stage['duration_ms']:,} ms" if stage.get("duration_ms") is not None else ""
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:0.25rem 0;'>"
            f"<span><span style='color:{color};font-weight:700;'>{icon}</span> {name}</span>"
            f"<span class='av-caption-muted'>{dur}</span></div>",
            unsafe_allow_html=True,
        )
        if stage.get("message"):
            st.caption(f"　{stage['message']}")
        if stage.get("error"):
            st.caption(f"　⚠️ {stage['error']}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Total time", f"{total_ms / 1000:.1f} s")
    if metadata:
        c2.metric("Pipeline ver.", metadata.get("pipeline_version", "—"))
    if cache_key:
        st.caption(f"Cache key: `{cache_key}`")
