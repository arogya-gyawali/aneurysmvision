"""AneurysmVision — Streamlit entry point.

Run with:
    streamlit run frontend/app.py

This script only sets up page config, shared CSS, and navigation.
Navigation is intentionally minimal: Home runs the entire pipeline
automatically and renders every output inline (patient info, labeled 3D
vessel map, cross-sections, measurements, AI summary, export, pipeline
detail), so there's no separate page per workflow step to click through.
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
_theme = layout.theme_toggle()
layout.inject_css(_theme)

# Paths must be relative to this file (frontend/), not absolute Path objects —
# Streamlit resolves st.Page paths as main_script_parent / page.
nav = st.navigation(
    [
        st.Page("pages/1_home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/mri_overview.py", title="MRI", icon="🧲"),
        st.Page("pages/10_settings_help.py", title="Settings & Help", icon="⚙️"),
    ]
)
nav.run()
