# reports/latex_report_generator.py
# Comments in English only
from __future__ import annotations

from shutil import copy2
from config.paths import FIG_DIR, REPORT_DIR

import subprocess
from pathlib import Path

from pathlib import Path
from typing import Any, Dict, Optional

from config.paths import REPORT_DIR, TABLE_DIR, TEMPLATE_DIR, TEMPLATE_FI_TEX, TEMPLATE_FE_TEX
#from engineering_notation import EngNumber


def format_eng(value, precision=3):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if value == 0:
        return "0"

    import math

    prefixes = {
        -12: "p",
        -9: "n",
        -6: "u",
        -3: "m",
         0: "",
         3: "k",
         6: "M",
         9: "G",
        12: "T",
    }

    exp = int(math.floor(math.log10(abs(value)) / 3) * 3)
    exp = max(min(exp, 12), -12)

    scaled = value / (10 ** exp)
    return f"{scaled:.3g} {prefixes[exp]}"

# Comments in English only
from pathlib import Path


def clean_reports_directory(path: str | Path = "./tex_files/reports") -> int:
    """
    Delete ALL files inside the directory,
    but keep subdirectories untouched.
    """

    target_dir = Path(path)

    if target_dir.exists() is False:
        return 0

    removed = 0

    for item in target_dir.iterdir():

        # Remove only files
        if item.is_file():
            item.unlink()
            removed = removed + 1

        # Ignore directories completely
        # (do not recurse, do not delete)

    return removed






