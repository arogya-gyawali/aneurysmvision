"""AneurysmVision — Voice Copilot page.

Records a clinical question, transcribes via Deepgram, then routes to
the backend report_generator for an AI answer. Falls back to canned
offline answers when services are unavailable.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import frontend.data_client as dc
from frontend.utils import compute_risk, finding_label


_OFFLINE_ANSWERS: dict[str, str] = {
    "What is the rupture risk?":
        "Based on the detected biomarkers, the risk assessment is derived from aspect ratio, "
        "volume, and maximum diameter. An aspect ratio above 1.6 is associated with higher rupture risk.",
    "What is the recommended treatment?":
        "Treatment decision depends on aneurysm size, location, and patient factors. "
        "Aneurysms > 5 mm at AComA or MCA bifurcation typically warrant neurosurgical consultation.",
    "Should we schedule follow-up?":
        "Conservative management with MRA follow-up in 6–12 months is appropriate for small "
        "(< 5 mm) unruptured aneurysms without high-risk morphology.",
    "Are there multiple aneurysms?":
        "The pipeline reports the total aneurysm count in the study-level metadata. "
        "Each detected lesion has independent biomarkers and risk scores.",
    "What does the aspect ratio mean?":
        "Aspect ratio = dome height / neck width. Values >= 1.6 correlate with higher rupture "
        "risk in the literature and are a key Terac evaluation dimension.",
}

_PRESET_QUESTIONS = list(_OFFLINE_ANSWERS.keys())


def _transcribe(audio_bytes: bytes) -> str | None:
    try:
        from deepgram import DeepgramClient, PrerecordedOptions, FileSource
        import os
        api_key = os.getenv("DEEPGRAM_API_KEY", "")
        if not api_key:
            return None
        client = DeepgramClient(api_key)
        payload: FileSource = {"buffer": audio_bytes}
        options = PrerecordedOptions(model="nova-2", smart_format=True, language="en", punctuate=True)
        resp = client.listen.prerecorded.v("1").transcribe_file(payload, options)
        return resp.results.channels[0].alternatives[0].transcript.strip()
    except Exception:
        return None


def _ask_claude(question: str, report: dict | None, bio: dict) -> str | None:
    try:
        import anthropic, os, json
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        context_parts = [f"Biomarkers: {json.dumps(bio, indent=2)}"]
        if report:
            context_parts.append(f"Report summary: {report.get('summary', '')}")
        context = "\n\n".join(context_parts)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=(
                "You are a neuroradiology AI assistant. Answer the clinician's question "
                "in 2-3 sentences using only the provided data. Never invent measurements."
            ),
            messages=[{"role": "user", "content": f"{context}\n\nQuestion: {question}"}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None


def show() -> None:
    st.title("Voice Copilot")
    st.caption("Ask a clinical question by voice or text — powered by Deepgram + Claude.")

    result = st.session_state.get("av_result")
    if result is None:
        result = dc.get_sample_result()
        st.session_state["av_result"] = result

    aneurysms = dc.aneurysm_list(result)
    report = dc.get_report(result)

    # Aneurysm selector for context
    if aneurysms:
        labels = [finding_label(a) for a in aneurysms]
        sel = st.selectbox("Aneurysm context", labels, key="voice_sel")
        finding = aneurysms[labels.index(sel)]
        bio = finding.get("biomarkers", {})
        risk = compute_risk(bio)
        st.markdown(
            f"**Selected:** {sel} — Risk: "
            f"<span style='color:{risk.color}'>{risk.level} ({risk.score}/100)</span>",
            unsafe_allow_html=True,
        )
    else:
        bio = {}

    st.divider()

    # ---- Voice input ----
    st.subheader("Record Question")
    audio = st.audio_input("Click to record", key="voice_audio")
    question_from_audio: str | None = None
    if audio:
        audio_bytes = audio.read()
        with st.spinner("Transcribing…"):
            question_from_audio = _transcribe(audio_bytes)
        if question_from_audio:
            st.success(f"Transcribed: **{question_from_audio}**")
        else:
            st.warning("Transcription unavailable (no Deepgram key). Using text input instead.")

    # ---- Text / preset input ----
    st.subheader("Or Type / Choose a Question")
    preset = st.selectbox("Preset questions", ["— custom —"] + _PRESET_QUESTIONS, key="voice_preset")
    text_q = st.text_input("Custom question", key="voice_text")

    # Resolve final question
    final_q: str | None = None
    if question_from_audio:
        final_q = question_from_audio
    elif preset != "— custom —":
        final_q = preset
    elif text_q.strip():
        final_q = text_q.strip()

    ask_btn = st.button("Ask", type="primary", use_container_width=True, disabled=final_q is None)

    if ask_btn and final_q:
        with st.spinner("Consulting AI…"):
            answer = _ask_claude(final_q, report, bio)

        if answer is None:
            answer = _OFFLINE_ANSWERS.get(final_q, "I don't have enough context to answer that question from the available data.")
            st.info("Offline answer (Claude not available):", icon="💡")
        else:
            st.success("AI Answer:")

        st.markdown(f"> {answer}")

        # ---- History ----
        if "voice_history" not in st.session_state:
            st.session_state["voice_history"] = []
        st.session_state["voice_history"].append({"Q": final_q, "A": answer})

    history = st.session_state.get("voice_history", [])
    if history:
        with st.expander(f"Session history ({len(history)})"):
            for item in reversed(history):
                st.markdown(f"**Q:** {item['Q']}")
                st.markdown(f"**A:** {item['A']}")
                st.divider()


show()
