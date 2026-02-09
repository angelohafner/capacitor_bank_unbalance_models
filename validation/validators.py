from __future__ import annotations

from typing import Dict, Any
from typing import List
from diagrams.h_bridge_drawing import ValidationResult, validate_h_bridge_inputs


class NominalDataError(ValueError):
    pass


def validate_nominal_data(topology: str, data: Dict[str, Any]) -> None:
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
    right_branch_required = ("yy_internal_fuses", "yy_external_fuses")
    if topology in right_branch_required:
        if (Pt - Pa) < 1:
            raise NominalDataError(f"Combinação inválida: o lado direito teria Pt-Pa={Pt - Pa} (< 1).")

    if topology == "y_internal_fuses":
        if Pa != Pt:
            raise NominalDataError("Para y_internal_fuses, Pt deve ser igual a Pa.")

    # Internal-fuse topologies require P and the divisibility constraint Pa % P == 0.
    if topology in ("yy_internal_fuses", "y_internal_fuses"):
        if "P" not in data:
            raise NominalDataError("Dados nominais incompletos: chave ausente 'P'.")
        P = int(data["P"])
        if P < 1:
            raise NominalDataError("P deve ser >= 1.")
        if (Pa % P) != 0:
            raise NominalDataError(f"Combinação inválida: Pa deve ser múltiplo de P. (Pa={Pa}, P={P})")



def validate_inputs(topology: str, data: Dict[str, Any]) -> ValidationResult:
    """Unified input validation dispatch by topology.

    Returns ValidationResult instead of raising, so UI code can decide how to display.
    """

    # H-bridge has its own dedicated validator
    if topology in ("h_bridge_internal_fuses", "h_bridge_external_fuses"):
        S = int(data.get("S", 7))
        St = int(data.get("St", 3))
        Pt = int(data.get("Pt", 9))
        Pa = int(data.get("Pa", 5))
        P = int(data.get("P", 2))
        return validate_h_bridge_inputs(S=S, St=St, Pt=Pt, Pa=Pa, P=P)

    # For the other topologies, reuse the nominal-data validator
    try:
        validate_nominal_data(topology=topology, data=data)
    except NominalDataError as exc:
        return ValidationResult(is_valid=False, errors=[str(exc)], warnings=[])

    return ValidationResult(is_valid=True, errors=[], warnings=[])