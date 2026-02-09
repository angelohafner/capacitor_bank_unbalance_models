# validacao.py
# Comments in English only

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class Validacao:
    """Input validation centralized in a single class.

    One method per topology, named exactly as the topology key.
    Each method returns ValidationResult (no exceptions).
    """

    def validar(self, topology: str, data: Dict[str, Any]) -> ValidationResult:
        fn = getattr(self, topology, None)
        if fn is None or not callable(fn):
            return ValidationResult(
                is_valid=False,
                errors=[f"Unsupported topology '{topology}'."],
                warnings=[],
            )
        return fn(data)

    # ---------------- Common helpers ----------------

    def _as_int(self, data: Dict[str, Any], key: str, errors: List[str], default: Optional[int] = None) -> Optional[int]:
        if key not in data:
            if default is None:
                errors.append(f"Missing required key '{key}'.")
                return None
            return default
        try:
            return int(data[key])
        except Exception:
            errors.append(f"{key} must be an integer.")
            return None

    def _validate_common_nominal(self, topology: str, data: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        S = self._as_int(data, "S", errors)
        Pt = self._as_int(data, "Pt", errors)
        Pa = self._as_int(data, "Pa", errors)

        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        if S is not None and S < 1:
            errors.append("S must be >= 1.")
        if Pt is not None and Pt < 1:
            errors.append("Pt must be >= 1.")
        if Pa is not None and Pa < 0:
            errors.append("Pa must be >= 0.")
        if (Pa is not None) and (Pt is not None) and (Pa > Pt):
            errors.append("Pa must be <= Pt.")

        # For double-wye topologies we need a right branch
        if topology in ("yy_internal_fuses", "yy_external_fuses"):
            if (Pt is not None) and (Pa is not None) and ((Pt - Pa) < 1):
                errors.append(f"Invalid combination: right side would be Pt-Pa={Pt - Pa} (< 1).")

        # For single-wye internal fuses: all units are on the same branch
        if topology == "y_internal_fuses":
            if (Pt is not None) and (Pa is not None) and (Pa != Pt):
                errors.append("For y_internal_fuses, Pt must be equal to Pa.")

        return ValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def _validate_internal_fuse_constraint(self, data: Dict[str, Any], errors: List[str]) -> None:
        P = self._as_int(data, "P", errors)
        Pa = self._as_int(data, "Pa", errors)
        if P is None or Pa is None:
            return
        if P < 1:
            errors.append("P must be >= 1.")
            return
        if (Pa % P) != 0:
            errors.append(f"Invalid combination: Pa must be a multiple of P. (Pa={Pa}, P={P})")

    # ---------------- Topology methods ----------------

    def y_internal_fuses(self, data: Dict[str, Any]) -> ValidationResult:
        base = self._validate_common_nominal("y_internal_fuses", data)
        if not base.is_valid:
            return base
        errors = list(base.errors)
        warnings = list(base.warnings)

        # Internal fuse constraint
        self._validate_internal_fuse_constraint(data, errors)

        return ValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def y_external_fuses(self, data: Dict[str, Any]) -> ValidationResult:
        base = self._validate_common_nominal("y_external_fuses", data)
        return base

    def yy_internal_fuses(self, data: Dict[str, Any]) -> ValidationResult:
        base = self._validate_common_nominal("yy_internal_fuses", data)
        if not base.is_valid:
            return base
        errors = list(base.errors)
        warnings = list(base.warnings)

        # Internal fuse constraint
        self._validate_internal_fuse_constraint(data, errors)

        return ValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def yy_external_fuses(self, data: Dict[str, Any]) -> ValidationResult:
        base = self._validate_common_nominal("yy_external_fuses", data)
        return base

    def h_bridge_internal_fuses(self, data: Dict[str, Any]) -> ValidationResult:
        return self._validate_h_bridge(data)

    def h_bridge_external_fuses(self, data: Dict[str, Any]) -> ValidationResult:
        return self._validate_h_bridge(data)

    # ---------------- H-bridge specific ----------------

    def _validate_h_bridge(self, data: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        S = self._as_int(data, "S", errors)
        St = self._as_int(data, "St", errors)
        Pt = self._as_int(data, "Pt", errors)
        Pa = self._as_int(data, "Pa", errors)
        P = self._as_int(data, "P", errors)

        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Basic ranges
        if S is not None and S < 2:
            errors.append("S must be >= 2.")
        if St is not None and S is not None:
            if (St < 1) or (St > (S - 1)):
                errors.append("St must satisfy 1 <= St <= S-1.")
        if Pt is not None and Pt < 1:
            errors.append("Pt must be >= 1.")
        if Pa is not None and Pt is not None:
            if (Pa < 1) or (Pa >= Pt):
                errors.append("Pa must satisfy 1 <= Pa <= Pt-1.")
        if P is not None and P < 1:
            errors.append("P must be >= 1.")
        if (Pa is not None) and (P is not None) and (Pa < P):
            errors.append("Pa must be >= P.")
        if (Pt is not None) and (P is not None) and (Pt < (2 * P)):
            errors.append("Pt must be >= 2*P.")

        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Warnings aligned with the prior behavior (no hard error)
        if (Pt is not None) and (P is not None):
            if ((Pt // P) % 2) != 0:
                warnings.append("Pt//P is odd (right-side split into two equal big groups becomes asymmetric).")

        if (Pa is not None) and (P is not None):
            if (Pa - P) < 1:
                warnings.append("Pa == P: left leg becomes a single ladder block (no split).")

        return ValidationResult(is_valid=True, errors=errors, warnings=warnings)
