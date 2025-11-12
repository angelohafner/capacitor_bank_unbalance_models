import pandas as pd
from typing import Iterable, Union

Number = Union[int, float]

class Table02SingleWye:
    """
    Table 2 — Unbalance calculations for the single wye-connected capacitor bank (Figure 28)

    Required parameters (constructor):
      S  : total series groups
      Pt : parallel units per phase

    Options:
      Cu_fixed : per-unit capacitor-unit current factor used in Iu = Vcu * Cu (default = 1.0)

    Usage:
      tabela = Table02SingleWye(S=5, Pt=15, Cu_fixed=1.0)
      tabela.calcular(G=0)            # G=0 grounded, G=1 ungrounded
      print(tabela.exportar("markdown"))
      tabela.salvar_excel("Table02.xlsx")
    """

    def __init__(self, S: int, Pt: int, Cu_fixed: float = 1.0):
        self.S = S
        self.Pt = Pt
        self.Cu_fixed = float(Cu_fixed)  # explicit: Cu = constant (default 1.0)
        self.df = pd.DataFrame()
        self._validate()

    # -------------------- validation --------------------
    def _validate(self):
        if self.S <= 0 or self.Pt <= 0:
            raise ValueError("S and Pt must be positive.")
        # S>=2 is typical, but not enforced here.

    @staticmethod
    def _safe_div(num: Number, den: Number, name: str) -> float:
        if abs(den) < 1e-12:
            raise ZeroDivisionError(f"Zero denominator in {name}.")
        return float(num) / float(den)

    # -------------------- Table 2 formulas --------------------
    def _Cg(self, n: int) -> float:
        # Cg = (Pt - n) / Pt
        return self._safe_div(self.Pt - n, self.Pt, "Cg")

    def _Cp(self, Cg: float) -> float:
        # Cp = (S * Cg) / ( Cg * (S - 1) + 1 )
        num = self.S * Cg
        den = Cg * (self.S - 1) + 1.0
        return self._safe_div(num, den, "Cp")

    def _Vng(self, Cp: float, G: int) -> float:
        # Vng = G * ( 3 / (2 + Cp) - 1 )
        inner = self._safe_div(3.0, 2.0 + Cp, "Vng inner")
        return G * (inner - 1.0)

    def _Vln(self, Vng: float) -> float:
        # Vln = 1 + Vng
        return 1.0 + Vng

    def _Vcu(self, Vln: float, Cp: float, Cg: float) -> float:
        # Vcu = (Vln * Cp) / Cg
        # Observação prática: quando Cg -> 0 (n = Pt), a tabela muitas vezes adota o caso-limite Vcu = Vln * S.
        if abs(Cg) < 1e-12:
            return Vln * self.S
        return self._safe_div(Vln * Cp, Cg, "Vcu")

    def _Iu(self, Vcu: float) -> float:
        # Iu = Vcu * Cu (Cu is fixed here)
        return Vcu * self.Cu_fixed

    def _Iph(self, Cp: float, Vln: float) -> float:
        # Iph = Cp * Vln
        return Cp * Vln

    def _Ig(self, Iph: float, G: int) -> float:
        # Ig = (1 - G) * (1 - Iph)
        return (1 - G) * (1.0 - Iph)

    # -------------------- main API --------------------
    def calcular(self, G: int, n_values: Iterable[int] = None):
        """
        Compute rows for grounding type G (0 grounded, 1 ungrounded).
        n_values defaults to range(0, Pt+1) → n = 0..Pt blown fuses.
        """
        if G not in (0, 1):
            raise ValueError("G must be 0 (grounded) or 1 (ungrounded).")
        if n_values is None:
            n_values = range(0, self.Pt - 2)

        rows = []
        for n in n_values:
            n = int(n)
            if n < 0 or n > self.Pt:
                raise ValueError("n must be between 0 and Pt (inclusive).")

            Cg  = self._Cg(n)
            Cp  = self._Cp(Cg)
            Vng = self._Vng(Cp, G)
            Vln = self._Vln(Vng)
            Vcu = self._Vcu(Vln, Cp, Cg)
            Iu  = self._Iu(Vcu)
            Iph = self._Iph(Cp, Vln)
            Ig  = self._Ig(Iph, G)

            rows.append({
                "G": G,
                "n": n,
                "Cu(fixed)": round(self.Cu_fixed, 6),
                "Cg": round(Cg, 6),
                "Cp": round(Cp, 6),
                "Vng": round(Vng, 6),
                "Vln": round(Vln, 6),
                "Vcu": round(Vcu, 6),
                "Iu": round(Iu, 6),
                "Iph": round(Iph, 6),
                "Ig": round(Ig, 6),
            })

        self.df = pd.DataFrame(rows)
        return self.df

    # -------------------- export helpers --------------------
    def exportar(self, formato: str = "markdown"):
        if self.df.empty:
            raise ValueError("Execute calcular(G) before exporting.")
        if formato == "markdown":
            try:
                return self.df.to_markdown(index=False)  # requer 'tabulate'
            except Exception:
                return self.df.to_string(index=False)
        if formato == "csv":
            return self.df.to_csv(index=False)
        if formato == "json":
            return self.df.to_json(orient="records", indent=2)
        if formato == "latex":
            return self.df.to_latex(index=False, escape=False)
        return self.df

    def salvar_excel(self, filepath: str = "Table02.xlsx"):
        if self.df.empty:
            raise ValueError("Execute calcular(G) before saving.")
        self.df.to_excel(filepath, index=False)


# -------------------- exemplo de uso --------------------
# if __name__ == "__main__":
#     # Exemplo: S=5, Pt=15, Cu = 1.0 (fixo)
#     tabela2 = Table02SingleWye(S=4, Pt=8, Cu_fixed=1.0)
#
#     # G = 0 (grounded) ou G = 1 (ungrounded)
#     tabela2.calcular(G=0)
#
#     print(tabela2.exportar("markdown"))
#     tabela2.salvar_excel("Table02.xlsx")
#     print("Excel salvo: Table02.xlsx")
