import plotly.graph_objects as go


class Group:
    def __init__(
        self,
        P=3,
        S=4,
        Pa=6,
        x0=0.0,
        y0=0.0,
        dx=1.6,
        dy=2.4,
        block_gap=3.2,
        plate_gap=0.25,
        plate_half_width=0.45,
        lead_length=0.75,
        global_bus_offset=1.2,
        terminal_extra=1.0,
        add_center_terminals=True,
        line_color="black",
        w_std=2,
        w_plate=4,
    ):
        self.P = P
        self.S = S
        self.Pa = Pa
        self.x0 = x0
        self.y0 = y0
        self.dx = dx
        self.dy = dy
        self.block_gap = block_gap
        self.plate_gap = plate_gap
        self.plate_half_width = plate_half_width
        self.lead_length = lead_length
        self.global_bus_offset = global_bus_offset
        self.terminal_extra = terminal_extra
        self.add_center_terminals = add_center_terminals
        self.line_color = line_color
        self.w_std = w_std
        self.w_plate = w_plate

        self._shapes = []
        self._bounds = {"x_min": 0.0, "x_max": 0.0, "y_min": 0.0, "y_max": 0.0}
        self._n_blocks = 0

        # Exposed ports
        self.x_center = None
        self.y_top_global = None
        self.y_bot_global = None

    def _draw_capacitor_shapes(self, x=0.0, y=0.0):
        y_top_plate = y + self.plate_gap / 2.0
        y_bot_plate = y - self.plate_gap / 2.0

        shapes = []

        shapes.append(
            dict(
                type="line",
                x0=x,
                x1=x,
                y0=y_top_plate,
                y1=y_top_plate + self.lead_length,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        shapes.append(
            dict(
                type="line",
                x0=x,
                x1=x,
                y0=y_bot_plate,
                y1=y_bot_plate - self.lead_length,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        shapes.append(
            dict(
                type="line",
                x0=x - self.plate_half_width,
                x1=x + self.plate_half_width,
                y0=y_top_plate,
                y1=y_top_plate,
                line=dict(width=self.w_plate, color=self.line_color),
            )
        )

        shapes.append(
            dict(
                type="line",
                x0=x - self.plate_half_width,
                x1=x + self.plate_half_width,
                y0=y_bot_plate,
                y1=y_bot_plate,
                line=dict(width=self.w_plate, color=self.line_color),
            )
        )

        return shapes

    def _draw_parallel_group(self, P=3, x0=0.0, y0=0.0):
        shapes = []

        i = 0
        while i < P:
            xi = x0 + float(i) * self.dx
            shapes = shapes + self._draw_capacitor_shapes(x=xi, y=y0)
            i = i + 1

        x_left = x0
        x_right = x0 + float(P - 1) * self.dx

        y_top_bus = y0 + self.plate_gap / 2.0 + self.lead_length
        y_bot_bus = y0 - self.plate_gap / 2.0 - self.lead_length

        shapes.append(
            dict(
                type="line",
                x0=x_left,
                x1=x_right,
                y0=y_top_bus,
                y1=y_top_bus,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        shapes.append(
            dict(
                type="line",
                x0=x_left,
                x1=x_right,
                y0=y_bot_bus,
                y1=y_bot_bus,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        info = {
            "y_top_bus": y_top_bus,
            "y_bot_bus": y_bot_bus,
            "x_left": x_left,
            "x_right": x_right,
        }
        return shapes, info

    def _draw_series_of_parallel_groups(self, P=3, S=4, x0=0.0, y0=0.0):
        shapes = []
        infos = []

        k = 0
        while k < S:
            yk = y0 - float(k) * self.dy
            g_shapes, g_info = self._draw_parallel_group(P=P, x0=x0, y0=yk)
            shapes = shapes + g_shapes
            infos.append(g_info)
            k = k + 1

        x_link = x0 + 0.5 * float(P - 1) * self.dx

        k = 0
        while k < (S - 1):
            shapes.append(
                dict(
                    type="line",
                    x0=x_link,
                    x1=x_link,
                    y0=infos[k]["y_bot_bus"],
                    y1=infos[k + 1]["y_top_bus"],
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )
            k = k + 1

        ports = {
            "x_link": x_link,
            "y_top": infos[0]["y_top_bus"],
            "y_bot": infos[S - 1]["y_bot_bus"],
        }

        bounds = {
            "x_min": x0 - 1.2,
            "x_max": x0 + float(P - 1) * self.dx + 1.2,
            "y_max": ports["y_top"] + 1.6,
            "y_min": ports["y_bot"] - 1.6,
        }

        return shapes, bounds, ports

    def build(self):
        if self.P < 1:
            raise ValueError("P must be >= 1")
        if self.Pa < 0:
            raise ValueError("Pa must be >= 0")
        if (self.Pa % self.P) != 0:
            raise ValueError(f"Invalid: Pa/P must be integer. Got Pa={self.Pa}, P={self.P}")

        self._n_blocks = int(self.Pa / self.P)
        if self._n_blocks < 1:
            raise ValueError("Pa/P resulted in 0 blocks. Increase Pa or reduce P.")

        shapes_all = []
        ports_list = []
        bounds_list = []

        block_width = float(self.P - 1) * self.dx

        b = 0
        while b < self._n_blocks:
            xb = self.x0 + float(b) * (block_width + self.block_gap)

            block_shapes, block_bounds, block_ports = self._draw_series_of_parallel_groups(
                P=self.P,
                S=self.S,
                x0=xb,
                y0=self.y0,
            )

            shapes_all = shapes_all + block_shapes
            ports_list.append(block_ports)
            bounds_list.append(block_bounds)

            b = b + 1

        y_top_node = ports_list[0]["y_top"]
        y_bot_node = ports_list[0]["y_bot"]

        self.y_top_global = y_top_node + self.global_bus_offset
        self.y_bot_global = y_bot_node - self.global_bus_offset

        x_left = ports_list[0]["x_link"]
        x_right = ports_list[self._n_blocks - 1]["x_link"]
        self.x_center = 0.5 * (x_left + x_right)

        shapes_all.append(
            dict(
                type="line",
                x0=x_left,
                x1=x_right,
                y0=self.y_top_global,
                y1=self.y_top_global,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        shapes_all.append(
            dict(
                type="line",
                x0=x_left,
                x1=x_right,
                y0=self.y_bot_global,
                y1=self.y_bot_global,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        b = 0
        while b < self._n_blocks:
            xb = ports_list[b]["x_link"]

            shapes_all.append(
                dict(
                    type="line",
                    x0=xb,
                    x1=xb,
                    y0=self.y_top_global,
                    y1=y_top_node,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

            shapes_all.append(
                dict(
                    type="line",
                    x0=xb,
                    x1=xb,
                    y0=y_bot_node,
                    y1=self.y_bot_global,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

            b = b + 1

        if self.add_center_terminals is True:
            shapes_all.append(
                dict(
                    type="line",
                    x0=self.x_center,
                    x1=self.x_center,
                    y0=self.y_top_global,
                    y1=self.y_top_global + self.terminal_extra,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

            shapes_all.append(
                dict(
                    type="line",
                    x0=self.x_center,
                    x1=self.x_center,
                    y0=self.y_bot_global - self.terminal_extra,
                    y1=self.y_bot_global,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

        x_min = bounds_list[0]["x_min"]
        x_max = bounds_list[0]["x_max"]
        y_min = bounds_list[0]["y_min"]
        y_max = bounds_list[0]["y_max"]

        b = 1
        while b < self._n_blocks:
            if bounds_list[b]["x_min"] < x_min:
                x_min = bounds_list[b]["x_min"]
            if bounds_list[b]["x_max"] > x_max:
                x_max = bounds_list[b]["x_max"]
            if bounds_list[b]["y_min"] < y_min:
                y_min = bounds_list[b]["y_min"]
            if bounds_list[b]["y_max"] > y_max:
                y_max = bounds_list[b]["y_max"]
            b = b + 1

        if self.y_top_global + self.terminal_extra + 0.8 > y_max:
            y_max = self.y_top_global + self.terminal_extra + 0.8
        if self.y_bot_global - self.terminal_extra - 0.8 < y_min:
            y_min = self.y_bot_global - self.terminal_extra - 0.8

        self._shapes = shapes_all
        self._bounds = {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}

        return self._shapes, self._bounds, self._n_blocks


class GroupPartial(Group):
    """
    Like Group, but draws a total Pt that may not be a multiple of P.
    It draws full blocks of size P, plus one last partial block if Pt % P != 0.
    """

    def __init__(self, Pt=5, **kwargs):
        super().__init__(Pa=0, **kwargs)
        self.Pt = Pt

    def build(self):
        if self.P < 1:
            raise ValueError("P must be >= 1")
        if self.Pt < 1:
            raise ValueError("Pt must be >= 1")

        n_full = int(self.Pt // self.P)
        p_last = int(self.Pt - self.P * n_full)

        n_blocks = n_full
        if p_last > 0:
            n_blocks = n_blocks + 1

        shapes_all = []
        ports_list = []
        bounds_list = []

        block_width_full = float(self.P - 1) * self.dx

        b = 0
        while b < n_blocks:
            is_last_partial = False
            if (b == n_blocks - 1) and (p_last > 0):
                is_last_partial = True

            if is_last_partial is True:
                P_block = p_last
            else:
                P_block = self.P

            xb = self.x0 + float(b) * (block_width_full + self.block_gap)

            block_shapes, block_bounds, block_ports = self._draw_series_of_parallel_groups(
                P=P_block,
                S=self.S,
                x0=xb,
                y0=self.y0,
            )

            shapes_all = shapes_all + block_shapes
            ports_list.append(block_ports)
            bounds_list.append(block_bounds)

            b = b + 1

        y_top_node = ports_list[0]["y_top"]
        y_bot_node = ports_list[0]["y_bot"]

        self.y_top_global = y_top_node + self.global_bus_offset
        self.y_bot_global = y_bot_node - self.global_bus_offset

        x_left = ports_list[0]["x_link"]
        x_right = ports_list[n_blocks - 1]["x_link"]
        self.x_center = 0.5 * (x_left + x_right)

        shapes_all.append(
            dict(
                type="line",
                x0=x_left,
                x1=x_right,
                y0=self.y_top_global,
                y1=self.y_top_global,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        shapes_all.append(
            dict(
                type="line",
                x0=x_left,
                x1=x_right,
                y0=self.y_bot_global,
                y1=self.y_bot_global,
                line=dict(width=self.w_std, color=self.line_color),
            )
        )

        b = 0
        while b < n_blocks:
            xb = ports_list[b]["x_link"]

            shapes_all.append(
                dict(
                    type="line",
                    x0=xb,
                    x1=xb,
                    y0=self.y_top_global,
                    y1=y_top_node,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

            shapes_all.append(
                dict(
                    type="line",
                    x0=xb,
                    x1=xb,
                    y0=y_bot_node,
                    y1=self.y_bot_global,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

            b = b + 1

        if self.add_center_terminals is True:
            shapes_all.append(
                dict(
                    type="line",
                    x0=self.x_center,
                    x1=self.x_center,
                    y0=self.y_top_global,
                    y1=self.y_top_global + self.terminal_extra,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

            shapes_all.append(
                dict(
                    type="line",
                    x0=self.x_center,
                    x1=self.x_center,
                    y0=self.y_bot_global - self.terminal_extra,
                    y1=self.y_bot_global,
                    line=dict(width=self.w_std, color=self.line_color),
                )
            )

        x_min = bounds_list[0]["x_min"]
        x_max = bounds_list[0]["x_max"]
        y_min = bounds_list[0]["y_min"]
        y_max = bounds_list[0]["y_max"]

        b = 1
        while b < n_blocks:
            if bounds_list[b]["x_min"] < x_min:
                x_min = bounds_list[b]["x_min"]
            if bounds_list[b]["x_max"] > x_max:
                x_max = bounds_list[b]["x_max"]
            if bounds_list[b]["y_min"] < y_min:
                y_min = bounds_list[b]["y_min"]
            if bounds_list[b]["y_max"] > y_max:
                y_max = bounds_list[b]["y_max"]
            b = b + 1

        if self.y_top_global + self.terminal_extra + 0.8 > y_max:
            y_max = self.y_top_global + self.terminal_extra + 0.8
        if self.y_bot_global - self.terminal_extra - 0.8 < y_min:
            y_min = self.y_bot_global - self.terminal_extra - 0.8

        self._shapes = shapes_all
        self._bounds = {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}

        return self._shapes, self._bounds, n_blocks


class Branch:
    def __init__(self, group: Group, group_gap=0.5, star_drop=1.2):
        self.group = group
        self.group_gap = group_gap
        self.star_drop = star_drop

        self._shapes = []
        self._bounds = {"x_min": 0.0, "x_max": 0.0, "y_min": 0.0, "y_max": 0.0}

        # Exposed ports
        self.x_centers = []
        self.y_star = None
        self.y_top_globals = []
        self.y_bot_globals = []

    def _clone_like(self, base_group, x0_new):
        # Comment: Clone base_group preserving its type (Group vs GroupPartial)
        if isinstance(base_group, GroupPartial) is True:
            g = GroupPartial(
                Pt=base_group.Pt,
                P=base_group.P,
                S=base_group.S,
                x0=x0_new,
                y0=base_group.y0,
                dx=base_group.dx,
                dy=base_group.dy,
                block_gap=base_group.block_gap,
                plate_gap=base_group.plate_gap,
                plate_half_width=base_group.plate_half_width,
                lead_length=base_group.lead_length,
                global_bus_offset=base_group.global_bus_offset,
                terminal_extra=base_group.terminal_extra,
                add_center_terminals=base_group.add_center_terminals,
                line_color=base_group.line_color,
                w_std=base_group.w_std,
                w_plate=base_group.w_plate,
            )
            return g

        g = Group(
            P=base_group.P,
            S=base_group.S,
            Pa=base_group.Pa,
            x0=x0_new,
            y0=base_group.y0,
            dx=base_group.dx,
            dy=base_group.dy,
            block_gap=base_group.block_gap,
            plate_gap=base_group.plate_gap,
            plate_half_width=base_group.plate_half_width,
            lead_length=base_group.lead_length,
            global_bus_offset=base_group.global_bus_offset,
            terminal_extra=base_group.terminal_extra,
            add_center_terminals=base_group.add_center_terminals,
            line_color=base_group.line_color,
            w_std=base_group.w_std,
            w_plate=base_group.w_plate,
        )
        return g

    def build(self):
        g0 = self._clone_like(self.group, self.group.x0)
        s0, b0, _ = g0.build()
        width0 = b0["x_max"] - b0["x_min"]

        g1 = self._clone_like(self.group, self.group.x0 + (width0 + self.group_gap))
        s1, b1, _ = g1.build()

        g2 = self._clone_like(self.group, self.group.x0 + 2.0 * (width0 + self.group_gap))
        s2, b2, _ = g2.build()

        shapes_all = []
        shapes_all = shapes_all + s0
        shapes_all = shapes_all + s1
        shapes_all = shapes_all + s2

        y_bot_min = g0.y_bot_global
        if g1.y_bot_global < y_bot_min:
            y_bot_min = g1.y_bot_global
        if g2.y_bot_global < y_bot_min:
            y_bot_min = g2.y_bot_global

        self.y_star = y_bot_min - self.star_drop

        shapes_all.append(
            dict(
                type="line",
                x0=g0.x_center,
                x1=g2.x_center,
                y0=self.y_star,
                y1=self.y_star,
                line=dict(width=self.group.w_std, color=self.group.line_color),
            )
        )

        shapes_all.append(
            dict(
                type="line",
                x0=g0.x_center,
                x1=g0.x_center,
                y0=g0.y_bot_global,
                y1=self.y_star,
                line=dict(width=self.group.w_std, color=self.group.line_color),
            )
        )
        shapes_all.append(
            dict(
                type="line",
                x0=g1.x_center,
                x1=g1.x_center,
                y0=g1.y_bot_global,
                y1=self.y_star,
                line=dict(width=self.group.w_std, color=self.group.line_color),
            )
        )
        shapes_all.append(
            dict(
                type="line",
                x0=g2.x_center,
                x1=g2.x_center,
                y0=g2.y_bot_global,
                y1=self.y_star,
                line=dict(width=self.group.w_std, color=self.group.line_color),
            )
        )

        x_min = min(b0["x_min"], b1["x_min"], b2["x_min"])
        x_max = max(b0["x_max"], b1["x_max"], b2["x_max"])
        y_min = min(b0["y_min"], b1["y_min"], b2["y_min"], self.y_star - 0.8)
        y_max = max(b0["y_max"], b1["y_max"], b2["y_max"])

        self._shapes = shapes_all
        self._bounds = {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}

        self.x_centers = [g0.x_center, g1.x_center, g2.x_center]
        self.y_top_globals = [g0.y_top_global, g1.y_top_global, g2.y_top_global]
        self.y_bot_globals = [g0.y_bot_global, g1.y_bot_global, g2.y_bot_global]

        return self._shapes, self._bounds


class BankDiagram:
    def __init__(
        self,
        P=3,
        S=4,
        Pt=11,
        Pa_left=6,
        x0=0.0,
        y0=0.0,
        dx=1.6,
        dy=2.4,
        block_gap=3.2,
        plate_gap=0.25,
        plate_half_width=0.45,
        lead_length=0.75,
        global_bus_offset=1.2,
        terminal_extra=1.0,
        add_center_terminals=True,
        line_color="black",
        w_std=2,
        w_plate=4,
        branch_group_gap=0.5,
        branch_star_drop=1.2,
        right_extra_gap=3.0,
        fig_width=800,
        fig_height=500,
        # CT / TR geometry
        ct_w=1.6,
        ct_h=0.9,
        tr_w=1.2,
        tr_h=0.9,
        gap_down_ct_tr=0.6,
        gap_down_tr_gnd=0.6,
        # Ground symbol
        ground_w1=1.2,
        ground_w2=0.8,
        ground_w3=0.4,
        ground_dy=0.2,
        # Phase buses
        phase_bus_offset=1.8,
        phase_bus_spacing=0.9,
        phase_drop_gap=0.2,
        phase_label_offset=1.2,
    ):
        self.P = P
        self.S = S
        self.Pt = Pt
        self.Pa_left = Pa_left

        self.x0 = x0
        self.y0 = y0
        self.dx = dx
        self.dy = dy
        self.block_gap = block_gap
        self.plate_gap = plate_gap
        self.plate_half_width = plate_half_width
        self.lead_length = lead_length
        self.global_bus_offset = global_bus_offset
        self.terminal_extra = terminal_extra
        self.add_center_terminals = add_center_terminals
        self.line_color = line_color
        self.w_std = w_std
        self.w_plate = w_plate

        self.branch_group_gap = branch_group_gap
        self.branch_star_drop = branch_star_drop
        self.right_extra_gap = right_extra_gap

        self.fig_width = fig_width
        self.fig_height = fig_height

        self.ct_w = ct_w
        self.ct_h = ct_h
        self.tr_w = tr_w
        self.tr_h = tr_h
        self.gap_down_ct_tr = gap_down_ct_tr
        self.gap_down_tr_gnd = gap_down_tr_gnd

        self.ground_w1 = ground_w1
        self.ground_w2 = ground_w2
        self.ground_w3 = ground_w3
        self.ground_dy = ground_dy

        self.phase_bus_offset = phase_bus_offset
        self.phase_bus_spacing = phase_bus_spacing
        self.phase_drop_gap = phase_drop_gap
        self.phase_label_offset = phase_label_offset

        self._shapes = []
        self._annotations = []
        self._bounds = {"x_min": 0.0, "x_max": 0.0, "y_min": 0.0, "y_max": 0.0}

    def _line(self, x0, x1, y0, y1):
        return dict(
            type="line",
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
            line=dict(width=self.w_std, color=self.line_color),
        )

    def _rect(self, x0, x1, y0, y1):
        return dict(
            type="rect",
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
            line=dict(width=self.w_std, color=self.line_color),
            fillcolor="rgba(255,255,255,1.0)",
        )

    def _build_left_branch(self):
        left_group = Group(
            P=self.P,
            S=self.S,
            Pa=self.Pa_left,
            x0=self.x0,
            y0=self.y0,
            dx=self.dx,
            dy=self.dy,
            block_gap=self.block_gap,
            plate_gap=self.plate_gap,
            plate_half_width=self.plate_half_width,
            lead_length=self.lead_length,
            global_bus_offset=self.global_bus_offset,
            terminal_extra=self.terminal_extra,
            add_center_terminals=self.add_center_terminals,
            line_color=self.line_color,
            w_std=self.w_std,
            w_plate=self.w_plate,
        )
        left_branch = Branch(left_group, group_gap=self.branch_group_gap, star_drop=self.branch_star_drop)
        shapes_l, bounds_l = left_branch.build()
        return left_branch, shapes_l, bounds_l

    def _build_right_branch(self, x0_right):
        pb = self.Pt - self.Pa_left
        if pb < 1:
            raise ValueError("Pt - Pa_left must be >= 1 for the right wye.")

        right_group = GroupPartial(
            Pt=pb,
            P=self.P,
            S=self.S,
            x0=x0_right,
            y0=self.y0,
            dx=self.dx,
            dy=self.dy,
            block_gap=self.block_gap,
            plate_gap=self.plate_gap,
            plate_half_width=self.plate_half_width,
            lead_length=self.lead_length,
            global_bus_offset=self.global_bus_offset,
            terminal_extra=self.terminal_extra,
            add_center_terminals=self.add_center_terminals,
            line_color=self.line_color,
            w_std=self.w_std,
            w_plate=self.w_plate,
        )
        right_branch = Branch(right_group, group_gap=self.branch_group_gap, star_drop=self.branch_star_drop)
        shapes_r, bounds_r = right_branch.build()
        return right_branch, shapes_r, bounds_r

    def _add_ct_tr_ground(self, shapes, annotations, x_l, x_r, y_star):
        x_mid = 0.5 * (x_l + x_r)

        ct_y0 = y_star - 0.5 * self.ct_h
        ct_y1 = y_star + 0.5 * self.ct_h
        ct_x0 = x_mid - 0.5 * self.ct_w
        ct_x1 = x_mid + 0.5 * self.ct_w

        tr_y1 = ct_y0 - self.gap_down_ct_tr
        tr_y0 = tr_y1 - self.tr_h
        tr_x0 = x_mid - 0.5 * self.tr_w
        tr_x1 = x_mid + 0.5 * self.tr_w

        shapes.append(self._line(x0=x_l, x1=ct_x0, y0=y_star, y1=y_star))
        shapes.append(self._line(x0=ct_x1, x1=x_r, y0=y_star, y1=y_star))

        shapes.append(self._rect(x0=ct_x0, x1=ct_x1, y0=ct_y0, y1=ct_y1))
        shapes.append(self._line(x0=x_mid, x1=x_mid, y0=ct_y0, y1=tr_y1))

        shapes.append(self._rect(x0=tr_x0, x1=tr_x1, y0=tr_y0, y1=tr_y1))
        shapes.append(self._line(x0=x_mid, x1=x_mid, y0=tr_y0, y1=tr_y0 - self.gap_down_tr_gnd))

        gnd_y = tr_y0 - self.gap_down_tr_gnd

        shapes.append(self._line(x0=x_mid - 0.5 * self.ground_w1, x1=x_mid + 0.5 * self.ground_w1, y0=gnd_y, y1=gnd_y))
        shapes.append(self._line(x0=x_mid - 0.5 * self.ground_w2, x1=x_mid + 0.5 * self.ground_w2, y0=gnd_y - self.ground_dy, y1=gnd_y - self.ground_dy))
        shapes.append(self._line(x0=x_mid - 0.5 * self.ground_w3, x1=x_mid + 0.5 * self.ground_w3, y0=gnd_y - 2.0 * self.ground_dy, y1=gnd_y - 2.0 * self.ground_dy))

        annotations.append(dict(x=x_mid, y=y_star, text="CT", showarrow=False, xanchor="center", yanchor="middle"))
        annotations.append(dict(x=x_mid, y=0.5 * (tr_y0 + tr_y1), text="TR", showarrow=False, xanchor="center", yanchor="middle"))

        y_ground_low = gnd_y - 2.0 * self.ground_dy
        return y_ground_low

    def _add_phase_buses(self, shapes, annotations, left_branch, right_branch):
        all_x_centers = [
            left_branch.x_centers[0], left_branch.x_centers[1], left_branch.x_centers[2],
            right_branch.x_centers[0], right_branch.x_centers[1], right_branch.x_centers[2],
        ]
        all_y_tops = [
            left_branch.y_top_globals[0], left_branch.y_top_globals[1], left_branch.y_top_globals[2],
            right_branch.y_top_globals[0], right_branch.y_top_globals[1], right_branch.y_top_globals[2],
        ]

        x_bus_left = min(all_x_centers) - self.phase_label_offset
        x_bus_right = max(all_x_centers) + self.phase_label_offset
        y_top_max = max(all_y_tops)

        y_bus_A = y_top_max + self.phase_bus_offset + 0.0 * self.phase_bus_spacing
        y_bus_B = y_top_max + self.phase_bus_offset + 1.0 * self.phase_bus_spacing
        y_bus_C = y_top_max + self.phase_bus_offset + 2.0 * self.phase_bus_spacing

        shapes.append(self._line(x0=x_bus_left, x1=x_bus_right, y0=y_bus_A, y1=y_bus_A))
        shapes.append(self._line(x0=x_bus_left, x1=x_bus_right, y0=y_bus_B, y1=y_bus_B))
        shapes.append(self._line(x0=x_bus_left, x1=x_bus_right, y0=y_bus_C, y1=y_bus_C))

        shapes.append(self._line(x0=left_branch.x_centers[0], x1=left_branch.x_centers[0], y0=y_bus_A, y1=left_branch.y_top_globals[0] + self.phase_drop_gap))
        shapes.append(self._line(x0=left_branch.x_centers[1], x1=left_branch.x_centers[1], y0=y_bus_B, y1=left_branch.y_top_globals[1] + self.phase_drop_gap))
        shapes.append(self._line(x0=left_branch.x_centers[2], x1=left_branch.x_centers[2], y0=y_bus_C, y1=left_branch.y_top_globals[2] + self.phase_drop_gap))

        shapes.append(self._line(x0=right_branch.x_centers[0], x1=right_branch.x_centers[0], y0=y_bus_A, y1=right_branch.y_top_globals[0] + self.phase_drop_gap))
        shapes.append(self._line(x0=right_branch.x_centers[1], x1=right_branch.x_centers[1], y0=y_bus_B, y1=right_branch.y_top_globals[1] + self.phase_drop_gap))
        shapes.append(self._line(x0=right_branch.x_centers[2], x1=right_branch.x_centers[2], y0=y_bus_C, y1=right_branch.y_top_globals[2] + self.phase_drop_gap))

        annotations.append(dict(x=x_bus_left - 0.4, y=y_bus_A, text="A", showarrow=False, xanchor="right", yanchor="middle"))
        annotations.append(dict(x=x_bus_left - 0.4, y=y_bus_B, text="B", showarrow=False, xanchor="right", yanchor="middle"))
        annotations.append(dict(x=x_bus_left - 0.4, y=y_bus_C, text="C", showarrow=False, xanchor="right", yanchor="middle"))

        y_phase_top = max(y_bus_A, y_bus_B, y_bus_C)
        y_phase_bot = min(y_bus_A, y_bus_B, y_bus_C)
        return y_phase_top, y_phase_bot

    def build(self):
        left_branch, shapes_l, bounds_l = self._build_left_branch()

        left_width = bounds_l["x_max"] - bounds_l["x_min"]
        dx_right = left_width + self.right_extra_gap
        x0_right = self.x0 + dx_right

        right_branch, shapes_r, bounds_r = self._build_right_branch(x0_right=x0_right)

        shapes_all = []
        annotations = []

        shapes_all = shapes_all + shapes_l
        shapes_all = shapes_all + shapes_r

        x_l = left_branch.x_centers[1]
        x_r = right_branch.x_centers[1]

        y_star = left_branch.y_star
        if right_branch.y_star < y_star:
            y_star = right_branch.y_star

        y_ground_low = self._add_ct_tr_ground(shapes=shapes_all, annotations=annotations, x_l=x_l, x_r=x_r, y_star=y_star)

        y_phase_top, y_phase_bot = self._add_phase_buses(shapes=shapes_all, annotations=annotations, left_branch=left_branch, right_branch=right_branch)

        x_min = min(bounds_l["x_min"], bounds_r["x_min"])
        x_max = max(bounds_l["x_max"], bounds_r["x_max"])

        y_min = min(bounds_l["y_min"], bounds_r["y_min"])
        if y_ground_low - 0.8 < y_min:
            y_min = y_ground_low - 0.8
        if y_phase_bot - 0.8 < y_min:
            y_min = y_phase_bot - 0.8

        y_max = max(bounds_l["y_max"], bounds_r["y_max"])
        if y_phase_top + 0.8 > y_max:
            y_max = y_phase_top + 0.8

        self._shapes = shapes_all
        self._annotations = annotations
        self._bounds = {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}

        return self._shapes, self._bounds, self._annotations

    def make_figure(self):
        if len(self._shapes) == 0:
            self.build()

        fig = go.Figure()
        fig.update_layout(
            shapes=self._shapes,
            annotations=self._annotations,
            xaxis=dict(visible=False, range=[self._bounds["x_min"], self._bounds["x_max"]]),
            yaxis=dict(visible=False, range=[self._bounds["y_min"], self._bounds["y_max"]]),
            width=self.fig_width,
            height=self.fig_height,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        return fig



# # -------------------------
# # Usage
# # -------------------------
# diagram = BankDiagram(
#     P=3,
#     S=4,
#     Pt=11,
#     Pa_left=6,
#     x0=0.0,
#     y0=0.0,
# )
#
# fig = diagram.make_figure()
# fig.show()

class SingleWyeBankDiagram(BankDiagram):
    """Single-wye diagram using the same drawing primitives as BankDiagram.

    The original BankDiagram is a double-wye arrangement (left + right branches).
    This subclass draws only the left branch and connects its star point to the
    CT/TR/ground stack.
    """

    def _add_phase_buses_single(self, shapes, annotations, left_branch):
        all_x_centers = [left_branch.x_centers[0], left_branch.x_centers[1], left_branch.x_centers[2]]
        all_y_tops = [left_branch.y_top_globals[0], left_branch.y_top_globals[1], left_branch.y_top_globals[2]]

        x_bus_left = min(all_x_centers) - self.phase_label_offset
        x_bus_right = max(all_x_centers) + self.phase_label_offset
        y_top_max = max(all_y_tops)

        y_bus_A = y_top_max + self.phase_bus_offset + 0.0 * self.phase_bus_spacing
        y_bus_B = y_top_max + self.phase_bus_offset + 1.0 * self.phase_bus_spacing
        y_bus_C = y_top_max + self.phase_bus_offset + 2.0 * self.phase_bus_spacing

        shapes.append(self._line(x0=x_bus_left, x1=x_bus_right, y0=y_bus_A, y1=y_bus_A))
        shapes.append(self._line(x0=x_bus_left, x1=x_bus_right, y0=y_bus_B, y1=y_bus_B))
        shapes.append(self._line(x0=x_bus_left, x1=x_bus_right, y0=y_bus_C, y1=y_bus_C))

        shapes.append(self._line(x0=left_branch.x_centers[0], x1=left_branch.x_centers[0], y0=y_bus_A, y1=left_branch.y_top_globals[0] + self.phase_drop_gap))
        shapes.append(self._line(x0=left_branch.x_centers[1], x1=left_branch.x_centers[1], y0=y_bus_B, y1=left_branch.y_top_globals[1] + self.phase_drop_gap))
        shapes.append(self._line(x0=left_branch.x_centers[2], x1=left_branch.x_centers[2], y0=y_bus_C, y1=left_branch.y_top_globals[2] + self.phase_drop_gap))

        annotations.append(dict(x=x_bus_left - 0.4, y=y_bus_A, text="A", showarrow=False, xanchor="right", yanchor="middle"))
        annotations.append(dict(x=x_bus_left - 0.4, y=y_bus_B, text="B", showarrow=False, xanchor="right", yanchor="middle"))
        annotations.append(dict(x=x_bus_left - 0.4, y=y_bus_C, text="C", showarrow=False, xanchor="right", yanchor="middle"))

        y_phase_top = max(y_bus_A, y_bus_B, y_bus_C)
        y_phase_bot = min(y_bus_A, y_bus_B, y_bus_C)
        return y_phase_top, y_phase_bot

    def build(self):
        left_branch, shapes_l, bounds_l = self._build_left_branch()

        shapes_all = []
        annotations = []
        shapes_all = shapes_all + shapes_l

        x_center = left_branch.x_centers[1]
        x_l = x_center - self.ct_w
        x_r = x_center + self.ct_w

        y_star = left_branch.y_star

        y_ground_low = self._add_ct_tr_ground(
            shapes=shapes_all,
            annotations=annotations,
            x_l=x_l,
            x_r=x_r,
            y_star=y_star,
        )

        y_phase_top, y_phase_bot = self._add_phase_buses_single(
            shapes=shapes_all,
            annotations=annotations,
            left_branch=left_branch,
        )

        x_min = bounds_l["x_min"]
        x_max = bounds_l["x_max"]

        y_min = bounds_l["y_min"]
        if y_ground_low - 0.8 < y_min:
            y_min = y_ground_low - 0.8
        if y_phase_bot - 0.8 < y_min:
            y_min = y_phase_bot - 0.8

        y_max = bounds_l["y_max"]
        if y_phase_top + 0.8 > y_max:
            y_max = y_phase_top + 0.8

        self._shapes = shapes_all
        self._annotations = annotations
        self._bounds = {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}

        return self._shapes, self._bounds, self._annotations
