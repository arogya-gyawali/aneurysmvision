"""MRI — single-page overview of what MRI is and what this platform's
AI-assisted analysis covers, plus a fast path straight into the real
brain/aneurysm workflow.

Visual design on this page intentionally departs from the rest of the
app: it mirrors a public-hospital-system look (deep navy + white,
generous whitespace, equal-weight icon grid, understated text-link
CTAs) rather than the app's clinical-dashboard styling — this page is
informational/front-door, not a working tool screen. The shared
animated background from layout.py is suppressed here for that reason.

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
    /* Suppress the app-wide animated background + gradient topbar on this
       page only — institutional sites read calm, not flashy. */
    [data-testid="stAppViewContainer"], .stApp, .main, .block-container {
        background: #f4f6f9 !important;
    }
    .av-topbar { background: linear-gradient(120deg, #0b2f5c 0%, #14467f 100%) !important; }

    .nyhh-eyebrow {
        text-transform: uppercase; letter-spacing: .12em; font-size: 0.72rem;
        font-weight: 700; color: #2f6fb3; margin-bottom: 0.4rem;
    }
    .nyhh-hero {
        background: linear-gradient(120deg, #0b2f5c 0%, #14467f 100%);
        border-radius: 16px; padding: 2.5rem 2.5rem 2rem; color: #ffffff; margin-bottom: 1.5rem;
    }
    .nyhh-hero h1 { color: #ffffff; font-weight: 800; margin: 0 0 0.6rem 0; font-size: 2.1rem; }
    .nyhh-hero p { color: #cbd8ea; font-size: 1.02rem; max-width: 700px; line-height: 1.55; margin: 0; }

    .nyhh-action {
        background: #ffffff; border-radius: 12px; padding: 1.1rem 1rem; text-align: center;
        height: 100%; border: 1px solid #e2e8f0;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .nyhh-action:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(11,47,92,0.12); }
    .nyhh-action .icon-circle {
        width: 48px; height: 48px; border-radius: 50%; background: #eaf1fb; color: #0b2f5c;
        display: flex; align-items: center; justify-content: center; font-size: 1.4rem;
        margin: 0 auto 0.6rem auto;
    }
    .nyhh-action h5 { margin: 0 0 0.25rem 0; font-size: 0.95rem; color: #0b2f5c; }
    .nyhh-action p { margin: 0; font-size: 0.78rem; color: #64748b; }

    .nyhh-section { padding: 1.75rem 0 0.5rem 0; }
    .nyhh-section h2 { color: #0b2f5c; font-weight: 800; font-size: 1.5rem; margin: 0 0 0.25rem 0; }
    .nyhh-section .sub { color: #64748b; font-size: 0.92rem; margin-bottom: 1.25rem; }

    .nyhh-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #2f6fb3;
        border-radius: 10px; padding: 1.1rem 1.25rem; height: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .nyhh-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(11,47,92,0.10); }
    .nyhh-card h4 { margin: 0 0 0.35rem 0; font-size: 0.98rem; color: #0b2f5c; }
    .nyhh-card p { margin: 0; font-size: 0.83rem; color: #475569; line-height: 1.45; }

    .nyhh-feature { border-left-color: #0d9488; }
    .nyhh-readmore { color: #2f6fb3; font-size: 0.8rem; font-weight: 700; text-decoration: none; }

    .nyhh-soon {
        background: #eef1f5; border: 1px dashed #c7d2e0; border-radius: 10px; padding: 0.9rem 1.1rem;
    }
    .nyhh-soon .tag {
        display: inline-block; background: #dbe6f3; color: #0b2f5c; border-radius: 6px;
        padding: 0.1rem 0.5rem; font-size: 0.66rem; font-weight: 700; letter-spacing: .03em;
        text-transform: uppercase; margin-left: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="nyhh-hero">
        <div class="nyhh-eyebrow" style="color:#9fc1e8;">Imaging &amp; Diagnostics</div>
        <h1>MRI</h1>
        <p>
            Magnetic Resonance Imaging (MRI) uses strong magnetic fields and radio waves —
            no ionizing radiation — to produce detailed cross-sectional images of soft tissue,
            organs, and blood vessels. Different acquisition sequences (T1, T2, FLAIR, DWI, TOF, etc.)
            each highlight different tissue properties, which is why MRI is the modality of choice for
            detailed brain, spine, and joint evaluation — including the TOF-MRA sequence this platform
            analyzes for cerebral aneurysms.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

action_cols = st.columns(4)
actions = [
    ("🧪", "Demo Patient", "Load sample data", "demo"),
    ("📤", "Upload Scan", "Bring your own BIDS file", "pages/2_upload.py"),
    ("🎯", "ROI Selection", "Review detected regions", "pages/4_roi_selection.py"),
    ("🧠", "3D Visualization", "Explore the reconstruction", "pages/5_3d_visualization.py"),
]
for col, (icon, title, desc, target) in zip(action_cols, actions):
    with col:
        st.markdown(
            f"""
            <div class="nyhh-action">
                <div class="icon-circle">{icon}</div>
                <h5>{title}</h5>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open →", key=f"act_{title}", use_container_width=True):
            if target == "demo":
                st.session_state["av_result"] = dc.get_sample_result()
                st.session_state.pop("av_selected_id", None)
                st.rerun()
            else:
                if not result and target != "pages/2_upload.py":
                    st.session_state["av_result"] = dc.get_sample_result()
                st.switch_page(target)

st.markdown(
    """
    <div class="nyhh-section">
        <h2>What AI-Assisted MRI Analysis Includes</h2>
        <div class="sub">A platform-level view of how the analysis approach reads an MRI study.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
overview_cards = [
    ("Multi-Sequence Analysis", "Reads across sequences (T1, T2, FLAIR, TOF, etc.) for a fuller picture than any single sequence alone."),
    ("Tissue Characterization", "Differentiates normal from abnormal tissue patterns to flag regions worth a closer look."),
    ("Rapid Processing", "Surfaces structured findings in a fraction of the time of a fully manual read."),
    ("Multi-Organ Compatibility", "The same underlying approach extends to brain, spine, joints, and beyond — brain is what's implemented today."),
]
cols = st.columns(4)
for col, (title, desc) in zip(cols, overview_cards):
    with col:
        st.markdown(f"<div class='nyhh-card'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="nyhh-section">
        <h2>Key Capabilities</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
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
            st.markdown(f"<div class='nyhh-card nyhh-feature'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)
    st.markdown("")

st.markdown(
    """
    <div class="nyhh-section">
        <h2>Specialized Analysis</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

brain_l, brain_r = st.columns([3, 2])
with brain_l:
    st.markdown(
        """
        <div class="nyhh-card" style="border-left-width:6px;">
            <h4 style="font-size:1.15rem;">Brain MRI — available now</h4>
            <p>
                AI-powered brain MRI interpretation, with cerebral aneurysm detection on TOF-MRA
                as this platform's current capability. Broader brain analysis is the active roadmap.
            </p>
            <ul style="color:#475569; font-size:0.85rem; margin:0.6rem 0 0 1.1rem; padding:0;">
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
for col, name in zip(soon_cols, ["Knee MRI", "Spine MRI", "Shoulder MRI"]):
    with col:
        st.markdown(
            f"""
            <div class="nyhh-soon">
                <strong>{name}</strong><span class="tag">Coming soon</span>
                <p style="margin:0.4rem 0 0 0; font-size:0.78rem; color:#64748b;">Not yet implemented in this platform.</p>
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
