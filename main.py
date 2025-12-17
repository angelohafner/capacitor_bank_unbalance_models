# Comments in English only
from __future__ import annotations

import streamlit as st

from latex_report_generator import LatexReportGenerator
from main_part_1 import run_main_part_1
from topology_registry import get_topology_config
from utils_streamlit import show_downloads


ctx = run_main_part_1()

topologia = ctx["topologia"]
dados_nominais_banco = ctx["dados_nominais_banco"]

config = get_topology_config(topologia)

# ---------------- Run computation ----------------
tabela, df_ieee, df_real = config.compute(dados_nominais_banco)

st.success(f"Tabela gerada ({config.label}).")

# ---------------- Downloads ----------------
show_downloads(
    xlsx_file=config.download_xlsx,
    acp_file=config.download_acp,
)

# ---------------- LaTeX report ----------------
generator = LatexReportGenerator(template_path=config.template_tex)
output_file = generator.generate(topologia, dados_nominais_banco)

st.dataframe(df_real)
generator.compile_pdf(tex_path=output_file)
