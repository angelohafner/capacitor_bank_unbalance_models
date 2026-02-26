# Comments in English only
from __future__ import annotations

import plotly.graph_objects as go


class CapacitorSymbol:
    """Capacitor symbol using two parallel plates (no conductor between plates)."""

    def __init__(
        self,
        *,
        plate_width: float = 0.9,
        plate_gap: float = 0.4,
        wire_width: int = 2,
        plate_line_width: int = 3,
    ):
        self.plate_width = float(plate_width)
        self.plate_gap = float(plate_gap)
        self.wire_width = int(wire_width)
        self.plate_line_width = int(plate_line_width)

    def draw(self, fig: go.Figure, *, x: float, y_center: float) -> tuple[float, float]:
        y_top_plate = y_center + self.plate_gap / 2.0
        y_bottom_plate = y_center - self.plate_gap / 2.0

        fig.add_trace(
            go.Scatter(
                x=[x - self.plate_width / 2.0, x + self.plate_width / 2.0],
                y=[y_top_plate, y_top_plate],
                mode="lines",
                line=dict(color="black", width=self.plate_line_width),
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[x - self.plate_width / 2.0, x + self.plate_width / 2.0],
                y=[y_bottom_plate, y_bottom_plate],
                mode="lines",
                line=dict(color="black", width=self.plate_line_width),
                showlegend=False,
            )
        )

        return y_top_plate, y_bottom_plate


class GroundSymbol:
    """Ground symbol with three horizontal bars."""

    def __init__(
        self,
        *,
        w1: float = 0.54,
        w2: float = 0.36,
        w3: float = 0.18,
        gap: float = 0.25,
        wire_width: int = 2,
    ):
        self.w1 = float(w1)
        self.w2 = float(w2)
        self.w3 = float(w3)
        self.gap = float(gap)
        self.wire_width = int(wire_width)

    def draw(self, fig: go.Figure, *, x: float, y_top: float) -> float:
        y1 = y_top
        y2 = y_top - self.gap
        y3 = y_top - 2.0 * self.gap

        fig.add_trace(
            go.Scatter(
                x=[x - self.w1 / 2.0, x + self.w1 / 2.0],
                y=[y1, y1],
                mode="lines",
                line=dict(color="black", width=self.wire_width),
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[x - self.w2 / 2.0, x + self.w2 / 2.0],
                y=[y2, y2],
                mode="lines",
                line=dict(color="black", width=self.wire_width),
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[x - self.w3 / 2.0, x + self.w3 / 2.0],
                y=[y3, y3],
                mode="lines",
                line=dict(color="black", width=self.wire_width),
                showlegend=False,
            )
        )

        return y3


class TRBox:
    """Rectangular TR box with centered label."""

    def __init__(
        self,
        *,
        width: float = 0.72,
        height: float = 1.2,
        wire_width: int = 2,
        text: str = "TR",
        font_size: int = 18,
    ):
        self.width = float(width)
        self.height = float(height)
        self.wire_width = int(wire_width)
        self.text = str(text)
        self.font_size = int(font_size)

    def draw(self, fig: go.Figure, *, x_center: float, y_top: float) -> float:
        y_bottom = y_top - self.height

        fig.add_shape(
            type="rect",
            x0=x_center - self.width / 2.0,
            x1=x_center + self.width / 2.0,
            y0=y_bottom,
            y1=y_top,
            line=dict(color="black", width=self.wire_width),
            fillcolor="white",
        )

        fig.add_annotation(
            x=x_center,
            y=(y_top + y_bottom) / 2.0,
            text=self.text,
            showarrow=False,
            font=dict(size=self.font_size, color="black"),
        )

        return y_bottom


class SeriesCapacitorString:
    """Vertical series string of capacitors."""

    def __init__(
        self,
        *,
        S: int = 4,
        unit_height: float = 2.4,
        capacitor: CapacitorSymbol | None = None,
        wire_width: int = 2,
    ):
        self.S = int(S)
        self.unit_height = float(unit_height)
        self.wire_width = int(wire_width)
        if capacitor is None:
            capacitor = CapacitorSymbol(wire_width=self.wire_width)
        self.capacitor = capacitor

    def draw(self, fig: go.Figure, *, x: float, y_top: float) -> float:
        y_current = float(y_top)

        for i in range(self.S):
            y_center = y_top - (i + 0.5) * self.unit_height
            y_top_plate, y_bottom_plate = self.capacitor.draw(fig, x=x, y_center=y_center)

            fig.add_trace(
                go.Scatter(
                    x=[x, x],
                    y=[y_current, y_top_plate],
                    mode="lines",
                    line=dict(color="black", width=self.wire_width),
                    showlegend=False,
                )
            )

            y_next = y_top - (i + 1) * self.unit_height
            fig.add_trace(
                go.Scatter(
                    x=[x, x],
                    y=[y_bottom_plate, y_next],
                    mode="lines",
                    line=dict(color="black", width=self.wire_width),
                    showlegend=False,
                )
            )

            y_current = y_next

        return y_current


