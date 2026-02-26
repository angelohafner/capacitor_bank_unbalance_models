
# Capacitor Bank Unbalance Analysis – IEEE C37.99-2012

This project implements a **Streamlit-based engineering tool** for **analysis, validation, and visualization of shunt capacitor bank arrangements**, fully aligned with **IEEE C37.99-2012 – Guide for the Protection of Shunt Capacitor Banks**.

Unlike purely illustrative tools, this application **computes neutral current and neutral voltage**, using the selected bank topology and electrical parameters, and supports protection-oriented studies.

---

## 1. Purpose

The main objectives of this project are:

- Model different **capacitor bank topologies** used in medium- and high-voltage systems;
- **Compute neutral current and neutral voltage** according to IEEE C37.99 principles;
- Enforce **topology-dependent electrical and geometrical constraints**;
- Provide clear **Plotly-based electrical diagrams** suitable for engineering analysis;
- Serve as a foundation for protection settings, validation, and reporting.

The focus is on **steady-state unbalance behavior**, not on electromagnetic transients.

---

## 2. Normative Basis – IEEE C37.99-2012

IEEE C37.99-2012 establishes methodologies for:

- Detection of **capacitor unit failures**;
- Evaluation of **neutral current (Iₙ)** and **neutral voltage (Vₙ)**;
- Distinction between **single-star, double-star, and H-bridge arrangements**;
- Impact of **internal vs. external fuses** on sensitivity and measurement;
- Proper use of **grounding transformers** and neutral connections.

This project follows the standard by:

- Applying **different calculation and validation rules per topology**;
- Computing neutral quantities consistent with the selected arrangement;
- Explicitly modeling the neutral point and grounding path when applicable;
- Avoiding invalid parameter combinations that would violate IEEE assumptions.

---

## 3. Implemented Topologies

### 3.1 `yy_internal_fuses`
- Double-star arrangement
- Internal fuses
- Uses parameters:
  - `Pa`, `P`, `Pt`, `S`
- Enforces integer relationship `Pa / P`
- Computes:
  - Neutral current
  - Neutral voltage

---

### 3.2 `yy_external_fuses`
- Double-star arrangement
- External fuses
- **Does not use parameter `P`**
- No `Pa / P` validation is applied
- Neutral quantities are computed using IEEE external-fuse assumptions

---

### 3.3 `h_bridge_internal`
- H-bridge arrangement
- Internal fuses
- Uses parameters:
  - `Pt`, `Pa`, `P`, `S`, `St`
- Dedicated validation logic
- High sensitivity to single-unit failures
- Computes neutral current and voltage per bridge imbalance

---

### 3.4 `y_internal_fuses`
- Single-star arrangement
- Internal fuses
- Fixed parameters:
  - `Pa = 1`
  - `Pt = 1`
- User input is intentionally locked
- Includes:
  - Neutral bus
  - Grounding transformer (`TR`)
  - Explicit ground symbol
- Neutral current and voltage are calculated
- Diagram rendered at reduced scale (50%) for clarity

---

## 4. Electrical Quantities Calculated

The application calculates, depending on topology:

- Neutral current (Iₙ)
- Neutral voltage (Vₙ)
- Phase and branch unbalance indicators
- Per-unit and absolute quantities (as configured)

These values are suitable for:

- Protection sensitivity analysis
- Alarm and trip threshold definition
- Comparative studies between topologies

---

## 5. Project Architecture

### Main Files

```
main.py
main_part_1.py
utils_streamlit.py
validators.py
bank_diagram.py
```

### Responsibilities

- **`bank_diagram.py`**
  - Core electrical modeling
  - Neutral current and voltage computation
  - Plotly-based diagram generation
  - Raises errors for invalid arrangements

- **`validators.py`**
  - Topology-specific validation rules
  - Returns `ValidationResult` objects

- **`utils_streamlit.py`**
  - Dispatches validation by topology
  - Connects inputs to diagram and calculations

- **`main_part_1.py`**
  - Streamlit UI
  - Parameter inputs
  - Context management

---

## 6. Validation Strategy

Validation is **explicitly topology-based**, following IEEE C37.99 logic:

- No generic validation across topologies
- Each arrangement defines:
  - Required parameters
  - Forbidden parameters
  - Structural constraints

This avoids:
- False errors
- Hidden assumptions
- Misinterpretation of IEEE rules

---

## 7. Visualization

- All diagrams are generated **programmatically via Plotly**
- No static images are used
- Electrical symbols:
  - True capacitor symbols (parallel plates)
  - Series connections without illegal conductors
  - Explicit neutral and grounding paths

---

## 8. Scope and Limitations

Included:
- Steady-state unbalance analysis
- Neutral current and voltage calculation
- Structural validation

Not included (by design):
- Electromagnetic transient simulation
- Switching overvoltages
- Insulation coordination
- Relay time grading

---

## 9. Intended Use

This tool is suitable for:

- Engineering studies of shunt capacitor banks
- Protection philosophy definition
- Academic and professional analysis
- Pre-design validation before ATP/EMTP studies

---

## 10. Standards and References

- IEEE C37.99-2012  
  *Guide for the Protection of Shunt Capacitor Banks*

---
