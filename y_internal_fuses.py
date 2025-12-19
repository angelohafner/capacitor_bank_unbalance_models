# y_internal_fuses.py
# Comments in English only

from __future__ import annotations

from typing import Iterable, Union

import pandas as pd


Number = Union[int, float]


class Table07SingleWyeInternalFuses:
    """Table 7 variant for a single-wye capacitor bank with internal fuses.

    This class mirrors the double-wye Table 7 equations, with the additional
    constraint Pt == Pa (single branch only). As a result, the neutral unbalance
    current term In is always zero.
    """

    def __init__(self, S: int, Pt: int, Pa: int, P: int, N: int, Su: int):
        self.S = S
        self.Pt = Pt
        self.Pa = Pa
        self.P = P
        self.N = N
        self.Su = Su
        self.df = pd.DataFrame()
        self._validate()

    def _validate(self) -> None:
        if any(v <= 0 for v in (self.S, self.Pt, self.Pa, self.P, self.N, self.Su)):
            raise ValueError("All parameters must be positive.")
        if self.Pa != self.Pt:
            raise ValueError("For y_internal_fuses, Pt must be equal to Pa.")

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

    def _In(self) -> float:
        # Single-wye: Pt == Pa, so (Pt - Pa) == 0.
        return 0.0

    # ---------------- main ----------------
    def calcular(self, G: int, f_values: Iterable[int] | None = None):
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
            In = self._In()

            resultados.append(
                {
                    "G": G,
                    "f": f,
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
                    "In": round(In, 6),
                }
            )

        self.df = pd.DataFrame(resultados)
        return self.df
