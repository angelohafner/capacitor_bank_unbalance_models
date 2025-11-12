# utils_streamlit.py
# Comments in English only
import os
import json
import io
import streamlit as st
import pandas as pd


def ensure_export_dir():
    """Create 'exported' folder if it does not exist."""
    os.makedirs("exported", exist_ok=True)


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
            st.image(path, caption=f"Topology: {topologia}", width="stretch")
    else:
        st.image(path, caption=f"Topology: {topologia}", width="stretch")


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


def show_downloads(base_name: str, payload_for_dict=None, dict_basename: str | None = None):
    """
    Render download buttons for Excel and LaTeX files in 'exported',
    and (optionally) extra JSON/TXT for a dict-like payload.

    Parameters
    ----------
    base_name : str
        Base filename for .xlsx and .tex (without folder).
    payload_for_dict : any, optional
        Dict-like or pandas object to serialize (e.g., df_ieee3ext).
    dict_basename : str, optional
        Base filename for JSON/TXT (defaults to base_name if None).
    """
    xlsx_path = os.path.join("exported", f"{base_name}.xlsx")
    tex_path = os.path.join("exported", f"{base_name}.tex")

    # Excel
    if os.path.exists(xlsx_path):
        with open(xlsx_path, "rb") as f_xlsx:
            st.download_button(
                label=f"⬇️ Baixar {base_name}.xlsx",
                data=f_xlsx,
                file_name=f"{base_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.info(f"Arquivo não encontrado: {xlsx_path}")

    # LaTeX
    if os.path.exists(tex_path):
        with open(tex_path, "rb") as f_tex:
            st.download_button(
                label=f"⬇️ Baixar {base_name}.tex",
                data=f_tex,
                file_name=f"{base_name}.tex",
                mime="application/x-tex",
            )
    else:
        st.info(f"Arquivo não encontrado: {tex_path}")

    # Optional dict/DataFrame export as JSON/TXT
    if payload_for_dict is not None:
        dict_base = dict_basename if dict_basename else base_name

        json_bytes = _serialize_to_json_bytes(payload_for_dict)
        st.download_button(
            label=f"⬇️ Baixar {dict_base}.json",
            data=io.BytesIO(json_bytes),
            file_name=f"{dict_base}.json",
            mime="application/json",
        )

        txt_bytes = _serialize_to_txt_bytes(payload_for_dict)
        st.download_button(
            label=f"⬇️ Baixar {dict_base}.txt",
            data=io.BytesIO(txt_bytes),
            file_name=f"{dict_base}.txt",
            mime="text/plain",
        )
