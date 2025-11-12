import pandas as pd

class Table06HBridgeMinimal:
    """
    Table 6 — Unbalance calculations for the H-bridge capacitor bank (Figure 32)

    Parameters (required):
      S  : total series groups
      St : series groups (H leg to neutral)
      Pt : parallel units per phase
      Pa : parallel units on the "left" side of H

    Notes:
      - Cu is fixed as 1.0 everywhere (Cu = 1.0)
      - Therefore, Iu = 1 * Vcu = Vcu
    """

    def __init__(self, S: int, St: int, Pt: int, Pa: int):
        self.S  = S
        self.St = St
        self.Pt = Pt
        self.Pa = Pa
        self.df = pd.DataFrame()
        self._validate()

    # -------------------- validation --------------------
    def _validate(self):
        if any(v <= 0 for v in (self.S, self.St, self.Pt, self.Pa)):
            raise ValueError("S, St, Pt, Pa must be positive.")
        if self.S <= self.St:
            raise ValueError("Require S > St (Ih denominator (S-St) must not be zero).")

    @staticmethod
    def _safe_div(num, den, name):
        if den == 0:
            raise ZeroDivisionError(f"Zero denominator in {name}.")
        return num / den

    # -------------------- Table 6 formulas --------------------
    def _Chn(self, n: int) -> float:
        # Chn = ((Pa - n) * Pa) / ( (Pa - n)*(St - 1) + Pa ) + (Pt - Pa)/St
        num = (self.Pa - n) * self.Pa
        den = (self.Pa - n) * (self.St - 1) + self.Pa
        term1 = self._safe_div(num, den, "Chn term1")
        term2 = self._safe_div(self.Pt - self.Pa, self.St, "Chn term2")
        return term1 + term2

    def _Cp(self, Chn: float) -> float:
        # Cp = (Chn * Pt) / ( Chn*(S - St) + Pt )
        num = Chn * self.Pt
        den = Chn * (self.S - self.St) + self.Pt
        return self._safe_div(num, den, "Cp")

    def _Vln(self, Cp: float, Cp0: float, G: int) -> float:
        # Vln = 1 + G * ( 3 / (2 + Cp/Cp0) - 1 )
        ratio = self._safe_div(Cp, Cp0, "Cp/Cp0")
        inner = self._safe_div(3.0, 2.0 + ratio, "Vln inner")
        return 1.0 + G * (inner - 1.0)

    def _Vhn(self, Cp: float, Chn: float) -> float:
        # Vhn = Cp / Chn
        return self._safe_div(Cp, Chn, "Vhn")

    def _Ih(self, Vln: float, Vhn: float) -> float:
        # Ih = -Vln * (St/S - Vhn) * ( 1/(S - St) + 1/St ) * ( S*(Pt - Pa)/Pt )
        termA = (self.St / self.S) - Vhn
        termB = self._safe_div(1.0, self.S - self.St, "Ih termB1") + self._safe_div(1.0, self.St, "Ih termB2")
        termC = self._safe_div(self.S * (self.Pt - self.Pa), self.Pt, "Ih termC")
        return - Vln * termA * termB * termC

    def _Vcu(self, Vln: float, Vhn: float, n: int) -> float:
        # Vcu = (Vln * Vhn * Pa * S) / ( Pa + (St - 1) * (Pa - n) )
        num = Vln * Vhn * self.Pa * self.S
        den = self.Pa + (self.St - 1) * (self.Pa - n)
        return self._safe_div(num, den, "Vcu")

    def _Iu(self, Vcu: float) -> float:
        # Cu = 1.0 → Iu = 1 * Vcu
        return 1.0 * Vcu

    # -------------------- cálculo principal --------------------
    def calcular(self, G: int, n_values=None):
        """
        Calculate all values for the given grounding type G (0 = grounded, 1 = ungrounded)
        and store them in self.df
        """
        if G not in (0, 1):
            raise ValueError("G must be 0 or 1 (0 = grounded, 1 = ungrounded).")

        rows = []

        # Reference Cp(0)
        Chn0 = self._Chn(0)
        Cp0  = self._Cp(Chn0)

        for n in n_values:
            if n == "SU":
                Vln0 = self._Vln(Cp0, Cp0, G)
                Vhn0 = self._Vhn(Cp0, Chn0)
                Ih0  = self._Ih(Vln0, Vhn0)
                rows.append({
                    "n": "SU",
                    "Cu(=1)": 1.0,
                    "Chn": round(Chn0, 6),
                    "Cp": round(Cp0, 6),
                    "Cp0": round(Cp0, 6),
                    "Vln": round(Vln0, 6),
                    "Vhn": round(Vhn0, 6),
                    "Ih": round(Ih0, 6),
                    "Vcu": "SC",
                    "Iu(=1*Vcu)": "SC"
                })
                continue

            n = int(n)
            if n < 0 or n > self.Pa:
                raise ValueError("n must be between 0 and Pa (inclusive).")

            Chn = self._Chn(n)
            Cp  = self._Cp(Chn)
            Vln = self._Vln(Cp, Cp0, G)
            Vhn = self._Vhn(Cp, Chn)
            Ih  = self._Ih(Vln, Vhn)
            Vcu = self._Vcu(Vln, Vhn, n)
            Iu  = self._Iu(Vcu)

            rows.append({
                "n": n,
                "Cu(=1)": 1.0,
                "Chn": round(Chn, 6),
                "Cp": round(Cp, 6),
                "Cp0": round(Cp0, 6),
                "Vln": round(Vln, 6),
                "Vhn": round(Vhn, 6),
                "Ih": round(Ih, 6),
                "Vcu": round(Vcu, 6),
                "Iu(=1*Vcu)": round(Iu, 6)
            })

        self.df = pd.DataFrame(rows)
        return self.df

    # -------------------- export helpers --------------------
    def exportar(self, formato="markdown"):
        if self.df.empty:
            raise ValueError("Execute calcular() before exporting.")
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

    def salvar_excel(self, filepath="Table06.xlsx"):
        if self.df.empty:
            raise ValueError("Execute calcular() before saving.")
        self.df.to_excel(filepath, index=False)


# -------------------- programa principal --------------------
# if __name__ == "__main__":
#     tabela = Table06HBridgeMinimal(S=5, St=3, Pt=15, Pa=8)
#     tabela.calcular(G=0)  # grounded bank
#
#     # Print result
#     print(tabela.exportar("markdown"))
#
#     # Save to Excel
#     tabela.salvar_excel("Table06.xlsx")
#     print("Excel salvo: Table06.xlsx")
