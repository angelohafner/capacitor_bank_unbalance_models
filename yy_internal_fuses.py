import pandas as pd
from typing import Iterable, Union

Number = Union[int, float]

class Table07DoubleWyeFig34:
    """
    Table 7 — Unbalance calculations for the double wye-connected capacitor bank (Figure 34)
    """

    def __init__(self, S, Pt, Pa, P, N, Su):
        self.S = S
        self.Pt = Pt
        self.Pa = Pa
        self.P = P
        self.N = N
        self.Su = Su
        self.df = pd.DataFrame()
        self._validate()

    def _validate(self):
        if any(v <= 0 for v in (self.S, self.Pt, self.Pa, self.P, self.N, self.Su)):
            raise ValueError("All parameters must be positive.")

    @staticmethod
    def _safe_div(num: Number, den: Number, name: str) -> float:
        if abs(den) < 1e-12:
            raise ZeroDivisionError(f"Zero denominator in {name}.")
        return float(num) / float(den)

    # ---------------- formulas ----------------
    def _Ci(self, f: int) -> float:
        return self._safe_div(self.N - f, self.N, "Ci")

    def _Vg(self, f: int) -> float:
        num = self.Su * self.N
        den = (self.Su - 1) * (self.N - f) + self.N
        return self._safe_div(num, den, "Vg")

    def _Cu(self, Ci: float) -> float:
        num = self.Su * Ci
        den = Ci * (self.Su - 1) + 1
        return self._safe_div(num, den, "Cu")

    def _Cg(self, Cu: float) -> float:
        return self._safe_div(self.P - 1 + Cu, self.P, "Cg")

    def _Cs(self, Cg: float) -> float:
        num = self.S * Cg
        den = Cg * (self.S - 1) + 1
        return self._safe_div(num, den, "Cs")

    def _Cp(self, Cs: float) -> float:
        num = Cs * self.P + (self.Pt - self.P)
        den = self.Pt
        return self._safe_div(num, den, "Cp")

    def _Vng(self, Cp: float, G: int) -> float:
        inner = self._safe_div(3.0, 2.0 + Cp, "Vng inner")
        return G * (inner - 1.0)

    def _Vln(self, Vng: float) -> float:
        return 1.0 + Vng

    def _Vcu(self, Vln: float, Cs: float, Cg: float) -> float:
        return self._safe_div(Vln * Cs, Cg, "Vcu")

    def _Ve(self, Vcu: float, Vg: float) -> float:
        return Vcu * Vg

    def _Iu(self, Vcu: float, Cu: float) -> float:
        return Vcu * Cu

    def _Ist(self, Cs: float, Vln: float) -> float:
        return Cs * Vln

    def _Iph(self, Cp: float, Vln: float) -> float:
        return Cp * Vln

    def _Ig(self, Iph: float, G: int) -> float:
        return (1 - G) * (1 - Iph)

    def _In(self, Vng: float, G: int) -> float:
        num = 3.0 * Vng * G * (self.Pt - self.Pa)
        den = self.Pt
        return self._safe_div(num, den, "In")

    def _Id(self, Vln: float, Cp: float) -> float:
        # Cálculo mantido internamente, mas não exibido
        return Vln * (1 - Cp)

    # ---------------- main ----------------
    def calcular(self, G: int, f_values: Iterable[int] = None):
        if G not in (0, 1):
            raise ValueError("G must be 0 (grounded) or 1 (ungrounded).")
        if f_values is None:
            f_values = range(0, self.N)

        resultados = []
        for f in f_values:
            Ci = self._Ci(f)
            Vg = self._Vg(f)
            Cu = self._Cu(Ci)
            Cg = self._Cg(Cu)
            Cs = self._Cs(Cg)
            Cp = self._Cp(Cs)
            Vng = self._Vng(Cp, G)
            Vln = self._Vln(Vng)
            Vcu = self._Vcu(Vln, Cs, Cg)
            Ve = self._Ve(Vcu, Vg)
            Iu = self._Iu(Vcu, Cu)
            Ist = self._Ist(Cs, Vln)
            Iph = self._Iph(Cp, Vln)
            Ig = self._Ig(Iph, G)
            In = self._In(Vng, G)
            _ = self._Id(Vln, Cp)  # cálculo interno, não exibido

            resultados.append({
                "G": G, "f": f,
                "Ci": round(Ci, 6),
                "Vg": round(Vg, 6),
                "Cu": round(Cu, 6),
                "Cg": round(Cg, 6),
                "Cs": round(Cs, 6),
                "Cp": round(Cp, 6),
                "Vng": round(Vng, 6),
                "Vln": round(Vln, 6),
                "Vcu": round(Vcu, 6),
                "Ve": round(Ve, 6),
                "Iu": round(Iu, 6),
                "Ist": round(Ist, 6),
                "Iph": round(Iph, 6),
                "Ig": round(Ig, 6),
                "In": round(In, 6)
            })

        self.df = pd.DataFrame(resultados)
        return self.df

    # ---------------- export helpers ----------------
    def exportar(self, formato="markdown"):
        if self.df.empty:
            raise ValueError("Execute calcular(G) before exporting.")
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

    def salvar_excel(self, filepath="Table07.xlsx"):
        if self.df.empty:
            raise ValueError("Execute calcular(G) before saving.")
        self.df.to_excel(filepath, index=False)


# ---------------- exemplo ----------------
# if __name__ == "__main__":
#     tabela7 = Table07DoubleWyeFig34(S=4, Pt=11, Pa=6, P=3, N=14, Su=3)
#     tabela7.calcular(G=1)
#     print(tabela7.exportar("markdown"))
#     tabela7.salvar_excel("Table07.xlsx")
#     print("Excel salvo: Table07.xlsx")
