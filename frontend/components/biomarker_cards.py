"""Biomarker metric cards for a single aneurysm finding.

Fields map 1:1 to `BiomarkerSet` in api_contract.md.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.utils import compute_risk, finding_label, location_label, risk_badge_html

_CARD_SPECS: list[tuple[str, str, str]] = [
    ("volume_mm3", "Volume", "mm³"),
    ("max_diameter_mm", "Max Diameter", "mm"),
    ("neck_width_mm", "Neck Width", "mm"),
    ("dome_height_mm", "Dome Height", "mm"),
    ("aspect_ratio", "Aspect Ratio", ""),
    ("size_ratio", "Size Ratio", ""),
    ("irregularity_index", "Irregularity Index", ""),
]

_FLAGS = {
    "aspect_ratio": lambda v: v is not None and v >= 1.6,
    "irregularity_index": lambda v: v is not None and v >= 1.3,
}


def render(finding: dict[str, Any]) -> None:
    bio = finding.get("biomarkers", {}) or {}
    risk = compute_risk(bio)
    use_cm = st.session_state.get("av_unit", "mm") == "cm"

    header_l, header_r = st.columns([3, 1])
    with header_l:
        st.markdown(f"<div class='av-section-header'>{finding_label(finding)}</div>", unsafe_allow_html=True)
        st.caption(
            f"{location_label(finding.get('location', ''))} · "
            f"{finding.get('location_detail', '—')} · "
            f"confidence {finding.get('confidence', 0) * 100:.0f}%"
        )
    with header_r:
        st.markdown(risk_badge_html(risk), unsafe_allow_html=True)

    cols = st.columns(4)
    for idx, (key, label, unit) in enumerate(_CARD_SPECS):
        value = bio.get(key)
        if value is None:
            continue
        flagged = _FLAGS.get(key, lambda _v: False)(value)
        accent = "#ef4444" if flagged else "var(--av-border)"
        display_value, display_unit = value, unit
        if use_cm and unit == "mm":
            display_value, display_unit = value / 10, "cm"
        elif use_cm and unit == "mm³":
            display_value, display_unit = value / 1000, "cm³"
        value_str = f"{display_value:.2f}" if isinstance(display_value, float) else str(display_value)
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div class="av-card" style="border-top:3px solid {accent}; margin-bottom:0.75rem;">
                    <div class="av-card-label">{label}</div>
                    <div class="av-card-value">{value_str}{(' ' + display_unit) if display_unit else ''}</div>
                    {"<div class='av-card-sub' style='color:#ef4444;'>Above typical threshold</div>" if flagged else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )

    if risk.rationale:
        with st.expander("Why this risk level?"):
            for item in risk.rationale:
                st.markdown(f"- {item}")
