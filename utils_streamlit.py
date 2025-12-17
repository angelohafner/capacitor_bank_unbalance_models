# utils_streamlit.py
# Comments in English only
import os
import json
import io
import streamlit as st
import pandas as pd
import zipfile
from bank_diagram import BankDiagram
from h_bridge_drawing import HCompleteWithNeutralCT, validate_h_bridge_inputs



def ensure_export_dir():
    """Create 'exported' folder if it does not exist."""
    os.makedirs("./tex_files/tables", exist_ok=True)

def show_topology_figure(dados_nominais_banco):
    """Show figure for the selected topology (if available)."""
    figs_dir = "./tex_files/figs"
    mapping = {
        "yy_external_fuses": "Figure29-yy_external_fuses.png",
        "h_bridge_external_fuses": "Figure32-h_bridge_external_fuses.png",
        "yy_internal_fuses": "Figure34-yy_internal_fuses.png",
        "h_bridge_internal_fuses": "Figure36-h_bridge_internal_fuses.png",
    }
    topologia = dados_nominais_banco["topologia_protecao"]
    if topologia == "h_bridge_external_fuses" or topologia == "h_bridge_internal_fuses":
        filename = None
    else:
        filename = mapping.get(topologia)
        if not filename:
            st.warning(f"No figure defined for topology '{topologia}'")
            return

        path = os.path.join(figs_dir, filename)
        if not os.path.exists(path):
            st.error(f"Figure not found: {path}")
            return

    if topologia == "h_bridge_external_fuses" or topologia == "h_bridge_internal_fuses":
        # Draw dynamically (adapted from ponte_h_desenho.py)
        S = int(dados_nominais_banco["S"])
        St = int(dados_nominais_banco["St"])
        Pt = int(dados_nominais_banco["Pt"])
        Pa = int(dados_nominais_banco["Pa"])
        # External-fuse topology does not provide P; use a reasonable default for drawing.
        if "P" in dados_nominais_banco:
            P = int(dados_nominais_banco["P"])
        else:
            P = 2

        result = validate_h_bridge_inputs(S=S, St=St, Pt=Pt, Pa=Pa, P=P)
        if not result.is_valid:
            st.error("Parâmetros inválidos para o desenho do arranjo H-Bridge:")
            for msg in result.errors:
                st.write("- " + msg)
            if len(result.warnings) > 0:
                st.warning("Avisos:")
                for msg in result.warnings:
                    st.write("- " + msg)
            return

        if len(result.warnings) > 0:
            with st.expander("Avisos do desenho (H-Bridge)", expanded=False):
                for msg in result.warnings:
                    st.write("- " + msg)

        fuse_enabled = False #(topologia == "h_bridge_internal_fuses")

        h = HCompleteWithNeutralCT(
            Pt=Pt,
            Pa=Pa,
            P=P,
            S=S,
            St=St,
            fuse_enabled=fuse_enabled,
        )

        fig = h.make_figure(title=f"H-Bridge ({'FI' if fuse_enabled else 'FE'})")
        st.plotly_chart(fig, use_container_width=True)
    elif topologia == "yy_internal_fuses": #, "yy_external_fuses"
        diagram = BankDiagram(
            P=dados_nominais_banco["P"],
            S=dados_nominais_banco["S"],
            Pt=dados_nominais_banco["Pt"],
            Pa_left=dados_nominais_banco["Pa"],
            x0=0.0,
            y0=0.0,
        )
        fig = diagram.make_figure()
        st.plotly_chart(fig, use_container_width=True)
    elif topologia == "yy_external_fuses":
        diagram = BankDiagram(
            # P=Pa para poder aproveitar classe dos fusiveis internos
            P=dados_nominais_banco["Pa"],
            S=dados_nominais_banco["S"],
            Pt=dados_nominais_banco["Pt"],
            Pa_left=dados_nominais_banco["Pa"],
            x0=0.0,
            y0=0.0,
        )
        fig = diagram.make_figure()
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.image(path, caption=f"Topology: {topologia}", use_container_width=True)


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

    # Build full paths
    xlsx_path = os.path.join("tex_files", "tables", xlsx_file) if xlsx_file else None
    tex_path  = os.path.join("tex_files", "tables", tex_file)  if tex_file else None
    acp_path  = os.path.join("atp_files", acp_file)            if acp_file else None

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

    zip_buffer.seek(0)

    # Single button
    st.download_button(
        label="⬇️ Baixar todos os arquivos",
        data=zip_buffer,
        file_name=f"{base_name or 'files'}.zip",
        mime="application/zip",
    )


