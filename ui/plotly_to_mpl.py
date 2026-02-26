# plotly_to_mpl.py
from __future__ import annotations

from typing import Tuple, Any, Dict, List, Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


def _parse_rgba_to_mpl(color_str: str):
    s = str(color_str).strip()
    if s.startswith("rgba(") is False:
        return (1.0, 1.0, 1.0, 1.0)
    s = s.replace("rgba(", "").replace(")", "")
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 4:
        return (1.0, 1.0, 1.0, 1.0)
    r = float(parts[0]) / 255.0
    g = float(parts[1]) / 255.0
    b = float(parts[2]) / 255.0
    a = float(parts[3])
    return (r, g, b, a)


def plotly_figure_to_matplotlib(fig_plotly: Any, figsize: Tuple[float, float] = (8.0, 8.0)) -> Tuple[Figure, Axes]:
    """
    Render a Plotly go.Figure (shapes + annotations) into Matplotlib.
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)

    shapes = list(getattr(fig_plotly.layout, "shapes", []) or [])
    annotations = list(getattr(fig_plotly.layout, "annotations", []) or [])

    # Draw shapes
    for shp in shapes:
        d = shp.to_plotly_json() if hasattr(shp, "to_plotly_json") else dict(shp)
        t = d.get("type", "")

        if t == "line":
            x0 = float(d["x0"]); x1 = float(d["x1"])
            y0 = float(d["y0"]); y1 = float(d["y1"])
            line_cfg = d.get("line", {}) or {}
            lw = float(line_cfg.get("width", 2.0))
            color = str(line_cfg.get("color", "black"))
            ax.plot([x0, x1], [y0, y1], linewidth=lw, color=color)

        if t == "rect":
            x0 = float(d["x0"]); x1 = float(d["x1"])
            y0 = float(d["y0"]); y1 = float(d["y1"])
            w = x1 - x0
            h = y1 - y0

            line_cfg = d.get("line", {}) or {}
            lw = float(line_cfg.get("width", 2.0))
            edge = str(line_cfg.get("color", "black"))

            fill = d.get("fillcolor", "rgba(255,255,255,1.0)")
            face = _parse_rgba_to_mpl(fill)

            ax.add_patch(Rectangle((x0, y0), w, h, linewidth=lw, edgecolor=edge, facecolor=face))

    # Draw annotations
    for ann in annotations:
        a = ann.to_plotly_json() if hasattr(ann, "to_plotly_json") else dict(ann)
        text = str(a.get("text", ""))
        x = float(a.get("x", 0.0))
        y = float(a.get("y", 0.0))

        xanchor = str(a.get("xanchor", "center"))
        yanchor = str(a.get("yanchor", "middle"))

        ha = "center"
        if xanchor == "left":
            ha = "left"
        if xanchor == "right":
            ha = "right"

        va = "center"
        if yanchor == "top":
            va = "top"
        if yanchor == "bottom":
            va = "bottom"

        fs = 11
        font_cfg = a.get("font", {}) or {}
        if "size" in font_cfg:
            fs = int(font_cfg["size"])

        ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color="black")

    # Axis ranges (important!)
    xr = getattr(fig_plotly.layout.xaxis, "range", None)
    yr = getattr(fig_plotly.layout.yaxis, "range", None)
    if xr is not None:
        ax.set_xlim(float(xr[0]), float(xr[1]))
    if yr is not None:
        ax.set_ylim(float(yr[0]), float(yr[1]))

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    return fig, ax
