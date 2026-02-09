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


class LatexReportGenerator:
    """Generate LaTeX reports from topology-specific templates."""

    def __init__(self, template_path: str | Path | None = None) -> None:
        if template_path is not None:
            self.template_path = Path(template_path)
        else:
            self.template_path = None

    # ------------------------------------------------------------------
    # Static helpers expected by the project
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

        #################################################
        # Mapeamento de keys: antiga -> nova
        key_map = {
            "tensao_trifasica_banco_V": r"$V_{trabalho}\,\mathrm{(V)}$",
            "potencia_trifasica_banco_VAr": r"$Q_{trabalho}\,\mathrm{(VAr)}$",
            "V_rated": r"$V_{nominal}\,\mathrm{(V)}$",
            "Q_rated": r"$Q_{nominal}\,\mathrm{(VAr)}$",
            "frequencia_Hz": r"$f\,\mathrm{(Hz)}$",
            "S": r"S",
            "St": r"St",
            "Pt": r"Pt",
            "Pa": r"Pa",
            "G": r"G",
            "topologia_protecao": "Topologia de Protecao",
        }

        # Novo dicionario com keys alteradas
        data_latex = {
            key_map.get(k, k): v
            for k, v in data.items()
        }
        ##################################

        keys = list(data.keys())
        if sort_keys is True:
            keys.sort()

        lines: list[str] = []
        lines.append(r"\centering")
        lines.append(r"\begin{tabular}{ll}")
        lines.append(r"\hline")
        lines.append(r"\textbf{Variável} & \textbf{Valor} \\")
        lines.append(r"\hline")


        data_latex.pop("Topologia de Protecao", None)
        keys_latex = list(data_latex.keys())

        for k in keys_latex:
            v = data_latex[k]
            # \\\\ ✅ Isso faz o arquivo .tex sair com \\ no fim de cada linha.
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
    def _template_from_topology(self, topology: str) -> Path:
        topology = str(topology).strip()

        if topology.endswith("_external_fuses"):
            return TEMPLATE_FE_TEX

        if topology.endswith("_internal_fuses"):
            return TEMPLATE_FI_TEX

        # Fallback
        return TEMPLATE_DIR / f"TEMPLATE__{topology}.tex"

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
                "- Put the required template file there (e.g., TEMPLATE__FI.tex / TEMPLATE__FE.tex)\n"
            )
            self._show_streamlit_error_if_available(msg)
            raise FileNotFoundError(str(self.template_path))

        return self.template_path.read_text(encoding="utf-8")

    def fill_template(self, content: str, topology: str, data: Dict[str, Any]) -> str:
        """Replace a minimal set of placeholders in the template."""

        content = content.replace("{{TOPOLOGY}}", str(topology))

        for k in ["S", "Pt", "Pa", "P", "St"]:
            if k in data:
                content = content.replace(f"{{{{{k}}}}}", str(data[k]))

        return content

    def save_report(self, content: str, topology: str) -> str:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        output_path = REPORT_DIR / f"report__{topology}.tex"
        output_path.write_text(content, encoding="utf-8")
        return str(output_path)

    def generate(self, topology: str, data: Dict[str, Any]) -> str:
        """Load template, fill placeholders, save output. Returns output path."""

        self.template_path = self._template_from_topology(topology)

        content = self.load_template()
        content = self.fill_template(content, topology, data)
        output_path = self.save_report(content, topology)
        return output_path

    def compile_pdf(self, *, tex_path: str | Path) -> str:
        """
        Compile a .tex file into PDF using latexmk.
        Returns the generated PDF path as string.
        """
        tex_path_obj = Path(tex_path)

        if tex_path_obj.exists() is False:
            raise FileNotFoundError(str(tex_path_obj))

        # Run latexmk in the directory where the .tex file is located
        workdir = tex_path_obj.parent

        command = [
            "latexmk",
            "-pdf",
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
            # Show full log to help debugging
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

