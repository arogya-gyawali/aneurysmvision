"""Fully automatic, single-screen output: everything the pipeline produces,
rendered inline the moment a result exists.

Primary clinical content (patient info, labeled 3D vessel map, measurements,
AI summary) stays fully expanded so a doctor sees it at a glance. Secondary
detail (cross-sections, follow-up Q&A, export formats, raw pipeline timing)
is tucked into collapsed expanders so the page doesn't read as a wall of
options — open them only if you need them.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend import data_client as dc
from frontend.components import (
    ai_chat,
    biomarker_cards,
    layout,
    mesh_viewer,
    patient_panel,
    report_export,
    report_panel,
    slice_viewer,
    status_panel,
)
from frontend.utils import finding_label


def render(result: dict[str, Any]) -> None:
    if dc.is_demo(result):
        st.info("Demo mode — this is `backend/sample_output.json`, standing in for the live pipeline.", icon="ℹ️")

    st.markdown("<div class='av-section-header'>Patient & Study</div>", unsafe_allow_html=True)
    patient_panel.render(result)

    aneurysms = result.get("aneurysms", []) or []

    st.markdown("")
    st.markdown(
        "<div class='av-section-header'>3D Vessel Map — every detected territory labeled</div>",
        unsafe_allow_html=True,
    )
    focused = None
    if not aneurysms:
        st.info("No aneurysm findings were detected for this study.")
    else:
        ids = [f.get("id") for f in aneurysms]
        selected_id = st.session_state.get("av_selected_id")
        if selected_id not in ids:
            selected_id = ids[0]
            st.session_state["av_selected_id"] = selected_id

        if len(aneurysms) > 1:
            labels = {f.get("id"): finding_label(f) for f in aneurysms}
            chosen = st.radio(
                "Focus finding", ids, index=ids.index(selected_id),
                format_func=lambda fid: labels.get(fid, fid), horizontal=True, key="av_home_focus",
            )
            if chosen != selected_id:
                st.session_state["av_selected_id"] = chosen
                selected_id = chosen

        mesh_viewer.render(aneurysms, selected_id, height=560, show_other_rois=True, show_labels=True)
        st.caption("Every detected vessel/territory is labeled directly in the scene — the focused finding is highlighted, others stay visible in gray.")

        focused = next((f for f in aneurysms if f.get("id") == selected_id), aneurysms[0])

        with st.expander("🩻 Cross-sections for this finding"):
            slice_viewer.render(result.get("study", {}) or {}, focused)

        st.markdown("")
        st.markdown("<div class='av-section-header'>Measurements</div>", unsafe_allow_html=True)
        biomarker_cards.render(focused)

    st.markdown("")
    report = result.get("report")
    report_panel.render(report, result.get("job_id", "—"), is_demo=dc.is_demo(result))
    if report:
        with st.expander("💬 Ask a follow-up question"):
            ai_chat.render(report, focused)

    with st.expander("⬇️ Export report (Markdown / JSON / PDF)"):
        report_export.render(result)

    with st.expander("⚙️ Pipeline details"):
        status_panel.render(result.get("stages", []), result.get("metadata"), result.get("cache_key"))
