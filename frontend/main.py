"""AneurysmVision — Streamlit entry point (frontend).

Run with:
    streamlit run frontend/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

import frontend.data_client as dc
from frontend.utils import compute_risk

st.set_page_config(
    page_title="AneurysmVision",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Sidebar ----
with st.sidebar:
    st.image("https://via.placeholder.com/160x40/3b82f6/ffffff?text=AneurysmVision", use_column_width=True)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Reports", "Voice Copilot"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Backend status
    alive = dc.backend_alive()
    st.markdown(
        f"**Backend:** {'🟢 Live' if alive else '🟡 Demo mode'}",
        help="Live = in-process pipeline importable. Demo = sample_output.json.",
    )

    # Active risk badge from last dashboard load
    risk = st.session_state.get("av_risk")
    if risk:
        st.markdown(
            f"**Active risk:** <span style='color:{risk.color};font-weight:bold'>"
            f"{risk.level} ({risk.score}/100)</span>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("AneurysmVision v0.1.0")

# ---- Page routing ----
_base = Path(__file__).parent / "pages"

if page == "Dashboard":
    exec(open(_base / "dashboard.py").read())   # noqa: S102
elif page == "Reports":
    exec(open(_base / "reports.py").read())     # noqa: S102
elif page == "Voice Copilot":
    exec(open(_base / "voice.py").read())       # noqa: S102
