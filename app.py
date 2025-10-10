import sqlite3
import streamlit as st
import pandas as pd
from database import (
    init_db,
    adicionar_gasto,
    listar_gastos_por_usuario,
    listar_gastos_por_mes,
    calcular_total_geral,
    excluir_gasto,
    adicionar_gasto_recorrente
)
from pdf_generator import gerar_pdf

init_db()
st.set_page_config(page_title="Controle de Gastos", layout="centered")
st.title("💰 Controle de Gastos")

# 🔐 Login simples
if "usuario" not in st.session_state:
    with st.form("form_login"):
        nome_usuario = st.text_input("👤 Digite seu nome para continuar")
        entrar = st.form_submit_button("Entrar")
        if entrar and nome_usuario.strip():
            st.session_state["usuario"] = nome_usuario.strip()
            st.rerun()
    st.stop()

usuario = st.session_state["usuario"]
st.sidebar.success(f"👋 Bem-vindo, {usuario}!")

# 🔄 Carrega os dados
dados = listar_gastos_por_usuario(usuario)
df = pd.DataFrame(dados, columns=["ID", "Nome", "Valor", "Mês"])

# 🗂️ Interface com abas
aba1, aba2, aba3 = st.tabs(["📥 Adicionar", "📊 Visualizar", "🛠️ Configurações"])

# 📥 Aba de Adição
with aba1:
    st.markdown("### ➕ Adicionar novo gasto")
    with st.form("form_gasto_simples"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do gasto")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        mes = st.selectbox("Mês", [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ])
        enviar = st.form_submit_button("➕ Adicionar gasto")
        if enviar:
            if not nome.strip():
                st.warning("⚠️ O campo 'Nome do gasto' é obrigatório.")
            elif valor <= 0:
                st.warning("⚠️ O valor deve ser maior que zero.")
            else:
                adicionar_gasto(nome, valor, mes, usuario)
                st.success("✅ Gasto adicionado com sucesso!")
                st.rerun()

    st.markdown("### 📆 Adicionar gasto recorrente")
    with st.form("form_gasto_recorrente"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Descrição do gasto fixo")
            meses = st.number_input("Número de meses", min_value=1, max_value=120, step=1)
        with col2:
            valor = st.number_input("Valor mensal (R$)", min_value=0.0, step=10.0)
            mes_inicial = st.selectbox("Mês de início", [
                'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
            ])
        enviar = st.form_submit_button("📆 Adicionar gasto recorrente")
        if enviar:
            adicionar_gasto_recorrente(nome, valor, meses, mes_inicial, usuario)
            st.success("✅ Gasto recorrente registrado com sucesso!")

# 📊 Aba de Visualização
with aba2:
    st.subheader("🔎 Filtrar gastos por mês")
    mes_filtro = st.selectbox("Escolha o mês", ["Todos"] + sorted(df["Mês"].unique()))
    if mes_filtro == "Todos":
        df_exibir = df
    else:
        dados_filtrados = listar_gastos_por_mes(mes_filtro, usuario)
        df_exibir = pd.DataFrame(dados_filtrados, columns=["ID", "Nome", "Valor", "Mês"])

    df_exibir = df_exibir.sort_values(by="Valor", ascending=False)

    if mes_filtro != "Todos" and not df_exibir.empty:
        maior_gasto = df_exibir.loc[df_exibir["Valor"].idxmax()]
        gasto_frequente = df_exibir["Nome"].value_counts().idxmax()
        st.info(f"💸 Maior gasto: {maior_gasto['Nome']} (R$ {maior_gasto['Valor']:.2f})")
        st.info(f"🔁 Gasto mais frequente: {gasto_frequente}")

    st.subheader("📋 Gastos Registrados")
    st.dataframe(df_exibir, use_container_width=True)

    st.download_button(
        label="📤 Exportar para CSV",
        data=df_exibir.to_csv(index=False).encode("utf-8"),
        file_name="gastos.csv",
        mime="text/csv"
    )

    col1, col2 = st.columns(2)
    with col1:
        total_geral = calcular_total_geral(usuario)
        st.metric("💰 Total Geral", f"R$ {total_geral:.2f}")
    with col2:
        if mes_filtro != "Todos" and not df_exibir.empty:
            total_mes = df_exibir["Valor"].sum()
            st.metric(f"📆 Total de {mes_filtro}", f"R$ {total_mes:.2f}")

    st.markdown("### 🗑️ Excluir Gasto")
    if not df.empty:
        with st.form("form_excluir"):
            id_para_excluir = st.selectbox("Selecione o ID para excluir", df["ID"])
            excluir = st.form_submit_button("🗑️ Excluir gasto")
            if excluir:
                excluir_gasto(id_para_excluir)
                st.success(f"Gasto com ID {id_para_excluir} excluído com sucesso!")
                st.rerun()
    else:
        st.info("ℹ️ Nenhum gasto disponível para excluir.")

# 🛠️ Aba de Configurações
with aba3:
    st.markdown("### 🧾 Gerar PDF por mês")
    with st.form("form_pdf"):
        mes_pdf = st.selectbox("Selecione o mês para gerar PDF", df["Mês"].unique() if not df.empty else [])
        gerar = st.form_submit_button("📥 Gerar PDF")
        if gerar:
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
                st.warning("⚠️ Selecione um mês válido.")

    st.markdown("### 🛠️ Atualizar Banco de Dados")
    with st.form("form_atualizacao_geral"):
        atualizar = st.form_submit_button("Executar atualização")
        if atualizar:
            try:
                conn = sqlite3.connect("gastos.db")
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(gastos)")
                colunas = [coluna[1] for coluna in cursor.fetchall()]
                if "usuario" not in colunas:
                    cursor.execute("ALTER TABLE gastos ADD COLUMN usuario TEXT")
                    conn.commit()
                    st.success("✅ Coluna 'usuario' adicionada com sucesso.")
                else:
                    st.info("ℹ️ A coluna 'usuario' já existe.")
                cursor.execute("UPDATE gastos SET usuario = ? WHERE usuario IS NULL OR usuario = ''", (usuario,))
                conn.commit()
                conn.close()
                st.success(f"✅ Registros antigos atualizados para o usuário '{usuario}'.")
            except Exception as e:
                st.error(f"❌ Erro ao atualizar banco: {e}")

    if usuario.lower() == "daniel":
        st.markdown("### 🛠️ Atualização do banco (admin)")
        with st.form("form_atualizacao_admin"):
            atualizar_admin = st.form_submit_button("Executar atualização (admin)")
            if atualizar_admin:
                try:
                    conn = sqlite3.connect("gastos.db")
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(gastos)")
                    colunas = [coluna[1] for coluna in cursor.fetchall()]
                    if "usuario" not in colunas:
                        cursor.execute("ALTER TABLE gastos ADD COLUMN usuario TEXT")
                        conn.commit()
                        st.success("✅ Coluna 'usuario' adicionada com sucesso.")
                    else:
                        st.info("ℹ️ A coluna 'usuario' já existe.")
                    cursor.execute("UPDATE gastos SET usuario = ? WHERE usuario IS NULL OR usuario = ''", (usuario,))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Registros antigos atualizados para o usuário '{usuario}'.")
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar banco: {e}")
    else:
        st.warning("⚠️ Esta função está disponível apenas para o administrador.")