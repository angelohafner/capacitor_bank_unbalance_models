# bank_diagram_mpl.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from bank_diagram import BankDiagram, SingleWyeBankDiagram


@dataclass
class MPLStyle:
    default_linewidth: float = 2.0
    default_color: str = "black"
    font_size: int = 11


def _parse_rgba_to_mpl(color_str: str) -> Tuple[float, float, float, float]:
    """
    Parse Plotly-like 'rgba(r,g,b,a)' into Matplotlib RGBA (0..1).
    """
    s = color_str.strip()
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


class BankDiagramMPL:
    """
    Matplotlib renderer for the existing Plotly BankDiagram.
    It reuses the exact same shapes/annotations so both outputs stay in sync.
    """

    def __init__(
        self,
        P: int = 3,
        S: int = 4,
        Pt: int = 11,
        Pa_left: int = 6,
        style: Optional[MPLStyle] = None,
        **kwargs: Any,
    ) -> None:
        if style is None:
            style = MPLStyle()
        self.style = style

        # Keep the same signature as the Plotly diagram
        self._plotly_diagram = BankDiagram(P=P, S=S, Pt=Pt, Pa_left=Pa_left, **kwargs)

        self._shapes: List[Dict[str, Any]] = []
        self._annotations: List[Dict[str, Any]] = []
        self._bounds: Dict[str, float] = {}

    def build(self) -> Tuple[List[Dict[str, Any]], Dict[str, float], List[Dict[str, Any]]]:
        shapes, bounds, annotations = self._plotly_diagram.build()
        self._shapes = shapes
        self._bounds = bounds
        self._annotations = annotations
        return shapes, bounds, annotations

    def make_figure(self, figsize: Tuple[float, float] = (8.0, 8.0)) -> Tuple[Figure, Axes]:
        if len(self._shapes) == 0:
            self.build()

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)

        # Draw shapes
        i = 0
        while i < len(self._shapes):
            shp = self._shapes[i]
            shp_type = shp.get("type", "")

            if shp_type == "line":
                x0 = float(shp["x0"])
                x1 = float(shp["x1"])
                y0 = float(shp["y0"])
                y1 = float(shp["y1"])

                line_cfg = shp.get("line", {})
                lw = float(line_cfg.get("width", self.style.default_linewidth))
                color = str(line_cfg.get("color", self.style.default_color))

                ax.plot([x0, x1], [y0, y1], linewidth=lw, color=color)

            if shp_type == "rect":
                x0 = float(shp["x0"])
                x1 = float(shp["x1"])
                y0 = float(shp["y0"])
                y1 = float(shp["y1"])

                w = x1 - x0
                h = y1 - y0

                line_cfg = shp.get("line", {})
                lw = float(line_cfg.get("width", self.style.default_linewidth))
                edge_color = str(line_cfg.get("color", self.style.default_color))

                fillcolor = shp.get("fillcolor", "rgba(255,255,255,1.0)")
                face_rgba = _parse_rgba_to_mpl(str(fillcolor))

                rect = Rectangle(
                    (x0, y0),
                    w,
                    h,
                    linewidth=lw,
                    edgecolor=edge_color,
                    facecolor=face_rgba,
                )
                ax.add_patch(rect)

            i = i + 1

        # Draw annotations (phase labels, etc.)
        j = 0
        while j < len(self._annotations):
            ann = self._annotations[j]
            text = str(ann.get("text", ""))

            x = float(ann.get("x", 0.0))
            y = float(ann.get("y", 0.0))

            xanchor = str(ann.get("xanchor", "center"))
            yanchor = str(ann.get("yanchor", "middle"))

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

            ax.text(x, y, text, ha=ha, va=va, fontsize=self.style.font_size, color="black")
            j = j + 1

        # Apply bounds from the Plotly diagram
        ax.set_xlim(float(self._bounds["x_min"]), float(self._bounds["x_max"]))
        ax.set_ylim(float(self._bounds["y_min"]), float(self._bounds["y_max"]))
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

        return fig, ax


class SingleWyeBankDiagramMPL(BankDiagramMPL):
    def __init__(
        self,
        P: int = 3,
        S: int = 4,
        Pt: int = 11,
        Pa_left: int = 6,
        style: Optional[MPLStyle] = None,
        **kwargs: Any,
    ) -> None:
        if style is None:
            style = MPLStyle()
        self.style = style

        # Single-wye uses the Plotly subclass
        self._plotly_diagram = SingleWyeBankDiagram(P=P, S=S, Pt=Pt, Pa_left=Pa_left, **kwargs)

        self._shapes = []
        self._annotations = []
        self._bounds = {}
