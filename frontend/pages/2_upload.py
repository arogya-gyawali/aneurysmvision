"""Patient Upload — drop a BIDS-structured scan and the pipeline runs
automatically. The doctor only clicks something manually when the
patient ID can't be auto-detected from the filename.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend import data_client as dc
from frontend.components import layout

result = layout.require_result()
layout.top_bar(result, "Upload")

st.markdown("<div class='av-section-header'>Upload Patient Scan</div>", unsafe_allow_html=True)
st.caption(
    "Drop a BIDS-named TOF-MRA NIfTI file (e.g. `sub-042_ses-01_acq-3d_tof_run-1_angio.nii.gz`) — "
    "analysis starts automatically as soon as the patient ID is recognized, no extra clicks needed."
)

uploaded = st.file_uploader("NIfTI file", type=["gz", "nii"], accept_multiple_files=False)

_BIDS_RE = re.compile(
    r"sub-(?P<sub>[a-zA-Z0-9]+)(?:_ses-(?P<ses>[a-zA-Z0-9]+))?.*?(?P<suffix>angio|MRA|swi|T1w)\.(?P<ext>nii(?:\.gz)?)$"
)


def _run_and_redirect(subject_id: str, session_id: str | None, gen_report: bool, gen_mesh: bool, sig: str) -> None:
    suffix = ".nii.gz" if uploaded.name.endswith(".gz") else ".nii"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    with st.spinner(f"Analyzing sub-{subject_id} automatically…"):
        st.session_state["av_result"] = dc.run_analysis(
            nifti_path=tmp_path, generate_report=gen_report, generate_mesh=gen_mesh,
        )
    os.unlink(tmp_path)
    st.session_state.pop("av_selected_id", None)
    st.session_state["av_last_upload_sig"] = sig
    st.toast(f"Analysis complete for sub-{subject_id} — opening patient overview", icon="✅")
    st.switch_page("pages/3_patient_overview.py")


if uploaded is not None:
    match = _BIDS_RE.search(uploaded.name)
    meta = match.groupdict() if match else {}
    upload_sig = f"{uploaded.name}:{uploaded.size}"
    already_processed = st.session_state.get("av_last_upload_sig") == upload_sig

    st.markdown("**File**")
    st.write(f"`{uploaded.name}` — {uploaded.size / 1_000_000:.1f} MB")

    gen_report, gen_mesh = st.columns(2)
    gen_report = gen_report.checkbox("Generate AI report", value=True)
    gen_mesh = gen_mesh.checkbox("Generate mesh", value=True)

    if match:
        sub, ses = meta.get("sub", ""), meta.get("ses")
        st.success(
            f"Patient identified automatically: **sub-{sub}**" + (f", ses-{ses}" if ses else ""),
            icon="✅",
        )
        if already_processed:
            st.info("Already analyzed — go to Patient Overview to view results.", icon="ℹ️")
            if st.button("Open Patient Overview →", type="primary", width="stretch"):
                st.switch_page("pages/3_patient_overview.py")
        else:
            _run_and_redirect(sub, ses, gen_report, gen_mesh, upload_sig)
    else:
        st.warning(
            "Couldn't auto-detect the patient ID from this filename — enter it below to start analysis.",
            icon="⚠️",
        )
        c1, c2 = st.columns(2)
        subject = c1.text_input("Subject ID")
        session = c2.text_input("Session (optional)")
        if st.button("Start Analysis", type="primary", disabled=not subject, width="stretch"):
            _run_and_redirect(subject, session or None, gen_report, gen_mesh, upload_sig)

st.markdown("---")
st.markdown("<div class='av-section-header'>Or Skip Straight to a Demo Patient</div>", unsafe_allow_html=True)
if st.button("🧪 Load Demo Patient (sample_output.json)", width="stretch"):
    st.session_state["av_result"] = dc.get_sample_result()
    st.session_state.pop("av_selected_id", None)
    st.switch_page("pages/3_patient_overview.py")
