"""Cross-Section / Slice Viewer."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import layout, slice_viewer
from frontend.utils import finding_label

result = layout.require_result()
layout.top_bar(result, "Cross-Sections")

if not result:
    layout.empty_state(
        "🩻", "No patient loaded", "Load a patient to inspect cross-sections.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

aneurysms = result.get("aneurysms", [])
finding = None
if aneurysms:
    selected_id = st.session_state.get("av_selected_id") or aneurysms[0]["id"]
    labels = [finding_label(a) for a in aneurysms]
    ids = [a["id"] for a in aneurysms]
    idx = ids.index(selected_id) if selected_id in ids else 0
    chosen = st.selectbox("ROI to center crosshair on", labels, index=idx)
    finding = aneurysms[labels.index(chosen)]
    st.session_state["av_selected_id"] = finding["id"]

slice_viewer.render(result.get("study", {}) or {}, finding)

nav_l, nav_r = st.columns(2)
with nav_l:
    if st.button("← Back to 3D Visualization", width="stretch"):
        st.switch_page("pages/5_3d_visualization.py")
with nav_r:
    if st.button("Continue to Measurements →", type="primary", width="stretch"):
        st.switch_page("pages/7_measurements.py")
