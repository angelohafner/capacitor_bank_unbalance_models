dados_nominais_banco_yy_internal_fuses = {
    # Dados elétricos do banco
    "tensao_trifasica_banco_V": 69000,         # [V] tensão linha-linha nominal
    "potencia_trifasica_banco_VAr": 15e6,      # [VAr] potência total do banco trifásico
    "frequencia_Hz": 60,                       # [Hz] frequência nominal

    # Estrutura elétrica
    "S": 4,    # grupos em série por fase
    "Pt": 11,  # unidades em paralelo por fase
    "Pa": 6,   # unidades auxiliares (conforme topologia)
    "P": 3,    # unidades principais (conforme topologia)
    "N": 14,   # elementos em série por célula
    "Su": 3,   # células em série por unidade

    "G": 1,

    # Tipo de proteção/topologia
    "topologia_protecao": "yy_internal_fuses"  # texto descritivo opcional
}

dados_nominais_banco_yy_external_fuses = {
    # Dados elétricos do banco
    "tensao_trifasica_banco_V": 69000,         # [V] tensão linha-linha nominal
    "potencia_trifasica_banco_VAr": 15e6,      # [VAr] potência total do banco trifásico
    "frequencia_Hz": 60,                       # [Hz] frequência nominal

    # Estrutura elétrica (dupla estrela com fusíveis externos)
    "S": 4,    # grupos em série por fase
    "Pt": 14,  # unidades em paralelo por fase
    "Pa": 8,

    "G": 1,    # 0 = aterrado, 1 = isolado (default: isolado)

    # Tipo de proteção/topologia
    "topologia_protecao": "yy_external_fuses"  # texto descritivo opcional
}



dados_nominais_banco_h_bridge_internal_fuses = {
    # Dados elétricos do banco
    "tensao_trifasica_banco_V": 69000,         # [V] tensão linha-linha nominal
    "potencia_trifasica_banco_VAr": 15e6,      # [VAr] potência total do banco trifásico
    "frequencia_Hz": 60,                       # [Hz] frequência nominal

    # Estrutura elétrica conforme figura
    "S": 7,    # grupos em série - total
    "St": 3,   # grupos em série, perna H até o neutro
    "Pt": 9,   # unidades em paralelo por fase
    "Pa": 5,   # unidades em paralelo no "lado esquerdo" do H
    "P": 2,    # unidades em paralelo na coluna afetada
    "N": 16,   # elementos paralelos em cada grupo
    "Su": 3,   # grupos em série em cada unidade capacitiva

    "G": 0,

    # Tipo de proteção/topologia
    "topologia_protecao": "h_bridge_internal_fuses"  # descrição opcional
}

dados_nominais_banco_h_bridge_external_fuses = {
    # Dados elétricos do banco
    "tensao_trifasica_banco_V": 69000,         # [V] tensão linha-linha nominal
    "potencia_trifasica_banco_VAr": 15e6,      # [VAr] potência total do banco trifásico
    "frequencia_Hz": 60,                       # [Hz] frequência nominal

    # Estrutura elétrica (para fusíveis externos)
    "S": 5,    # grupos em série - total (ligeiramente menor pois fusíveis externos protegem o conjunto)
    "St": 3,   # grupos em série por perna (H até o neutro)
    "Pt": 15,  # unidades em paralelo por fase (maior para compensar fusíveis externos)
    "Pa": 8,   # unidades paralelas no lado esquerdo do H

    # Tipo de proteção/topologia
    "topologia_protecao": "h_bridge_external_fuses"  # descrição opcional
}
