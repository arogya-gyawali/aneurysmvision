"""AI Summary / Clinical Assistant."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.components import ai_chat, layout, report_panel
from frontend.utils import finding_label

result = layout.require_result()
layout.top_bar(result, "AI Summary")

if not result:
    layout.empty_state(
        "🤖", "No patient loaded", "Load a patient to generate an AI clinical summary.",
        cta_label="Go to Upload", cta_page="pages/2_upload.py",
    )
    st.stop()

aneurysms = result.get("aneurysms", [])
finding = None
if aneurysms:
    selected_id = st.session_state.get("av_selected_id") or aneurysms[0]["id"]
    labels = [finding_label(a) for a in aneurysms]
    ids = [a["id"] for a in aneurysms]
    idx = ids.index(selected_id) if selected_id in ids else 0
    chosen = st.selectbox("Finding context for follow-up questions", labels, index=idx)
    finding = aneurysms[labels.index(chosen)]
    st.session_state["av_selected_id"] = finding["id"]

report = result.get("report")

action_l, action_r = st.columns(2)
with action_l:
    if st.button("🔄 Regenerate summary", width="stretch", help="Re-runs report generation (falls back to the cached draft while the backend stage is a stub)."):
        from frontend import data_client as dc

        study = result.get("study", {}) or {}
        st.session_state["av_result"] = dc.run_analysis(nifti_path=study.get("nifti_path"), generate_report=True)
        st.rerun()
with action_r:
    if report:
        st.code(report.get("summary", ""), language=None)
        st.caption("Use the copy icon above to copy the summary.")

report_panel.render(report, result.get("job_id", "—"), is_demo=result.get("_source") == "sample")

st.markdown("---")
ai_chat.render(report, finding)

nav_l, nav_r = st.columns(2)
with nav_l:
    if st.button("← Back to Measurements", width="stretch"):
        st.switch_page("pages/7_measurements.py")
with nav_r:
    if st.button("Continue to Report & Export →", type="primary", width="stretch"):
        st.switch_page("pages/9_report_export.py")
