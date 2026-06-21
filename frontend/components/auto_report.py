"""Fully automatic, single-screen output: everything the pipeline produces,
rendered inline the moment a result exists — patient info, a labeled 3D
vessel map, per-finding measurements, and the AI summary last.

No page-to-page navigation here on purpose: once a doctor uploads a scan,
the whole read should appear top to bottom on one screen.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend import data_client as dc
from frontend.components import biomarker_cards, layout, mesh_viewer, patient_panel, report_panel
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

        mesh_viewer.render(
            aneurysms, selected_id, height=560, show_other_rois=True, show_labels=True,
        )
        st.caption("Every detected vessel/territory is labeled directly in the scene — the focused finding is highlighted, others stay visible in gray.")

        st.markdown("")
        st.markdown("<div class='av-section-header'>Measurements</div>", unsafe_allow_html=True)
        focused = next((f for f in aneurysms if f.get("id") == selected_id), aneurysms[0])
        biomarker_cards.render(focused)

    st.markdown("")
    report_panel.render(result.get("report"), result.get("job_id", "—"), is_demo=dc.is_demo(result))
