"""3D surface mesh generation for aneurysm visualization.

Maps to ``clabtoolkit.surfacetools`` and ``clabtoolkit.visualizationtools`` (deferred).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.models import AneurysmFinding, MeshData


def generate_meshes(
    findings: list[AneurysmFinding],
    roi_volumes: dict[str, Any],
    output_dir: Path,
) -> list[AneurysmFinding]:
    """Generate GLB meshes for each finding and attach ``MeshData``."""
    raise NotImplementedError("Mesh generation not implemented (stage 3).")
