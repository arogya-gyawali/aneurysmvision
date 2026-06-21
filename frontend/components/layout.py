"""Shared chrome for every page: theme CSS, top bar, and empty states.

Keeping this in one place means all 10 pages stay visually consistent
without re-implementing the same markup.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

_STATUS_COLORS = {
    "completed": "#16a34a",
    "running": "#2563eb",
    "queued": "#6b7280",
    "failed": "#dc2626",
    "skipped": "#6b7280",
}

_CSS = """
<style>
:root {
    --av-blue: #2563eb;
    --av-teal: #0d9488;
    --av-bg-soft: #f8fafc;
    --av-border: #e2e8f0;
}

.block-container { padding-top: 1.5rem; max-width: 1400px; }

.av-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    border-radius: 14px;
    padding: 0.9rem 1.5rem;
    margin-bottom: 1.25rem;
    color: #f1f5f9;
}
.av-topbar-title { font-size: 1.15rem; font-weight: 700; letter-spacing: .01em; }
.av-topbar-sub { font-size: 0.78rem; color: #94a3b8; margin-top: 0.1rem; }
.av-topbar-right { display: flex; align-items: center; gap: 0.75rem; font-size: 0.85rem; }

.av-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
    border: 1px solid var(--av-border);
}
.av-card-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: .06em; color: #64748b; font-weight: 700; }
.av-card-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin-top: 0.15rem; line-height: 1.2; }
.av-card-sub { font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem; }

.av-badge {
    display: inline-block; padding: 0.28rem 0.75rem; border-radius: 999px;
    font-weight: 700; font-size: 0.78rem; letter-spacing: .02em;
}

.av-section-header { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0.25rem 0 0.75rem 0; }
.av-caption-muted { color: #94a3b8; font-size: 0.82rem; }

.av-empty-state {
    text-align: center; padding: 3rem 1.5rem; border: 1.5px dashed var(--av-border);
    border-radius: 16px; background: var(--av-bg-soft); color: #64748b;
}
.av-empty-state .icon { font-size: 2.4rem; margin-bottom: 0.5rem; }
.av-empty-state .title { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0.35rem; }

.av-mock-tag {
    display: inline-block; background: #fef3c7; color: #92400e; border-radius: 6px;
    padding: 0.12rem 0.55rem; font-size: 0.68rem; font-weight: 700; letter-spacing: .03em;
    text-transform: uppercase; vertical-align: middle; margin-left: 0.4rem;
}

[data-testid="stSidebarNav"] { padding-top: 0.5rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def mock_tag(text: str = "Demo data") -> str:
    """Small honesty label for UI driven by placeholder/synthetic data."""
    return f"<span class='av-mock-tag'>{text}</span>"


def top_bar(result: dict[str, Any] | None, page_label: str) -> None:
    """Persistent header: app name, current page, patient/job, status."""
    if result:
        study = result.get("study", {}) or {}
        bids = study.get("bids") or {}
        patient = f"sub-{bids.get('sub', '—')}"
        status = result.get("status", "unknown")
        color = _STATUS_COLORS.get(status, "#94a3b8")
        right = (
            f"<span>Patient: <strong>{patient}</strong></span>"
            f"<span class='av-badge' style='background:{color}33;color:#f1f5f9;border:1px solid {color};'>"
            f"{status.upper()}</span>"
        )
    else:
        right = "<span class='av-caption-muted' style='color:#94a3b8;'>No patient loaded</span>"

    st.markdown(
        f"""
        <div class="av-topbar">
            <div>
                <div class="av-topbar-title">🧠 AneurysmVision</div>
                <div class="av-topbar-sub">{page_label}</div>
            </div>
            <div class="av-topbar-right">{right}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, body: str, cta_label: str | None = None, cta_page: str | None = None) -> None:
    """Standard empty state shown when no patient/result is loaded yet."""
    st.markdown(
        f"""
        <div class="av-empty-state">
            <div class="icon">{icon}</div>
            <div class="title">{title}</div>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cta_label and cta_page:
        st.markdown("")
        col = st.columns([1, 1, 1])[1]
        with col:
            if st.button(cta_label, width="stretch", type="primary"):
                st.switch_page(cta_page)


def require_result() -> dict[str, Any] | None:
    """Fetch the active AnalysisResult from session state, or None."""
    return st.session_state.get("av_result")
