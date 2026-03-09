# 💰 Controle de Gastos Profissional

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://controledegasto.streamlit.app/)

O **Controle de Gastos** é uma aplicação web interativa e gratuita para registrar, analisar e gerenciar suas finanças pessoais. Desenvolvido em **Python** e impulsionado pelo **Streamlit**, ele fornece uma interface deslumbrante e dinâmica, ideal tanto para uso em desktop quanto pelo celular.

🌟 **Totalmente Gratuito e Disponível na Nuvem!**  
Você não precisa instalar nada para começar a usar. Basta acessar o link abaixo, criar sua conta (segura e individual) e começar a controlar seus gastos hoje mesmo:
👉 [**Acessar o App Controle de Gastos**](https://controledegasto.streamlit.app/)

## 🚀 Funcionalidades Principais

- 🔐 **Sistema Seguro de Autenticação**: Contas individuais protegidas por e-mail e hash de senhas. Acesso exclusivo e particionado (cada usuário vê apenas seus dados).
- 👑 **Painel de Administrador**: Controle completo de acessos, com funções para reset remoto de senhas e gerenciamento de permissões integrados ao sistema.
- 📱 **Visão Geral (Dashboard) Dinâmico**: Acesse rapidamente seus Saldos Mensais, métricas de despesas e um **Gráfico de Pizza Interativo**. Clique nas fatias para listar imediatamente os gastos que as compõem!
- 🏷️ **Categorização de Despesas**: Organize seus gastos com categorias (Alimentação, Transporte, Moradia, etc.) de forma simples ou crie faturas parceladas.
- 📆 **Gastos Recorrentes e Contas a Vencer**: Planeje boletos ou gastos que duram vários meses, e acompanhe o prazo de vencimento na tela, com badges dinâmicos de proximidade.
- ⚡ **Ações Rápidas & Edição**: Marque contas pendenciais como Pagas ("🔵 Pago"), ou edite atributos e categorias de qualquer despesa sem trocar de tela (usando Modal fluído).
- 📤 **Importação Inteligente (CSV)**: Suba o extrato do seu banco digital (Nubank, Itaú, C6...) em formato `.csv` e adicione despesas em lote ao sistema em 1 clique.
- 🧾 **Exportação de Relatórios (PDF)**: Gere resumos completos da sua movimentação financeira em PDF a qualquer momento.

## 🛠️ Tecnologias Utilizadas

- **Interface Tabela**: Streamlit
- **Processamento de Dados**: Pandas
- **Gráficos**: Plotly Express
- **Banco de Dados**: PostgreSQL na Nuvem (nuvem Supabase, substituto do SQLite)
- **Criptografia**: Hash `hashlib` (SHA-256)
- **Gerador de Documentos**: ReportLab

## 📦 Como Rodar Localmente

Adicione suas credenciais do Banco PostgreSQL dentro do arquivo `.env` localizado na raiz do projeto:
```env
DATABASE_URL=postgres://usuario:senha@host:5432/dbname
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

Inicie o servidor local do aplicativo:
```bash
streamlit run app.py
```

## 👨‍💻 Autor
**Daniel Paulino**  
Campinas, SP - Brasil  
*dpaulino37@gmail.com*