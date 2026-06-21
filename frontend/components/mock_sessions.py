"""Recent-session cards for the Home page.

The contract has no "list of past jobs" endpoint yet, so this is an
explicitly-labeled demo list. Once the backend exposes job history,
swap `recent_sessions()` for a real call — the Home page doesn't change.
"""

from __future__ import annotations

RECENT_SESSIONS: list[dict[str, str]] = [
    {
        "job_id": "av-20250620-7f3a9c2e",
        "patient": "sub-042",
        "date": "2025-06-20",
        "status": "completed",
        "findings": "2 aneurysms",
    },
    {
        "job_id": "av-20250618-2a1bd771",
        "patient": "sub-039",
        "date": "2025-06-18",
        "status": "completed",
        "findings": "No aneurysms",
    },
    {
        "job_id": "av-20250617-9c0e4f12",
        "patient": "sub-037",
        "date": "2025-06-17",
        "status": "failed",
        "findings": "QC failed — motion artifact",
    },
]


def recent_sessions() -> list[dict[str, str]]:
    return RECENT_SESSIONS
