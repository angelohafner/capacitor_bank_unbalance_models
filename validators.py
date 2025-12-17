# Comments in English only
from __future__ import annotations

from typing import Dict, Any


class NominalDataError(ValueError):
    pass


def validate_nominal_data(topology: str, data: Dict[str, Any]) -> None:
    """Validate the nominal dictionary according to the selected topology.

    This function is UI-agnostic (no Streamlit dependencies).
    Raise NominalDataError with human-readable messages.
    """
    required_common = ["S", "Pt", "Pa"]
    for key in required_common:
        if key not in data:
            raise NominalDataError(f"Dados nominais incompletos: chave ausente '{key}'.")

    S = int(data["S"])
    Pt = int(data["Pt"])
    Pa = int(data["Pa"])

    if S < 1:
        raise NominalDataError("S deve ser >= 1.")
    if Pt < 1:
        raise NominalDataError("Pt deve ser >= 1.")
    if Pa < 0:
        raise NominalDataError("Pa deve ser >= 0.")
    if Pa > Pt:
        raise NominalDataError("Pa deve ser <= Pt.")
    if (Pt - Pa) < 1:
        raise NominalDataError(f"Combinação inválida: o lado direito teria Pt-Pa={Pt - Pa} (< 1).")

    # Internal-fuse topologies require P and the divisibility constraint Pa % P == 0.
    if topology in ("yy_internal_fuses"):
        if "P" not in data:
            raise NominalDataError("Dados nominais incompletos: chave ausente 'P'.")
        P = int(data["P"])
        if P < 1:
            raise NominalDataError("P deve ser >= 1.")
        if (Pa % P) != 0:
            raise NominalDataError(f"Combinação inválida: Pa deve ser múltiplo de P. (Pa={Pa}, P={P})")
