"""AneurysmVision — Dashboard page.

Shows study metadata, per-aneurysm biomarkers, risk assessment,
and a placeholder 3-D visualisation (real GLB viewer pending stage 3).
"""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import frontend.data_client as dc
from frontend.utils import compute_risk, finding_label, format_stage_status, location_label


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sample_banner() -> None:
    st.info(
        "**Demo mode** — showing sample data from `backend/sample_output.json`. "
        "Upload a real NIfTI file below to run the live pipeline.",
        icon="ℹ️",
    )


def _risk_gauge(risk_score: int, risk_level: str, risk_color: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": f"Risk: {risk_level}", "font": {"color": risk_color, "size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#6b7280"},
            "bar": {"color": risk_color, "thickness": 0.3},
            "bgcolor": "#1f2937",
            "bordercolor": "#374151",
            "steps": [
                {"range": [0, 20],  "color": "#14532d"},
                {"range": [20, 45], "color": "#713f12"},
                {"range": [45, 70], "color": "#7c2d12"},
                {"range": [70, 100],"color": "#450a0a"},
            ],
            "threshold": {"line": {"color": risk_color, "width": 4}, "thickness": 0.75, "value": risk_score},
        },
        number={"font": {"color": "#f9fafb", "size": 32}, "suffix": " / 100"},
    ))
    fig.update_layout(
        paper_bgcolor="#111827",
        font_color="#f9fafb",
        height=260,
        margin={"t": 30, "b": 10, "l": 20, "r": 20},
    )
    return fig


