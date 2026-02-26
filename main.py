# Comments in English only
from __future__ import annotations
from pathlib import Path
import streamlit as st

from reports.latex_report_generator import LatexReportGenerator, clean_reports_directory
from main_part_1 import run_main_part_1
from topology_registry import get_topology_config
from ui.utils_streamlit import show_downloads


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
    fig_file="bank_diagram_matplotlib.pdf",
)

# ---------------- LaTeX report ----------------
st.dataframe(df_real)
st.write(dados_nominais_banco)
clean_reports_directory()

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

if st.button("Compilar PDF"):
    generator = LatexReportGenerator(template_path=config.template_tex)
    output_file = generator.generate(topologia, dados_nominais_banco)
    generator.compile_pdf(tex_path=output_file)

    # latexmk gera o PDF com o mesmo nome do .tex
    pdf_path = Path(output_file).with_suffix(".pdf")
    st.session_state.pdf_path = pdf_path

    st.success("PDF compilado com sucesso.")

    if st.session_state.pdf_path and st.session_state.pdf_path.exists():
        with open(st.session_state.pdf_path, "rb") as f:
            st.download_button(
                label="Baixar PDF",
                data=f,
                file_name=st.session_state.pdf_path.name,
                mime="application/pdf",
            )



