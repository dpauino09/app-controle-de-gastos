import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import (
    init_db,
    adicionar_gasto,
    listar_gastos_por_usuario,
    listar_gastos_por_mes,
    calcular_total_geral,
    excluir_gasto
)
from pdf_generator import gerar_pdf

init_db()
st.set_page_config(page_title="Controle de Gastos", layout="centered")
st.title("💰 Controle de Gastos")

# 🔐 Login simples
if "usuario" not in st.session_state:
    st.session_state["usuario"] = st.text_input("👤 Digite seu nome para continuar")
    st.stop()

usuario = st.session_state["usuario"]
st.sidebar.success(f"👋 Bem-vindo, {usuario}!")

# 📝 Formulário para adicionar gasto
with st.form("form_gasto"):
    nome = st.text_input("Nome do gasto")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    mes = st.selectbox("Mês", [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ])
    enviar = st.form_submit_button("Adicionar")

    if enviar:
        if not nome.strip():
            st.warning("⚠️ O nome do gasto não pode estar vazio.")
        elif valor <= 0:
            st.warning("⚠️ O valor deve ser maior que zero.")
        else:
            adicionar_gasto(nome, valor, mes, usuario)
            st.success("✅ Gasto adicionado com sucesso!")
            st.rerun()

# 📋 Carrega os dados
dados = listar_gastos_por_usuario(usuario)
df = pd.DataFrame(dados, columns=["ID", "Nome", "Valor", "Mês"])

# 🔎 Filtro por mês
st.subheader("🔎 Filtrar gastos por mês")
mes_filtro = st.selectbox("Escolha o mês", ["Todos"] + sorted(df["Mês"].unique()))

if mes_filtro == "Todos":
    df_exibir = df
else:
    dados_filtrados = listar_gastos_por_mes(mes_filtro, usuario)
    df_exibir = pd.DataFrame(dados_filtrados, columns=["ID", "Nome", "Valor", "Mês"])

df_exibir = df_exibir.sort_values(by="Valor", ascending=False)

# 📊 Destaques do mês
if mes_filtro != "Todos" and not df_exibir.empty:
    maior_gasto = df_exibir.loc[df_exibir["Valor"].idxmax()]
    gasto_frequente = df_exibir["Nome"].value_counts().idxmax()
    st.info(f"💸 Maior gasto: {maior_gasto['Nome']} (R$ {maior_gasto['Valor']:.2f})")
    st.info(f"🔁 Gasto mais frequente: {gasto_frequente}")

# 📋 Exibe os gastos filtrados
st.subheader("📋 Gastos Registrados")
st.dataframe(df_exibir, use_container_width=True)

# 📤 Exportar para CSV
st.download_button(
    label="📤 Exportar para CSV",
    data=df_exibir.to_csv(index=False).encode("utf-8"),
    file_name="gastos.csv",
    mime="text/csv"
)

# 💵 Totais lado a lado
col1, col2 = st.columns(2)
with col1:
    total_geral = calcular_total_geral(usuario)
    st.metric("💰 Total Geral", f"R$ {total_geral:.2f}")
with col2:
    if mes_filtro != "Todos" and not df_exibir.empty:
        total_mes = df_exibir["Valor"].sum()
        st.metric(f"📆 Total de {mes_filtro}", f"R$ {total_mes:.2f}")

# 📈 Gráfico de gastos por mês
st.subheader("📈 Gráfico de Gastos por Mês")
conn = sqlite3.connect("gastos.db")
cursor = conn.cursor()
cursor.execute("SELECT mes, SUM(valor) FROM gastos WHERE usuario = ? GROUP BY mes", (usuario,))
dados_grafico = cursor.fetchall()
conn.close()

meses = [linha[0] for linha in dados_grafico]
valores = [linha[1] for linha in dados_grafico]

