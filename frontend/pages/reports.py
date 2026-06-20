"""AneurysmVision — Reports page.

Renders the Claude-generated ReportDraft and collects Terac evaluations.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import frontend.data_client as dc
from frontend.utils import compute_risk, finding_label


_TERAC_PATH = Path(__file__).parent.parent.parent / "outputs" / "terac_evaluations.jsonl"


def _save_terac(job_id: str, finding_id: str, scores: dict[str, int]) -> None:
    overall = round(sum(scores.values()) / len(scores))
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "job_id": job_id,
        "finding_id": finding_id,
        **scores,
        "overall_score": overall,
    }
    _TERAC_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_TERAC_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _load_terac_history() -> list[dict]:
    if not _TERAC_PATH.exists():
        return []
    records = []
    with open(_TERAC_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def show() -> None:
    st.title("Clinical Report")

    result = st.session_state.get("av_result")
    if result is None:
        result = dc.get_sample_result()
        st.session_state["av_result"] = result

    if dc.is_demo(result):
        st.info("**Demo mode** — report generated from sample data.", icon="ℹ️")

    report = dc.get_report(result)
    aneurysms = dc.aneurysm_list(result)
    job_id = result.get("job_id", "unknown")

    # ---- Aneurysm selector ----
    if aneurysms:
        labels = [finding_label(a) for a in aneurysms]
        selected_label = st.selectbox("Aneurysm", labels, key="rep_sel")
        finding = aneurysms[labels.index(selected_label)]
        bio = finding.get("biomarkers", {})
        risk = compute_risk(bio)

        col1, col2, col3 = st.columns(3)
        col1.metric("Max Diameter", f"{bio.get('max_diameter_mm', '—')} mm")
        col2.metric("Volume",       f"{bio.get('volume_mm3', '—')} mm³")
        col3.metric(
            "Risk Level",
            risk.level,
            delta=f"Score {risk.score}/100",
            delta_color="inverse" if risk.level in ("High", "Critical") else "off",
        )
        finding_id = finding.get("id", "unknown")
    else:
        st.warning("No aneurysms in result.")
        finding_id = "none"

    st.divider()

    # ---- Report body ----
    if report:
        st.subheader("Summary")
        st.write(report.get("summary", ""))

        st.subheader("Findings")
        for item in report.get("findings", []):
            st.markdown(f"- {item}")

        st.subheader("Recommendations")
        for item in report.get("recommendations", []):
            st.markdown(f"- {item}")

        meta_col1, meta_col2 = st.columns(2)
        meta_col1.caption(f"Model: `{report.get('model', '—')}`")
        gen_at = report.get("generated_at", "")
        if gen_at:
            try:
                dt = datetime.fromisoformat(str(gen_at).replace("Z", "+00:00"))
                gen_at = dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                pass
        meta_col2.caption(f"Generated: {gen_at}")

        # ---- Download ----
        report_json = json.dumps(report, default=str, indent=2)
        st.download_button(
            "Download report (JSON)",
            data=report_json,
            file_name=f"{job_id}_report.json",
            mime="application/json",
        )
    else:
        st.info("No report available. Enable 'Generate report' when running the pipeline.")

    st.divider()

    # ---- Terac evaluation ----
    st.subheader("Terac Human Evaluation")
    st.caption("Rate the AI-generated report across five clinical dimensions.")

    if report:
        with st.form("terac_form"):
            accuracy     = st.select_slider("Accuracy",           options=[1,2,3,4,5], value=3)
            relevance    = st.select_slider("Clinical Relevance", options=[1,2,3,4,5], value=3)
            clarity      = st.select_slider("Clarity",            options=[1,2,3,4,5], value=3)
            completeness = st.select_slider("Completeness",       options=[1,2,3,4,5], value=3)
            safety       = st.select_slider("Safety",             options=[1,2,3,4,5], value=3)
            submitted    = st.form_submit_button("Submit evaluation")

        if submitted:
            scores = {
                "accuracy": accuracy,
                "clinical_relevance": relevance,
                "clarity": clarity,
                "completeness": completeness,
                "safety": safety,
            }
            _save_terac(job_id, finding_id, scores)
            overall = round(sum(scores.values()) / len(scores))
            st.success(f"Evaluation saved! Overall score: {overall}/5")

    # ---- History ----
    history = _load_terac_history()
    if history:
        with st.expander(f"Evaluation history ({len(history)} records)"):
            import pandas as pd
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True, hide_index=True)
            avg = df["overall_score"].mean() if "overall_score" in df.columns else None
            if avg is not None:
                badge_color = "#22c55e" if avg >= 4 else "#eab308" if avg >= 3 else "#ef4444"
                st.markdown(
                    f"**Mean overall score:** "
                    f"<span style='color:{badge_color};font-weight:bold'>{avg:.2f}/5</span>",
                    unsafe_allow_html=True,
                )


show()
