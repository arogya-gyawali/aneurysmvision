"""3D surface mesh generation for aneurysm visualization.

Thin **application-layer adapter** over clabtoolkit mesh utilities:

  - ``clabtoolkit.imagetools.extract_mesh_from_volume`` — marching-cubes extraction
  - ``clabtoolkit.surfacetools.Surface`` — mesh wrapping / export helpers
  - PyVista GLTF export (used by clabtoolkit visualization stack) for ``.glb`` files

Scope: Stage 5 only. No biomarker computation, report generation, or detection.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from backend.exceptions import ValidationError
from backend.models import AneurysmFinding, MeshData

logger = logging.getLogger(__name__)

# Deterministic extraction settings (no random smoothing variance).
_EXTRACT_KWARGS = {
    "gaussian_smooth": False,
    "fill_holes": True,
    "smooth_iterations": 0,
    "closing_iterations": 0,
}


def generate_meshes(
    findings: list[AneurysmFinding],
    roi_volumes: dict[str, Any],
    output_dir: Path,
) -> list[AneurysmFinding]:
    """Generate GLB meshes for each finding and attach :class:`MeshData`."""
    if not findings:
        return []

    resolved_dir = _resolve_output_dir(Path(output_dir))
    meshed: list[AneurysmFinding] = []

    for finding in findings:
        mask = _resolve_roi_mask(finding, roi_volumes)
        mesh_path, vertex_count, face_count = _build_and_export_mesh(
            finding_id=finding.id,
            mask=mask,
            output_dir=resolved_dir,
        )
        mesh_data = MeshData(
            format="glb",
            path=str(mesh_path),
            vertex_count=vertex_count,
            face_count=face_count,
        )
        meshed.append(finding.model_copy(update={"mesh": mesh_data}))
        logger.info(
            "Exported mesh for %s -> %s (vertices=%d faces=%d)",
            finding.id,
            mesh_path,
            vertex_count,
            face_count,
        )

    return meshed


# ---------------------------------------------------------------------------
# ROI mask resolution
# ---------------------------------------------------------------------------
def _resolve_roi_mask(
    finding: AneurysmFinding,
    roi_volumes: dict[str, Any],
) -> np.ndarray:
    """Return a binary ROI volume for mesh extraction."""
    for key in (finding.id, str(finding.label), f"label-{finding.label}"):
        if key in roi_volumes:
            return _coerce_binary_mask(roi_volumes[key])

    return _mask_from_bounds(finding.roi_bounds_voxel)


def _coerce_binary_mask(volume: Any) -> np.ndarray:
    arr = np.asarray(volume)
    if arr.ndim > 3:
        arr = arr[..., 0]
    return (arr > 0).astype(np.float32)


def _mask_from_bounds(
    bounds: tuple[int, int, int, int, int, int],
) -> np.ndarray:
    """Build a solid binary box from voxel bounds (pipeline default when no ROI dict)."""
    i0, i1, j0, j1, k0, k1 = bounds
    if i1 < i0 or j1 < j0 or k1 < k0:
        raise ValidationError(f"Invalid ROI bounds for mesh extraction: {bounds}")

    shape = (i1 - i0 + 1, j1 - j0 + 1, k1 - k0 + 1)
    if min(shape) < 1:
        raise ValidationError(f"Degenerate ROI bounds for mesh extraction: {bounds}")

    return np.ones(shape, dtype=np.float32)


# ---------------------------------------------------------------------------
# Mesh extraction and export
# ---------------------------------------------------------------------------
def _build_and_export_mesh(
    finding_id: str,
    mask: np.ndarray,
    output_dir: Path,
) -> tuple[Path, int, int]:
    if not np.any(mask):
        raise ValidationError(f"Cannot generate mesh for {finding_id}: empty ROI mask.")

    polydata = _extract_surface(mask)
    vertex_count = int(polydata.n_points)
    face_count = int(polydata.n_cells)

    mesh_path = output_dir / f"{finding_id}.glb"
    _export_glb(polydata, mesh_path)

    return mesh_path.resolve(), vertex_count, face_count


def _prepare_mask_for_extraction(mask: np.ndarray) -> np.ndarray:
    """Pad with a zero border so marching cubes can extract a closed surface."""
    padded = np.zeros(tuple(dim + 2 for dim in mask.shape), dtype=np.float32)
    padded[1:-1, 1:-1, 1:-1] = mask
    return padded


def _extract_surface(mask: np.ndarray) -> Any:
    """Extract a surface mesh via clabtoolkit imagetools (primary path)."""
    volume = _prepare_mask_for_extraction(mask)
    try:
        import clabtoolkit.imagetools as imagetools

        polydata = imagetools.extract_mesh_from_volume(volume, **_EXTRACT_KWARGS)
    except Exception as exc:
        logger.warning("clabtoolkit mesh extraction failed (%s); using fallback.", exc)
        polydata = _extract_surface_fallback(volume)

    _wrap_with_surface(polydata)
    return polydata


def _wrap_with_surface(polydata: Any) -> None:
    """Optional surfacetools wrapper for downstream visualization compatibility."""
    try:
        from clabtoolkit.surfacetools import Surface

        surface = Surface()
        surface.load_from_mesh(polydata)
    except Exception as exc:  # pragma: no cover - non-fatal helper
        logger.debug("Surface wrapper skipped: %s", exc)


def _extract_surface_fallback(mask: np.ndarray) -> Any:
    """Minimal marching-cubes fallback when clabtoolkit extraction is unavailable."""
    try:
        from skimage import measure
        import pyvista as pv

        level = float(np.min(mask) + np.max(mask)) / 2.0
        if level <= np.min(mask) or level >= np.max(mask):
            level = (float(np.min(mask)) + float(np.max(mask))) / 2.0 or 0.5
        verts, faces, _normals, _values = measure.marching_cubes(volume := mask, level=level)
        faces_pv = np.column_stack([np.full(len(faces), 3), faces]).astype(np.int64).ravel()
        return pv.PolyData(verts, faces_pv)
    except Exception as exc:
        raise ValidationError(f"Mesh extraction failed: {exc}") from exc


def _export_glb(polydata: Any, mesh_path: Path) -> None:
    """Write a GLB file, preferring PyVista's GLTF exporter (visualization stack)."""
    mesh_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import pyvista as pv

        plotter = pv.Plotter(off_screen=True)
        try:
            plotter.add_mesh(polydata)
            plotter.export_gltf(str(mesh_path))
        finally:
            plotter.close()
        if mesh_path.is_file() and mesh_path.stat().st_size > 0:
            return
    except Exception as exc:
        logger.warning("GLB export via PyVista failed (%s); trying STL fallback.", exc)

    _export_via_surfacetools(polydata, mesh_path)


