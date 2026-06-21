"""Settings / Help / Admin."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import layout

result = layout.require_result()
layout.top_bar(result, "Settings & Help")

st.markdown("<div class='av-section-header'>Display Preferences</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    unit = st.radio("Measurement units", ["mm", "cm"], index=0 if st.session_state.get("av_unit", "mm") == "mm" else 1, horizontal=True)
    st.session_state["av_unit"] = unit
with c2:
    density = st.radio("Layout density", ["Comfortable", "Compact"], horizontal=True)
    st.session_state["av_density"] = density
st.caption("Theme (light, clinical blue/teal palette) is fixed for visual consistency across the app — see `.streamlit/config.toml`.")

st.markdown("---")
st.markdown("<div class='av-section-header'>3D Viewer Defaults</div>", unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)
st.session_state["av_default_show_others"] = d1.checkbox("Show other ROIs by default", value=st.session_state.get("av_default_show_others", True))
st.session_state["av_default_show_labels"] = d2.checkbox("Show labels by default", value=st.session_state.get("av_default_show_labels", False))
st.session_state["av_default_show_axes"] = d3.checkbox("Show axes by default", value=st.session_state.get("av_default_show_axes", True))
st.session_state["av_default_opacity"] = d4.slider("Default opacity", 0.2, 1.0, st.session_state.get("av_default_opacity", 0.92))

st.markdown("---")
st.markdown("<div class='av-section-header'>Help Guide</div>", unsafe_allow_html=True)
st.markdown(
    "**Suggested workflow:** Upload → ROI Selection → 3D Visualization → Cross-Sections → "
    "Measurements → AI Summary → Report & Export."
)

with st.expander("Glossary — what does this mean?"):
    glossary = {
        "MCA / ACA / ICA / PCA": "Middle / Anterior / Internal Carotid / Posterior cerebral arteries — vascular territories where aneurysms commonly form.",
        "AComA / PComA": "Anterior / Posterior communicating artery — common aneurysm sites near the skull base.",
        "Aspect ratio": "Dome height ÷ neck width. Higher values (≥1.6) are associated with elevated rupture risk.",
        "Size ratio": "Aneurysm size relative to the parent vessel diameter.",
        "Neck width": "Width of the aneurysm where it joins the parent vessel — narrower necks are often more amenable to coiling.",
        "Irregularity index": "A surface-shape score; values above 1.0 suggest lobulation, a feature linked to higher risk.",
        "SNR / CNR": "Signal-to-noise / contrast-to-noise ratio — image quality measures affecting detection confidence.",
        "Motion score": "Normalized motion-artifact score (0–1, lower is better).",
    }
    for term, definition in glossary.items():
        st.markdown(f"**{term}** — {definition}")

with st.expander("Data privacy notice"):
    st.markdown(
        "- This demo build operates entirely on synthetic sample data (`backend/sample_output.json`).\n"
        "- **Do not upload real patient data containing PHI** to this demo deployment.\n"
        "- When connected to a live backend, processing is in-process (per `api_contract.md`) — "
        "no scan data leaves the host unless the backend's own integrations (e.g. report generation) are configured to do so.\n"
        "- AI-generated content is a drafting aid only and always requires physician review."
    )

st.markdown("---")
st.markdown("<div class='av-section-header'>Reset</div>", unsafe_allow_html=True)
st.caption("Clears the loaded patient, ROI selection, chat history, and notes — does not affect backend data.")
if st.button("⚠️ Reset application state", type="secondary"):
    st.session_state.clear()
    st.success("Application state cleared.")
    st.rerun()
