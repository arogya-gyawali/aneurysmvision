"""3D Visualization — the hero page. Large interactive Plotly workspace."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import layout, mesh_viewer
from frontend.utils import compute_risk, finding_label, risk_badge_html

result = layout.require_result()
layout.top_bar(result, "3D Visualization")

if not result:
    layout.empty_state(
        "🧠", "No patient loaded", "Load a patient to explore the 3D reconstruction.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

aneurysms = result.get("aneurysms", [])
if not aneurysms:
    st.success("No aneurysms detected — nothing to render in 3D for this study.")
    st.stop()

selected_id = st.session_state.get("av_selected_id") or aneurysms[0]["id"]
labels = [finding_label(a) for a in aneurysms]
ids = [a["id"] for a in aneurysms]
sel_idx = ids.index(selected_id) if selected_id in ids else 0

control_l, control_r = st.columns([2, 3])
with control_l:
    chosen = st.selectbox("Active ROI", labels, index=sel_idx)
    st.session_state["av_selected_id"] = ids[labels.index(chosen)]
finding = aneurysms[labels.index(chosen)]
risk = compute_risk(finding.get("biomarkers", {}) or {})
with control_r:
    st.markdown(
        f"<div style='padding-top:1.7rem;'>{risk_badge_html(risk)}</div>",
        unsafe_allow_html=True,
    )

with st.expander("Layers & display", expanded=False):
    lc1, lc2, lc3, lc4 = st.columns(4)
    show_others = lc1.checkbox("Other ROIs", value=st.session_state.get("av_default_show_others", True))
    show_labels = lc2.checkbox("Labels", value=st.session_state.get("av_default_show_labels", False))
    show_axes = lc3.checkbox("Axes", value=st.session_state.get("av_default_show_axes", True))
    opacity = lc4.slider("Selected opacity", 0.2, 1.0, st.session_state.get("av_default_opacity", 0.92))

st.markdown(
    "<div style='display:flex;gap:1rem;align-items:center;margin:0.25rem 0;'>"
    "<span style='color:#94a3b8;font-size:0.8rem;'>● Selected ROI (risk-colored)</span>"
    "<span style='color:#94a3b8;font-size:0.8rem;'>● Other detected ROIs (muted)</span>"
    "</div>",
    unsafe_allow_html=True,
)

mesh_viewer.render(
    aneurysms,
    st.session_state["av_selected_id"],
    height=680,
    show_other_rois=show_others,
    opacity_override=opacity,
    show_labels=show_labels,
    show_axes=show_axes,
)
st.caption("Drag to rotate, scroll to zoom, use the toolbar's camera icon to export a PNG snapshot or reset the view.")

nav_l, nav_r = st.columns(2)
with nav_l:
    if st.button("← Back to ROI Selection", width="stretch"):
        st.switch_page("pages/4_roi_selection.py")
with nav_r:
    if st.button("Continue to Cross-Sections →", type="primary", width="stretch"):
        st.switch_page("pages/6_cross_sections.py")
