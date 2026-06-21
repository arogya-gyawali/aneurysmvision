"""Composes and exports the final clinical hand-off report.

Builds a Markdown report from the full `AnalysisResult`, always available
for download. Also offers a PDF export when `fpdf2` is installed — this
is an optional dependency so the page degrades gracefully without it.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from frontend.utils import compute_risk, finding_label, location_label


def build_markdown_report(result: dict[str, Any]) -> str:
    study = result.get("study", {}) or {}
    bids = study.get("bids") or {}
    report = result.get("report") or {}
    aneurysms = result.get("aneurysms", [])

    lines = [
        "# AneurysmVision — Clinical Report",
        "",
        f"**Job ID:** {result.get('job_id', '—')}  ",
        f"**Patient:** sub-{bids.get('sub', '—')}"
        + (f", ses-{bids.get('ses')}" if bids.get("ses") else "") + "  ",
        f"**Modality:** {study.get('modality', '—')}  ",
        f"**Status:** {result.get('status', '—')}  ",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "> AI-assisted draft. Requires physician review before clinical use.",
        "",
        f"## Findings ({len(aneurysms)})",
        "",
    ]
    for finding in aneurysms:
        bio = finding.get("biomarkers", {}) or {}
        risk = compute_risk(bio)
        lines += [
            f"### {finding_label(finding)}",
            f"- Location: {location_label(finding.get('location', ''))} — {finding.get('location_detail', '—')}",
            f"- Confidence: {finding.get('confidence', 0) * 100:.0f}%",
            f"- Risk: {risk.level} ({risk.score}/100)",
            f"- Volume: {bio.get('volume_mm3', '—')} mm³, Max diameter: {bio.get('max_diameter_mm', '—')} mm, "
            f"Neck width: {bio.get('neck_width_mm', '—')} mm, Aspect ratio: {bio.get('aspect_ratio', '—')}",
            "",
        ]

    if report:
        lines += [
            "## AI Clinical Summary",
            "",
            report.get("summary", ""),
            "",
            "**Findings**",
        ]
        lines += [f"- {item}" for item in report.get("findings", [])]
        lines += ["", "**Recommendations**"]
        lines += [f"- {item}" for item in report.get("recommendations", [])]
        lines += ["", f"_Model: {report.get('model', '—')} · Generated: {report.get('generated_at', '—')}_"]

    return "\n".join(lines)


def _build_pdf(markdown_text: str) -> bytes | None:
    try:
        from fpdf import FPDF
    except ImportError:
        return None
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    replacements = {"³": "3", "—": "-", "·": "-", "–": "-", "✅": "", "⚠️": "!", "🎯": ""}
    for raw_line in markdown_text.splitlines():
        line = raw_line.replace("**", "").replace("# ", "").replace("> ", "").replace("_", "")
        for old, new in replacements.items():
            line = line.replace(old, new)
        line = line.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, line or " ", new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


def render(result: dict[str, Any]) -> None:
    st.markdown("<div class='av-section-header'>Export Report</div>", unsafe_allow_html=True)

    markdown_text = build_markdown_report(result)
    job_id = result.get("job_id", "report")

    with st.expander("Preview report", expanded=True):
        st.markdown(markdown_text)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Download Markdown", data=markdown_text, file_name=f"{job_id}_report.md",
            mime="text/markdown", width="stretch",
        )
    with c2:
        st.download_button(
            "Download structured data (JSON)", data=json.dumps(result, default=str, indent=2),
            file_name=f"{job_id}_data.json", mime="application/json", width="stretch",
        )
    with c3:
        pdf_bytes = _build_pdf(markdown_text)
        if pdf_bytes:
            st.download_button(
                "Download PDF", data=pdf_bytes, file_name=f"{job_id}_report.pdf",
                mime="application/pdf", width="stretch",
            )
        else:
            st.button("Download PDF", disabled=True, width="stretch", help="Install `fpdf2` to enable PDF export.")

    st.caption("To export a 3D viewer snapshot, use the camera icon in the chart's toolbar on the 3D Visualization page.")
