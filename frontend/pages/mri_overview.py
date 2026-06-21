"""MRI — single-page overview of what MRI is and what this platform's
AI-assisted analysis covers, plus a fast path straight into the real
brain/aneurysm workflow.

Deliberately one continuous page (no internal tabs/sub-pages) so a
clinician can read top to bottom and jump straight into the workflow —
not click through a maze of sub-screens.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend import data_client as dc
from frontend.components import layout

result = layout.require_result()
layout.top_bar(result, "MRI")

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"], .stApp, .main, .block-container { background: transparent !important; }
    .av-mri-bg {
        position: fixed; inset: 0; z-index: -1; overflow: hidden;
        pointer-events: none; background: #f8fafc;
    }
    .av-mri-bg .ring {
        position: absolute; top: 50%; left: 50%; filter: grayscale(1);
        transform: translate(-50%, -50%);
    }
    .av-mri-bg .ring.outer { font-size: 34rem; opacity: 0.05; animation: av-spin-cw 40s linear infinite; }
    .av-mri-bg .ring.inner { font-size: 19rem; opacity: 0.045; animation: av-spin-ccw 24s linear infinite; }
    @keyframes av-spin-cw  { from { transform: translate(-50%,-50%) rotate(0deg); }   to { transform: translate(-50%,-50%) rotate(360deg); } }
    @keyframes av-spin-ccw { from { transform: translate(-50%,-50%) rotate(360deg); } to { transform: translate(-50%,-50%) rotate(0deg); } }
    .av-mri-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:1.1rem 1.25rem;
                   box-shadow:0 1px 3px rgba(15,23,42,0.06); height:100%; }
    .av-mri-card h4 { margin:0 0 0.35rem 0; font-size:0.98rem; color:#0f172a; }
    .av-mri-card p { margin:0; font-size:0.82rem; color:#64748b; line-height:1.4; }
    .av-mri-soon { background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px; padding:0.9rem 1.1rem; }
    </style>
    <div class="av-mri-bg"><div class="ring outer">🧠</div><div class="ring inner">🧠</div></div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="padding: 0.5rem 0 0.25rem 0;">
        <h1 style="margin-bottom:0.25rem;">What is MRI?</h1>
        <p style="color:#475569; font-size:1.05rem; max-width:760px;">
            Magnetic Resonance Imaging (MRI) uses strong magnetic fields and radio waves —
            no ionizing radiation — to produce detailed cross-sectional images of soft tissue,
            organs, and blood vessels. Different acquisition sequences (T1, T2, FLAIR, DWI, TOF, etc.)
            each highlight different tissue properties, which is why MRI is the modality of choice
            for detailed brain, spine, and joint evaluation — including the TOF-MRA sequence this
            platform analyzes for cerebral aneurysms.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

quick_l, quick_r = st.columns(2)
with quick_l:
    if st.button("⚡ Start Brain Aneurysm Analysis (demo patient)", type="primary", use_container_width=True):
        st.session_state["av_result"] = dc.get_sample_result()
        st.session_state.pop("av_selected_id", None)
        st.switch_page("pages/4_roi_selection.py")
with quick_r:
    if st.button("📤 Upload a real scan instead", use_container_width=True):
        st.switch_page("pages/2_upload.py")

st.markdown("---")
st.markdown("<div class='av-section-header'>What AI-Assisted MRI Analysis Includes</div>", unsafe_allow_html=True)
overview_cards = [
    ("Multi-Sequence Analysis", "Reads across sequences (T1, T2, FLAIR, TOF, etc.) for a fuller picture than any single sequence alone."),
    ("Tissue Characterization", "Differentiates normal from abnormal tissue patterns to flag regions worth a closer look."),
    ("Rapid Processing", "Surfaces structured findings in a fraction of the time of a fully manual read."),
    ("Multi-Organ Compatibility", "The same underlying approach extends to brain, spine, joints, and beyond — brain is what's implemented today."),
]
cols = st.columns(4)
for col, (title, desc) in zip(cols, overview_cards):
    with col:
        st.markdown(f"<div class='av-mri-card'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

st.markdown("")
st.markdown("<div class='av-section-header'>Key Capabilities</div>", unsafe_allow_html=True)
feature_cards = [
    ("Advanced Segmentation", "Delineates structures precisely enough to support reliable measurements."),
    ("Contrast Enhancement Analysis", "Assesses perfusion and lesion characteristics on contrast-enhanced scans."),
    ("Diffusion Tensor Imaging (DTI)", "Visualizes white-matter tracts for neurological assessment."),
    ("Longitudinal Comparison", "Tracks change against prior scans to monitor progression or treatment response."),
    ("Quantitative Measurements", "Volumetric and dimensional measurements to support treatment planning."),
    ("Multi-Planar Reconstruction", "Axial, sagittal, and coronal views from a single acquisition."),
]
for row_start in range(0, len(feature_cards), 3):
    row_cols = st.columns(3)
    for col, (title, desc) in zip(row_cols, feature_cards[row_start:row_start + 3]):
        with col:
            st.markdown(f"<div class='av-mri-card'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)
    st.markdown("")

st.markdown("---")
st.markdown("<div class='av-section-header'>Specialized Analysis</div>", unsafe_allow_html=True)

brain_l, brain_r = st.columns([3, 2])
with brain_l:
    st.markdown(
        """
        <div class="av-mri-card" style="border-top:4px solid #2563eb;">
            <h4 style="font-size:1.1rem;">🧠 Brain MRI — available now</h4>
            <p>
                AI-powered brain MRI interpretation, with cerebral aneurysm detection on TOF-MRA
                as this platform's current capability. Broader brain analysis is the active roadmap.
            </p>
            <ul style="color:#64748b; font-size:0.85rem; margin:0.5rem 0 0 1rem; padding:0;">
                <li><strong>Vascular / aneurysm detection</strong> — implemented, see the workflow below</li>
                <li>White matter analysis — roadmap</li>
                <li>Tumor detection — roadmap</li>
                <li>Stroke assessment — roadmap</li>
                <li>Brain structure review — roadmap</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
with brain_r:
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("Explore Brain / Aneurysm Workflow →", type="primary", use_container_width=True):
        if not result:
            st.session_state["av_result"] = dc.get_sample_result()
        st.switch_page("pages/5_3d_visualization.py")
    st.caption("Jumps straight into 3D visualization with the active (or demo) patient — no extra clicks.")

st.markdown("")
soon_cols = st.columns(3)
for col, (name, icon) in zip(soon_cols, [("Knee MRI", "🦵"), ("Spine MRI", "🦴"), ("Shoulder MRI", "💪")]):
    with col:
        st.markdown(
            f"""
            <div class="av-mri-soon">
                <strong>{icon} {name}</strong>
                <span class="av-mock-tag" style="margin-left:0.5rem;">Coming soon</span>
                <p style="margin:0.4rem 0 0 0; font-size:0.78rem; color:#94a3b8;">Not yet implemented in this platform.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    "This page is an informational overview of MRI and the analysis approach this platform is built on. "
    "Only brain TOF-MRA aneurysm detection is a live, working capability today — everything else above "
    "describes the broader direction, not current functionality."
)
