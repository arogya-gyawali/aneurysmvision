"""AneurysmVision — Streamlit entry point.

Run with:
    streamlit run frontend/app.py

This script only sets up page config, shared CSS, and navigation. Page
content lives in frontend/pages/ — one module per item in the product's
workflow (Home, MRI, Upload, Patient Overview, ROI Selection, 3D
Visualization, Cross-Sections, Measurements, AI Summary, Report & Export,
Settings & Help).
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from frontend.components import layout

st.set_page_config(
    page_title="AneurysmVision",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
layout.inject_css()

# Paths must be relative to this file (frontend/), not absolute Path objects —
# Streamlit resolves st.Page paths as main_script_parent / page.
nav = st.navigation(
    [
        st.Page("pages/1_home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/mri_overview.py", title="MRI", icon="🧲"),
        st.Page("pages/2_upload.py", title="Upload", icon="📤"),
        st.Page("pages/3_patient_overview.py", title="Patient Overview", icon="🧾"),
        st.Page("pages/4_roi_selection.py", title="ROI Selection", icon="🎯"),
        st.Page("pages/5_3d_visualization.py", title="3D Visualization", icon="🧠"),
        st.Page("pages/6_cross_sections.py", title="Cross-Sections", icon="🩻"),
        st.Page("pages/7_measurements.py", title="Measurements", icon="📏"),
        st.Page("pages/8_ai_summary.py", title="AI Summary", icon="🤖"),
        st.Page("pages/9_report_export.py", title="Report & Export", icon="📄"),
        st.Page("pages/10_settings_help.py", title="Settings & Help", icon="⚙️"),
    ]
)
nav.run()
