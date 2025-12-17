# Comments in English only
"""
H-bridge topology drawing helpers (Plotly shapes).

This module is adapted from the user's `ponte_h_desenho.py` example and is meant to be
used inside the Streamlit project (no Colab-specific bits).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

import plotly.graph_objects as go


# ============================================================
# Validation
# ============================================================

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]


def validate_h_bridge_inputs(S: int, St: int, Pt: int, Pa: int, P: int) -> ValidationResult:
    # Comments in English only
    errors: List[str] = []
    warnings: List[str] = []

    # Basic checks
    for name, val in [("S", S), ("St", St), ("Pt", Pt), ("Pa", Pa), ("P", P)]:
        if not isinstance(val, int):
            errors.append(f"{name} must be an integer.")
        else:
            if val < 1:
                errors.append(f"{name} must be >= 1.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    if S < 2:
        errors.append("S must be >= 2.")
    if St < 1 or St > (S - 1):
        errors.append("St must satisfy 1 <= St <= S-1.")
    if Pa < 1 or Pa >= Pt:
        errors.append("Pa must satisfy 1 <= Pa <= Pt-1.")
    if P < 1:
        errors.append("P must be >= 1.")
    if Pa < P:
        errors.append("Pa must be >= P.")
    if Pt < (2 * P):
        errors.append("Pt must be >= 2*P.")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # if (Pt % P) != 0:
    #     warnings.append("Pt is not a multiple of P (some parallel units may not be represented).")

    if ((Pt // P) % 2) != 0:
        warnings.append("Pt//P is odd (right-side split into two equal big groups becomes asymmetric).")

    if (Pa - P) < 1:
        warnings.append("Pa == P: left leg becomes a single ladder block (no split).")

    return ValidationResult(is_valid=True, errors=errors, warnings=warnings)


# ============================================================
# Symbols
# ============================================================

class CapacitorSymbolExact:
    def __init__(
        self,
        plate_gap: float = 0.25,
        plate_half_width: float = 0.45,
        line_color: str = "black",
        w_std: int = 2,
        w_plate: int = 4,
        fuse_enabled: bool = False,
        fuse_w: float = 0.35,
        fuse_h: float = 0.22,
    ):
        self.plate_gap = plate_gap
        self.plate_half_width = plate_half_width
        self.line_color = line_color
        self.w_std = w_std
        self.w_plate = w_plate

        self.fuse_enabled = fuse_enabled
        self.fuse_w = fuse_w
        self.fuse_h = fuse_h

    def shapes_between(self, x: float, y_top_node: float, y_bot_node: float) -> List[Dict]:
        if y_top_node <= y_bot_node:
            raise ValueError("y_top_node must be greater than y_bot_node")

        y_mid = 0.5 * (y_top_node + y_bot_node)
        y_top_plate = y_mid + 0.5 * self.plate_gap
        y_bot_plate = y_mid - 0.5 * self.plate_gap

        shapes: List[Dict] = []
        # Leads
        shapes.append(self._line(x, y_top_node, x, y_top_plate, self.w_std))
        shapes.append(self._line(x, y_bot_plate, x, y_bot_node, self.w_std))
        # Plates
        shapes.append(self._line(x - self.plate_half_width, y_top_plate, x + self.plate_half_width, y_top_plate, self.w_plate))
        shapes.append(self._line(x - self.plate_half_width, y_bot_plate, x + self.plate_half_width, y_bot_plate, self.w_plate))

        # Optional internal fuse symbol (simple small rectangle on the top lead)
        if self.fuse_enabled:
            y_fuse_center = 0.5 * (y_top_node + y_top_plate)
            shapes.append(
                dict(
                    type="rect",
                    x0=x - 0.5 * self.fuse_w,
                    y0=y_fuse_center - 0.5 * self.fuse_h,
                    x1=x + 0.5 * self.fuse_w,
                    y1=y_fuse_center + 0.5 * self.fuse_h,
                    line=dict(width=self.w_std, color=self.line_color),
                    fillcolor="rgba(0,0,0,0)",
                )
            )

        return shapes

    def _line(self, x1: float, y1: float, x2: float, y2: float, width: int) -> Dict:
        return dict(type="line", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(width=width, color=self.line_color))


# ============================================================
# Geometry building blocks
# ============================================================

class LadderBlock:
    def __init__(
        self,
        S: int = 7,
        n_parallel: int = 2,
        x0: float = 0.0,
        y0: float = 0.0,
        dx_string: float = 2.2,
        dy_level: float = 2.8,
        line_color: str = "black",
        w_std: int = 2,
        w_plate: int = 4,
        fuse_enabled: bool = False,
    ):
        self.S = S
        self.n_parallel = n_parallel
        self.x0 = x0
        self.y0 = y0
        self.dx_string = dx_string
        self.dy_level = dy_level

        self.line_color = line_color
        self.w_std = w_std

        self.cap = CapacitorSymbolExact(
            plate_gap=0.25,
            plate_half_width=0.45,
            line_color=line_color,
            w_std=w_std,
            w_plate=w_plate,
            fuse_enabled=fuse_enabled,
        )

    def build(self) -> Dict[str, object]:
        shapes: List[Dict] = []

        xs: List[float] = []
        k = 0
        while k < self.n_parallel:
            xs.append(self.x0 + k * self.dx_string)
            k = k + 1

        y_nodes: List[float] = []
        i = 0
        while i < (self.S + 1):
            y_nodes.append(self.y0 - i * self.dy_level)
            i = i + 1

        j = 0
        while j < self.n_parallel:
            xj = xs[j]
            i = 0
            while i < self.S:
                shapes = shapes + self.cap.shapes_between(x=xj, y_top_node=y_nodes[i], y_bot_node=y_nodes[i + 1])
                i = i + 1
            j = j + 1

        x_left = xs[0]
        x_right = xs[-1]

        i = 0
        while i < (self.S + 1):
            yi = y_nodes[i]
            shapes.append(self._line(x_left, yi, x_right, yi))
            i = i + 1

        return {
            "shapes": shapes,
            "x_left": x_left,
            "x_right": x_right,
            "y_top": y_nodes[0],
            "y_bottom": y_nodes[-1],
            "y_nodes": y_nodes,
        }

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> Dict:
        return dict(type="line", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(width=self.w_std, color=self.line_color))


class HLeftLeg:
    def __init__(
        self,
        S: int = 7,
        P: int = 2,
        Pa: int = 5,
        dx_string: float = 2.2,
        dy_level: float = 2.8,
        x_gap: float = 8.0,
        line_color: str = "black",
        w_std: int = 2,
        w_plate: int = 4,
        fuse_enabled: bool = False,
    ):
        self.S = S
        self.P = P
        self.Pa = Pa
        self.x_gap = x_gap
        self.line_color = line_color
        self.w_std = w_std

        self.block_left = LadderBlock(S=S, n_parallel=P, dx_string=dx_string, dy_level=dy_level, line_color=line_color, w_std=w_std, w_plate=w_plate, fuse_enabled=fuse_enabled)
        self.block_right = LadderBlock(S=S, n_parallel=(Pa - P), dx_string=dx_string, dy_level=dy_level, line_color=line_color, w_std=w_std, w_plate=w_plate, fuse_enabled=fuse_enabled)

    def build(self, x0: float = 0.0, y0: float = 0.0) -> Dict[str, object]:
        shapes: List[Dict] = []

        self.block_left.x0 = x0
        self.block_left.y0 = y0
        b1 = self.block_left.build()
        shapes = shapes + b1["shapes"]

        # If (Pa - P) == 0, the right block degenerates; keep behavior stable.
        if (self.Pa - self.P) > 0:
            self.block_right.x0 = x0 + self.x_gap
            self.block_right.y0 = y0
            b2 = self.block_right.build()
            shapes = shapes + b2["shapes"]
            x_right = b2["x_right"]
            x_right_bus = b2["x_left"]
        else:
            b2 = None
            x_right = b1["x_right"]
            x_right_bus = b1["x_right"]

        y_top = b1["y_top"]
        y_bottom = b1["y_bottom"]

        x_left_bus = b1["x_right"]

        shapes.append(self._line(x_left_bus, y_top, x_right_bus, y_top))
        shapes.append(self._line(x_left_bus, y_bottom, x_right_bus, y_bottom))

        return {
            "shapes": shapes,
            "x_left": b1["x_left"],
            "x_right": x_right,
            "y_top": y_top,
            "y_bottom": y_bottom,
            "y_nodes": b1["y_nodes"],
        }

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> Dict:
        return dict(type="line", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(width=self.w_std, color=self.line_color))


class HRightLeg:
    def __init__(
        self,
        Pt: int = 9,
        P: int = 2,
        S: int = 7,
        dx_string: float = 2.2,
        dy_level: float = 2.8,
        x_gap_big: float = 9.0,
        line_color: str = "black",
        w_std: int = 2,
        w_plate: int = 4,
        fuse_enabled: bool = False,
    ):
        self.Pt = Pt
        self.P = P
        self.S = S
        self.x_gap_big = x_gap_big
        self.line_color = line_color
        self.w_std = w_std

        n_strings_total = self.Pt // self.P
        self.n_big_groups = n_strings_total // 2

        self.blocks: List[LadderBlock] = []
        idx = 0
        while idx < self.n_big_groups:
            self.blocks.append(LadderBlock(S=S, n_parallel=P, dx_string=dx_string, dy_level=dy_level, line_color=line_color, w_std=w_std, w_plate=w_plate, fuse_enabled=fuse_enabled))
            idx = idx + 1

    def build(self, x0: float = 0.0, y0: float = 0.0) -> Dict[str, object]:
        if self.n_big_groups < 1:
            raise ValueError("n_big_groups must be >= 1")

        shapes: List[Dict] = []
        built: List[Dict[str, object]] = []

        idx = 0
        while idx < len(self.blocks):
            blk = self.blocks[idx]
            blk.x0 = x0 + idx * self.x_gap_big
            blk.y0 = y0
            b = blk.build()
            built.append(b)
            shapes = shapes + b["shapes"]
            idx = idx + 1

        y_top = built[0]["y_top"]
        y_bottom = built[0]["y_bottom"]

        x_min = built[0]["x_left"]
        x_max = built[0]["x_right"]

        idx = 1
        while idx < len(built):
            if built[idx]["x_left"] < x_min:
                x_min = built[idx]["x_left"]
            if built[idx]["x_right"] > x_max:
                x_max = built[idx]["x_right"]
            idx = idx + 1

        shapes.append(self._line(x_min, y_top, x_max, y_top))
        shapes.append(self._line(x_min, y_bottom, x_max, y_bottom))

        return {
            "shapes": shapes,
            "x_left": x_min,
            "x_right": x_max,
            "y_top": y_top,
            "y_bottom": y_bottom,
            "y_nodes": built[0]["y_nodes"],
        }

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> Dict:
        return dict(type="line", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(width=self.w_std, color=self.line_color))


class HCompleteWithNeutralCT:
    def __init__(
        self,
        Pt: int = 9,
        Pa: int = 5,
        P: int = 2,
        S: int = 7,
        St: int = 3,
        dx_string: float = 2.2,
        dy_level: float = 2.8,
        gap_between_legs: float = 14.0,
        left_internal_gap: float = 8.0,
        right_group_gap: float = 9.0,
        bus_stub: float = 7.0,
        ct_box_w: float = 3.2,
        ct_box_h: float = 1.4,
        line_color: str = "black",
        w_std: int = 2,
        w_plate: int = 4,
        fuse_enabled: bool = False,
    ):
        self.Pt = Pt
        self.Pa = Pa
        self.P = P
        self.S = S
        self.St = St

        self.gap_between_legs = gap_between_legs
        self.bus_stub = bus_stub
        self.ct_box_w = ct_box_w
        self.ct_box_h = ct_box_h

        self.line_color = line_color
        self.w_std = w_std

        if (St < 1) or (St > (S - 1)):
            raise ValueError("St must satisfy 1 <= St <= S-1")

        self.left_leg = HLeftLeg(S=S, P=P, Pa=Pa, dx_string=dx_string, dy_level=dy_level, x_gap=left_internal_gap, line_color=line_color, w_std=w_std, w_plate=w_plate, fuse_enabled=fuse_enabled)
        self.right_leg = HRightLeg(Pt=Pt, P=P, S=S, dx_string=dx_string, dy_level=dy_level, x_gap_big=right_group_gap, line_color=line_color, w_std=w_std, w_plate=w_plate, fuse_enabled=fuse_enabled)

    def make_figure(self, x0: float = 0.0, y0: float = 0.0, width: int = 1600, height: int = 400,
                    title: Optional[str] = None) -> go.Figure:
        shapes: List[Dict] = []
        annotations: List[Dict] = []

        left = self.left_leg.build(x0=x0, y0=y0)
        shapes = shapes + left["shapes"]

        x_right_leg = left["x_right"] + self.gap_between_legs
        right = self.right_leg.build(x0=x_right_leg, y0=y0)
        shapes = shapes + right["shapes"]

        y_top = left["y_top"]
        y_bottom = left["y_bottom"]
        x_global_left = left["x_left"]
        x_global_right = right["x_right"]

        # Global top/bottom buses
        shapes.append(self._line(x_global_left, y_top, x_global_right, y_top))
        shapes.append(self._line(x_global_left, y_bottom, x_global_right, y_bottom))

        # Center stubs (top and bottom) - shortened to 1/4 of bus_stub (visual only)
        x_center = 0.5 * (x_global_left + x_global_right)
        stub_len = 0.25 * self.bus_stub
        shapes.append(self._line(x_center, y_top, x_center, y_top + stub_len))
        shapes.append(self._line(x_center, y_bottom, x_center, y_bottom - stub_len))

        # Neutral line y from St: k = S - St
        k = self.S - self.St
        y_neutral = left["y_nodes"][k]

        # CT box coords
        x_ct0 = x_center - 0.5 * self.ct_box_w
        x_ct1 = x_center + 0.5 * self.ct_box_w
        y_ct0 = y_neutral - 0.5 * self.ct_box_h
        y_ct1 = y_neutral + 0.5 * self.ct_box_h

        # Neutral line split: stop at box edges (do not cross the box)
        shapes.append(self._line(x_global_left, y_neutral, x_ct0, y_neutral))
        shapes.append(self._line(x_ct1, y_neutral, x_global_right, y_neutral))

        # CT box
        shapes.append(
            dict(
                type="rect",
                x0=x_ct0,
                y0=y_ct0,
                x1=x_ct1,
                y1=y_ct1,
                line=dict(width=self.w_std, color=self.line_color),
                fillcolor="white",
            )
        )

        # CT label
        annotations.append(
            dict(
                x=x_center,
                y=y_neutral,
                text="CT",
                showarrow=False,
                font=dict(size=18, color="black"),
                xanchor="center",
                yanchor="middle",
            )
        )

        # Limits
        pad_x = 1.0
        pad_y = 0.2
        x_min = x_global_left - pad_x
        x_max = x_global_right + pad_x
        y_min = y_bottom - stub_len - pad_y
        y_max = y_top + stub_len + pad_y

        fig = go.Figure()
        fig.update_layout(
            shapes=shapes,
            annotations=annotations,
            xaxis=dict(visible=False, range=[x_min, x_max], fixedrange=True),
            yaxis=dict(visible=False, range=[y_min, y_max], fixedrange=True),
            width=width,
            height=height,
            margin=dict(l=5, r=5, t=20 if title else 5, b=5),
            title=dict(text=title, x=0.5) if title else None,
        )
        return fig

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> Dict:
        return dict(type="line", x0=x1, y0=y1, x1=x2, y1=y2, line=dict(width=self.w_std, color=self.line_color))
