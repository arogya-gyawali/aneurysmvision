"""Plotly 3D viewer for detected aneurysms.

`AnalysisResult.aneurysms[].mesh` only carries a server-side GLB path
(api_contract.md: MeshData). Until that file is reachable from the
frontend host, `_geometry_for_finding` falls back to a mock ellipsoid
sized from the finding's biomarkers. When a real GLB becomes readable
at `mesh.path` (and `trimesh` is installed), it is loaded automatically
and the UI does not change — this is the Checkpoint 3 swap point.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from frontend.utils import compute_risk, finding_label, location_label


def _ellipsoid_mesh(center: tuple[float, float, float], radii: tuple[float, float, float], resolution: int = 22):
    cx, cy, cz = center
    rx, ry, rz = (max(r, 0.5) for r in radii)

    theta = np.linspace(0, np.pi, resolution)
    phi = np.linspace(0, 2 * np.pi, resolution)
    theta, phi = np.meshgrid(theta, phi)

    x = cx + rx * np.sin(theta) * np.cos(phi)
    y = cy + ry * np.sin(theta) * np.sin(phi)
    z = cz + rz * np.cos(theta)
    x, y, z = x.flatten(), y.flatten(), z.flatten()

    n = resolution
    i, j, k = [], [], []
    for a in range(n - 1):
        for b in range(n - 1):
            p0 = a * n + b
            p1 = p0 + 1
            p2 = p0 + n
            p3 = p2 + 1
            i += [p0, p1]
            j += [p1, p3]
            k += [p2, p2]
    return x, y, z, np.array(i), np.array(j), np.array(k)


def _load_glb_mesh(path: str):
    try:
        import trimesh
    except ImportError:
        return None
    if not Path(path).exists():
        return None
    try:
        mesh = trimesh.load(path, force="mesh")
        v, f = mesh.vertices, mesh.faces
        return v[:, 0], v[:, 1], v[:, 2], f[:, 0], f[:, 1], f[:, 2]
    except Exception:
        return None


def _geometry_for_finding(finding: dict[str, Any]) -> tuple[tuple, str]:
    mesh_meta = finding.get("mesh") or {}
    path = mesh_meta.get("path")
    if path:
        real = _load_glb_mesh(path)
        if real is not None:
            return real, "real"

    bio = finding.get("biomarkers", {}) or {}
    cx, cy, cz = finding.get("centroid_mm", (0.0, 0.0, 0.0))
    rx = bio.get("max_diameter_mm", 4.0) / 2.0
    ry = (bio.get("neck_width_mm") or rx * 1.4) / 2.0
    rz = (bio.get("dome_height_mm") or rx * 1.6) / 2.0
    geom = _ellipsoid_mesh((cx, cy, cz), (rx, ry, rz))
    return geom, "mock"


def render(
    aneurysms: list[dict[str, Any]],
    selected_id: str | None,
    height: int = 620,
    show_other_rois: bool = True,
    opacity_override: float | None = None,
    show_labels: bool = False,
    show_axes: bool = True,
) -> None:
    if not aneurysms:
        st.info("No aneurysm findings to visualize for this study.")
        return

    if selected_id is None:
        selected_id = aneurysms[0].get("id")

    visible_findings = [
        f for f in aneurysms if f.get("id") == selected_id or show_other_rois
    ]

    fig = go.Figure()
    source_label = "mock"

    for finding in visible_findings:
        is_selected = finding.get("id") == selected_id
        (x, y, z, i, j, k), source = _geometry_for_finding(finding)
        if is_selected:
            source_label = source

        bio = finding.get("biomarkers", {}) or {}
        risk = compute_risk(bio)
        color = risk.color if is_selected else "#94a3b8"
        opacity = opacity_override if opacity_override is not None else (0.92 if is_selected else 0.28)

        fig.add_trace(
            go.Mesh3d(
                x=x, y=y, z=z, i=i, j=j, k=k,
                color=color,
                opacity=opacity,
                flatshading=False,
                lighting={"ambient": 0.55, "diffuse": 0.8, "specular": 0.3, "roughness": 0.6},
                lightposition={"x": 100, "y": 200, "z": 150},
                name=finding_label(finding),
                hovertext=(
                    f"{finding_label(finding)}<br>"
                    f"Risk: {risk.level} ({risk.score}/100)<br>"
                    f"Location: {location_label(finding.get('location', ''))}"
                ),
                hoverinfo="text",
                showscale=False,
            )
        )

        if show_labels:
            cx, cy, cz = finding.get("centroid_mm", (0, 0, 0))
            fig.add_trace(
                go.Scatter3d(
                    x=[cx], y=[cy], z=[cz + 2],
                    mode="text",
                    text=[finding_label(finding)],
                    textfont={"color": color, "size": 11},
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    axis_style = {
        "color": "#64748b", "gridcolor": "#1e293b", "showbackground": False,
        "visible": show_axes,
    }
    fig.update_layout(
        paper_bgcolor="#0b1220",
        scene={
            "bgcolor": "#0b1220",
            "xaxis": {"title": "x (mm)", **axis_style},
            "yaxis": {"title": "y (mm)", **axis_style},
            "zaxis": {"title": "z (mm)", **axis_style},
            "aspectmode": "data",
            "camera": {"eye": {"x": 1.4, "y": 1.4, "z": 0.9}},
        },
        margin={"t": 10, "b": 0, "l": 0, "r": 0},
        height=height,
        showlegend=False,
        uirevision="av-mesh",
    )

    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    tag = "Server-side GLB mesh" if source_label == "real" else "Mock geometry (biomarker-derived ellipsoid) — swaps to real GLB automatically once backend exports it"
    st.caption(f"🔹 {tag}")