class ThreePhaseYInternalFusesDiagram:
    """Three-phase single-wye diagram used for y_internal_fuses."""

    def __init__(
        self,
        *,
        S: int = 4,
        x_positions: list[float] | None = None,
        phase_labels: list[str] | None = None,
        y_top: float = 7.0,
        unit_height: float = 2.4,
        wire_width: int = 2,
        plate_line_width: int = 3,
        plate_width: float = 0.9,
        plate_gap: float = 0.4,
        tr_box_width: float = 0.72,
        tr_box_height: float = 1.2,
        tr_gap_above: float = 0.8,
        tr_gap_below: float = 0.9,
        ground_gap: float = 0.25,
        ground_w1: float = 0.54,
        ground_w2: float = 0.36,
        ground_w3: float = 0.18,
    ):
        if x_positions is None:
            x_positions = [-4.0, 0.0, 4.0]
        if phase_labels is None:
            phase_labels = ["Phase A", "Phase B", "Phase C"]

        self.S = int(S)
        self.x_positions = x_positions
        self.phase_labels = phase_labels
        self.y_top = float(y_top)
        self.unit_height = float(unit_height)
        self.wire_width = int(wire_width)

        self.capacitor = CapacitorSymbol(
            plate_width=plate_width,
            plate_gap=plate_gap,
            wire_width=wire_width,
            plate_line_width=plate_line_width,
        )
        self.string = SeriesCapacitorString(
            S=self.S,
            unit_height=self.unit_height,
            capacitor=self.capacitor,
            wire_width=self.wire_width,
        )

        self.tr_box = TRBox(
            width=tr_box_width,
            height=tr_box_height,
            wire_width=self.wire_width,
            text="TR",
            font_size=18,
        )
        self.ground = GroundSymbol(
            w1=ground_w1,
            w2=ground_w2,
            w3=ground_w3,
            gap=ground_gap,
            wire_width=self.wire_width,
        )

        self.tr_gap_above = float(tr_gap_above)
        self.tr_gap_below = float(tr_gap_below)

    def make_figure(self, *, width: int = 900, height: int = 700) -> go.Figure:
        fig = go.Figure()

        y_bottom_nodes: list[float] = []
        for x, label in zip(self.x_positions, self.phase_labels):
            y_bottom = self.string.draw(fig, x=x, y_top=self.y_top)
            y_bottom_nodes.append(y_bottom)

            fig.add_trace(
                go.Scatter(
                    x=[x],
                    y=[self.y_top],
                    mode="markers+text",
                    marker=dict(size=8, color="black"),
                    text=[label],
                    textposition="top center",
                    showlegend=False,
                )
            )

        y_star = y_bottom_nodes[0]

        fig.add_trace(
            go.Scatter(
                x=[self.x_positions[0], self.x_positions[-1]],
                y=[y_star, y_star],
                mode="lines",
                line=dict(color="black", width=self.wire_width),
                showlegend=False,
            )
        )

        x_center = 0.0
        y_tr_top = y_star - self.tr_gap_above
        fig.add_trace(
            go.Scatter(
                x=[x_center, x_center],
                y=[y_star, y_tr_top],
                mode="lines",
                line=dict(color="black", width=self.wire_width),
                showlegend=False,
            )
        )

        y_tr_bottom = self.tr_box.draw(fig, x_center=x_center, y_top=y_tr_top)

        y_ground_top = y_tr_bottom - self.tr_gap_below
        fig.add_trace(
            go.Scatter(
                x=[x_center, x_center],
                y=[y_tr_bottom, y_ground_top],
                mode="lines",
                line=dict(color="black", width=self.wire_width),
                showlegend=False,
            )
        )
        self.ground.draw(fig, x=x_center, y_top=y_ground_top)

        fig.update_layout(
            title=f"Three-Phase Y Capacitor Bank (S = {self.S}) with TR and Ground",
            width=width,
            height=height,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor="white",
            margin=dict(l=40, r=40, t=60, b=40),
        )

        return fig
