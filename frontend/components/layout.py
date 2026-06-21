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
    --av-purple: #7c3aed;
    --av-bg-soft: #f8fafc;
    --av-border: #e2e8f0;
}

[data-testid="stAppViewContainer"], .stApp, .main, .block-container { background: transparent !important; }

.av-bg-wrap {
    position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none;
    background: #f8fafc;
}
.av-bg-wrap .blob {
    position: absolute; border-radius: 50%; filter: blur(60px); opacity: 0.16;
}
.av-bg-wrap .blob.b1 { width: 32rem; height: 32rem; top: -8rem; left: -6rem; background: var(--av-blue); animation: av-orbit-a 50s linear infinite; }
.av-bg-wrap .blob.b2 { width: 26rem; height: 26rem; bottom: -6rem; right: -4rem; background: var(--av-teal); animation: av-orbit-b 60s linear infinite; }
.av-bg-wrap .blob.b3 { width: 22rem; height: 22rem; top: 40%; left: 60%; background: var(--av-purple); animation: av-orbit-a 70s linear infinite reverse; }
.av-bg-wrap .brain {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    font-size: 30rem; line-height: 1; opacity: 0.07;
    filter: saturate(2.2) hue-rotate(195deg) brightness(1.3);
    animation: av-spin-cw 50s linear infinite;
}
.av-bg-wrap .brain.inner {
    font-size: 17rem; opacity: 0.06; animation: av-spin-ccw 30s linear infinite;
    filter: saturate(2.4) hue-rotate(150deg) brightness(1.3);
}
@keyframes av-spin-cw  { from { transform: translate(-50%,-50%) rotate(0deg); }   to { transform: translate(-50%,-50%) rotate(360deg); } }
@keyframes av-spin-ccw { from { transform: translate(-50%,-50%) rotate(360deg); } to { transform: translate(-50%,-50%) rotate(0deg); } }
@keyframes av-orbit-a { from { transform: rotate(0deg) translateX(2rem); } to { transform: rotate(360deg) translateX(2rem); } }
@keyframes av-orbit-b { from { transform: rotate(0deg) translateX(-3rem); } to { transform: rotate(-360deg) translateX(-3rem); } }

.block-container { padding-top: 1.5rem; max-width: 1400px; }

.av-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #1e3a8a 0%, #4c1d95 55%, #0d9488 100%);
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
    border-top: 3px solid transparent;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.av-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(15,23,42,0.10); }
.av-card.accent-blue   { border-top-color: var(--av-blue); }
.av-card.accent-teal   { border-top-color: var(--av-teal); }
.av-card.accent-purple { border-top-color: var(--av-purple); }
.av-card-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: .06em; color: #64748b; font-weight: 700; }
.av-card-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin-top: 0.15rem; line-height: 1.2; }
.av-card-sub { font-size: 0.75rem; color: #94a3b8; margin-top: 0.2rem; }

.av-badge {
    display: inline-block; padding: 0.28rem 0.75rem; border-radius: 999px;
    font-weight: 700; font-size: 0.78rem; letter-spacing: .02em;
}

.av-section-header {
    font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0.25rem 0 0.75rem 0;
    padding-left: 0.65rem; border-left: 4px solid var(--av-blue);
}
.av-caption-muted { color: #94a3b8; font-size: 0.82rem; }

.av-gradient-text {
    background: linear-gradient(90deg, var(--av-blue), var(--av-purple), var(--av-teal)) !important;
    -webkit-background-clip: text !important; background-clip: text !important;
    color: transparent !important; -webkit-text-fill-color: transparent !important;
}

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
<div class="av-bg-wrap">
    <div class="blob b1"></div>
    <div class="blob b2"></div>
    <div class="blob b3"></div>
    <div class="brain">🧠</div>
    <div class="brain inner">🧠</div>
</div>
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
