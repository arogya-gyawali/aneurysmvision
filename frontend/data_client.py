"""Contract-driven data access layer for the AneurysmVision frontend.

Per backend/api_contract.md, the frontend consumes a single typed response
(`AnalysisResult`). This module serves either the live backend pipeline
output or backend/sample_output.json as that response, and runs both through
the normalization layer in `frontend.normalize` so components always see one
stable, frontend-friendly shape (BIDS aliases + deterministic defaults).

The backend pipeline is never modified; normalization is a pure read-only
adapter. See `frontend/normalize.py` for the full schema and mapping rules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from frontend.normalize import normalize_result

_SAMPLE_PATH = Path(__file__).parent.parent / "backend" / "sample_output.json"
_BACKEND_AVAILABLE: bool | None = None


def _check_backend() -> bool:
    global _BACKEND_AVAILABLE
    if _BACKEND_AVAILABLE is not None:
        return _BACKEND_AVAILABLE
    try:
        import backend.models  # noqa: F401
        import backend.pipeline  # noqa: F401

        _BACKEND_AVAILABLE = True
    except Exception:
        _BACKEND_AVAILABLE = False
    return _BACKEND_AVAILABLE


def _load_sample() -> dict[str, Any]:
    with open(_SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _sample_with_flag() -> dict[str, Any]:
    data = normalize_result(_load_sample())
    data["_source"] = "sample"
    return data


def backend_alive() -> bool:
    """Return True when the backend package is importable."""
    return _check_backend()


def run_analysis(
    nifti_path: str | None = None,
    dataset_root: str | None = None,
    subject: str | None = None,
    session: str | None = None,
    generate_report: bool = True,
    generate_mesh: bool = True,
) -> dict[str, Any]:
    """Run the pipeline and return an AnalysisResult dict.

    Falls back to sample_output.json whenever the live pipeline is
    unavailable or raises (expected while backend stages are stubs).
    """
    if _check_backend():
        try:
            from backend.models import AnalysisRequest, BidsEntities
            from backend.pipeline import run_pipeline

            if dataset_root and subject:
                req = AnalysisRequest(
                    dataset_root=dataset_root,
                    bids_entities=BidsEntities(
                        sub=subject, ses=session, suffix="angio", extension="nii.gz"
                    ),
                    generate_report=generate_report,
                    generate_mesh=generate_mesh,
                )
            elif nifti_path:
                req = AnalysisRequest(
                    nifti_path=nifti_path,
                    generate_report=generate_report,
                    generate_mesh=generate_mesh,
                )
            else:
                return _sample_with_flag()

            result = run_pipeline(req)
            data = (
                result.model_dump(mode="json", by_alias=True)
                if hasattr(result, "model_dump")
                else dict(result)
            )
            data = normalize_result(data)
            data["_source"] = "live"
            return data
        except Exception:
            pass

    return _sample_with_flag()


def get_sample_result() -> dict[str, Any]:
    """Return the sample output with the demo flag set, always."""
    return _sample_with_flag()


def aneurysm_list(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("aneurysms", [])


def get_report(result: dict[str, Any]) -> dict[str, Any] | None:
    return result.get("report")


def get_study(result: dict[str, Any]) -> dict[str, Any]:
    return result.get("study", {})


def get_stages(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("stages", [])


def is_demo(result: dict[str, Any]) -> bool:
    return result.get("_source") == "sample"
