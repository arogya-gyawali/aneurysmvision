"""Report / Export — final hand-off document."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import layout, report_export, status_panel

result = layout.require_result()
layout.top_bar(result, "Report & Export")

if not result:
    layout.empty_state(
        "📄", "No patient loaded", "Load a patient to generate an exportable report.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

report_export.render(result)

st.markdown("---")
status_panel.render(result.get("stages", []), result.get("metadata"), result.get("cache_key"))

if st.button("← Back to AI Summary", width="stretch"):
    st.switch_page("pages/8_ai_summary.py")
