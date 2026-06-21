"""Patient Upload — load a BIDS-structured scan and run the pipeline."""

from __future__ import annotations

import os
import re
import sys
import tempfile
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend import data_client as dc
from frontend.components import layout

result = layout.require_result()
layout.top_bar(result, "Upload")

st.markdown("<div class='av-section-header'>Upload Patient Scan</div>", unsafe_allow_html=True)
st.caption(
    "Upload a single TOF-MRA NIfTI file (BIDS-named, e.g. `sub-042_ses-01_acq-3d_tof_run-1_angio.nii.gz`). "
    "Full folder/zip ingestion is a backend roadmap item — for now this covers the single-file path the contract supports today."
)

uploaded = st.file_uploader("NIfTI file", type=["gz", "nii"], accept_multiple_files=False)

_BIDS_RE = re.compile(
    r"sub-(?P<sub>[a-zA-Z0-9]+)(?:_ses-(?P<ses>[a-zA-Z0-9]+))?.*?(?P<suffix>angio|MRA|swi|T1w)\.(?P<ext>nii(?:\.gz)?)$"
)

if uploaded is not None:
    match = _BIDS_RE.search(uploaded.name)

    progress = st.progress(0, text="Scanning file…")
    for pct, msg in [(35, "Scanning file…"), (70, "Validating BIDS naming…"), (100, "Ready")]:
        time.sleep(0.15)
        progress.progress(pct, text=msg)

    st.markdown("**File**")
    st.write(f"`{uploaded.name}` — {uploaded.size / 1_000_000:.1f} MB")

    if match:
        st.success("BIDS entities parsed successfully from filename.", icon="✅")
        meta = match.groupdict()
    else:
        st.warning(
            "Could not confidently parse BIDS entities from the filename. "
            "You can still proceed — fill in the subject ID manually below.",
            icon="⚠️",
        )
        meta = {"sub": "", "ses": "", "suffix": "angio", "ext": "nii.gz"}

    st.markdown("**Patient metadata**")
    c1, c2, c3 = st.columns(3)
    subject = c1.text_input("Subject ID", value=meta.get("sub") or "")
    session = c2.text_input("Session (optional)", value=meta.get("ses") or "")
    c3.text_input("Suffix", value=meta.get("suffix") or "angio", disabled=True)

    gen_report = st.checkbox("Generate AI report", value=True)
    gen_mesh = st.checkbox("Generate mesh", value=True)

    run_disabled = not subject
    if run_disabled:
        st.caption("Enter a subject ID to enable analysis.")

    if st.button("Run Analysis", type="primary", disabled=run_disabled, width="stretch"):
        suffix = ".nii.gz" if uploaded.name.endswith(".gz") else ".nii"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        with st.spinner("Running pipeline… falling back to demo data for stages not yet implemented."):
            st.session_state["av_result"] = dc.run_analysis(
                nifti_path=tmp_path, generate_report=gen_report, generate_mesh=gen_mesh,
            )
        os.unlink(tmp_path)
        st.session_state.pop("av_selected_id", None)
        st.success("Analysis complete.")
        st.rerun()

st.markdown("---")
st.markdown("<div class='av-section-header'>Or Skip Straight to a Demo Patient</div>", unsafe_allow_html=True)
if st.button("🧪 Load Demo Patient (sample_output.json)", width="stretch"):
    st.session_state["av_result"] = dc.get_sample_result()
    st.session_state.pop("av_selected_id", None)
    st.rerun()

result = layout.require_result()
if result:
    st.markdown("---")
    st.success(f"Active patient: **sub-{(result.get('study', {}).get('bids') or {}).get('sub', '—')}** ({result.get('status')})")
    if st.button("Continue to Patient Overview →", type="primary", width="stretch"):
        st.switch_page("pages/3_patient_overview.py")
