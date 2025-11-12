# Comments in English only
import os
import streamlit as st

from master_bank_classes import MasterBankClasses
from input_widgets import get_dados_nominais_banco
from utils_streamlit import ensure_export_dir, show_topology_figure, show_downloads


# ---------------- Page config ----------------
# Force light theme
st.set_page_config(page_title="Desbalanceamento - Banco de Capacitores", page_icon="──∥──", layout="centered", initial_sidebar_state="expanded")

# Apply theme override (works for Streamlit >= 1.31)
st.markdown("""
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
""", unsafe_allow_html=True)

st.markdown(
    "# Desbalanceamento para um banco de capacitores "
    "[IEEE C37.99](https://standards.ieee.org/ieee/C37.99/5511/)"
)

# ---------------- Header row ----------------
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    topologia = st.selectbox(
        "Topologia de proteção:",
        ["yy_internal_fuses", "yy_external_fuses", "h_bridge_internal_fuses", "h_bridge_external_fuses"],
    )

with col2:
    transformer_type_option = ["TC", "TP"]
    selected_transformer_type_option = st.selectbox("Proteção com TC ou TP?:", transformer_type_option)

with col3:
    if selected_transformer_type_option == "TC":
        tc_secondary_options = [5, 1]
        secondary_current_tc = st.selectbox("Corrente secundária [A]:", tc_secondary_options)
        secondary_voltage_tp = None
    else:
        tp_secondary_options = [115]
        secondary_voltage_tp = st.selectbox("Tensão secundária [V]:", tp_secondary_options)
        secondary_current_tc = None

# ---------------- Build nominal dictionary from UI ----------------
show_topology_figure(topologia)
ensure_export_dir()

dados_nominais_banco = get_dados_nominais_banco(topologia)
if not dados_nominais_banco:
    st.stop()

# ---------------- Run according to topology ----------------
match topologia:
    case "h_bridge_internal_fuses":
        # Table 8
        tabela8, df_ieee8, df_real8 = MasterBankClasses.compute_table08_from_dict(
            dados_nominais_banco,
            tex_filename=os.path.join("exported", "tabela8_real.tex"),
            xlsx_filename=os.path.join("exported", "tabela8_real.xlsx"),
            f_values=None,
            export_tex=True,
            export_xlsx=True,
        )
        st.success("Tabela 8 gerada (H-Bridge com fusíveis internos).")
        show_downloads(
            base_name="tabela8_real",
            payload_for_dict=df_ieee8,
            dict_basename="df_ieee8",   # df_ieee8.json / df_ieee8.txt
        )

    case "yy_internal_fuses":
        # Table 7
        tabela7, df_ieee7, df_real7 = MasterBankClasses.compute_table07_from_dict(
            dados_nominais_banco,
            tex_filename=os.path.join("exported", "tabela7_real.tex"),
            xlsx_filename=os.path.join("exported", "tabela7_real.xlsx"),
            f_values=None,
            export_tex=True,
            export_xlsx=True,
        )
        st.success("Tabela 7 gerada (Dupla estrela com fusíveis internos).")
        show_downloads(
            base_name="tabela7_real",
            payload_for_dict=df_ieee7,
            dict_basename="df_ieee7",   # df_ieee7.json / df_ieee7.txt
        )

    case "h_bridge_external_fuses":
        # Table 6
        tabela6, df_ieee6, df_real6 = MasterBankClasses.compute_table06_from_dict(
            dados_nominais_banco,
            tex_filename=os.path.join("exported", "tabela6_real.tex"),
            xlsx_filename=os.path.join("exported", "tabela6_real.xlsx"),
            export_tex=True,
            export_xlsx=True,
        )
        st.success("Tabela 6 gerada (H-Bridge com fusíveis externos).")
        show_downloads(
            base_name="tabela6_real",
            payload_for_dict=df_ieee6,
            dict_basename="df_ieee6",   # df_ieee6.json / df_ieee6.txt
        )

    case "yy_external_fuses":
        # Table 3 (external)
        tabela3ext, df_ieee3ext, df_real3ext = MasterBankClasses.compute_table03_from_dict(
            dados_nominais_banco,
            tex_filename=os.path.join("exported", "tabela3ext_real.tex"),
            xlsx_filename=os.path.join("exported", "tabela3ext_real.xlsx"),
            f_values=None,
            export_tex=True,
            export_xlsx=True,
        )
        st.success("Tabela 3 (externa) gerada (Dupla estrela com fusíveis externos).")
        show_downloads(
            base_name="tabela3ext_real",
            payload_for_dict=df_ieee3ext,
            dict_basename="df_ieee3ext",  # df_ieee3ext.json / df_ieee3ext.txt
        )

    case _:
        st.error("Topologia não reconhecida.")