fig, ax = plt.subplots()
ax.bar(meses, valores, color="#4CAF50")
ax.set_title("Gastos por Mês")
ax.set_xlabel("Mês")
ax.set_ylabel("Total (R$)")
plt.xticks(rotation=45)
st.pyplot(fig)

# 🗑️ Exclusão de gasto
with st.expander("🗑️ Excluir Gasto"):
    if not df.empty:
        id_para_excluir = st.selectbox("Selecione o ID para excluir", df["ID"])
        if st.button("Excluir gasto"):
            excluir_gasto(id_para_excluir)
            st.success(f"Gasto com ID {id_para_excluir} excluído com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum gasto disponível para excluir.")

# 🔄 Botão de atualização manual
if st.button("🔄 Atualizar Dados"):
    st.rerun()

# 🧾 Geração de PDF
with st.expander("🧾 Gerar PDF por mês"):
    mes_pdf = st.selectbox("Selecione o mês para gerar PDF", df["Mês"].unique() if not df.empty else [])
    if st.button("Gerar PDF"):
        if mes_pdf:
            caminho_pdf = gerar_pdf(mes_pdf, usuario)
            with open(caminho_pdf, "rb") as f:
                st.download_button(
                    label=f"📥 Baixar PDF de {mes_pdf}",
                    data=f,
                    file_name=caminho_pdf,
                    mime="application/pdf"
                )
            st.success(f"📄 PDF do mês {mes_pdf} gerado com sucesso!")
        else:
            st.warning

# 🛠️ Atualização do banco de dados (coluna 'usuario' e registros antigos)
with st.expander("🛠️ Atualizar Banco de Dados"):
    if st.button("Executar atualização"):
        try:
            conn = sqlite3.connect("gastos.db")
            cursor = conn.cursor()

            # Verifica se a coluna 'usuario' já existe
            cursor.execute("PRAGMA table_info(gastos)")
            colunas = [coluna[1] for coluna in cursor.fetchall()]

            if "usuario" not in colunas:
                cursor.execute("ALTER TABLE gastos ADD COLUMN usuario TEXT")
                conn.commit()
                st.success("✅ Coluna 'usuario' adicionada com sucesso.")
            else:
                st.info("ℹ️ A coluna 'usuario' já existe.")

            # Atualiza registros antigos com o nome do usuário atual
            cursor.execute("UPDATE gastos SET usuario = ? WHERE usuario IS NULL OR usuario = ''", (usuario,))
            conn.commit()
            conn.close()
            st.success(f"✅ Registros antigos atualizados para o usuário '{usuario}'.")
        except Exception as e:
            st.error(f"❌ Erro ao atualizar banco: {e}")

# 🛠️ Atualização do banco de dados (somente para administrador)
with st.expander("🛠️ Atualizar Banco de Dados"):
    if usuario.lower() == "daniel":
        if st.button("Executar atualização"):
            try:
                conn = sqlite3.connect("gastos.db")
                cursor = conn.cursor()

                # Verifica se a coluna 'usuario' já existe
                cursor.execute("PRAGMA table_info(gastos)")
                colunas = [coluna[1] for coluna in cursor.fetchall()]

                if "usuario" not in colunas:
                    cursor.execute("ALTER TABLE gastos ADD COLUMN usuario TEXT")
                    conn.commit()
                    st.success("✅ Coluna 'usuario' adicionada com sucesso.")
                else:
                    st.info("ℹ️ A coluna 'usuario' já existe.")

                # Atualiza registros antigos com o nome do usuário atual
                cursor.execute("UPDATE gastos SET usuario = ? WHERE usuario IS NULL OR usuario = ''", (usuario,))
                conn.commit()
                conn.close()
                st.success(f"✅ Registros antigos atualizados para o usuário '{usuario}'.")
            except Exception as e:
                st.error(f"❌ Erro ao atualizar banco: {e}")
    else:
        st.warning("⚠️ Esta função está disponível apenas para o administrador.")