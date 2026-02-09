import streamlit as st

def get_dados_nominais_banco(topologia: str):
    # Comments in English only
    st.subheader("Banco de Capacitores")

    # Common electrical data (left: colA, middle: colB, right: colC)
    colA, colB, colC = st.columns(3)

    with colA:
        tensao_trifasica_banco_V = 1e3 * st.number_input(
            label="kV de trabalho:",
            min_value=1.0, max_value=1000.0, value=35.5
        )
        V_rated = 1e3 * st.number_input(
            label="kV de nominal:",
            min_value=1.0, max_value=1000.0, value=40.0
        )
    with colB:
        potencia_trifasica_banco_VAr = 1e6 * st.number_input(
            label="MVAr de trabalho:",
            min_value=0.1, max_value=100.0, value=15.0
        )
        Q_rated = 1e-6 * potencia_trifasica_banco_VAr * (V_rated / tensao_trifasica_banco_V) ** 2
        st.number_input(
            label="MVAr nominal (calculado):",
            value=float(Q_rated),
            disabled=True
        )

    with colC:
        frequencia_Hz = st.number_input(
            label="Frequência nominal (Hz):",
            min_value=40, max_value=70, value=60
        )
        G_sel = st.selectbox("Aterramento:", ["Aterrado (0)", "Isolado (1)"], index=1)
        G = 1 if "1" in G_sel else 0

    # Topology-specific inputs in 3 columns for compact UI
    st.subheader("Arranjo")
    c1, c2, c3 = st.columns(3)

    
    if topologia == "y_internal_fuses":
        with c1:
            S  = st.number_input("Grupos em série por fase (S):", 1, 20, 4)
            Pt = st.number_input(
                label="Unidades em paralelo por fase (Pt):",
                value=1,
                disabled=True,
            )
        with c2:
            Pa = 1
            st.number_input(
                label="Unidades paralelas fase afetada (Pa) (Pt=Pa):",
                value=1,
                disabled=True,
            )
            P  = st.number_input(
                label="Unidades paralelas ramo afetado (P):",
                value=1,
                disabled=True,
            )
        with c3:
            N  = st.number_input("Elementos em paralelo por célula (N):", 1, 50, 14)
            Su = st.number_input("Elementos em série por célula (Su):", 1, 10, 3)

        return {
            "tensao_trifasica_banco_V": tensao_trifasica_banco_V,
            "potencia_trifasica_banco_VAr": potencia_trifasica_banco_VAr,
            "V_rated": V_rated,
            "Q_rated": Q_rated,
            "frequencia_Hz": frequencia_Hz,
            "S": S, "Pt": Pt, "Pa": Pa, "P": P, "N": N, "Su": Su,
            "G": G,
            "topologia_protecao": "y_internal_fuses",
        }

    elif topologia == "yy_internal_fuses":
        with c1:
            S  = st.number_input("Grupos em série por fase (S):", 1, 20, 4)
            Pt = st.number_input("Unidades em paralelo por fase (Pt):", 1, 50, 11)
        with c2:
            Pa = st.number_input("Unidades paralelas fase afetada (Pa):", 1, 50, 6)
            P  = st.number_input("Unidades paralelas ramo afetado (P):", 1, 50, 3)
        with c3:
            N  = st.number_input("Elementos em paralelo por célula (N):", 1, 50, 14)
            Su = st.number_input("Elementos em série por célula (Su):", 1, 10, 3)


        return {
            "tensao_trifasica_banco_V": tensao_trifasica_banco_V,
            "potencia_trifasica_banco_VAr": potencia_trifasica_banco_VAr,
            "V_rated": V_rated,
            "Q_rated": Q_rated,
            "frequencia_Hz": frequencia_Hz,
            "S": S, "Pt": Pt, "Pa": Pa, "P": P, "N": N, "Su": Su,
            "G": G,
            "topologia_protecao": "yy_internal_fuses",
        }

    elif topologia == "yy_external_fuses":
        with c1:
            S  = st.number_input("Grupos em série por fase (S):", 1, 20, 4)
            Pt = st.number_input("Unidades em paralelo por fase (Pt):", 1, 50, 14)
        with c2:
            Pa = st.number_input("Unidades paralelas fase afetada (Pa):", 1, 50, 8)
        # with c3:
        #     G_sel = st.selectbox("Aterramento:", ["Aterrado (0)", "Isolado (1)"], index=1)
        #     G = 1 if "1" in G_sel else 0

        return {
            "tensao_trifasica_banco_V": tensao_trifasica_banco_V,
            "potencia_trifasica_banco_VAr": potencia_trifasica_banco_VAr,
            "V_rated": V_rated,
            "Q_rated": Q_rated,
            "frequencia_Hz": frequencia_Hz,
            "S": S, "Pt": Pt, "Pa": Pa,
            "G": G,
            "topologia_protecao": "yy_external_fuses",
        }

    elif topologia == "h_bridge_internal_fuses":
        with c1:
            S  = st.number_input("Grupos em série total (S):", 1, 20, 7)
            St = st.number_input("Grupos série por perna (St):", 1, 10, 3)
        with c2:
            Pt = st.number_input("Unidades paralelas por fase (Pt):", 1, 50, 9)
            Pa = st.number_input("Unidades no lado esquerdo (Pa):", 1, 50, 5)
            P  = st.number_input("Unidades na coluna afetada (P):", 1, 50, 2)
        with c3:
            N = st.number_input("Elementos paralelos por grupo (N):", 1, 50, 16)
            Su = st.number_input("Grupos série por unidade (Su):", 1, 10, 3)
        #     G_sel = st.selectbox("Aterramento:", ["Aterrado (0)", "Isolado (1)"], index=0)
        #     G = 1 if "1" in G_sel else 0

        return {
            "tensao_trifasica_banco_V": tensao_trifasica_banco_V,
            "potencia_trifasica_banco_VAr": potencia_trifasica_banco_VAr,
            "V_rated": V_rated,
            "Q_rated": Q_rated,
            "frequencia_Hz": frequencia_Hz,
            "S": S, "St": St, "Pt": Pt, "Pa": Pa, "P": P, "N": N, "Su": Su,
            "G": G,
            "topologia_protecao": "h_bridge_internal_fuses",
        }

    elif topologia == "h_bridge_external_fuses":
        with c1:
            S  = st.number_input("Grupos em série total (S):", 1, 20, 5)
            St = st.number_input("Grupos série por perna (St):", 1, 10, 3)
        with c2:
            Pt = st.number_input("Unidades paralelas por fase (Pt):", 1, 50, 15)
            Pa = st.number_input("Unidades no lado esquerdo (Pa):", 1, 50, 8)
        # with c3:
        #     G_sel = st.selectbox("Aterramento:", ["Aterrado (0)", "Isolado (1)"], index=1)
        #     G = 1 if "1" in G_sel else 0

        return {
            "tensao_trifasica_banco_V": tensao_trifasica_banco_V,
            "potencia_trifasica_banco_VAr": potencia_trifasica_banco_VAr,
            "V_rated": V_rated,
            "Q_rated": Q_rated,
            "frequencia_Hz": frequencia_Hz,
            "S": S, "St": St, "Pt": Pt, "Pa": Pa,
            "G": G,
            "topologia_protecao": "h_bridge_external_fuses",
        }

    else:
        st.warning("Selecione uma topologia válida.")
        return None
