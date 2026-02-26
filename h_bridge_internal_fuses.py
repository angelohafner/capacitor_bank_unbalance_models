import numpy as np
import pandas as pd

class Tabela08HBridgeCalculada:
    def __init__(self, S, St, Pt, Pa, P, N, Su):
        """Initialize parameters according to IEEE figure notes."""
        self.S  = S
        self.St = St
        self.Pt = Pt
        self.Pa = Pa
        self.P  = P
        self.N  = N
        self.Su = Su

        self.df = pd.DataFrame()
        self._check_parameters()

    # ----------------- Validation -----------------
    def _check_parameters(self):
        if self.S <= 0 or self.St <= 0 or self.Pt <= 0 or self.P <= 0 or self.N <= 0 or self.Su <= 0:
            raise ValueError("All parameters must be positive.")
        if self.S == self.St:
            raise ValueError("S == St leads to division by zero in Ih formula. Use St < S.")

    # ----------------- Formula implementation -----------------
    def _Cu(self, f):
        return self.Su * (self.N - f) / ((self.N - f) * (self.Su - 1) + self.N)

    def _Chn(self, Cu):
        return ((Cu + self.P - 1) * self.P) / ((Cu + self.P - 1) * (self.St - 1) + self.P) + (self.Pt - self.P) / self.St

    def _Cp(self, Chn):
        return (Chn * self.Pt) / (Chn * (self.S - self.St) + self.Pt)

    def _Vln(self, Cp, Cp0, G):
        return 1 + G * ((3 / (2 + Cp / Cp0)) - 1)

    def _Vh(self, Cp, Chn):
        return Cp / Chn

    def _Ih(self, Vln, Vh):
        return -Vln * ((self.St / self.S) - Vh) * ((1 / (self.S - self.St)) + (1 / self.St)) * ((self.S * (self.Pt - self.Pa)) / self.Pt)

    def _Vcu(self, Vln, Vh, Cu):
        return (Vln * Vh * self.P * self.S) / (self.P + (self.St - 1) * (Cu + self.P - 1))

    def _Ve(self, Vcu, f):
        return (Vcu * self.Su * self.N) / (self.Su * (self.N - f) + f)

    def _Iu(self, Vcu, Cu):
        return Vcu * Cu

    # ----------------- Main calculation -----------------
    def calcular(self, G):
        """Compute Table 8 (H-Bridge) values for chosen G = 0 or 1."""
        if G not in (0, 1):
            raise ValueError("G must be 0 or 1.")

        resultados = []

        # Reference Cp(0)
        Cu0 = self._Cu(0)
        Chn0 = self._Chn(Cu0)
        Cp0 = self._Cp(Chn0)

        f_values = np.arange(self.N).tolist()
        for f in f_values:
            Cu = self._Cu(f)
            Chn = self._Chn(Cu)
            Cp = self._Cp(Chn)
            Vln = self._Vln(Cp, Cp0, G)
            Vh = self._Vh(Cp, Chn)
            Ih = self._Ih(Vln, Vh)
            Vcu = self._Vcu(Vln, Vh, Cu)
            Ve = self._Ve(Vcu, f)
            Iu = self._Iu(Vcu, Cu)

            resultados.append({
                "G": G,
                "f": f,
                "Cu": round(Cu, 6),
                "Chn": round(Chn, 6),
                "Cp": round(Cp, 6),
                "Cp0": round(Cp0, 6),
                "Vln": round(Vln, 6),
                "Vh": round(Vh, 6),
                "Ih": round(Ih, 6),
                "Vcu": round(Vcu, 6),
                "Ve": round(Ve, 6),
                "Iu": round(Iu, 6)
            })

        self.df = pd.DataFrame(resultados)

    # ----------------- Export -----------------
    def exportar(self, formato="markdown"):
        if self.df.empty:
            raise ValueError("You must call calcular(G) before exporting.")

        if formato == "markdown":
            return self.df.to_markdown(index=False)
        elif formato == "csv":
            return self.df.to_csv(index=False)
        elif formato == "json":
            return self.df.to_json(orient="records", indent=2)
        elif formato == "latex":
            return self.df.to_latex(index=False, escape=False)
        else:
            return self.df

    def salvar_excel(self, filepath="Tabela08.xlsx"):
        """Save current table to an Excel .xlsx file."""
        if self.df.empty:
            raise ValueError("You must call calcular(G) before saving.")
        # Use openpyxl as the default Excel writer engine
        self.df.to_excel(filepath, index=False)


# ----------------- Example usage -----------------
# if __name__ == "__main__":
    # tabela = Tabela08HBridgeCalculada(S=7, St=3, Pt=9, Pa=5, P=2, N=16, Su=3)
    # tabela.calcular(G=0)  # or G=1
    #
    # # Print on screen
    # print(tabela.exportar("markdown"))
    #
    # # Save to Excel
    # tabela.salvar_excel("Tabela08.xlsx")
    # print("Excel salvo em: Tabela08.xlsx")

