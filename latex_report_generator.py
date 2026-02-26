# Comments in English only
import os
import subprocess
import streamlit as st


class LatexReportGenerator:
    """
    Loads a LaTeX template, replaces {{keys}} with values from a dictionary,
    and writes Relatorio-{topology}.tex inside ./tex_files/reports.
    """

    def __init__(self, template_path: str, output_dir: str = r"./tex_files/"):
        self.template_path = template_path
        self.output_dir = output_dir

    def load_template(self) -> str:
        """Read template file and return its content."""
        with open(self.template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def fill_template(self, content: str, topology: str, data: dict) -> str:
        """Replace all {{key}} placeholders with dictionary values."""
        for key, value in data.items():
            placeholder = "{{" + key + "}}"
            content = content.replace(placeholder, str(value))

        # Replace {{topologia}} as well
        content = content.replace("{{topologia}}", topology)
        return content

    def save_report(self, content: str, topology: str) -> str:
        """Save final LaTeX file inside ./tex_files/reports."""
        output_dir_abs = os.path.abspath(self.output_dir)
        os.makedirs(output_dir_abs, exist_ok=True)

        filename = "Relatorio-{0}.tex".format(topology)
        output_path = os.path.join(output_dir_abs, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def generate(self, topology: str, data: dict) -> str:
        """
        Main method: load template, fill placeholders, save output.
        Returns the full path of the generated .tex file.
        """
        content = self.load_template()
        content = self.fill_template(content, topology, data)
        output_path = self.save_report(content, topology)
        return output_path

    def compile_pdf(self, tex_path: str, latex_cmd: str = r"xelatex") -> str:
        """
        Compile a .tex file to PDF using xelatex.
        The working directory is the folder containing the .tex file.
        Returns the full path of the generated PDF.
        Also renders a Streamlit button to trigger compilation.
        """

        tex_path_abs = os.path.abspath(tex_path)
        workdir = os.path.dirname(tex_path_abs)
        tex_filename = os.path.basename(tex_path_abs)

        # --------------------------------------------
        # Botão no Streamlit para executar a compilação
        # --------------------------------------------
        st.subheader("📄 Compilação do relatório em PDF")

        if st.button("▶️ Compilar PDF agora"):
            try:
                run_index = 0
                while run_index < 2:
                    result = subprocess.run(
                        [
                            latex_cmd,
                            "-interaction=nonstopmode",
                            "-halt-on-error",
                            tex_filename,
                        ],
                        cwd=workdir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if result.returncode != 0:
                        raise RuntimeError(
                            "LaTeX compilation failed.\nSTDOUT:\n{0}\n\nSTDERR:\n{1}".format(
                                result.stdout, result.stderr
                            )
                        )
                    run_index = run_index + 1

                pdf_path = os.path.splitext(tex_path_abs)[0] + ".pdf"
                # st.success(f"PDF gerado com sucesso: {pdf_path}")

                # Botão de download do PDF
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                    )

                return pdf_path

            except Exception as e:
                st.error(f"❌ Erro ao compilar PDF:\n{e}")
                return ""

        # Caso o usuário ainda não clique o botão
        st.info("Pressione o botão acima para gerar o PDF.")
        return ""

    # ---------------------------------------------------------
    # Build a LaTeX tabular from a dictionary (dados_nominais_banco)
    # ---------------------------------------------------------
    # Comments in English only
    import os

    def export_dict_tabular(data: dict, filename: str = "tabela_dados_nominais.tex") -> str:
        """
        Build and save a LaTeX tabular from a dictionary (dados_nominais_banco).
        - Uses friendly labels and unit conversions for some known keys.
        - Moves the last key of the dict to the first row in the table.
        - Saves the result in ./tex_files/tables/<filename>.
        """

        # Directory where the .tex file will be saved
        output_dir = r"./tex_files/tables"
        os.makedirs(output_dir, exist_ok=True)

        # Friendly names + unit conversions
        substitutions = {
            "tensao_trifasica_banco_V": (
                "Tensão fase-fase do banco (kV)",
                lambda v: float(v) / 1000.0,
            ),
            "potencia_trifasica_banco_VAr": (
                "Potência do banco (MVAR)",
                lambda v: float(v) / 1_000_000.0,
            ),
            "frequencia_Hz": (
                "Frequência (Hz)",
                lambda v: v,
            ),
            "topologia_protecao": (
                "Topologia de proteção",
                lambda v: (
                    {
                        "yy_internal_fuses":  "Fusíveis Internos Dupla Estrela",
                        "y_internal_fuses":   "Fusíveis Internos Estrela Simples",
                        "yy_external_fuses":  "Fusíveis Externos Dupla Estrela",
                        "h_bridge_internal_fuses": "Fusíveis Internos Ponte H",
                        "h_bridge_external_fuses": "Fusíveis Externos Ponte H",
                    }.get(str(v), str(v))
                ),
            ),
        }

        # Build the table
        lines = []
        lines.append(r"\begin{tabular}{cc}")
        lines.append(r"\hline")
        lines.append(r"Parâmetro & Valor \\")
        lines.append(r"\hline")

        # Reorder keys: move last entry to the first position
        keys = list(data.keys())
        if len(keys) > 1:
            keys = [keys[-1]] + keys[:-1]

        for key in keys:
            value = data[key]

            if key in substitutions:
                label, converter = substitutions[key]
                new_value = converter(value)

                # Format numeric values with 2 decimals and comma
                if isinstance(new_value, (int, float)):
                    value_tex = f"{new_value:.2f}".replace(".", ",")
                else:
                    value_tex = str(new_value)

                lines.append(f"{label} & {value_tex} \\\\")

            else:
                # Default formatting: escape underscores in the key
                key_tex = str(key).replace("_", r"\_")
                value_tex = str(value)
                lines.append(f"{key_tex} & {value_tex} \\\\")

        lines.append(r"\hline")
        lines.append(r"\end{tabular}")

        tabular_text = "\n".join(lines)

        # Save the .tex file
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tabular_text)

        return output_path



