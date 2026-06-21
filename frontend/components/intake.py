"""Unified upload-and-go intake widget.

Drop a BIDS-named scan and analysis starts immediately — no separate
"Run" button, no page-to-page navigation. Manual subject entry only
appears as a fallback when the filename can't be auto-parsed (typing
into that field can't safely auto-trigger the pipeline on every
keystroke, so it gets one explicit "Start Analysis" click instead).
"""

from __future__ import annotations

import os
import re
import tempfile

import streamlit as st

from frontend import data_client as dc

_BIDS_RE = re.compile(
    r"sub-(?P<sub>[a-zA-Z0-9]+)(?:_ses-(?P<ses>[a-zA-Z0-9]+))?.*?(?P<suffix>angio|MRA|swi|T1w)\.(?P<ext>nii(?:\.gz)?)$"
)


def _run(uploaded, subject: str, session: str | None, gen_report: bool, gen_mesh: bool, sig: str) -> None:
    suffix = ".nii.gz" if uploaded.name.endswith(".gz") else ".nii"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    with st.spinner(f"Analyzing sub-{subject} automatically — detection, biomarkers, mesh, and AI summary…"):
        st.session_state["av_result"] = dc.run_analysis(
            nifti_path=tmp_path, generate_report=gen_report, generate_mesh=gen_mesh,
        )
    os.unlink(tmp_path)
    st.session_state.pop("av_selected_id", None)
    st.session_state["av_last_upload_sig"] = sig
    st.toast(f"Analysis complete for sub-{subject}", icon="✅")
    st.rerun()


def render(key_prefix: str = "intake") -> None:
    """Render the upload + demo-patient widgets. Auto-runs the pipeline
    in place — caller just re-checks `layout.require_result()` afterward."""
    up_col, demo_col = st.columns([2, 1])
    with up_col:
        uploaded = st.file_uploader(
            "Drop a BIDS-named NIfTI file (.nii / .nii.gz)", type=["gz", "nii"], key=f"{key_prefix}_file",
        )
    with demo_col:
        st.markdown("<div style='height:1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("🧪 Or load a demo patient", key=f"{key_prefix}_demo", width="stretch"):
            st.session_state["av_result"] = dc.get_sample_result()
            st.session_state.pop("av_selected_id", None)
            st.rerun()

    if uploaded is None:
        return

    match = _BIDS_RE.search(uploaded.name)
    sig = f"{uploaded.name}:{uploaded.size}"
    already_processed = st.session_state.get("av_last_upload_sig") == sig

    gen_report = st.session_state.setdefault(f"{key_prefix}_gen_report", True)
    gen_mesh = st.session_state.setdefault(f"{key_prefix}_gen_mesh", True)

    if match:
        sub, ses = match.group("sub"), match.group("ses")
        if already_processed:
            st.success(f"sub-{sub} already analyzed — results below.", icon="✅")
        else:
            st.success(f"Patient identified automatically: **sub-{sub}**" + (f", ses-{ses}" if ses else ""), icon="✅")
            _run(uploaded, sub, ses, gen_report, gen_mesh, sig)
    else:
        st.warning("Couldn't auto-detect the patient ID from this filename — enter it to start analysis.", icon="⚠️")
        c1, c2 = st.columns(2)
        subject = c1.text_input("Subject ID", key=f"{key_prefix}_manual_sub")
        session = c2.text_input("Session (optional)", key=f"{key_prefix}_manual_ses")
        if st.button("Start Analysis", type="primary", disabled=not subject, key=f"{key_prefix}_manual_run"):
            _run(uploaded, subject, session or None, gen_report, gen_mesh, sig)