def _placeholder_3d(finding: dict) -> go.Figure:
    """Simple sphere placeholder until stage-3 GLB rendering is ready."""
    import math
    bio = finding.get("biomarkers", {})
    r = (bio.get("max_diameter_mm", 4.0) / 2.0)
    cx, cy, cz = finding.get("centroid_mm", (0, 0, 0))

    N = 30
    phi = [math.pi * i / N for i in range(N + 1)]
    theta = [2 * math.pi * j / N for j in range(N + 1)]

    xs, ys, zs = [], [], []
    for p in phi:
        for t in theta:
            xs.append(cx + r * math.sin(p) * math.cos(t))
            ys.append(cy + r * math.sin(p) * math.sin(t))
            zs.append(cz + r * math.cos(p))

    fig = go.Figure(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers",
        marker={"size": 2, "color": zs, "colorscale": "Plasma", "opacity": 0.6},
    ))
    fig.update_layout(
        paper_bgcolor="#111827",
        scene={"bgcolor": "#111827", "xaxis": {"color": "#6b7280"}, "yaxis": {"color": "#6b7280"}, "zaxis": {"color": "#6b7280"}},
        margin={"t": 10, "b": 10, "l": 0, "r": 0},
        height=380,
        title={"text": "3D Position (GLB mesh viewer — Stage 3)", "font": {"color": "#6b7280", "size": 12}},
    )
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def show() -> None:
    st.title("Aneurysm Dashboard")

    # ---- Input / run controls ----
    with st.expander("Run analysis", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nifti_file = st.file_uploader("Upload NIfTI (.nii / .nii.gz)", type=["nii", "gz"])
        with col2:
            gen_report = st.checkbox("Generate report", value=True)
            gen_mesh   = st.checkbox("Generate mesh",   value=True)
        run_btn = st.button("Run pipeline", type="primary", use_container_width=True)

    # ---- Fetch / cache result ----
    if "av_result" not in st.session_state or run_btn:
        if nifti_file and run_btn:
            import tempfile, os
            suffix = ".nii.gz" if nifti_file.name.endswith(".gz") else ".nii"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(nifti_file.read())
                tmp_path = tmp.name
            with st.spinner("Running pipeline…"):
                st.session_state["av_result"] = dc.run_analysis(
                    nifti_path=tmp_path,
                    generate_report=gen_report,
                    generate_mesh=gen_mesh,
                )
            os.unlink(tmp_path)
        else:
            st.session_state["av_result"] = dc.get_sample_result()

    result = st.session_state["av_result"]

    if dc.is_demo(result):
        _sample_banner()

    # ---- Study metadata strip ----
    study = dc.get_study(result)
    bids  = study.get("bids") or {}
    quality = study.get("quality") or {}
    voxels  = study.get("voxel_dimensions_mm") or {}

    st.subheader("Study")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Subject",  f"sub-{bids.get('sub', '—')}")
    c2.metric("Session",  f"ses-{bids.get('ses', '—')}" if bids.get("ses") else "—")
    c3.metric("Modality", study.get("modality", "TOF-MRA"))
    qc_pass = quality.get("passed_qc")
    c4.metric("QC", "✓ Passed" if qc_pass else ("✗ Failed" if qc_pass is False else "—"))

    if quality:
        qc1, qc2, qc3 = st.columns(3)
        qc1.metric("SNR",      f"{quality.get('snr', '—')}")
        qc2.metric("CNR",      f"{quality.get('contrast_to_noise', '—')}")
        qc3.metric("Motion",   f"{quality.get('motion_score', '—')}")

    st.divider()

    # ---- Aneurysm findings ----
    aneurysms = dc.aneurysm_list(result)
    n = len(aneurysms)

    if n == 0:
        st.success("No aneurysms detected in this study.")
        return

    st.subheader(f"Detected Aneurysms: {n}")

    labels = [finding_label(a) for a in aneurysms]
    selected_label = st.selectbox("Select aneurysm", labels, key="dash_sel")
    finding = aneurysms[labels.index(selected_label)]
    bio = finding.get("biomarkers", {})

    risk = compute_risk(bio)
    st.session_state["av_risk"] = risk  # used by sidebar badge

    # ---- Two-column layout: gauge + 3D ----
    left, right = st.columns([1, 2])
    with left:
        st.plotly_chart(_risk_gauge(risk.score, risk.level, risk.color), use_container_width=True)
        st.markdown(f"**Confidence:** {finding.get('confidence', 0)*100:.0f}%")
        st.markdown(f"**Location:** {location_label(str(finding.get('location', '—')))}")
        st.markdown(f"**Detail:** {finding.get('location_detail', '—')}")
        if risk.rationale:
            with st.expander("Risk factors"):
                for r_item in risk.rationale:
                    st.markdown(f"- {r_item}")
    with right:
        st.plotly_chart(_placeholder_3d(finding), use_container_width=True)

    # ---- Biomarker table ----
    st.subheader("Biomarkers")
    bm_rows = {
        "Volume (mm³)":            bio.get("volume_mm3"),
        "Max Diameter (mm)":       bio.get("max_diameter_mm"),
        "Neck Width (mm)":         bio.get("neck_width_mm"),
        "Dome Height (mm)":        bio.get("dome_height_mm"),
        "Aspect Ratio":            bio.get("aspect_ratio"),
        "Size Ratio":              bio.get("size_ratio"),
        "Irregularity Index":      bio.get("irregularity_index"),
    }
    import pandas as pd
    df = pd.DataFrame(
        [(k, f"{v:.3f}" if isinstance(v, float) else str(v)) for k, v in bm_rows.items() if v is not None],
        columns=["Metric", "Value"],
    )
    st.dataframe(df, hide_index=True, use_container_width=True)

    # ---- Mesh info ----
    mesh = finding.get("mesh")
    if mesh:
        st.caption(
            f"Mesh: {mesh.get('format','?').upper()} · "
            f"{mesh.get('vertex_count','?'):,} vertices · "
            f"{mesh.get('face_count','?'):,} faces · "
            f"`{mesh.get('path','?')}`"
        )

    # ---- Pipeline stages ----
    stages = dc.get_stages(result)
    if stages:
        with st.expander("Pipeline stages"):
            for s in stages:
                icon, color = format_stage_status(s)
                dur = f"{s.get('duration_ms','?')} ms" if s.get("duration_ms") else ""
                err = f" — {s.get('error')}" if s.get("error") else ""
                msg = f" — {s.get('message')}" if s.get("message") else ""
                st.markdown(
                    f"<span style='color:{color}'>{icon}</span> **{s['name']}** {dur}{msg}{err}",
                    unsafe_allow_html=True,
                )


show()
