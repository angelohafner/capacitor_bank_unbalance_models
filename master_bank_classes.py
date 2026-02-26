# master_bank_classes.py
import logging
from typing import Tuple, Optional, Iterable, Protocol, Dict, Any, Callable
import os
import numpy as np
import pandas as pd

from yy_internal_fuses import Table07DoubleWyeFig34
from y_internal_fuses import Table07SingleWyeInternalFuses
from h_bridge_internal_fuses import Tabela08HBridgeCalculada
from h_bridge_external_fuses import Table06HBridgeMinimal
from yy_external_fuses import Table03DoubleWyeFig29
from electrical_utils import ElectricalUtils


class _TableProtocol(Protocol):
    """Minimal interface required by MasterBankClasses."""
    df: pd.DataFrame
    def calcular(self, G: int) -> pd.DataFrame: ...




def _coerce_inputs(d: Dict[str, Any], keys_int: Iterable[str], default_G: int = 0) -> Dict[str, Any]:
    """Coerce common integer keys and provide a default for G."""
    out = dict(d)
    for k in keys_int:
        if k in out:
            out[k] = int(out[k])
    out["G"] = int(out.get("G", default_G))
    return out


def _postprocess_and_export(
    df_ieee: pd.DataFrame,
    dados: Dict[str, Any],
    tex_filename: str,
    xlsx_filename: str,
    f_values: Iterable[int],
    export_tex: bool,
    export_xlsx: bool,
    real_units_hook: Optional[Callable[[pd.DataFrame, Dict[str, Any]], pd.DataFrame]] = None,
    transpose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert IEEE p.u. to real units, manage 'f' labels, and export artifacts.
    real_units_hook: optional callable to apply table-specific conversions.
    """
    bases = ElectricalUtils.calcular_nominais_celula(dados)
    df_real = ElectricalUtils.converter_unidades(df_ieee, bases)
    if real_units_hook is not None:
        df_real = real_units_hook(df_real, bases)

    if "f" in df_ieee.columns:
        f_values = df_ieee["f"]
        key_f = "f"
    elif "n" in df_ieee.columns:
        f_values = df_ieee["n"]
        key_f = "n"
    else:
        f_values = range(len(df_real))
        key_f = None

    # Find harmonic/order where Vcu is maximum but <= 1.1
    line_max_vcu = None
    if "Vcu" in df_ieee.columns and key_f is not None:
        mask = df_ieee["Vcu"] <= 1.1
        if mask.any():
            idx_max = df_ieee.loc[mask, "Vcu"].idxmax()
            line_max_vcu = int(df_ieee.loc[idx_max, key_f])

    logging.getLogger(__name__).info("line_max_vcu (f or n) = %s", line_max_vcu)

    if export_tex:
        ElectricalUtils.exportar_df_latex(
            df_real,
            tex_filename,
            f_values=f_values,
            line_max_vcu=line_max_vcu,
        )
    if export_xlsx:
        ElectricalUtils.exportar_df_excel(
            df_real,
            filename=xlsx_filename,
            f_values=f_values,
        )

    return df_ieee, df_real


class MasterBankClasses:
    """Factory/runner helpers for capacitor-bank unbalance tables."""

    @staticmethod
    def compute_table07_from_dict(
        dados_nominais_banco: dict,
        tex_filename: str = "tabela7_real.tex",
        xlsx_filename: str = "tabela7_real.xlsx",
        f_values: Optional[Iterable[int]] = None,
        export_tex: bool = True,
        export_xlsx: bool = True,
        transpose: bool = False,
    ) -> Tuple[Table07DoubleWyeFig34, pd.DataFrame, pd.DataFrame]:
        """
        Build Table07DoubleWyeFig34 from dict, compute per-unit, convert to real units, export.
        Expected keys: S, Pt, Pa, P, N, Su, G, tensao_trifasica_banco_V, potencia_trifasica_banco_VAr, frequencia_Hz.
        """
        d = _coerce_inputs(dados_nominais_banco, keys_int=("S", "Pt", "Pa", "P", "N", "Su", "G"))
        tabela7 = Table07DoubleWyeFig34(
            S=d["S"], Pt=d["Pt"], Pa=d["Pa"], P=d["P"], N=d["N"], Su=d["Su"]
        )
        df_ieee = tabela7.calcular(G=d["G"])
        df_ieee, df_real = _postprocess_and_export(
            df_ieee=df_ieee,
            dados=d,
            tex_filename=tex_filename,
            xlsx_filename=xlsx_filename,
            f_values=f_values,
            export_tex=export_tex,
            export_xlsx=export_xlsx,
            real_units_hook=None,
        )
        return tabela7, df_ieee, df_real


    @staticmethod
    def compute_table07_single_from_dict(
        dados_nominais_banco: dict,
        tex_filename: str = "tabela7y_real.tex",
        xlsx_filename: str = "tabela7y_real.xlsx",
        f_values: Optional[Iterable[int]] = None,
        export_tex: bool = True,
        export_xlsx: bool = True,
        transpose: bool = False,
    ) -> Tuple[Table07SingleWyeInternalFuses, pd.DataFrame, pd.DataFrame]:
        """
        Build Table07SingleWyeInternalFuses from dict, compute per-unit, convert to real units, export.
        Expected keys: S, Pt, Pa, P, N, Su, G, tensao_trifasica_banco_V, potencia_trifasica_banco_VAr, frequencia_Hz.
        Note: For this topology, Pt must be equal to Pa.
        """
        d = _coerce_inputs(dados_nominais_banco, keys_int=("S", "Pt", "Pa", "P", "N", "Su", "G"))
        tabela7 = Table07SingleWyeInternalFuses(
            S=d["S"], Pt=d["Pt"], Pa=d["Pa"], P=d["P"], N=d["N"], Su=d["Su"]
        )
        df_ieee = tabela7.calcular(G=d["G"])
        df_ieee, df_real = _postprocess_and_export(
            df_ieee=df_ieee,
            dados=d,
            tex_filename=tex_filename,
            xlsx_filename=xlsx_filename,
            f_values=f_values,
            export_tex=export_tex,
            export_xlsx=export_xlsx,
            real_units_hook=None,
        )
        return tabela7, df_ieee, df_real

    @staticmethod
    def compute_table08_from_dict(
        dados_nominais_banco: dict,
        f_values: Iterable[int],
        tex_filename: str = "tabela8_real.tex",
        xlsx_filename: str = "tabela8_real.xlsx",
        export_tex: bool = True,
        export_xlsx: bool = True,
        transpose: bool = False,
    ) -> Tuple[Tabela08HBridgeCalculada, pd.DataFrame, pd.DataFrame]:
        """
        Build Tabela08 (H-bridge, internal fuses), compute per-unit, convert to real units, export.
        Extra real columns: Cp_uF, C_unit_uF, V_phase_V (when Cp, Cu, Vln are present).
        Expected keys: S, St, Pt, Pa, P, N, Su, G, tensao_trifasica_banco_V, potencia_trifasica_banco_VAr, frequencia_Hz.
        """
        d = _coerce_inputs(dados_nominais_banco, keys_int=("S", "St", "Pt", "Pa", "P", "N", "Su", "G"))
        tabela8 = Tabela08HBridgeCalculada(
            S=d["S"], St=d["St"], Pt=d["Pt"], Pa=d["Pa"], P=d["P"], N=d["N"], Su=d["Su"]
        )
        tabela8.calcular(G=d["G"])
        df_ieee = tabela8.df.copy()

        def _hook(df: pd.DataFrame, bases: Dict[str, Any]) -> pd.DataFrame:
            """Add table-08 specific real-unit columns."""
            out = df.copy()
            if "Cp" in out.columns:
                out["Cp_uF"] = out["Cp"] * bases["C_phase"] * 1e6
            if "Cu" in out.columns:
                out["C_unit_uF"] = out["Cu"] * bases["C_unit"] * 1e6
            if "Vln" in out.columns:
                out["V_phase_V"] = out["Vln"] * bases["V_phase"]
            return out

        df_ieee, df_real = _postprocess_and_export(
            df_ieee=df_ieee,
            dados=d,
            tex_filename=tex_filename,
            xlsx_filename=xlsx_filename,
            f_values=f_values,
            export_tex=export_tex,
            export_xlsx=export_xlsx,
            real_units_hook=_hook,
        )
        return tabela8, df_ieee, df_real

    @staticmethod
    def compute_table06_from_dict(
        dados_nominais_banco: dict,
        tex_filename: str = "tabela6_real.tex",
        xlsx_filename: str = "tabela6_real.xlsx",
        export_tex: bool = True,
        export_xlsx: bool = True,
        transpose: bool = False,
    ) -> Tuple[Table06HBridgeMinimal, pd.DataFrame, pd.DataFrame]:
        """
        Build Table06 (H-bridge, external fuses minimal), compute per-unit, convert to real units, export.
        Expected keys: S, St, Pt, Pa, G, tensao_trifasica_banco_V, potencia_trifasica_banco_VAr, frequencia_Hz.
        """
        d = _coerce_inputs(dados_nominais_banco, keys_int=("S", "St", "Pt", "Pa", "G"))
        tabela6 = Table06HBridgeMinimal(S=d["S"], St=d["St"], Pt=d["Pt"], Pa=d["Pa"])
        n_values = np.arange(0, d["Pa"], 1)
        df_ieee = tabela6.calcular(G=d["G"], n_values=n_values)
        df_ieee, df_real = \
            _postprocess_and_export(df_ieee=df_ieee,
                                    dados=d,
                                    tex_filename=tex_filename,
                                    xlsx_filename=xlsx_filename,
                                    f_values=n_values,
                                    export_tex=export_tex,
                                    export_xlsx=export_xlsx,
                                    real_units_hook=None,
            )

        return tabela6, df_ieee, df_real


    @staticmethod
    def compute_table03_from_dict(
        dados_nominais_banco: dict,
        tex_filename: str = "tabela3ext_real.tex",
        xlsx_filename: str = "tabela3ext_real.xlsx",
        f_values: Optional[Iterable[int]] = None,
        export_tex: bool = True,
        export_xlsx: bool = True,
        transpose: bool = False,
    ) -> Tuple[Table03DoubleWyeFig29, pd.DataFrame, pd.DataFrame]:
        """
        Build Table03 (double wye, external fuses), compute per-unit, convert to real units, export.
        Expected keys: S, Pt, Pa, G, tensao_trifasica_banco_V, potencia_trifasica_banco_VAr, frequencia_Hz.
        Optional: Cu_fixed (defaults to 1.0)
        """
        # Coerce ints and provide default G
        d = _coerce_inputs(dados_nominais_banco, keys_int=("S", "Pt", "Pa", "G"))

        # Optional fixed Cu factor (Iu = Vcu * Cu_fixed)
        cu_fixed = float(dados_nominais_banco.get("Cu_fixed", 1.0))

        # Instantiate IEEE Table 3 model
        tabela3 = Table03DoubleWyeFig29(S=d["S"], Pt=d["Pt"], Pa=d["Pa"], Cu_fixed=cu_fixed)

        # Choose n sweep (defaults mimic the class if None)
        n_values = None
        if f_values is not None:
            # if user provided an explicit sequence of f (here: n), reuse it
            n_values = list(f_values)

        # Run per-unit computation
        df_ieee = tabela3.calcular(G=d["G"], n_values=n_values)

        # Post-process: convert to real units and export (Cp→μF, Vng→V, Ig/In→A, etc.)
        df_ieee, df_real = _postprocess_and_export(
            df_ieee=df_ieee,
            dados=d,
            tex_filename=tex_filename,
            xlsx_filename=xlsx_filename,
            f_values=(n_values if n_values is not None else df_ieee.get("n")),
            export_tex=export_tex,
            export_xlsx=export_xlsx,
            real_units_hook=None,  # no extra columns beyond the generic converter
        )

        return tabela3, df_ieee, df_real
