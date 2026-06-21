"""Home / Landing — upload and the entire read happens automatically, right here.

No step buttons, no clicking through separate pages: dropping a scan
triggers detection, measurements, the labeled 3D vessel map, and the AI
summary in one continuous scroll.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import auto_report, intake, layout
from frontend.components.mock_sessions import recent_sessions

result = layout.require_result()
layout.top_bar(result, "Home")

st.markdown(
    """
    <div style="padding: 0.5rem 0 0.5rem 0;">
        <h1 class="av-gradient-text" style="margin-bottom:0.25rem; font-weight:800;">Vascular review, without the busywork</h1>
        <p style="color:var(--av-text-secondary); font-size:1.05rem; max-width:680px;">
            Drop a patient's scan below — detection, 3D reconstruction with every
            vessel labeled, measurements, and an AI-drafted summary all run
            automatically, right here, with no extra clicks.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

intake.render(key_prefix="home")

st.markdown("---")

result = layout.require_result()
if result:
    auto_report.render(result)
else:
    layout.empty_state(
        "🧠",
        "No patient loaded yet",
        "Drop a BIDS-named scan or load the demo patient above — the full read will appear here automatically.",
    )

st.markdown("---")
st.markdown(
    "<div class='av-section-header'>Recent Sessions " + layout.mock_tag("Demo data") + "</div>",
    unsafe_allow_html=True,
)
status_colors = {"completed": "#16a34a", "failed": "#dc2626", "running": "#2563eb"}
session_cols = st.columns(3)
for col, sess in zip(session_cols, recent_sessions()):
    color = status_colors.get(sess["status"], "#6b7280")
    with col:
        st.markdown(
            f"""
            <div class="av-card">
                <div class="av-card-label">{sess['patient']} · {sess['date']}</div>
                <div class="av-card-value" style="font-size:1.1rem;">{sess['findings']}</div>
                <span class='av-badge' style='background:{color}1a;color:{color};margin-top:0.5rem;'>{sess['status'].upper()}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption("AneurysmVision v0.1.0 · Frontend built against backend/api_contract.md")
