import pandas as pd
from typing import Iterable, Union

Number = Union[int, float]

class Table03DoubleWyeFig29:
    """
    Table 3 — Unbalance calculations for the double wye-connected capacitor bank (Figure 29)
    """

    def __init__(self, S: int, Pt: int, Pa: int, Cu_fixed: float = 1.0):
        self.S = S
        self.Pt = Pt
        self.Pa = Pa
        self.Cu_fixed = float(Cu_fixed)
        self.df = pd.DataFrame()
        self._validate()

    def _validate(self):
        if any(v <= 0 for v in (self.S, self.Pt, self.Pa)):
            raise ValueError("S, Pt, Pa devem ser positivos.")

    @staticmethod
    def _safe_div(num: Number, den: Number, name: str) -> float:
        if abs(den) < 1e-12:
            raise ZeroDivisionError(f"Divisão por zero em {name}.")
        return float(num) / float(den)

    # ---- Fórmulas da Tabela 3 ----
    def _Cg(self, n: int) -> float:
        return self._safe_div(self.Pa - n, self.Pa, "Cg")

    def _Cs(self, Cg: float) -> float:
        num = self.S * Cg
        den = Cg * (self.S - 1) + 1.0
        return self._safe_div(num, den, "Cs")

    def _Cp(self, Cs: float) -> float:
        num = Cs * self.Pa + (self.Pt - self.Pa)
        den = self.Pt
        return self._safe_div(num, den, "Cp")

    def _Vng(self, Cp: float, G: int) -> float:
        inner = self._safe_div(3.0, 2.0 + Cp, "Vng inner")
        return G * (inner - 1.0)

    def _Vln(self, Vng: float) -> float:
        return 1.0 + Vng

    def _Vcu(self, Vln: float, Cs: float, Cg: float) -> float:
        if abs(Cg) < 1e-12:
            return Vln * self.S
        return self._safe_div(Vln * Cs, Cg, "Vcu")

    def _Iu(self, Vcu: float) -> float:
        return Vcu * self.Cu_fixed

    def _Iy(self, Cs: float, Vln: float) -> float:
        return Cs * Vln

    def _Iph(self, Cp: float, Vln: float) -> float:
        return Cp * Vln

    def _Ig(self, Iph: float, G: int) -> float:
        return (1 - G) * (1.0 - Iph)

    def _In(self, Vng: float, G: int) -> float:
        return self._safe_div(3.0 * Vng * G * (self.Pt - self.Pa), self.Pt, "In")

    # ---- Execução principal ----
    def calcular(self, G: int, n_values: Iterable[int] = None):
        if G not in (0, 1):
            raise ValueError("G deve ser 0 (aterrado) ou 1 (isolado).")
        if n_values is None:
            n_values = range(0, self.Pa - 2)

        resultados = []
        for n in n_values:
            n = int(n)
            if n < 0 or n > self.Pa:
                raise ValueError("n fora do intervalo permitido.")

            Cg = self._Cg(n)
            Cs = self._Cs(Cg)
            Cp = self._Cp(Cs)
            Vng = self._Vng(Cp, G)
            Vln = self._Vln(Vng)
            Vcu = self._Vcu(Vln, Cs, Cg)
            Iu = self._Iu(Vcu)
            Iy = self._Iy(Cs, Vln)
            Iph = self._Iph(Cp, Vln)
            Ig = self._Ig(Iph, G)
            In = self._In(Vng, G)

            resultados.append({
                "G": G,
                "n": n,
                "Cu(fixed)": self.Cu_fixed,
                "Cg": round(Cg, 6),
                "Cs": round(Cs, 6),
                "Cp": round(Cp, 6),
                "Vng": round(Vng, 6),
                "Vln": round(Vln, 6),
                "Vcu": round(Vcu, 6),
                "Iu": round(Iu, 6),
                "Iy": round(Iy, 6),
                "Iph": round(Iph, 6),
                "Ig": round(Ig, 6),
                "In": round(In, 6),
            })

        self.df = pd.DataFrame(resultados)
        return self.df

    def exportar(self, formato="markdown"):
        if self.df.empty:
            raise ValueError("Execute calcular(G) antes de exportar.")
        if formato == "markdown":
            try:
                return self.df.to_markdown(index=False)
            except Exception:
                return self.df.to_string(index=False)
        if formato == "csv":
            return self.df.to_csv(index=False)
        if formato == "json":
            return self.df.to_json(orient="records", indent=2)
        if formato == "latex":
            return self.df.to_latex(index=False, escape=False)
        return self.df

    def salvar_excel(self, filepath="Table03.xlsx"):
        if self.df.empty:
            raise ValueError("Execute calcular(G) antes de salvar.")
        self.df.to_excel(filepath, index=False)


# ---- Exemplo de uso ----
# if __name__ == "__main__":
#     tabela3 = Table03DoubleWyeFig29(S=4, Pt=14, Pa=8, Cu_fixed=1.0)
#     tabela3.calcular(G=1)  # banco isolado
#     print(tabela3.exportar("markdown"))
#     tabela3.salvar_excel("Table03.xlsx")
#     print("Excel salvo: Table03.xlsx")
