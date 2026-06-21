"""Measurements — quantitative biomarkers for the active ROI, plus comparison."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import biomarker_cards, layout
from frontend.utils import finding_label

result = layout.require_result()
layout.top_bar(result, "Measurements")

if not result:
    layout.empty_state(
        "📏", "No patient loaded", "Load a patient to see quantitative measurements.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

aneurysms = result.get("aneurysms", [])
if not aneurysms:
    st.success("No aneurysms detected — no measurements to report.")
    st.stop()

selected_id = st.session_state.get("av_selected_id") or aneurysms[0]["id"]
labels = [finding_label(a) for a in aneurysms]
ids = [a["id"] for a in aneurysms]
idx = ids.index(selected_id) if selected_id in ids else 0
chosen = st.selectbox("Finding", labels, index=idx)
finding = aneurysms[labels.index(chosen)]
st.session_state["av_selected_id"] = finding["id"]

biomarker_cards.render(finding)

if len(aneurysms) > 1:
    st.markdown("---")
    st.markdown(
        f"<div class='av-section-header'>Comparison Across Findings {layout.mock_tag('Within this study only')}</div>",
        unsafe_allow_html=True,
    )
    st.caption("Longitudinal comparison against prior studies isn't available yet — the contract has no job-history endpoint.")
    import pandas as pd

    rows = []
    for a in aneurysms:
        bio = a.get("biomarkers", {}) or {}
        rows.append(
            {
                "Finding": finding_label(a),
                "Volume (mm³)": bio.get("volume_mm3"),
                "Max Diameter (mm)": bio.get("max_diameter_mm"),
                "Aspect Ratio": bio.get("aspect_ratio"),
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

nav_l, nav_r = st.columns(2)
with nav_l:
    if st.button("← Back to Cross-Sections", width="stretch"):
        st.switch_page("pages/6_cross_sections.py")
with nav_r:
    if st.button("Continue to AI Summary →", type="primary", width="stretch"):
        st.switch_page("pages/8_ai_summary.py")
