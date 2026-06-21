"""ROI Selection — pick the active vascular finding for the rest of the workflow."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import layout, roi_selector

result = layout.require_result()
layout.top_bar(result, "ROI Selection")

if not result:
    layout.empty_state(
        "🎯", "No patient loaded", "Load a patient first to see ROI candidates.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

aneurysms = result.get("aneurysms", [])
selected_id = roi_selector.render(aneurysms)

if selected_id:
    st.markdown("---")
    if st.button("Continue to 3D Visualization →", type="primary", width="stretch"):
        st.switch_page("pages/5_3d_visualization.py")
