"""ROI (Region of Interest) selection.

Each entry in `AnalysisResult.aneurysms[]` *is* a detected ROI per
api_contract.md — this component just presents that list in vascular,
doctor-facing language and lets the clinician pick the active one
(stored in `st.session_state["av_selected_id"]`, read by every other page).
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.utils import compute_risk, location_label

_ALL_TERRITORIES = [
    "middle_cerebral_artery",
    "anterior_cerebral_artery",
    "internal_carotid_artery",
    "basilar_artery",
    "posterior_cerebral_artery",
    "anterior_communicating_artery",
    "posterior_communicating_artery",
    "other",
]


def render(aneurysms: list[dict[str, Any]]) -> str | None:
    if not aneurysms:
        st.success("No ROI candidates — no aneurysms were detected in this study.")
        return None

    st.markdown("<div class='av-section-header'>Auto-detected ROI Candidates</div>", unsafe_allow_html=True)
    st.caption("Detected by the segmentation/detection stage. Ranked by detector confidence.")

    query = st.text_input("Search by vascular territory", placeholder="e.g. MCA, communicating artery…")

    ranked = sorted(aneurysms, key=lambda a: a.get("confidence", 0), reverse=True)
    if query:
        q = query.lower()
        ranked = [a for a in ranked if q in location_label(a.get("location", "")).lower()]

    if not ranked:
        st.info("No ROI matches that search term.")
        return st.session_state.get("av_selected_id")

    current = st.session_state.get("av_selected_id")
    for finding in ranked:
        risk = compute_risk(finding.get("biomarkers", {}) or {})
        is_active = finding.get("id") == current
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**{location_label(finding.get('location', ''))}**")
                st.caption(finding.get("location_detail", "—"))
            with c2:
                conf = finding.get("confidence", 0) * 100
                st.progress(min(int(conf), 100), text=f"Detector confidence: {conf:.0f}%")
                st.caption(f"Risk: {risk.level} ({risk.score}/100)")
            with c3:
                label = "Active ✓" if is_active else "Highlight ROI"
                if st.button(label, key=f"roi_btn_{finding['id']}", type="primary" if is_active else "secondary", width="stretch"):
                    st.session_state["av_selected_id"] = finding["id"]
                    st.toast(f"ROI set to {location_label(finding.get('location', ''))}", icon="🎯")
                    st.rerun()

    st.markdown("---")
    with st.expander("Manual override (clinician annotation)"):
        st.caption(
            "For documentation only — does not change the detector's output, "
            "only which territory label is noted alongside your review."
        )
        st.selectbox(
            "Vascular territory",
            options=_ALL_TERRITORIES,
            format_func=location_label,
            key="roi_manual_override",
        )

    return st.session_state.get("av_selected_id")
