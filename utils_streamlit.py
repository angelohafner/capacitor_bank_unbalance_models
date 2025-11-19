# utils_streamlit.py
# Comments in English only
import os
import json
import io
import streamlit as st
import pandas as pd


def ensure_export_dir():
    """Create 'exported' folder if it does not exist."""
    os.makedirs("./tex_files/tables", exist_ok=True)

def show_topology_figure(topologia: str):
    """Show figure for the selected topology (if available)."""
    figs_dir = "./tex_files/figs"
    mapping = {
        "yy_external_fuses": "Figure29-yy_external_fuses.png",
        "h_bridge_external_fuses": "Figure32-h_bridge_external_fuses.png",
        "yy_internal_fuses": "Figure34-yy_internal_fuses.png",
        "h_bridge_internal_fuses": "Figure36-h_bridge_internal_fuses.png",
    }
    filename = mapping.get(topologia)
    if not filename:
        st.warning(f"No figure defined for topology '{topologia}'")
        return

    path = os.path.join(figs_dir, filename)
    if not os.path.exists(path):
        st.error(f"Figure not found: {path}")
        return

    if topologia == "h_bridge_external_fuses" or topologia == "h_bridge_internal_fuses":
        left, center, right = st.columns([1, 4, 1])
        with center:
            st.image(path, caption=f"Topology: {topologia}", use_container_width=True)
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
):
    """
    Exibe botões de download para arquivos XLSX, TEX, PDF, JSON e TXT.

    Agora cada arquivo pode ter o nome definido individualmente.
    Se não for fornecido, tenta usar base_name como padrão.

    Parâmetros
    ----------
    base_name : str, opcional
        Nome base antigo (continua funcionando).
    xlsx_file, tex_file, pdf_file, json_file, txt_file : str, opcionais
        Nomes individuais dos arquivos.
    payload_for_dict : dict/DataFrame opcional
        Conteúdo para exportar via JSON/TXT.
    """

    # ====== 1) Resolver nomes ======
    if base_name:
        if xlsx_file is None:
            xlsx_file = f"{base_name}.xlsx"
        if tex_file is None:
            tex_file = f"{base_name}.tex"
        if json_file is None:
            json_file = f"{base_name}.json"
        if txt_file is None:
            txt_file = f"{base_name}.txt"

    # ====== 2) Caminhos completos ======
    xlsx_path = os.path.join("tex_files", "tables", xlsx_file) if xlsx_file else None
    tex_path  = os.path.join("tex_files", "tables", tex_file)  if tex_file else None

    # ====== 3) XLSX ======
    if xlsx_path and os.path.exists(xlsx_path):
        with open(xlsx_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Baixar {xlsx_file}",
                data=f,
                file_name=xlsx_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ====== 4) TEX ======
    if tex_path and os.path.exists(tex_path):
        with open(tex_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Baixar {tex_file}",
                data=f,
                file_name=tex_file,
                mime="application/x-tex",
            )

    # ====== 6) JSON e TXT ======
    if payload_for_dict is not None:
        if json_file:
            json_bytes = _serialize_to_json_bytes(payload_for_dict)
            st.download_button(
                label=f"⬇️ Baixar {json_file}",
                data=io.BytesIO(json_bytes),
                file_name=json_file,
                mime="application/json",
            )

        if txt_file:
            txt_bytes = _serialize_to_txt_bytes(payload_for_dict)
            st.download_button(
                label=f"⬇️ Baixar {txt_file}",
                data=io.BytesIO(txt_bytes),
                file_name=txt_file,
                mime="text/plain",
            )


