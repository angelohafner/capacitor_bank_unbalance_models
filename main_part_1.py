# Comments in English only
from __future__ import annotations
from pathlib import Path
import streamlit as st

from ui.input_widgets import get_dados_nominais_banco
from ui.utils_streamlit import ensure_export_dir, show_topology_figure
from reports.latex_report_generator import LatexReportGenerator
from validation.validators import validate_nominal_data, NominalDataError


def run_main_part_1():
    # ---------------- Page config ----------------
    st.set_page_config(
        page_title="Desbalanceamento - Banco de Capacitores",
        page_icon="──∥──",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # Apply theme override (works for Streamlit >= 1.31)
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background-color: white !important;
                color: black !important;
            }
            [data-testid="stSidebar"] {
                background-color: #f8f9fa !important;
                color: black !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "# Desbalanceamento para um banco de capacitores "
        "[IEEE C37.99](https://standards.ieee.org/ieee/C37.99/5511/)"
    )

    # ---------------- Header row ----------------
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        topologia = st.selectbox(
            "Topologia de proteção:",
            [
                "yy_internal_fuses",
                "y_internal_fuses",
                "h_bridge_internal_fuses",
                "yy_external_fuses",
                "h_bridge_external_fuses",
            ],
        )

    with col2:
        transformer_type_option = ["TC", "TP"]
        selected_transformer_type_option = st.selectbox(
            "Proteção com TC ou TP?:", transformer_type_option
        )

    with col3:
        if selected_transformer_type_option == "TC":
            tc_secondary_options = [5, 1]
            secondary_current_tc = st.selectbox(
                "Corrente secundária [A]:", tc_secondary_options
            )
            secondary_voltage_tp = None
        else:
            tp_secondary_options = [115]
            secondary_voltage_tp = st.selectbox(
                "Tensão secundária [V]:", tp_secondary_options
            )


    # ---------------- Build nominal dictionary from UI ----------------
    dados_nominais_banco = get_dados_nominais_banco(topologia)

    if not dados_nominais_banco:
        st.error("Preencha os dados nominais do banco para continuar.")
        st.stop()

    # ---------------- Validation ----------------
    try:
        validate_nominal_data(topologia, dados_nominais_banco)
    except NominalDataError as e:
        st.error(str(e))
        st.stop()
    except Exception:
        st.error("Parâmetros inválidos. Revise os dados informados.")
        st.stop()

    # ---------------- Show topology figure / exports ----------------
    show_topology_figure(dados_nominais_banco)
    ensure_export_dir()
    LatexReportGenerator.export_dict_tabular(
        data=dados_nominais_banco,
        filename="tabela_dados_nominais.tex",
    )

    return {
        "topologia": topologia,
        "dados_nominais_banco": dados_nominais_banco,
        "selected_transformer_type_option": selected_transformer_type_option,
        "secondary_current_tc": secondary_current_tc,
        "secondary_voltage_tp": secondary_voltage_tp,
    }
