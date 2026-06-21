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

_PAGES_DIR = Path(__file__).parent / "pages"

nav = st.navigation(
    [
        st.Page(_PAGES_DIR / "1_home.py", title="Home", icon="🏠", default=True),
        st.Page(_PAGES_DIR / "mri_overview.py", title="MRI", icon="🧲"),
        st.Page(_PAGES_DIR / "2_upload.py", title="Upload", icon="📤"),
        st.Page(_PAGES_DIR / "3_patient_overview.py", title="Patient Overview", icon="🧾"),
        st.Page(_PAGES_DIR / "4_roi_selection.py", title="ROI Selection", icon="🎯"),
        st.Page(_PAGES_DIR / "5_3d_visualization.py", title="3D Visualization", icon="🧠"),
        st.Page(_PAGES_DIR / "6_cross_sections.py", title="Cross-Sections", icon="🩻"),
        st.Page(_PAGES_DIR / "7_measurements.py", title="Measurements", icon="📏"),
        st.Page(_PAGES_DIR / "8_ai_summary.py", title="AI Summary", icon="🤖"),
        st.Page(_PAGES_DIR / "9_report_export.py", title="Report & Export", icon="📄"),
        st.Page(_PAGES_DIR / "10_settings_help.py", title="Settings & Help", icon="⚙️"),
    ]
)
nav.run()
