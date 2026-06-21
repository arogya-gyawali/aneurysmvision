"""AI clinical report panel, rendered from `ReportDraft` (api_contract.md).

Language stays deliberately cautious ("suggests", "may indicate" style is
the backend's responsibility to generate; this panel never rewrites
wording, it only displays it with a review disclaimer).
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import streamlit as st


def _format_timestamp(value: str) -> str:
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(value)


def render(report: dict[str, Any] | None, job_id: str, is_demo: bool = False) -> None:
    st.markdown("<div class='av-section-header'>AI Clinical Summary</div>", unsafe_allow_html=True)
    st.warning(
        "AI-assisted draft. **Requires physician review** before use in clinical decision-making.",
        icon="⚠️",
    )

    if not report:
        st.info("No report available for this job. Enable 'Generate report' when running the pipeline.")
        return

    st.markdown("**Summary**")
    st.write(report.get("summary", ""))

    findings = report.get("findings", [])
    if findings:
        st.markdown("**Findings**")
        for item in findings:
            st.markdown(f"- {item}")

    recs = report.get("recommendations", [])
    if recs:
        st.markdown("**Recommendations**")
        for item in recs:
            st.markdown(f"- {item}")

    meta1, meta2 = st.columns(2)
    meta1.caption(f"Model: `{report.get('model', '—')}`")
    meta2.caption(f"Generated: {_format_timestamp(report.get('generated_at', '—'))}")

    st.download_button(
        "Download report (JSON)",
        data=json.dumps(report, default=str, indent=2),
        file_name=f"{job_id}_report.json",
        mime="application/json",
        width="content",
    )
