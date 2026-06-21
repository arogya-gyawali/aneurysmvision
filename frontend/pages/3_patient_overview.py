"""Patient Overview — clinical summary sheet."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import layout, patient_panel
from frontend.utils import location_label

result = layout.require_result()
layout.top_bar(result, "Patient Overview")

if not result:
    layout.empty_state(
        "🧾", "No patient loaded", "Upload a scan or load the demo patient to see a summary here.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

bids = (result.get("study", {}) or {}).get("bids") or {}

st.markdown(f"<div class='av-section-header'>sub-{bids.get('sub', '—')} — Clinical Summary</div>", unsafe_allow_html=True)
st.markdown(
    "Age / sex are not part of the current API contract " + layout.mock_tag("Not available") + " — "
    "shown as placeholders below pending a demographics field on `StudyMetadata`.",
    unsafe_allow_html=True,
)
c1, c2 = st.columns(2)
c1.text_input("Age", value="—", disabled=True)
c2.text_input("Sex", value="—", disabled=True)

st.markdown("---")
patient_panel.render(result)

st.markdown("---")
st.markdown("<div class='av-section-header'>Detected Anatomy</div>", unsafe_allow_html=True)
aneurysms = result.get("aneurysms", [])
if aneurysms:
    for finding in aneurysms:
        st.markdown(
            f"- **{location_label(finding.get('location', ''))}** — {finding.get('location_detail', '—')} "
            f"(confidence {finding.get('confidence', 0) * 100:.0f}%)"
        )
else:
    st.success("No aneurysms detected in this study.")

st.markdown("---")
st.markdown("<div class='av-section-header'>Clinician Notes</div>", unsafe_allow_html=True)
st.session_state.setdefault("av_notes", "")
st.session_state["av_notes"] = st.text_area(
    "Observations for this review (saved with the exported report)",
    value=st.session_state["av_notes"],
    height=120,
    placeholder="e.g. Patient reports intermittent headaches, no prior imaging available…",
)

if st.button("Continue to ROI Selection →", type="primary", width="stretch"):
    st.switch_page("pages/4_roi_selection.py")
