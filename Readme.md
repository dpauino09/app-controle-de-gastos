# 💰 Controle de Gastos

Aplicativo web interativo para registrar, visualizar e exportar seus gastos mensais. Desenvolvido com Python e Streamlit, com suporte a múltiplos usuários via login simples.

## 🚀 Funcionalidades

- 🔐 Login por nome (cada usuário vê apenas seus próprios dados)
- ➕ Adicionar gastos com nome, valor e mês
- 🔎 Filtrar gastos por mês
- 📊 Visualizar totais gerais e mensais
- 📈 Gráfico de barras com gastos por mês
- 📤 Exportar dados para CSV
- 🧾 Gerar relatório em PDF por mês
- 🗑️ Excluir gastos por ID
- 🛠️ Atualizar banco de dados via interface (admin)
- 📱 Interface responsiva para celular

## 📦 Requisitos

- Python 3.9+
- Bibliotecas:
  - streamlit
  - pandas
  - matplotlib
  - reportlab
  - sqlite3 (embutido no Python)

Instale com:

```bash
pip install -r requirements.txt

rodar o app 
streamlit run app.py

app-controle-de-gastos/
├── app.py
├── database.py
├── pdf_generator.py
├── requirements.txt
└── README.md


Autor

Daniel paulino 
Campinas SP Brasil 
dpaulino37@gmail.com 