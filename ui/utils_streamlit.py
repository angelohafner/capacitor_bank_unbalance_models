# utils_streamlit.py
# Comments in English only
import os
from pathlib import Path
from config.paths import TABLE_DIR, ATP_DIR, FIG_DIR, ensure_directories
import json
import io
import streamlit as st
import pandas as pd
import zipfile
import kaleido
from diagrams.bank_diagram import BankDiagram, SingleWyeBankDiagram
from diagrams.h_bridge_drawing import HCompleteWithNeutralCT
from diagrams.bank_diagram_mpl import BankDiagramMPL
from validation.validators import validate_inputs
from diagrams.y_internal_fuses_diagram import ThreePhaseYInternalFusesDiagram
from ui.plotly_to_mpl import plotly_figure_to_matplotlib



def ensure_export_dir():
    """Create 'exported' folder if it does not exist."""
    ensure_directories()

def show_topology_figure(dados_nominais_banco):
    """Show figure for the selected topology (if available)."""
    topologia = dados_nominais_banco["topologia_protecao"]

    # ---------------- Plotly: single-wye internal fuses ----------------
    if topologia == "y_internal_fuses":
        S = int(dados_nominais_banco.get("S", 4))
        diagram = ThreePhaseYInternalFusesDiagram(S=S)
        fig_plotly = diagram.make_figure(width=450, height=350)
        st.plotly_chart(fig_plotly, width='stretch')
        fig_plotly.write_image(FIG_DIR/"bank_diagram_matplotlib.pdf")
        return
    # ---------------- Plotly: double-wye (yy) diagrams ----------------
    if topologia == "yy_internal_fuses":
        P = int(dados_nominais_banco.get("P", 3))
        S = int(dados_nominais_banco.get("S", 4))
        Pt = int(dados_nominais_banco.get("Pt", 11))
        Pa = int(dados_nominais_banco.get("Pa", 6))
        result = validate_inputs(topology=topologia, data=dados_nominais_banco)
        if result.is_valid is False:
            st.warning("\n".join(result.errors))
            return
        diagram = BankDiagram(P=P, S=S, Pt=Pt, Pa_left=Pa)
        fig_plotly = diagram.make_figure()
        st.plotly_chart(fig_plotly, width='stretch')
        fig_plotly.write_image(FIG_DIR / "bank_diagram_matplotlib.pdf")
        return

    if topologia == "yy_external_fuses":
        # External-fuse case does not provide P.
        # Force P=1 so Pa/P is always integer and the drawing does not depend on P.
        P = 1
        S = int(dados_nominais_banco.get("S", 4))
        Pt = int(dados_nominais_banco.get("Pt", 14))
        Pa = int(dados_nominais_banco.get("Pa", 8))
        result = validate_inputs(topology=topologia, data=dados_nominais_banco)
        if result.is_valid is False:
            st.warning("\n".join(result.errors))
            return
        diagram = BankDiagram(P=P, S=S, Pt=Pt, Pa_left=Pa)
        fig_plotly = diagram.make_figure()
        st.plotly_chart(fig_plotly, width='stretch')
        fig_plotly.write_image(FIG_DIR / "bank_diagram_matplotlib.pdf")
        return
    # ---------------- Plotly: H-bridge diagrams ----------------
    if topologia == "h_bridge_internal_fuses" or topologia == "h_bridge_external_fuses":
        S = int(dados_nominais_banco.get("S", 7))
        St = int(dados_nominais_banco.get("St", 3))
        Pt = int(dados_nominais_banco.get("Pt", 9))
        Pa = int(dados_nominais_banco.get("Pa", 5))
        P = int(dados_nominais_banco.get("P", 2))
        result = validate_inputs(topology=topologia, data=dados_nominais_banco)
        if result.is_valid is False:
            st.warning("\n".join(result.errors))
            return
        h = HCompleteWithNeutralCT(
            Pt=Pt,
            Pa=Pa,
            P=P,
            S=S,
            St=St,
            gap_between_legs=14.0,
            left_internal_gap=8.0,
            right_group_gap=9.0,
            bus_stub=7.0,
            ct_box_w=3.2,
            ct_box_h=1.4,
        )
        fig_plotly = h.make_figure(title="H-Bridge", width=1600, height=450)
        st.plotly_chart(fig_plotly, width='stretch')
        fig_plotly.write_image(FIG_DIR / "bank_diagram_matplotlib.pdf")
        return

    st.warning(f"No figure defined for topology '{topologia}'")


def _serialize_to_json_bytes(obj) -> bytes:
    """Serialize a dict/DataFrame/Series/list to JSON bytes (UTF-8)."""
    if isinstance(obj, pd.DataFrame):
        payload = obj.to_dict(orient="records")
    elif isinstance(obj, pd.Series):
        payload = obj.to_dict()
    else:
        payload = obj
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _serialize_to_txt_bytes(obj) -> bytes:
    """Serialize a dict/DataFrame/Series/list to a human-readable TXT bytes."""
    if isinstance(obj, pd.DataFrame):
        # Wide-friendly plain text table
        txt = obj.to_string(index=False)
    elif isinstance(obj, pd.Series):
        txt = obj.to_string()
    elif isinstance(obj, (dict, list, tuple)):
        # Pretty-print JSON-like
        txt = json.dumps(obj, ensure_ascii=False, indent=2)
    else:
        txt = str(obj)
    return txt.encode("utf-8")


def show_downloads(
    base_name: str | None = None,
    *,
    xlsx_file: str | None = None,
    tex_file: str | None = None,
    payload_for_dict=None,
    json_file: str | None = None,
    txt_file: str | None = None,
    acp_file: str | None = None,
    fig_file: str | None = None,
):
    """
    Single ZIP download button for all available files.
    """

    # Resolve default names
    if base_name:
        if xlsx_file is None:
            xlsx_file = f"{base_name}.xlsx"
        if tex_file is None:
            tex_file = f"{base_name}.tex"
        if json_file is None:
            json_file = f"{base_name}.json"
        if txt_file is None:
            txt_file = f"{base_name}.txt"
        if fig_file is None:
            fig_file = "bank_diagram_matplotlib.pdf"


    # Build full paths
    xlsx_path = str(TABLE_DIR / xlsx_file) if xlsx_file else None
    tex_path  = str(TABLE_DIR / tex_file)  if tex_file else None
    acp_path  = str(ATP_DIR / acp_file)    if acp_file else None
    fig_path = str(FIG_DIR / fig_file) if fig_file else None

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add XLSX
        if xlsx_path and os.path.exists(xlsx_path):
            zipf.write(xlsx_path, arcname=xlsx_file)
        # Add TEX
        if tex_path and os.path.exists(tex_path):
            zipf.write(tex_path, arcname=tex_file)
        # Add ACP
        if acp_path and os.path.exists(acp_path):
            zipf.write(acp_path, arcname=os.path.basename(acp_path))
        # Add JSON from payload
        if payload_for_dict is not None and json_file:
            json_bytes = _serialize_to_json_bytes(payload_for_dict)
            zipf.writestr(json_file, json_bytes)
        # Add TXT from payload
        if payload_for_dict is not None and txt_file:
            txt_bytes = _serialize_to_txt_bytes(payload_for_dict)
            zipf.writestr(txt_file, txt_bytes)
        # Add FIG
        if fig_path and os.path.exists(fig_path):
            zipf.write(fig_path, arcname=os.path.basename(fig_path))

    zip_buffer.seek(0)

    # Single button
    st.download_button(
        label="⬇️ Baixar todos os arquivos",
        data=zip_buffer,
        file_name=f"{base_name or 'files'}.zip",
        mime="application/zip",
    )