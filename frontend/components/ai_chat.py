"""Chat-style follow-up assistant for the AI Summary page.

Answers are grounded only in the loaded `AnalysisResult` (report + biomarkers).
Uses the Anthropic API when `ANTHROPIC_API_KEY` is set and the `anthropic`
package is installed; otherwise falls back to a small offline Q&A bank so
the page stays usable without any external dependency or key.
"""

from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

_OFFLINE_ANSWERS: dict[str, str] = {
    "What is the rupture risk?": (
        "Rupture risk here is approximated from aspect ratio, volume, and maximum diameter. "
        "An aspect ratio at or above 1.6 is associated with elevated risk in the literature. "
        "This is a screening heuristic, not a diagnosis."
    ),
    "What is the recommended treatment?": (
        "Treatment choice depends on size, location, and patient-specific factors. Aneurysms "
        "larger than 5 mm at the AComA or an MCA bifurcation typically warrant a neurosurgical "
        "or interventional radiology consultation."
    ),
    "Should we schedule follow-up?": (
        "Conservative management with MRA follow-up in 6–12 months may be reasonable for small "
        "(<5 mm) unruptured aneurysms without high-risk morphology, per the treating clinician's judgment."
    ),
    "What does the aspect ratio mean?": (
        "Aspect ratio is dome height divided by neck width. Values at or above 1.6 are commonly "
        "cited as suggestive of higher rupture risk."
    ),
}
_PRESET_QUESTIONS = list(_OFFLINE_ANSWERS.keys())


def _ask_claude(question: str, report: dict | None, bio: dict) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        context = [f"Biomarkers: {json.dumps(bio, indent=2)}"]
        if report:
            context.append(f"Report summary: {report.get('summary', '')}")
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=(
                "You are a neuroradiology assistant. Answer in 2-3 cautious sentences using only "
                "the provided data. Use 'suggests'/'may indicate' language, never a firm diagnosis."
            ),
            messages=[{"role": "user", "content": f"{chr(10).join(context)}\n\nQuestion: {question}"}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None


def render(report: dict[str, Any] | None, finding: dict[str, Any] | None) -> None:
    bio = (finding or {}).get("biomarkers", {}) or {}

    st.caption("Answers are generated from this study's data only and require physician review.")

    history: list[dict[str, str]] = st.session_state.setdefault("av_chat_history", [])
    for turn in history:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

    preset = st.selectbox("Preset questions", ["— choose —"] + _PRESET_QUESTIONS, key="chat_preset")
    typed = st.chat_input("Type a question about this finding…")

    question = typed or (preset if preset != "— choose —" else None)
    if question and question != st.session_state.get("av_last_question"):
        st.session_state["av_last_question"] = question
        history.append({"role": "user", "content": question})

        answer = _ask_claude(question, report, bio)
        offline = answer is None
        if offline:
            answer = _OFFLINE_ANSWERS.get(
                question, "I don't have enough context in this study's data to answer that confidently."
            )
        prefix = "*(offline answer — Claude not configured)*\n\n" if offline else ""
        history.append({"role": "assistant", "content": prefix + answer})
        st.rerun()
