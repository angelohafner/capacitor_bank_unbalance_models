# Capacitor Bank Unbalance Models

Aplicativo Streamlit e classes em Python para modelagem, análise e proteção de bancos de capacitores sob condições de desbalanceamento, conforme a norma **IEEE C37.99**.

Streamlit app and Python classes for modeling, analysis, and protection of capacitor banks under unbalance conditions according to **IEEE C37.99**.

---

## 🧩 Funcionalidades / Features

- Cálculo automático de tensões e correntes em topologias:
  - `yy_internal_fuses`
  - `yy_external_fuses`
  - `h_bridge_internal_fuses`
  - `h_bridge_external_fuses`
- Geração de tabelas IEEE e reais (`Table 6–8`)
- Exportação para **Excel (.xlsx)** e **LaTeX (.tex)**
- Interface web interativa via **Streamlit**
- Execução modular com classes Python reutilizáveis

---

## ⚙️ Instalação / Installation

```bash
# Clone o repositório / Clone the repository
git clone https://github.com/angelohafner/capacitor_bank_unbalance_models.git
cd capacitor_bank_unbalance_models

# Crie um ambiente virtual / Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # (Linux/macOS)
# ou / or
.venv\Scripts\activate     # (Windows)

# Instale as dependências / Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Execução / Run

```bash
streamlit run main.py
```

O aplicativo será aberto no navegador em:  
**http://localhost:8501**

---

## 📄 Estrutura do Projeto / Project Structure

```
capacitor_bank_unbalance_models/
├── main.py                    # Interface principal Streamlit
├── master_bank_classes.py     # Classes e métodos principais de cálculo
├── input_widgets.py           # Componentes de entrada Streamlit
├── utils_streamlit.py         # Funções auxiliares (exportação, figuras, etc.)
├── requirements.txt           # Dependências do projeto
└── export/                    # Arquivos gerados (.xlsx, .tex)
```

---

## 📘 Referência / Reference

- IEEE C37.99 — *Guide for the Protection of Shunt Capacitor Banks*  
- Implementação inspirada nas Tabelas 6–8 da norma IEEE C37.99-2012

---

## 👨‍💻 Autor / Author

**Angelo Alfredo Hafner**  
Engenheiro Eletricista – DAX-Energy  
https://dax.energy/
[GitHub](https://github.com/angelohafner)

---

## 🧾 Licença / License

Este projeto é distribuído sob a licença MIT.  
This project is distributed under the MIT License.
