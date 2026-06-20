"""Pipeline exception types."""

from __future__ import annotations


class PipelineError(Exception):
    """Base exception for pipeline failures."""


class ValidationError(PipelineError):
    """Raised when an ``AnalysisRequest`` fails validation."""


class StageNotImplementedError(PipelineError):
    """Raised when a pipeline stage has no implementation yet."""

    def __init__(self, stage: str, detail: str = "") -> None:
        self.stage = stage
        self.detail = detail
        message = f"Stage '{stage}' is not implemented yet."
        if detail:
            message = f"{message} {detail}"
        super().__init__(message)