class LatexReportGenerator:
    """Generate LaTeX reports from topology-specific templates."""

    def __init__(
        self,
        template_path: str | Path | None = None,
        *,
        clean_before_compile: bool = True,
        delete_pdf_on_clean: bool = False,
    ) -> None:
        if template_path is not None:
            self.template_path = Path(template_path)
        else:
            self.template_path = None

        self.clean_before_compile = clean_before_compile
        self.delete_pdf_on_clean = delete_pdf_on_clean

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _latex_escape(text: str) -> str:
        """Minimal LaTeX escaping for common special characters."""

        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        out = str(text)
        for k, v in replacements.items():
            out = out.replace(k, v)
        return out

    @staticmethod
    def export_dict_tabular(
        data: Dict[str, Any],
        output_tex_path: str | Path | None = None,
        *,
        filename: str | None = None,
        output_dir: str | Path | None = None,
        caption: str = "",
        label: str = "",
        sort_keys: bool = True,
    ) -> str:
        """
        Export a dict as a simple LaTeX tabular table.

        Compatibility:
        - If output_tex_path is provided, it is used directly.
        - Otherwise, 'filename' is required and the file is written to:
          output_dir (if provided) or TABLE_DIR (default).
        Returns the output path as string.
        """

        if output_tex_path is not None:
            out_path = Path(output_tex_path)
        else:
            if filename is None:
                raise ValueError("export_dict_tabular requires output_tex_path or filename")
            base_dir = Path(output_dir) if output_dir is not None else TABLE_DIR
            out_path = base_dir / filename

        out_path.parent.mkdir(parents=True, exist_ok=True)

        key_map = {
            "tensao_trifasica_banco_V": r"Tensao de Trabalho (V)",
            "potencia_trifasica_banco_VAr": r"Potencia de Trabalho (VAr)",
            "V_rated": r"Tensao Nominal (V)",
            "Q_rated": r"Potencia Nominal (VAr)",
            "frequencia_Hz": r"Frequencia (Hz)",
            "S": r"Unidades Series Fase-Neutro",
            "St": r"Unidades Series Fase-Neutro",
            "Pt": r"Unidades Paralelas Total",
            "Pa": r"Unidades Paralelas Ramo Esquerda",
            "P": r"Unidades Paralelas String Afetada",
            "N": r"Elementos internos em paralelo no grupo",
            "Su": r"Grupos de elementos em serie em uma unidade",
            "G": r"Aterrado (0) / Isolado (1)",
            "topologia_protecao": "Topologia de Protecao",
        }

        data_latex = {key_map.get(k, k): v for k, v in data.items()}
        data_latex.pop("Topologia de Protecao", None)

        keys_latex = list(data_latex.keys())
        if sort_keys is True:
            keys_latex.sort()

        lines: list[str] = []
        lines.append(r"\centering")
        lines.append(r"\begin{tabular}{lr}")
        lines.append(r"\hline")
        lines.append(r"\textbf{Variavel} & \textbf{Valor} \\")
        lines.append(r"\hline")

        for k in keys_latex:
            v = data_latex[k]
            lines.append(f"{k} & {format_eng(v)} \\\\")

        lines.append(r"\hline")
        lines.append(r"\end{tabular}")

        if caption.strip() != "":
            lines.append(rf"\caption{{{LatexReportGenerator._latex_escape(caption)}}}")
        if label.strip() != "":
            lines.append(rf"\label{{{LatexReportGenerator._latex_escape(label)}}}")

        lines.append("")

        out_path.write_text("\n".join(lines), encoding="utf-8")
        return str(out_path)

    # ------------------------------------------------------------------
    # Template and IO
    # ------------------------------------------------------------------

    def _template_from_topology(self, topology: str) -> Path:
        topology_str = str(topology).strip()

        if topology_str.endswith("_external_fuses"):
            return TEMPLATE_FE_TEX

        if topology_str.endswith("_internal_fuses"):
            return TEMPLATE_FI_TEX

        return TEMPLATE_DIR / f"TEMPLATE__{topology_str}.tex"

    def _show_streamlit_error_if_available(self, message: str) -> None:
        """Show Streamlit error if Streamlit is available and running."""

        try:
            import streamlit as st  # type: ignore

            st.error(message)
        except Exception:
            pass

    def load_template(self) -> str:
        if self.template_path is None:
            raise ValueError("template_path was not set before load_template().")

        if self.template_path.exists() is False:
            msg = (
                "LaTeX template file not found.\n\n"
                f"Expected path:\n{self.template_path}\n\n"
                "Fix:\n"
                "- Ensure ./templates exists in the project root\n"
                "- Put the required template file there\n"
            )
            self._show_streamlit_error_if_available(msg)
            raise FileNotFoundError(str(self.template_path))

        return self.template_path.read_text(encoding="utf-8")

    def fill_template(self, content: str, topology: str, data: Dict[str, Any]) -> str:
        """Replace a minimal set of placeholders in the template."""

        out = content.replace("{{TOPOLOGY}}", str(topology))

        keys_to_replace = ["S", "Pt", "Pa", "P", "St"]
        for k in keys_to_replace:
            if k in data:
                out = out.replace(f"{{{{{k}}}}}", str(data[k]))

        return out

    def save_report(self, content: str, topology: str, data: Dict[str, Any]) -> str:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        v_trab = str(round(data["tensao_trifasica_banco_V"] / 1e3, 1))
        p_trab = str(round(data["potencia_trifasica_banco_VAr"] / 1e6, 1))
        v_nom = str(round(data["V_rated"] / 1e3, 1))
        p_nom = str(round(data["Q_rated"] / 1e6, 1))

        pt = str(data.get("Pt", "xx"))
        s = str(data.get("S", "xx"))
        n = str(data.get("N", "xx"))
        su = str(data.get("Su", "xx"))
        g = str(data.get("G", "xx"))

        filename = (
            f"{topology}_"
            f"{v_trab}kV_trab___"
            f"{p_trab}MVAr_trab__"
            f"{v_nom}kV_nom___"
            f"{p_nom}MVAr_nom__"
            f"{s}S_{pt}Pt__"
            f"{su}Su_{n}N__"
            f"{g}G.tex"
        )

        output_path = REPORT_DIR / filename
        output_path.write_text(content, encoding="utf-8")
        return str(output_path)

    def generate(self, topology: str, data: Dict[str, Any]) -> str:
        """Load template, fill placeholders, save output. Returns output path."""

        self.template_path = self._template_from_topology(topology)

        content = self.load_template()
        content = self.fill_template(content, topology, data)
        output_path = self.save_report(content, topology, data)
        return output_path

    # ------------------------------------------------------------------
    # Build (clean + compile)
    # ------------------------------------------------------------------

    def _latexmk_clean(self, *, workdir: Path) -> None:
        """Run latexmk clean in workdir."""

        if workdir.exists() is False:
            return

        command = ["latexmk", "-C"]

        if self.delete_pdf_on_clean is True:
            command.append("-gg")

        subprocess.run(
            command,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            shell=False,
        )

    def compile_pdf(self, *, tex_path: str | Path) -> str:
        """
        Compile a .tex file into PDF using latexmk.
        Returns the generated PDF path as string.
        """

        tex_path_obj = Path(tex_path)

        if tex_path_obj.exists() is False:
            raise FileNotFoundError(str(tex_path_obj))

        workdir = tex_path_obj.parent

        if self.clean_before_compile is True:
            self._latexmk_clean(workdir=workdir)

        command = [
            "latexmk",
            "-pdf",
            "-gg",  # force full rebuild of dependencies
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path_obj.name,
        ]

        result = subprocess.run(
            command,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            shell=False,
        )

        if result.returncode != 0:
            error_msg = (
                "LaTeX compilation failed.\n\n"
                f"Command: {' '.join(command)}\n"
                f"Workdir: {workdir}\n\n"
                "STDOUT:\n"
                f"{result.stdout}\n\n"
                "STDERR:\n"
                f"{result.stderr}\n"
            )
            raise RuntimeError(error_msg)

        pdf_path = tex_path_obj.with_suffix(".pdf")

        if pdf_path.exists() is False:
            raise FileNotFoundError(str(pdf_path))

        return str(pdf_path)

    def generate_and_compile(self, *, topology: str, data: Dict[str, Any]) -> str:
        """Convenience method: generate .tex and compile to PDF. Returns PDF path."""

        tex_path = self.generate(topology, data)
        pdf_path = self.compile_pdf(tex_path=tex_path)
        return pdf_path

