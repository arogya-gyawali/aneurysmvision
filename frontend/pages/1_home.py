"""Home / Landing — first impression, workflow at a glance, recent sessions."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend import data_client as dc
from frontend.components import layout, patient_panel
from frontend.components.mock_sessions import recent_sessions

result = layout.require_result()
layout.top_bar(result, "Home")

st.markdown(
    """
    <div style="padding: 0.5rem 0 0.5rem 0;">
        <h1 style="margin-bottom:0.25rem;">Vascular review, without the busywork</h1>
        <p style="color:#64748b; font-size:1.05rem; max-width:680px;">
            Upload a BIDS scan, let detection find candidate aneurysms, then walk through
            3D reconstruction, cross-sections, measurements, and an AI-drafted summary —
            all in one calm workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

cta_l, cta_r = st.columns(2)
with cta_l:
    if st.button("📤 Upload BIDS Folder", type="primary", width="stretch"):
        st.switch_page("pages/2_upload.py")
with cta_r:
    if st.button("🧪 Load Demo Patient (sample data)", width="stretch"):
        st.session_state["av_result"] = dc.get_sample_result()
        st.session_state.pop("av_selected_id", None)
        st.success("Demo patient loaded — try the workflow below.")
        st.rerun()

st.markdown("")
steps = [
    ("📤", "Upload", "pages/2_upload.py"),
    ("🎯", "Select ROI", "pages/4_roi_selection.py"),
    ("🧠", "3D View", "pages/5_3d_visualization.py"),
    ("🩻", "Slices", "pages/6_cross_sections.py"),
    ("📏", "Measure", "pages/7_measurements.py"),
    ("🤖", "AI Summary", "pages/8_ai_summary.py"),
    ("📄", "Export", "pages/9_report_export.py"),
]
cols = st.columns(len(steps))
for col, (icon, label, page) in zip(cols, steps):
    with col:
        st.markdown(
            f"<div class='av-card' style='text-align:center;padding:0.75rem 0.4rem;'>{icon}<br/>{label}</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

if result:
    st.markdown("<div class='av-section-header'>Current Patient</div>", unsafe_allow_html=True)
    if dc.is_demo(result):
        st.info("Demo mode — this is `backend/sample_output.json`, standing in for the live pipeline.", icon="ℹ️")
    patient_panel.render(result)
    nav_l, nav_r = st.columns(2)
    with nav_l:
        if st.button("Continue to Patient Overview →", width="stretch"):
            st.switch_page("pages/3_patient_overview.py")
    with nav_r:
        if st.button("Skip to 3D Visualization →", width="stretch"):
            st.switch_page("pages/5_3d_visualization.py")
else:
    layout.empty_state(
        "🧠",
        "No patient loaded yet",
        "Upload a BIDS folder or load the demo patient above to start a review.",
    )

st.markdown("---")
st.markdown(
    "<div class='av-section-header'>Recent Sessions " + layout.mock_tag("Demo data") + "</div>",
    unsafe_allow_html=True,
)
status_colors = {"completed": "#16a34a", "failed": "#dc2626", "running": "#2563eb"}
session_cols = st.columns(3)
for col, sess in zip(session_cols, recent_sessions()):
    color = status_colors.get(sess["status"], "#6b7280")
    with col:
        st.markdown(
            f"""
            <div class="av-card">
                <div class="av-card-label">{sess['patient']} · {sess['date']}</div>
                <div class="av-card-value" style="font-size:1.1rem;">{sess['findings']}</div>
                <span class='av-badge' style='background:{color}1a;color:{color};margin-top:0.5rem;'>{sess['status'].upper()}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption("AneurysmVision v0.1.0 · Frontend built against backend/api_contract.md")