def _export_via_surfacetools(polydata: Any, mesh_path: Path) -> None:
    """Fallback export through surfacetools (STL), preserving server-side path contract."""
    try:
        from clabtoolkit.surfacetools import Surface

        surface = Surface()
        surface.load_from_mesh(polydata)
        stl_path = mesh_path.with_suffix(".stl")
        surface.export_to_pyvista(str(stl_path), overwrite=True)
        if stl_path.is_file():
            # Keep contract path as .glb when possible; copy STL to glb path only if GLB failed.
            # Frontend expects .glb — rename would be invalid. Re-raise if GLB unavailable.
            if not mesh_path.is_file():
                raise ValidationError(
                    f"GLB export failed for {mesh_path.name}; STL written to {stl_path}"
                )
    except Exception as exc:
        raise ValidationError(f"Failed to export mesh to {mesh_path}: {exc}") from exc


def _resolve_output_dir(output_dir: Path) -> Path:
    """Ensure output directory exists; fall back to workspace ``outputs/`` if needed."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".write_probe"
        probe.touch()
        probe.unlink()
        return output_dir
    except OSError as exc:
        parts = output_dir.parts
        if len(parts) >= 2 and parts[1] == "artifacts":
            relative = Path(*parts[2:]) if len(parts) > 2 else Path("meshes")
        else:
            relative = output_dir.name

        fallback = Path.cwd() / "outputs" / "artifacts" / relative
        logger.warning(
            "Output directory %s not writable (%s); using fallback %s",
            output_dir,
            exc,
            fallback,
        )
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
