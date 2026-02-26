import math
import pandas as pd
from typing import Iterable, Optional, Dict, Any


class ElectricalUtils:
    """Independent utility functions for power/capacitor-bank calculations."""

    # ============================================================
    # 0) Helpers
    # ============================================================
    @staticmethod
    def _round_or_int(x: Any, decimals: int) -> Any:
        """Return ints without decimals; others rounded to `decimals`."""
        if isinstance(x, (int, float)):
            if float(x).is_integer():
                return int(x)
            return round(float(x), decimals)
        return x

    @staticmethod
    def formatar_valores(valor: Any) -> Any:
        """Compat wrapper kept for external calls (2 decimals, ints preserved)."""
        return ElectricalUtils._round_or_int(valor, 4)

    # ============================================================
    # 1) Nominal (bank, unit, cell, element)
    # ============================================================
    @staticmethod
    def calcular_nominais_celula(dados_banco: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute nominal quantities for a star-connected 3φ capacitor bank.
        Keys expected in `dados_banco`:
          - tensao_trifasica_banco_V (V_LL) [V]
          - potencia_trifasica_banco_VAr (Q_total) [VAr]
          - frequencia_Hz [Hz]
          - S (series strings per phase)
          - Pt (parallel units per phase)
          - Su (series cells per unit)
          - N (series elements per cell)
        Returns a dict with SI units (V, A, F).
        """
        V_ll = float(dados_banco["tensao_trifasica_banco_V"])
        V_rated  = float(dados_banco["V_rated"])
        Q_total = float(dados_banco["potencia_trifasica_banco_VAr"])
        f = float(dados_banco["frequencia_Hz"])
        S = int(dados_banco["S"])
        Pt = int(dados_banco["Pt"])
        Su = int(dados_banco["Su"]) if "Su" in dados_banco else None
        N = int(dados_banco["N"]) if "N" in dados_banco else None

        # Phase-level
        V_phase = V_ll / math.sqrt(3.0)
        I_bank = Q_total / (math.sqrt(3.0) * V_ll)
        Q_phase = Q_total / 3.0
        C_phase = Q_phase / (2.0 * math.pi * f * (V_phase ** 2))

        # Unit (per phase split into S series strings and Pt parallel units)
        C_unit = (C_phase * S) / Pt
        V_unit = V_phase / S
        I_unit = I_bank / Pt

        C_grupo_serie = C_unit * Su if "Su" in dados_banco else None
        V_grupo_serie = V_unit / Su if "Su" in dados_banco else None
        I_grupo_serie = I_unit      if "Su" in dados_banco else None

        C_element = C_grupo_serie / N if "N" in dados_banco else None
        V_element = V_grupo_serie     if "N" in dados_banco else None
        I_element = I_grupo_serie / N if "N" in dados_banco else None

        return {
            "V_ll": V_ll,
            "V_phase": V_phase,
            "I_bank": I_bank,
            "C_phase": C_phase,
            "C_unit": C_unit,
            "V_unit": V_unit,
            "I_unit": I_unit,
            "C_grupo_serie": C_grupo_serie,
            "V_grupo_serie": V_grupo_serie,
            "I_grupo_serie": I_grupo_serie,
            "C_element": C_element,
            "V_element": V_element,
            "I_element": I_element,
            "V_rated": V_rated,
            "S": S,
        }

    # Optional base calculator (handy)
    @staticmethod
    def star_bank_nominals(Q_var: float, V_ll_V: float, f_Hz: float):
        """Return (I_nom_A, C_phase_F, V_phase_V) for a star-connected 3φ bank."""
        V_phase_V = V_ll_V / math.sqrt(3.0)
        I_nom_A = Q_var / (math.sqrt(3.0) * V_ll_V)
        C_phase_F = (Q_var / 3.0) / (2.0 * math.pi * f_Hz * (V_phase_V ** 2))
        return I_nom_A, C_phase_F, V_phase_V

    # ============================================================
    # 2) Per-unit → real units converter
    # ============================================================
    @staticmethod
    def converter_unidades(df: pd.DataFrame, resultados: Dict[str, float]) -> pd.DataFrame:
        """
        Convert per-unit columns from `df` into real units using `resultados`
        (output of `calcular_nominais_celula`).
        Expected columns (any subset): Cp, Cu, Vng, In, Ig.
        Creates: Cp_uF, C_unit_uF, V_phase_V, In_A, Ig_A (+ original p.u. columns).
        """
        out = pd.DataFrame()

        if "Cp" in df.columns:
            out["Cp"] = df["Cp"]
            out["Cp_uF"] = 1e6 * df["Cp"] * resultados["C_phase"]

        if "Cu" in df.columns:
            out["Cu"] = df["Cu"]
            out["C_unit_uF"] = 1e6 * df["Cu"] * resultados["C_unit"]

        if "Vng" in df.columns:
            out["Vng"] = df["Vng"]
            out["V_ng_V"] = df["Vng"] * resultados["V_phase"]

        if "In" in df.columns:
            out["In"] = df["In"]
            out["In_A"] = df["In"] * resultados["I_bank"]

        if "Ig" in df.columns:
            out["Ig"] = df["Ig"]
            out["Ig_A"] = df["Ig"] * resultados["I_bank"]

        if "Chn" in df.columns:
            out["Chn"] = df["Chn"]
            out["Chn_uF"] = df["Chn"] * resultados["C_phase"] * 1e6

        if "Vhn" in df.columns:
            out["Vhn"] = df["Vhn"]
            out["Vhn_V"] = df["Vhn"] * resultados["V_phase"]

        if "Ih" in df.columns:
            out["Ih"] = df["Ih"]
            out["Ih_A"] = df["Ih"] * resultados["I_bank"]

        if "Vcu" in df.columns:
            out["Vcu"] = df["Vcu"]
            # real unit voltage on the capacitor unit (kV)
            out["Vcu_kV"] = df["Vcu"] * resultados["V_unit"] * 1e-3

            # Vcu2 = (real unit voltage) / (rated unit voltage)
            if "V_rated" in resultados and "S" in resultados:
                V_unit_rated = (float(resultados["V_rated"]) / math.sqrt(3.0)) / float(resultados["S"])
                factor = resultados["V_unit"] / V_unit_rated
                out["Vcu2"] = df["Vcu"] * factor

        # Format: 2 decimals, keep integers without comma
        out = out.apply(lambda col: col.map(ElectricalUtils.formatar_valores))
        return out

    # ============================================================
    # 3) LaTeX exporter (exact row order & column format)
    # ============================================================
    @staticmethod
    def exportar_df_latex(
            df_real: pd.DataFrame,
            filename: str = "tabela.tex",
            f_values: Optional[Iterable[int]] = None,
            decimals: int = 2,
            transpose: bool = True,
            line_max_vcu: Optional[int] = None,
    ) -> str:
        r"""
        Export df_real to LaTeX in the format:

        (default) variables as rows, f as columns, then optionally transposed.

        If transpose=True, the table is transposed (each row is one harmonic f).

        If line_max_vcu is not None, the row where f == line_max_vcu
        is colored red, and the two rows above it (if they exist) are
        colored brown.
        """

        # --- column headers (f) ---
        if f_values is None:
            f_vals = list(range(len(df_real)))
        else:
            f_vals = list(f_values)

        n_cols = len(df_real)
        if len(f_vals) != n_cols:
            raise ValueError("`f_values` length must match number of rows in `df_real`.")

        # --- collect rows (only if the column exists) ---
        rows = []

        def add_row(label: str, colname: str):
            if colname in df_real.columns:
                rows.append((label, pd.to_numeric(df_real[colname], errors="coerce").values))

        def add_pair(label_pu: str, col_pu: str, label_si: str, col_si: str):
            if col_pu in df_real.columns:
                add_row(label_pu, col_pu)
                if col_si in df_real.columns:
                    add_row(label_si, col_si)

        # First row is f
        rows.append((r"\textit{\textbf{f}}", pd.to_numeric(f_vals, errors="coerce")))

        # Cp / Cu blocks
        add_pair(r"\textbf{\textit{C\textsubscript{p}} [pu]}", "Cp",
                 r"\textbf{\textit{C\textsubscript{p}} [$\mu$F]}", "Cp_uF")

        add_pair(r"\textbf{\textit{C\textsubscript{u}} [pu]}", "Cu",
                 r"\textbf{\textit{C\textsubscript{u}} [$\mu$F]}", "C_unit_uF")

        # Vng / V_phase
        add_pair(r"\textbf{\textit{V\textsubscript{ng}} [pu]}", "Vng",
                 r"\textbf{\textit{V\textsubscript{ng}} [V]}", "V_ng_V")

        # In / Ig (both pu and A)
        add_pair(r"\textbf{\textit{I\textsubscript{n}} [pu]}", "In",
                 r"\textbf{\textit{I\textsubscript{n}} [A]}", "In_A")

        add_pair(r"\textbf{\textit{I\textsubscript{g}} [pu]}", "Ig",
                 r"\textbf{\textit{I\textsubscript{g}} [A]}", "Ig_A")

        # Chn / Vhn / Ih / Vcu (pu and real units)
        add_pair(r"\textbf{\textit{C\textsubscript{hn}} [pu]}", "Chn",
                 r"\textbf{\textit{C\textsubscript{hn}} [$\mu$F]}", "Chn_uF")

        add_pair(r"\textbf{\textit{V\textsubscript{hn}} [pu]}", "Vhn",
                 r"\textbf{\textit{V\textsubscript{hn}} [V]}", "Vhn_V")

        add_pair(r"\textbf{\textit{I\textsubscript{h}} [pu]}", "Ih",
                 r"\textbf{\textit{I\textsubscript{h}} [A]}", "Ih_A")

        add_pair(r"\textbf{\textit{V\textsubscript{cu}} [pu]}", "Vcu",
                 r"\textbf{\textit{V\textsubscript{cu}} [kV]}", "Vcu_kV")

        add_row(r"\textbf{\textit{V\textsubscript{cu2}} [pu2]}", "Vcu2")

        # --- formatter for numbers ---
        def _fmt_cell(v, is_f_row: bool, decimals_: int):
            """
            - Linha do f (is_f_row=True): sempre inteiro.
            - Outras linhas: sempre `decimals_` casas decimais, com vírgula.
            """
            try:
                fv = float(v)
            except Exception:
                return str(v)

            if is_f_row:
                return str(int(fv))

            txt = f"{fv:.{decimals_}f}"
            return txt.replace(".", ",")

        # Build table as list-of-lists of strings: first col is label
        table_rows = []
        for label, values in rows:
            is_f_row = (label == r"\textit{\textbf{f}}")
            row = [label] + [_fmt_cell(v, is_f_row=is_f_row, decimals_=decimals) for v in values]
            table_rows.append(row)

        # Optional transpose (rows <-> columns)
        if transpose:
            transposed = []
            n_r = len(table_rows)
            n_c = len(table_rows[0])
            for j in range(n_c):
                transposed.append([table_rows[i][j] for i in range(n_r)])
            table_rows = transposed

        # --- build LaTeX table ---
        n_cols_out = len(table_rows[0]) - 1
        column_format = "r" + "r" * n_cols_out

        latex_lines = []
        latex_lines.append(f"\\begin{{tabular}}{{{column_format}}}")
        latex_lines.append("\\toprule")

        # Header
        header = " & ".join(table_rows[0]) + r" \\"
        latex_lines.append(header)
        latex_lines.append("\\midrule")

        # ---- color logic for body rows ----
        target_idx = None
        body_rows = table_rows[1:]

        if line_max_vcu is not None:
            for i, row in enumerate(body_rows):
                # first cell of each body row is f (already inteiro em string)
                try:
                    f_val = int(float(str(row[0]).replace(",", ".")))
                except Exception:
                    continue
                if f_val == line_max_vcu:
                    target_idx = i
                    break

        # Body
        for i, row in enumerate(body_rows):
            row_to_use = row

            if target_idx is not None:
                if i == target_idx:
                    row_to_use = [r"\textcolor{red}{" + cell + "}" for cell in row]
                elif i == target_idx - 2: #(or i == target_idx - 1 )
                    row_to_use = [r"\textcolor{blue}{" + cell + "}" for cell in row]

            line = " & ".join(row_to_use) + r" \\"
            latex_lines.append(line)

        latex_lines.append("\\bottomrule")
        latex_lines.append("\\end{tabular}")

        latex_table = "\n".join(latex_lines)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_table)

        return latex_table

    @staticmethod
    def exportar_df_excel(
            df_real: pd.DataFrame,
            filename: str = "tabela.xlsx",
            f_values: Optional[Iterable[int]] = None,
            transpose: bool = False,
    ) -> None:
        """
        Exporta df_real para Excel com rótulos de linha:
        f, Cp (pu), Cp (μF), Cu (pu), Cu (μF), Vng (pu), Vng (V),
        In (pu), In (A), Ig (pu), Ig (A),
        Chn (pu), Chn (μF), Vhn (pu), Vhn (V), Ih (pu), Ih (A), Vcu (pu), Vcu (V).

        Se transpose=True, a planilha é transposta (f em linhas).
        """

        if f_values is None:
            f_vals = list(range(len(df_real)))
        else:
            f_vals = list(f_values)

        n_cols = len(df_real)
        if len(f_vals) != n_cols:
            raise ValueError("`f_values` length must match number of rows in `df_real`.")

        rows = []

        def add_row(label: str, colname: str):
            if colname in df_real.columns:
                vals = list(df_real[colname].values)
                fmt_vals = []
                for v in vals:
                    try:
                        fv = float(v)
                        if fv.is_integer():
                            fmt_vals.append(int(fv))
                        else:
                            fmt_vals.append(round(fv, 2))
                    except Exception:
                        fmt_vals.append(v)
                rows.append((label, fmt_vals))

        def add_pair(label_pu: str, col_pu: str, label_si: str, col_si: str):
            if col_pu in df_real.columns:
                add_row(label_pu, col_pu)
                if col_si in df_real.columns:
                    add_row(label_si, col_si)

        # f row
        rows.append(("f", list(f_vals)))

        # Cp / Cu
        add_pair("Cp (pu)", "Cp", "Cp (μF)", "Cp_uF")
        add_pair("Cu (pu)", "Cu", "Cu (μF)", "C_unit_uF")

        # Vng
        add_pair("Vng (pu)", "Vng", "Vng (V)", "V_ng_V")

        # In / Ig
        add_pair("In (pu)", "In", "In (A)", "In_A")
        add_pair("Ig (pu)", "Ig", "Ig (A)", "Ig_A")

        # Chn / Vhn / Ih / Vcu
        add_pair("Chn (pu)", "Chn", "Chn (μF)", "Chn_uF")
        add_pair("Vhn (pu)", "Vhn", "Vhn (V)", "Vhn_V")
        add_pair("Ih (pu)", "Ih", "Ih (A)", "Ih_A")
        add_pair("Vcu (pu)", "Vcu", "Vcu (kV)", "Vcu_kV")
        add_row("Vcu2 (pu2)", "Vcu2")

        # Constrói DataFrame: linhas = labels; colunas = f
        data = {j: [r[1][j] for r in rows] for j in range(n_cols)}
        out = pd.DataFrame(data, index=[r[0] for r in rows])

        if transpose:
            out = out.T

        out.to_excel(filename, header=False, index=True)
        print("Tabela exportada para '{0}' (sem linha 'Label').".format(filename))
