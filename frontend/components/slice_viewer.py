"""Axial / coronal / sagittal slice viewer.

api_contract.md does not (yet) expose raw NIfTI slice data — only
`study.shape` and the ROI's `centroid_voxel`. This component renders a
deterministic synthetic slice (seeded by slice index, so it's stable
across reruns) with the ROI position overlaid, clearly tagged as a
preview. Swap `_synthetic_slice` for a real NIfTI slice loader once the
backend exposes one; the slider/tabs/overlay UI stays the same.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from frontend.components.layout import mock_tag

_PLANES = {
    "Axial": (0, 1, 2),
    "Coronal": (0, 2, 1),
    "Sagittal": (1, 2, 0),
}


def _synthetic_slice(dim_a: int, dim_b: int, slice_idx: int, blob_xy: tuple[float, float] | None) -> np.ndarray:
    rng = np.random.default_rng(seed=slice_idx * 7919 + dim_a)
    base = rng.normal(loc=0.25, scale=0.05, size=(dim_b, dim_a))

    yy, xx = np.mgrid[0:dim_b, 0:dim_a]
    cx, cy = dim_a * 0.5, dim_b * 0.55
    vessel = np.exp(-(((xx - cx) ** 2) / (2 * (dim_a * 0.05) ** 2) + ((yy - cy) ** 2) / (2 * (dim_b * 0.35) ** 2)))
    img = base + 0.55 * vessel

    if blob_xy is not None:
        bx, by = blob_xy
        blob = np.exp(-(((xx - bx) ** 2) + ((yy - by) ** 2)) / (2 * (min(dim_a, dim_b) * 0.04) ** 2))
        img += 0.6 * blob

    return np.clip(img, 0, 1.4)


def render(study: dict[str, Any], finding: dict[str, Any] | None) -> None:
    shape = study.get("shape") or [256, 256, 150]
    centroid_voxel = (finding or {}).get("centroid_voxel")

    st.markdown(
        f"<div class='av-section-header'>Cross-Section Viewer {mock_tag('Synthetic preview')}</div>",
        unsafe_allow_html=True,
    )
    st.caption("Real slice rendering is pending a backend NIfTI export endpoint. Positions are derived from the selected ROI's voxel centroid.")

    tabs = st.tabs(list(_PLANES.keys()))
    for tab, plane_name in zip(tabs, _PLANES.keys()):
        with tab:
            ax_a, ax_b, ax_depth = _PLANES[plane_name]
            dim_a, dim_b, dim_depth = shape[ax_a], shape[ax_b], shape[ax_depth]

            default_idx = int(centroid_voxel[ax_depth]) if centroid_voxel else dim_depth // 2
            ctrl_l, ctrl_r = st.columns([3, 1])
            with ctrl_l:
                slice_idx = st.slider(
                    f"{plane_name} slice", 0, max(dim_depth - 1, 1), min(default_idx, max(dim_depth - 1, 0)),
                    key=f"slice_{plane_name}",
                )
            with ctrl_r:
                sync = st.checkbox("Sync with 3D", value=True, key=f"sync_{plane_name}")

            brightness, contrast = st.columns(2)
            b_val = brightness.slider("Brightness", -0.3, 0.3, 0.0, key=f"bri_{plane_name}")
            c_val = contrast.slider("Contrast", 0.5, 2.0, 1.0, key=f"con_{plane_name}")

            blob_xy = None
            if centroid_voxel and sync:
                blob_xy = (centroid_voxel[ax_a], centroid_voxel[ax_b])

            img = _synthetic_slice(dim_a, dim_b, slice_idx, blob_xy)
            img = np.clip((img + b_val) * c_val, 0, 2)

            fig = go.Figure(go.Heatmap(z=img, colorscale="Greys_r", showscale=False))

            if blob_xy is not None:
                bx, by = blob_xy
                fig.add_shape(type="line", x0=bx, x1=bx, y0=0, y1=dim_b, line={"color": "#22c55e", "width": 1, "dash": "dot"})
                fig.add_shape(type="line", x0=0, x1=dim_a, y0=by, y1=by, line={"color": "#22c55e", "width": 1, "dash": "dot"})
                fig.add_shape(
                    type="circle", x0=bx - dim_a * 0.04, x1=bx + dim_a * 0.04, y0=by - dim_b * 0.04, y1=by + dim_b * 0.04,
                    line={"color": "#ef4444", "width": 2},
                )

            fig.update_layout(
                height=440,
                margin={"t": 10, "b": 10, "l": 10, "r": 10},
                paper_bgcolor="#0b1220",
                plot_bgcolor="#0b1220",
                xaxis={"visible": False, "scaleanchor": "y"},
                yaxis={"visible": False, "autorange": "reversed"},
            )
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
            st.caption(f"Slice {slice_idx} / {dim_depth - 1} · {plane_name.lower()} plane")
