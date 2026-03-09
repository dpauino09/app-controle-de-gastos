import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    init_db,
    adicionar_gasto,
    listar_gastos_por_usuario,
    listar_gastos_por_mes,
    calcular_total_geral,
    excluir_gasto,
    adicionar_gasto_recorrente,
    usuario_existe,
    cadastrar_usuario,
    verificar_senha,
    eh_admin,
    DB_PATH,
    adicionar_contas_parceladas,
    listar_contas_a_vencer,
    marcar_conta_status,
    excluir_conta_a_vencer,
    listar_usuarios,
    alterar_admin,
    resetar_senha_usuario,
    excluir_usuario,
    stats_globais,
    listar_todos_gastos,
    listar_todas_contas,
    adicionar_receita,
    listar_receitas_por_usuario,
    listar_receitas_por_mes,
    calcular_total_receitas,
    excluir_receita,
)
from pdf_generator import gerar_pdf

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

CATEGORIAS_GASTOS = [
    "Alimentação", "Moradia", "Transporte", "Saúde", 
    "Lazer", "Educação", "Vestuário", "Outros"
]

init_db()
st.set_page_config(
    page_title="Controle de Gastos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Fonte global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Header principal ── */
.app-header {
    background: linear-gradient(135deg, #00C896 0%, #007B5E 100%);
    border-radius: 16px;
    padding: 20px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.app-header h1 {
    color: #fff !important;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}
.app-header span { font-size: 2.2rem; }

/* ── Login card ── */
.login-card {
    background: #1A1D2E;
    border: 1px solid #2C3050;
    border-radius: 20px;
    padding: 40px 48px;
    max-width: 460px;
    margin: 60px auto 0 auto;
    box-shadow: 0 8px 40px rgba(0,200,150,0.10);
}
.login-card h2 {
    color: #00C896;
    font-weight: 700;
    margin-bottom: 24px;
    text-align: center;
}

/* ── Cards de seção ── */
.section-card {
    background: #1A1D2E;
    border: 1px solid #2C3050;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}

/* ── Divider de título de seção ── */
.section-title {
    color: #00C896;
    font-size: 1.1rem;
    font-weight: 600;
    border-left: 4px solid #00C896;
    padding-left: 10px;
    margin-bottom: 16px;
}

/* ── Métricas coloridas ── */
.metric-card {
    background: linear-gradient(135deg, #1A2E26 0%, #0F1E18 100%);
    border: 1px solid #00C89640;
    border-radius: 14px;
    padding: 18px 22px;
    text-align: center;
}
.metric-card .label {
    font-size: 0.8rem;
    color: #00C896;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.metric-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #F0F2F6;
    margin-top: 4px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #12152A !important;
    border-right: 1px solid #2C3050;
}
[data-testid="stSidebar"] .stButton button {
    width: 100%;
    background: #1E2437;
    border: 1px solid #2C3050;
    color: #F0F2F6;
    border-radius: 10px;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #FF4B4B22;
    border-color: #FF4B4B;
    color: #FF4B4B;
}

/* ── Abas ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 2px solid #2C3050;
    padding-bottom: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 10px 24px;
    font-weight: 600;
    color: #7A7F9A;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #1A1D2E !important;
    color: #00C896 !important;
    border-bottom: 2px solid #00C896;
}

/* ── Botão primário (submit) ── */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #00C896, #007B5E) !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s;
}
[data-testid="stFormSubmitButton"] button:hover { opacity: 0.85; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 10px !important;
    border-color: #2C3050 !important;
    background: #0F1117 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header principal ──
st.markdown("""
<div class="app-header">
  <span>💰</span>
  <h1>Controle de Gastos</h1>
</div>
""", unsafe_allow_html=True)

# 🔐 Login com senha
if "usuario" not in st.session_state:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<h2>🔐 Acesso ao sistema</h2>', unsafe_allow_html=True)
    with st.form("form_login"):
        email_usuario = st.text_input("📧 E-mail")
        senha = st.text_input("🔑 Senha", type="password")
        col_a, col_b = st.columns(2)
        with col_a:
            entrar = st.form_submit_button("➡️ Entrar", use_container_width=True)
        with col_b:
            cadastrar = st.form_submit_button("➕ Criar conta", use_container_width=True)

        if entrar:
            if not email_usuario.strip():
                st.warning("⚠️ Informe o e-mail.")
            elif "@" not in email_usuario:
                st.warning("⚠️ Informe um e-mail válido.")
            elif not usuario_existe(email_usuario.strip().lower()):
                st.error("❌ E-mail não encontrado. Clique em 'Criar conta'.")
            elif verificar_senha(email_usuario.strip().lower(), senha):
                st.session_state["usuario"] = email_usuario.strip().lower()
                st.rerun()
            else:
                st.error("❌ Senha incorreta.")

        if cadastrar:
            if not email_usuario.strip():
                st.warning("⚠️ Informe o e-mail.")
            elif "@" not in email_usuario:
                st.warning("⚠️ Informe um e-mail válido.")
            elif not senha.strip():
                st.warning("⚠️ A senha não pode estar vazia.")
            elif usuario_existe(email_usuario.strip().lower()):
                st.warning("⚠️ E-mail já cadastrado. Use 'Entrar'.")
            else:
                cadastrar_usuario(email_usuario.strip().lower(), senha)
                st.session_state["usuario"] = email_usuario.strip().lower()
                st.success("✅ Conta criada! Bem-vindo!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

usuario = st.session_state["usuario"]

# ── Sidebar ──
_display_name = usuario.split("@")[0].capitalize()
st.sidebar.markdown(f"""
<div style="text-align:center; padding: 12px 0 20px 0;">
  <div style="font-size:2.4rem;">ð¤</div>
  <div style="font-weight:700; font-size:1.05rem; color:#F0F2F6; margin-top:6px;">{_display_name}</div>
  <div style="font-size:0.72rem; color:#7A7F9A; margin-top:2px;">{usuario}</div>
  <div style="font-size:0.75rem; color:#00C896; font-weight:600; letter-spacing:0.04em; margin-top:4px;">{'⭐ Administrador' if eh_admin(usuario) else 'Usuário'}</div>
</div>
""", unsafe_allow_html=True)

# Resumo financeiro na sidebar (mês atual)
_mes_atual_sb_nome = MESES[datetime.now().month - 1]
_mes_atual_sb = f"{_mes_atual_sb_nome} {datetime.now().year}"
_gastos_sb_lista = listar_gastos_por_mes(_mes_atual_sb, usuario)
_total_gastos_sb = sum(g[2] for g in _gastos_sb_lista)

_receitas_sb_lista = listar_receitas_por_mes(_mes_atual_sb, usuario)
_total_receitas_sb = sum(r[2] for r in _receitas_sb_lista)

_saldo_sb = _total_receitas_sb - _total_gastos_sb
_saldo_cor = "#00C896" if _saldo_sb >= 0 else "#FF4B4B"
_saldo_bg  = "#1A2E26" if _saldo_sb >= 0 else "#2E1A1A"
_saldo_border = "#00C89640" if _saldo_sb >= 0 else "#FF4B4B40"
st.sidebar.markdown(f"""
<div style="display:flex;gap:8px;margin-bottom:10px;">
  <div style="flex:1;background:#1A2E26;border:1px solid #00C89640;border-radius:10px;padding:10px;text-align:center;">
    <div style="font-size:0.65rem;color:#00C896;font-weight:600;text-transform:uppercase;">💵 Receitas ({_mes_atual_sb_nome})</div>
    <div style="font-size:1rem;font-weight:700;color:#F0F2F6;">R$ {_total_receitas_sb:,.2f}</div>
  </div>
  <div style="flex:1;background:#2E1A1A;border:1px solid #FF4B4B40;border-radius:10px;padding:10px;text-align:center;">
    <div style="font-size:0.65rem;color:#FF6B6B;font-weight:600;text-transform:uppercase;">💸 Gastos ({_mes_atual_sb_nome})</div>
    <div style="font-size:1rem;font-weight:700;color:#F0F2F6;">R$ {_total_gastos_sb:,.2f}</div>
  </div>
</div>
<div style="background:{_saldo_bg};border:1px solid {_saldo_border};border-radius:10px;
            padding:12px 16px;text-align:center;margin-bottom:12px;">
  <div style="font-size:0.7rem;color:{_saldo_cor};font-weight:600;text-transform:uppercase;">💰 Saldo ({_mes_atual_sb_nome})</div>
  <div style="font-size:1.5rem;font-weight:700;color:{_saldo_cor};">R$ {_saldo_sb:,.2f}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# Resumo de contas pendentes na sidebar
_contas_sb = listar_contas_a_vencer(usuario)
_pendentes  = [c for c in _contas_sb if c[7] == "pendente"]
if _pendentes:
    _total_pend = sum(c[2] for c in _pendentes)
    st.sidebar.markdown(f"""
<div style="margin-top:12px; background:#2E1A1A; border:1px solid #FF4B4B40;
            border-radius:12px; padding:12px 16px; text-align:center;">
  <div style="font-size:0.75rem; color:#FF6B6B; font-weight:600;
              text-transform:uppercase; letter-spacing:0.05em;">⏳ Contas Pendentes</div>
  <div style="font-size:1.4rem; font-weight:700; color:#F0F2F6; margin-top:2px;">R$ {_total_pend:,.2f}</div>
  <div style="font-size:0.72rem; color:#7A7F9A;">{len(_pendentes)} parcela(s)</div>
</div>
""", unsafe_allow_html=True)

if eh_admin(usuario):
    st.sidebar.markdown("""
<div style="margin-top:16px; padding:10px 12px; background:#1A2E26;
            border:1px solid #00C89640; border-radius:10px;
            font-size:0.72rem; color:#7A7F9A;">
  <span style="color:#00C896;">☁️ Banco:</span> Supabase (nuvem)
</div>
""", unsafe_allow_html=True)

# 🔄 Carrega os dados
dados = listar_gastos_por_usuario(usuario)
df = pd.DataFrame(dados, columns=["ID", "Nome", "Valor", "Mês", "Categoria"])

# 🗂️ Interface com abas
if eh_admin(usuario):
    aba_dash, aba1, aba2, aba_rec, aba_plan, aba3, aba4, aba5 = st.tabs([
        "📱 Visão Geral", "📥 Adicionar", "📊 Visualizar", "💵 Receitas",
        "📈 Planejamento", "📅 Contas a Vencer", "🛠️ Configurações", "👑 Admin"
    ])
else:
    aba_dash, aba1, aba2, aba_rec, aba_plan, aba3, aba4 = st.tabs([
        "📱 Visão Geral", "📥 Adicionar", "📊 Visualizar", "💵 Receitas",
        "📈 Planejamento", "📅 Contas a Vencer", "🛠️ Configurações"
    ])
    aba5 = None

# 📱 Aba de Visão Geral (Dashboard)
with aba_dash:
    st.markdown('<p class="section-title">✨ Resumo do Mês Atual</p>', unsafe_allow_html=True)
    
    # Busca dados do mês atual para preencher o Dashboard
    mes_atual_str = f"{MESES[datetime.now().month - 1]} {datetime.now().year}"
    
    # Cards de métricas principais do Mês
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""
    <div class="metric-card">
      <div class="label">💳 Total de Receitas</div>
      <div class="value" style="color:#00C896;">R$ {_total_receitas_sb:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""
    <div class="metric-card">
      <div class="label">💸 Total de Gastos</div>
      <div class="value" style="color:#FF4B4B;">R$ {_total_gastos_sb:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""
    <div class="metric-card" style="border-color:{_saldo_border};">
      <div class="label">💰 Saldo Líquido</div>
      <div class="value" style="color:{_saldo_cor};">R$ {_saldo_sb:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart, col_bills = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<p class="section-title" style="font-size:0.95rem;">🍕 Gastos por Categoria</p>', unsafe_allow_html=True)
        # Preparando DataFrame de categorias
        df_mes_atual = df[df["Mês"] == mes_atual_str] if not df.empty else pd.DataFrame()
        
        if not df_mes_atual.empty:
            df_pizza = df_mes_atual.groupby("Categoria")["Valor"].sum().reset_index()
            import plotly.express as px
            fig_pie = px.pie(
                df_pizza, 
                values="Valor", 
                names="Categoria", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F0F2F6',
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True
            )
            # Ocultando textos pequenos na pizza para ficar clean
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum gasto registrado neste mês para gerar o gráfico.")

    with col_bills:
        st.markdown('<p class="section-title" style="font-size:0.95rem;">⏰ Próximas Contas</p>', unsafe_allow_html=True)
        # Filtrar contas do mês atual pendentes, ordenar por dia
        todas_contas_dash = listar_contas_a_vencer(usuario)
        contas_proximas = [c for c in todas_contas_dash if c[6] == mes_atual_str and c[7] == "pendente"]
        contas_proximas = sorted(contas_proximas, key=lambda x: x[5])[:3] # Pegar as 3 primeiras
        
        if not contas_proximas:
            st.success("✅ Tudo limpo! Nenhuma conta pendente para os próximos dias.")
        else:
            for c in contas_proximas:
                hoje_d = datetime.now()
                dia_v = c[5]
                try:
                    data_v = datetime(hoje_d.year, hoje_d.month, min(dia_v, 28))
                    dias_rest = (data_v - hoje_d).days
                    if dias_rest < 0: txt_dias = f"Vencida há {abs(dias_rest)}d"
                    elif dias_rest == 0: txt_dias = "Vence hoje!"
                    else: txt_dias = f"Vence em {dias_rest}d"
                except:
                    txt_dias = f"Dia {dia_v}"
                    
                st.markdown(f"""
                <div style="background:#1A1D2E; border:1px solid #2C3050; border-radius:12px; padding:12px; margin-bottom:10px;">
                    <div style="font-weight:600; color:#F0F2F6; font-size:0.9rem;">{c[1]}</div>
                    <div style="display:flex; justify-content:space-between; margin-top:4px; align-items:center;">
                        <span style="color:#FF4B4B; font-weight:700; font-size:1.1rem;">R$ {c[2]:.2f}</span>
                        <span style="font-size:0.7rem; color:#FFD700; background:#FFD70022; padding:2px 8px; border-radius:10px;">{txt_dias}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("""
        <div style="text-align:center; margin-top:20px;">
            <span style="color:#7A7F9A; font-size:0.8rem;">Vá para a aba de 'Contas a Vencer' para gerenciar.</span>
        </div>
        """, unsafe_allow_html=True)

# 📥 Aba de Adição
with aba1:
    st.markdown('<p class="section-title">➕ Adicionar novo gasto</p>', unsafe_allow_html=True)
    with st.form("form_gasto_simples"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do gasto")
            categoria = st.selectbox("Categoria", CATEGORIAS_GASTOS)
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            mes = st.selectbox("Mês", MESES, index=datetime.now().month - 1)
        enviar = st.form_submit_button("➕ Adicionar gasto")
        if enviar:
            if not nome.strip():
                st.warning("⚠️ O campo 'Nome do gasto' é obrigatório.")
            elif valor <= 0:
                st.warning("⚠️ O valor deve ser maior que zero.")
            else:
                mes_formatado = f"{mes} {datetime.now().year}"
                adicionar_gasto(nome, valor, mes_formatado, usuario, categoria)
                st.success("✅ Gasto adicionado com sucesso!")
                st.rerun()

    st.markdown('<p class="section-title" style="margin-top:28px;">📆 Adicionar gasto recorrente</p>', unsafe_allow_html=True)
    with st.form("form_gasto_recorrente"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Descrição do gasto fixo")
            categoria_rec = st.selectbox("Categoria (Recorrente)", CATEGORIAS_GASTOS)
            meses = st.number_input("Número de meses", min_value=1, max_value=120, step=1)
        with col2:
            valor = st.number_input("Valor mensal (R$)", min_value=0.0, step=10.0)
            mes_inicial = st.selectbox("Mês de início", MESES, index=datetime.now().month - 1)
        enviar = st.form_submit_button("📆 Adicionar gasto recorrente")
        if enviar:
            if not nome.strip():
                st.warning("⚠️ O campo 'Descrição do gasto fixo' é obrigatório.")
            elif valor <= 0:
                st.warning("⚠️ O valor mensal deve ser maior que zero.")
            else:
                adicionar_gasto_recorrente(nome, valor, meses, mes_inicial, usuario, categoria_rec)
                st.success(f"✅ Gasto recorrente '{nome}' registrado para {int(meses)} meses a partir de {mes_inicial}!")

# ✏️ Definição do Modal de Edição de Gasto
@st.dialog("Editar Gasto")
def modal_editar_gasto(gasto_id, nome_atual, valor_atual, mes_atual, categoria_atual):
    st.markdown(f"Editando: **{nome_atual}**")
    novo_nome = st.text_input("Nome", value=nome_atual)
    novo_valor = st.number_input("Valor (R$)", min_value=0.0, value=float(valor_atual), format="%.2f")
    nova_categoria = st.selectbox("Categoria", CATEGORIAS_GASTOS, index=CATEGORIAS_GASTOS.index(categoria_atual) if categoria_atual in CATEGORIAS_GASTOS else CATEGORIAS_GASTOS.index("Outros"))
    novo_mes = st.selectbox("Mês", [m for m in df["Mês"].unique()] + [mes_atual] if mes_atual not in df["Mês"].unique() else df["Mês"].unique(), index=list(df["Mês"].unique()).index(mes_atual) if mes_atual in df["Mês"].unique() else 0)
    
    if st.button("💾 Salvar Alterações", type="primary"):
        from database import atualizar_gasto
        atualizar_gasto(gasto_id, novo_nome, novo_valor, novo_mes, nova_categoria)
        st.success("Gasto atualizado!")
        st.rerun()

# 📊 Aba de Visualização
with aba2:
    st.markdown('<p class="section-title">🔎 Filtrar gastos por mês</p>', unsafe_allow_html=True)
    mes_filtro = st.selectbox("Escolha o mês", ["Todos"] + sorted(df["Mês"].unique()))
    if mes_filtro == "Todos":
        df_gastos = df.copy()
    else:
        dados_filtrados = listar_gastos_por_mes(mes_filtro, usuario)
        df_gastos = pd.DataFrame(dados_filtrados, columns=["ID", "Nome", "Valor", "Mês"])
        
    df_gastos["Tipo"] = "gasto"
    df_gastos["Status"] = "pago"
    
    # Adicionar contas a vencer na lista unificada
    contas_usuario = listar_contas_a_vencer(usuario)
    if mes_filtro != "Todos":
        contas_usuario = [c for c in contas_usuario if c[6] == mes_filtro]
        
    df_contas = pd.DataFrame(contas_usuario, columns=["ID", "Nome", "Valor", "Parcela Num", "Parcela Total", "Dia", "Mês", "Status"])
    if not df_contas.empty:
        df_contas["Tipo"] = "conta"
        df_contas_concat = df_contas[["ID", "Nome", "Valor", "Mês", "Tipo", "Status"]]
        df_exibir = pd.concat([df_gastos, df_contas_concat], ignore_index=True)
    else:
        df_exibir = df_gastos

    df_exibir = df_exibir.sort_values(by="Valor", ascending=False)

    if mes_filtro != "Todos" and not df_exibir.empty:
        maior_gasto = df_exibir.loc[df_exibir["Valor"].idxmax()]
        gasto_frequente = df_exibir["Nome"].value_counts().idxmax()
        st.info(f"💸 Maior gasto: {maior_gasto['Nome']} (R$ {maior_gasto['Valor']:.2f})")
        st.info(f"🔁 Gasto mais frequente: {gasto_frequente}")

    st.markdown('<p class="section-title" style="margin-top:8px;">📋 Gastos Registrados</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        total_geral = calcular_total_geral(usuario)
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">💰 Total Geral</div>
          <div class="value">R$ {total_geral:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if mes_filtro != "Todos" and not df_exibir.empty:
            total_mes = df_exibir["Valor"].sum()
            st.markdown(f"""
            <div class="metric-card">
              <div class="label">📆 Total de {mes_filtro}</div>
              <div class="value">R$ {total_mes:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if df_exibir.empty:
        st.info("ℹ️ Nenhum gasto encontrado.")
    else:
        # cabeçalho da lista
        hc1, hc2, hc3, hc4 = st.columns([4, 2, 2, 1])
        hc1.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>DESCRIÇÃO</span>", unsafe_allow_html=True)
        hc2.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>MÊS</span>", unsafe_allow_html=True)
        hc3.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>VALOR</span>", unsafe_allow_html=True)
        hc4.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'></span>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#2C3050;margin:4px 0 6px 0;'>", unsafe_allow_html=True)

        for _, row in df_exibir.iterrows():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])
            tipo = row.get("Tipo", "gasto")
            status = row.get("Status", "pago")
            
            if tipo == "conta":
                if status == "pendente":
                    cor_valor = "#FFD700"  # Amarelo (Conta parcelada pendente)
                else:
                    cor_valor = "#3B82F6"  # Azul (Conta parcelada paga)
            else:
                cor_valor = "#FF4B4B"      # Vermelho (Gasto normal/fixo)
                
            c1.markdown(f"<span style='color:#F0F2F6;font-weight:500;'>{row['Nome']}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='color:#7A7F9A;font-size:0.9rem;'>{row['Mês']}</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='color:{cor_valor};font-weight:600;'>R$ {row['Valor']:,.2f}</span>", unsafe_allow_html=True)
            
            # Botão de Editar (apenas para gastos normais por enquanto)
            if tipo == "gasto":
                if c4.button("✏️", key=f"edit_{tipo}_{row['ID']}", help="Editar Gasto"):
                    modal_editar_gasto(row['ID'], row['Nome'], row['Valor'], row['Mês'], row.get('Categoria', 'Outros'))
            else:
                c4.markdown("") # Placeholder vazio para manter o layout
                
            # Botão de Excluir
            if c5.button("🗑️", key=f"del_{tipo}_{row['ID']}", help=f"Excluir '{row['Nome']}'"):
                if tipo == "gasto":
                    excluir_gasto(row["ID"])
                else:
                    excluir_conta_a_vencer(row["ID"])
                st.rerun()

    st.markdown('<p class="section-title" style="margin-top:20px;">📊 Todos os gastos por mês (Gastos + Contas)</p>', unsafe_allow_html=True)
    
    # Coletar também as contas a vencer do usuário para unificar o gráfico
    contas_usuario = listar_contas_a_vencer(usuario)
    df_contas = pd.DataFrame(contas_usuario, columns=["ID", "Descrição", "Valor", "Parcela Num", "Parcela Total", "Dia", "Mês", "Status"])
    
    # Criar um DataFrame unificado para o gráfico
    df_grafico = df.copy()
    df_grafico["Tipo"] = "Gasto Normal/Fixo"
    
    df_contas_grafico = pd.DataFrame()
    if not df_contas.empty:
        df_contas_grafico = df_contas[["Descrição", "Valor", "Mês"]].copy()
        df_contas_grafico.rename(columns={"Descrição": "Nome"}, inplace=True)
        df_contas_grafico["Tipo"] = "Conta Parcelada"
        
    df_unificado = pd.concat([df_grafico, df_contas_grafico], ignore_index=True)
    
    if not df_unificado.empty:
        # Agrupar por Mês e Tipo
        df_chart = df_unificado.groupby(["Mês", "Tipo"])["Valor"].sum().reset_index()
        
        # Manter a ordem correta dos meses
        df_chart["ordem"] = df_chart["Mês"].apply(
            lambda m: next((i for i, nome_mes in enumerate(MESES) if m.startswith(nome_mes)), 99)
        )
        df_chart = df_chart.sort_values("ordem")
        
        # Usar o Plotly Express para criar um gráfico de barras empilhadas mais vistoso
        import plotly.express as px
        
        fig = px.bar(
            df_chart, 
            x="Mês", 
            y="Valor", 
            color="Tipo", 
            barmode="stack",
            color_discrete_map={"Gasto Normal/Fixo": "#FF6B6B", "Conta Parcelada": "#FFD700"},
            labels={"Valor": "Total (R$)", "Tipo": "Categoria"}
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F0F2F6',
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Sem dados para exibir no gráfico.")

# 💵 Aba Receitas
with aba_rec:
    # ── Salário ──
    st.markdown('<p class="section-title">💼 Salário mensal</p>', unsafe_allow_html=True)
    with st.form("form_salario"):
        col1, col2 = st.columns(2)
        with col1:
            salario_desc = st.text_input("Descrição (ex: Salário empresa X)", value="Salário")
        with col2:
            salario_valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0, format="%.2f", key="val_salario")
        mes_salario = st.selectbox("Mês de referência", MESES, index=datetime.now().month - 1, key="mes_salario")
        if st.form_submit_button("💼 Registrar salário", use_container_width=True):
            if salario_valor <= 0:
                st.warning("⚠️ Informe o valor do salário.")
            else:
                mes_fmt = f"{mes_salario} {datetime.now().year}"
                adicionar_receita(salario_desc.strip() or "Salário", salario_valor, "salario", mes_fmt, usuario)
                st.success(f"✅ Salário de R$ {salario_valor:,.2f} registrado para {mes_fmt}!")
                st.rerun()

    # ── Outros recebimentos ──
    st.markdown('<p class="section-title" style="margin-top:24px;">➕ Outros recebimentos</p>', unsafe_allow_html=True)
    st.caption("Ex: Bolsa Família, pensão, bicos, freelance, aluguel recebido…")
    with st.form("form_outro_recv"):
        col1, col2 = st.columns(2)
        with col1:
            outro_desc  = st.text_input("Descrição", placeholder="Ex: Bolsa Família")
        with col2:
            outro_valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f", key="val_outro")
        mes_outro = st.selectbox("Mês de referência", MESES, index=datetime.now().month - 1, key="mes_outro")
        if st.form_submit_button("➕ Adicionar recebimento", use_container_width=True):
            if not outro_desc.strip():
                st.warning("⚠️ Informe a descrição.")
            elif outro_valor <= 0:
                st.warning("⚠️ Informe o valor.")
            else:
                mes_fmt = f"{mes_outro} {datetime.now().year}"
                adicionar_receita(outro_desc.strip(), outro_valor, "extra", mes_fmt, usuario)
                st.success(f"✅ '{outro_desc}' de R$ {outro_valor:,.2f} registrado!")
                st.rerun()

    # ── Lista de receitas ──
    st.markdown('<p class="section-title" style="margin-top:28px;">📋 Recebimentos registrados</p>', unsafe_allow_html=True)
    receitas_todas = listar_receitas_por_usuario(usuario)

    if not receitas_todas:
        st.info("ℹ️ Nenhum recebimento registrado ainda.")
    else:
        df_rec = pd.DataFrame(receitas_todas, columns=["ID", "Descrição", "Valor", "Tipo", "Mês"])

        # filtro por mês
        meses_rec = ["Todos"] + sorted(df_rec["Mês"].unique().tolist())
        filtro_mes_rec = st.selectbox("Filtrar por mês", meses_rec, key="filtro_rec")
        df_rec_exib = df_rec if filtro_mes_rec == "Todos" else df_rec[df_rec["Mês"] == filtro_mes_rec]

        # totais
        total_sal   = df_rec_exib[df_rec_exib["Tipo"] == "salario"]["Valor"].sum()
        total_extra = df_rec_exib[df_rec_exib["Tipo"] == "extra"]["Valor"].sum()
        total_rec   = total_sal + total_extra
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""
        <div class="metric-card">
          <div class="label">💼 Salário</div>
          <div class="value">R$ {total_sal:,.2f}</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
        <div class="metric-card">
          <div class="label">➕ Outros</div>
          <div class="value">R$ {total_extra:,.2f}</div>
        </div>""", unsafe_allow_html=True)
        c3.markdown(f"""
        <div class="metric-card" style="border-color:#00C89680;">
          <div class="label">💰 Total</div>
          <div class="value" style="color:#00C896;">R$ {total_rec:,.2f}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # cabeçalho da lista
        hc1, hc2, hc3, hc4, hc5 = st.columns([4, 2, 2, 2, 1])
        hc1.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>DESCRIÇÃO</span>", unsafe_allow_html=True)
        hc2.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>TIPO</span>", unsafe_allow_html=True)
        hc3.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>MÊS</span>", unsafe_allow_html=True)
        hc4.markdown("<span style='font-size:0.75rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;'>VALOR</span>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#2C3050;margin:4px 0 6px 0;'>", unsafe_allow_html=True)

        for _, row in df_rec_exib.iterrows():
            tipo_badge = (
                "<span style='background:#00C89622;color:#00C896;padding:1px 8px;border-radius:12px;font-size:0.72rem;font-weight:600;'>💼 Salário</span>"
                if row["Tipo"] == "salario" else
                "<span style='background:#7B61FF22;color:#9B81FF;padding:1px 8px;border-radius:12px;font-size:0.72rem;font-weight:600;'>➕ Extra</span>"
            )
            c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
            c1.markdown(f"<span style='color:#F0F2F6;font-weight:500;'>{row['Descrição']}</span>", unsafe_allow_html=True)
            c2.markdown(tipo_badge, unsafe_allow_html=True)
            c3.markdown(f"<span style='color:#7A7F9A;font-size:0.9rem;'>{row['Mês']}</span>", unsafe_allow_html=True)
            c4.markdown(f"<span style='color:#00C896;font-weight:600;'>R$ {row['Valor']:,.2f}</span>", unsafe_allow_html=True)
            if c5.button("🗑️", key=f"del_rec_{row['ID']}", help=f"Excluir '{row['Descrição']}'"):
                excluir_receita(row["ID"])
                st.rerun()

# � Aba Planejamento
with aba_plan:
    st.markdown('<p class="section-title">📅 Mês para analisar</p>', unsafe_allow_html=True)

    _mes_atual = f"{MESES[datetime.now().month - 1]} {datetime.now().year}"
    # pega todos os meses com dados (receitas ou gastos)
    _todos_meses_plan = sorted(
        set([r[4] for r in listar_receitas_por_usuario(usuario)] +
            [g[3] for g in listar_gastos_por_usuario(usuario)]),
        key=lambda m: (
            int(m.split()[1]) if len(m.split()) > 1 else 0,
            next((i for i, n in enumerate(MESES) if m.startswith(n)), 99)
        )
    )
    _opcoes_plan = _todos_meses_plan if _todos_meses_plan else [_mes_atual]
    _mes_idx_def = _opcoes_plan.index(_mes_atual) if _mes_atual in _opcoes_plan else len(_opcoes_plan) - 1
    mes_plan = st.selectbox("", _opcoes_plan, index=_mes_idx_def, label_visibility="collapsed", key="sel_mes_plan")

    # ── dados do mês selecionado ──
    _rec_mes   = listar_receitas_por_mes(mes_plan, usuario)
    _gast_mes  = listar_gastos_por_mes(mes_plan, usuario)
    
    # Adicionar contas a vencer (parcelas) ao planejamento
    contas_usuario = listar_contas_a_vencer(usuario)
    contas_mes = [c for c in contas_usuario if c[6] == mes_plan]
    
    _total_rec_m  = sum(r[2] for r in _rec_mes)
    _total_gast_m = sum(g[2] for g in _gast_mes) + sum(c[2] for c in contas_mes)
    _saldo_m      = _total_rec_m - _total_gast_m

    # ── cards de resumo do mês ──
    st.markdown("<br>", unsafe_allow_html=True)
    _cc1, _cc2, _cc3 = st.columns(3)
    _cc1.markdown(f"""
    <div class="metric-card">
      <div class="label">💵 Receitas em {mes_plan}</div>
      <div class="value" style="color:#00C896;">R$ {_total_rec_m:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    _cc2.markdown(f"""
    <div class="metric-card">
      <div class="label">💸 Gastos em {mes_plan}</div>
      <div class="value" style="color:#FF6B6B;">R$ {_total_gast_m:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    _saldo_cor_m = "#00C896" if _saldo_m >= 0 else "#FF4B4B"
    _cc3.markdown(f"""
    <div class="metric-card" style="border-color:{_saldo_cor_m}40;">
      <div class="label">💰 Saldo do mês</div>
      <div class="value" style="color:{_saldo_cor_m};">R$ {_saldo_m:,.2f}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── meta de economia ──
    st.markdown('<p class="section-title">🎯 Meta de economia</p>', unsafe_allow_html=True)
    meta_economia = st.number_input(
        "Quanto você quer guardar este mês? (R$)",
        min_value=0.0, step=50.0, format="%.2f", key="meta_econ"
    )

    if _total_rec_m == 0:
        st.warning("⚠️ Registre suas receitas do mês para ver o planejamento.")
    else:
        _budget_disponivel = _total_rec_m - meta_economia
        _diff_gasto        = _budget_disponivel - _total_gast_m  # positivo = sobrou, negativo = estourou
        _porc_gasto        = (_total_gast_m / _total_rec_m * 100) if _total_rec_m > 0 else 0
        _porc_economia_real = (_saldo_m / _total_rec_m * 100) if _total_rec_m > 0 else 0
        _meta_ok           = _saldo_m >= meta_economia

        # ── barra de progresso dos gastos ──
        st.markdown(f"""
        <div style="margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:0.8rem;color:#7A7F9A;">Gastos vs receita</span>
          <span style="font-size:0.85rem;font-weight:600;color:{'#FF4B4B' if _porc_gasto > 100 else '#00C896' if _porc_gasto < 70 else '#FFD700'}">{_porc_gasto:.1f}% da receita</span>
        </div>""", unsafe_allow_html=True)
        _bar_pct = min(_porc_gasto, 100)
        _bar_cor = "#FF4B4B" if _porc_gasto > 90 else "#FFD700" if _porc_gasto > 70 else "#00C896"
        st.markdown(f"""
        <div style="background:#1A1D2E;border-radius:20px;height:14px;overflow:hidden;margin-bottom:20px;">
          <div style="width:{_bar_pct:.1f}%;height:100%;background:{_bar_cor};
                      border-radius:20px;transition:width 0.4s;"></div>
        </div>""", unsafe_allow_html=True)

        if meta_economia > 0:
            # barra da meta
            _meta_pct_ating = min((_saldo_m / meta_economia * 100) if meta_economia > 0 else 0, 100)
            _meta_cor       = "#00C896" if _meta_ok else "#FF4B4B"
            st.markdown(f"""
            <div style="margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:0.8rem;color:#7A7F9A;">Meta de economia atingida</span>
              <span style="font-size:0.85rem;font-weight:600;color:{_meta_cor};">{_meta_pct_ating:.1f}%</span>
            </div>
            <div style="background:#1A1D2E;border-radius:20px;height:14px;overflow:hidden;margin-bottom:20px;">
              <div style="width:{_meta_pct_ating:.1f}%;height:100%;background:{_meta_cor};
                          border-radius:20px;"></div>
            </div>""", unsafe_allow_html=True)

        # ── análise inteligente ──
        st.markdown('<p class="section-title">🤖 Análise</p>', unsafe_allow_html=True)

        # bloco principal
        if meta_economia > 0:
            if _meta_ok:
                _icone, _bg, _bord, _txt_cor = "✅", "#1A2E26", "#00C89640", "#00C896"
                _titulo = "Você está no caminho certo!"
                _msg    = f"Guardou <b>R$ {_saldo_m:,.2f}</b> este mês, superando sua meta de <b>R$ {meta_economia:,.2f}</b>. Parabéns! 🎉"
            else:
                _icone, _bg, _bord, _txt_cor = "⚠️", "#2E1A1A", "#FF4B4B40", "#FF6B6B"
                _titulo = "Meta não atingida ainda"
                _falta  = meta_economia - _saldo_m
                _msg    = f"Faltam <b>R$ {_falta:,.2f}</b> para atingir sua meta. Você precisa reduzir os gastos ou aumentar as receitas."
        else:
            if _saldo_m >= 0:
                _icone, _bg, _bord, _txt_cor = "💡", "#1A2E26", "#00C89640", "#00C896"
                _titulo = "Saldo positivo!"
                _msg    = f"Você terminou o mês com <b>R$ {_saldo_m:,.2f}</b> sobrando. Defina uma meta acima para planejar suas economias."
            else:
                _icone, _bg, _bord, _txt_cor = "🔴", "#2E1A1A", "#FF4B4B40", "#FF4B4B"
                _titulo = "Saldo negativo!"
                _msg    = f"Você gastou <b>R$ {abs(_saldo_m):,.2f}</b> a mais do que recebeu este mês."

        st.markdown(f"""
        <div style="background:{_bg};border:1px solid {_bord};border-radius:14px;padding:18px 22px;margin-bottom:14px;">
          <div style="font-size:1rem;font-weight:700;color:{_txt_cor};margin-bottom:6px;">{_icone} {_titulo}</div>
          <div style="font-size:0.9rem;color:#C0C4D6;line-height:1.6;">{_msg}</div>
        </div>""", unsafe_allow_html=True)

        # dicas extras
        _dicas = []
        if meta_economia > 0:
            st.markdown(f"""
            <div style="background:#1A1D2E;border:1px solid #2C3050;border-radius:12px;padding:14px 18px;margin-bottom:10px;">
              <div style="font-size:0.8rem;color:#7A7F9A;font-weight:600;text-transform:uppercase;margin-bottom:10px;">📊 Números do planejamento</div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:#C0C4D6;">Receita total</span>
                <span style="color:#00C896;font-weight:600;">R$ {_total_rec_m:,.2f}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:#C0C4D6;">Meta de economia</span>
                <span style="color:#FFD700;font-weight:600;">− R$ {meta_economia:,.2f}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;border-top:1px solid #2C3050;padding-top:6px;">
                <span style="color:#C0C4D6;">Orçamento para gastar</span>
                <span style="color:{'#00C896' if _budget_disponivel >= 0 else '#FF4B4B'};font-weight:700;">R$ {_budget_disponivel:,.2f}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:#C0C4D6;">Gastos realizados</span>
                <span style="color:#FF6B6B;font-weight:600;">− R$ {_total_gast_m:,.2f}</span>
              </div>
              <div style="display:flex;justify-content:space-between;border-top:1px solid #2C3050;padding-top:6px;">
                <span style="color:#C0C4D6;">{'Margem disponível' if _diff_gasto >= 0 else 'Excesso de gastos'}</span>
                <span style="color:{'#00C896' if _diff_gasto >= 0 else '#FF4B4B'};font-weight:700;">{'R$ '+f'{_diff_gasto:,.2f}' if _diff_gasto >= 0 else '− R$ '+f'{abs(_diff_gasto):,.2f}'}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        if _porc_gasto > 90:
            _dicas.append(("💡", "Seus gastos estão acima de 90% da sua receita. Tente identificar e reduzir gastos não essenciais."))
        if _porc_economia_real > 20:
            _dicas.append(("🌟", f"Você economizou {_porc_economia_real:.1f}% da sua receita este mês. Ótimo hábito financeiro!"))
        if _total_rec_m > 0 and _total_gast_m == 0:
            _dicas.append(("📝", "Nenhum gasto registrado para este mês. Adicione seus gastos para uma análise completa."))

        for _ico, _d in _dicas:
            st.markdown(f"""
            <div style="background:#1A1D2E;border-left:3px solid #FFD700;border-radius:8px;
                        padding:10px 14px;margin-bottom:8px;font-size:0.88rem;color:#C0C4D6;">
              {_ico} {_d}
            </div>""", unsafe_allow_html=True)

# �📅 Aba Contas a Vencer
with aba3:
    st.markdown('<p class="section-title">➕ Adicionar conta a vencer</p>', unsafe_allow_html=True)

    with st.form("form_conta"):
        col1, col2 = st.columns(2)
        with col1:
            desc_conta   = st.text_input("Descrição (ex: Maria, Aluguel)")
            valor_parcela = st.number_input("Valor por parcela (R$)", min_value=0.0, step=10.0, format="%.2f")
        with col2:
            num_parcelas = st.number_input("Número de parcelas", min_value=1, max_value=360, step=1, value=1)
            dia_venc     = st.number_input("Dia de vencimento", min_value=1, max_value=31, step=1, value=10)
        mes_inicio_conta = st.selectbox("Mês da 1ª parcela", MESES, index=datetime.now().month - 1)
        enviar_conta = st.form_submit_button("📅 Adicionar conta", use_container_width=True)

        if enviar_conta:
            if not desc_conta.strip():
                st.warning("⚠️ Informe a descrição da conta.")
            elif valor_parcela <= 0:
                st.warning("⚠️ O valor da parcela deve ser maior que zero.")
            else:
                adicionar_contas_parceladas(
                    desc_conta.strip(), valor_parcela,
                    int(num_parcelas), int(dia_venc),
                    mes_inicio_conta, usuario
                )
                st.success(
                    f"✅ '{desc_conta}' adicionada! "
                    f"{int(num_parcelas)}x de R$ {valor_parcela:.2f} "
                    f"— vence todo dia {int(dia_venc)}"
                )
                st.rerun()

    # ── Lista de contas ──
    st.markdown('<p class="section-title" style="margin-top:24px;">📋 Contas cadastradas</p>', unsafe_allow_html=True)

    contas = listar_contas_a_vencer(usuario)
    hoje   = datetime.now()

    if not contas:
        st.info("ℹ️ Nenhuma conta cadastrada ainda.")
    else:
        # filtra mês
        meses_com_contas = sorted(set(c[6] for c in contas))
        # Pega o mês atual como padrão do dropdown, se houver conta nele
        _mes_atual_contas = f"{MESES[hoje.month - 1]} {hoje.year}"
        _idx_padrao_conta = meses_com_contas.index(_mes_atual_contas) + 1 if _mes_atual_contas in meses_com_contas else 0
        
        filtro_mes_conta = st.selectbox("Filtrar por mês", ["Todos"] + meses_com_contas, index=_idx_padrao_conta)

        contas_filtradas = [
            c for c in contas
            if filtro_mes_conta == "Todos" or c[6] == filtro_mes_conta
        ]
        
        # totais resumo (agora usa as contas_filtradas em vez de todas)
        total_pendente = sum(c[2] for c in contas_filtradas if c[7] == "pendente")
        total_pago     = sum(c[2] for c in contas_filtradas if c[7] == "pago")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""
        <div class="metric-card">
          <div class="label">📋 Total parcelas {'(' + filtro_mes_conta + ')' if filtro_mes_conta != 'Todos' else ''}</div>
          <div class="value">{len(contas_filtradas)}</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
        <div class="metric-card" style="border-color:#FF6B6B40;">
          <div class="label" style="color:#FF6B6B;">⏳ Pendente</div>
          <div class="value">R$ {total_pendente:,.2f}</div>
        </div>""", unsafe_allow_html=True)
        c3.markdown(f"""
        <div class="metric-card" style="border-color:#00C89640;">
          <div class="label" style="color:#00C896;">✅ Pago</div>
          <div class="value">R$ {total_pago:,.2f}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for conta in contas_filtradas:
            cid, descricao, valor, parc_num, parc_total, dia, mes_v, status = conta

            # calcula urgência
            mes_nome = mes_v.split()[0]
            ano_v    = int(mes_v.split()[1]) if len(mes_v.split()) > 1 else hoje.year
            meses_idx = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
            mes_num  = meses_idx.index(mes_nome) + 1 if mes_nome in meses_idx else hoje.month
            try:
                data_venc = datetime(ano_v, mes_num, min(dia, 28))
                dias_restantes = (data_venc - hoje).days
            except Exception:
                dias_restantes = 999

            if status == "pago":
                border = "#00C896"
                badge  = '<span style="background:#00C89622;color:#00C896;padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;">✅ Pago</span>'
            elif dias_restantes < 0:
                border = "#FF4B4B"
                badge  = f'<span style="background:#FF4B4B22;color:#FF4B4B;padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;">🔴 Vencida há {abs(dias_restantes)}d</span>'
            elif dias_restantes <= 7:
                border = "#FFD700"
                badge  = f'<span style="background:#FFD70022;color:#FFD700;padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;">⚠️ Vence em {dias_restantes}d</span>'
            else:
                border = "#2C3050"
                badge  = f'<span style="background:#1A1D2E;color:#7A7F9A;padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;">📅 {dias_restantes}d</span>'

            parcela_txt = f"Parcela {parc_num}/{parc_total}" if parc_total > 1 else "À vista"

            b1, b2, b3 = st.columns([6, 2, 1])
            with b1:
                st.markdown(f"""
                <div style="background:#1A1D2E; border-left:4px solid {border}; border-radius:8px; padding:12px 16px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                  <div>
                    <div style="font-weight:600; color:#F0F2F6; font-size:1.05rem; margin-bottom:4px;">{descricao}</div>
                    <div style="color:#7A7F9A; font-size:0.85rem;"><i class="fa-regular fa-calendar" style="margin-right:4px;"></i>Vence dia <b style="color:#C0C4D6;">{dia:02d}</b> &bull; {mes_v}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="color:{border}; font-weight:700; font-size:1.15rem; margin-bottom:4px;">R$ {valor:,.2f}</div>
                    {badge}
                  </div>
                </div>""", unsafe_allow_html=True)
                
            with b2:
                if status == "pendente":
                    if st.button("✅ Pago", key=f"pay_conta_{cid}", help="Marcar como Pago", use_container_width=True):
                        marcar_conta_status(cid, "pago")
                        st.rerun()
                elif status == "pago":
                    if st.button("⏳ Pendente", key=f"pend_conta_{cid}", help="Desfazer e marcar como Pendente", use_container_width=True):
                        marcar_conta_status(cid, "pendente")
                        st.rerun()
            with b3:
                if st.button("🗑️", key=f"del_conta_{cid}", help="Excluir Parcela", use_container_width=True):
                    excluir_conta_a_vencer(cid)
                    st.rerun()

# �🛠️ Aba de Configurações
with aba4:
    st.markdown('<p class="section-title">🧾 Gerar PDF por mês</p>', unsafe_allow_html=True)
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

    st.markdown('<p class="section-title" style="margin-top:28px;">📤 Importar Extrato Bancário (CSV)</p>', unsafe_allow_html=True)
    st.info("O arquivo CSV do seu banco deve conter pelo menos as colunas: **Data**, **Descrição** e **Valor**.")
    
    arquivo_csv = st.file_uploader("Selecione seu arquivo .csv", type=["csv"])
    
    if arquivo_csv is not None:
        try:
            # Tenta ler o CSV, usando separadores comuns no Brasil
            df_import = pd.read_csv(arquivo_csv, sep=None, engine='python', encoding='utf-8-sig')
            
            # Padroniza nomes de colunas para minúsculas
            df_import.columns = [c.strip().lower() for c in df_import.columns]
            
            # Buscar colunas equivalentes
            col_data = next((c for c in df_import.columns if 'data' in c), None)
            col_desc = next((c for c in df_import.columns if 'descri' in c or 'hist' in c or 'nome' in c), None)
            col_valor = next((c for c in df_import.columns if 'valor' in c or 'quantia' in c), None)
            
            if col_data and col_desc and col_valor:
                st.success(f"✅ Colunas identificadas automaticamente! ({col_data}, {col_desc}, {col_valor})")
                
                # Input para o mês destino
                mes_destino = st.selectbox("Em qual mês/ano deseja lançar esses gastos?", MESES, index=datetime.now().month - 1, key="mes_import_csv")
                ano_destino = st.number_input("Ano", min_value=2000, value=datetime.now().year, key="ano_import_csv")
                
                if st.button("🚀 Processar Importação", type="primary"):
                    mes_formatado = f"{mes_destino} {ano_destino}"
                    gastos_importados = 0
                    
                    for _, row in df_import.iterrows():
                        try:
                            # Converte valor para float (lidando com R$, vírgulas, etc)
                            val_str = str(row[col_valor]).replace('R$', '').replace('.', '').replace(',', '.').strip()
                            if val_str.startswith('-'): # Alguns bancos exportam gastos como negativo
                                val_str = val_str[1:]
                            
                            valor_float = float(val_str)
                            descricao_str = str(row[col_desc]).strip()
                            
                            if valor_float > 0 and descricao_str:
                                adicionar_gasto(descricao_str, valor_float, mes_formatado, usuario, "Outros")
                                gastos_importados += 1
                        except:
                            continue # Pula linhas inválidas
                            
                    st.success(f"🎉 Importação concluída! {gastos_importados} gastos adicionados.")
                    st.rerun()
            else:
                st.error("❌ Não foi possível identificar as colunas (Data, Descrição, Valor) no seu arquivo.")
                
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

    st.markdown('<p class="section-title" style="margin-top:20px;">☁️ Informações do Banco</p>', unsafe_allow_html=True)
    st.info("ℹ️ O banco de dados está hospedado no Supabase (nuvem). Não são necessárias migrações manuais.", icon="☁️")

# 👑 Aba Admin
if aba5 is not None:
    with aba5:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#2A1F00,#1A1300);
                    border:1px solid #FFD70040; border-radius:16px; padding:18px 24px;
                    margin-bottom:24px;">
          <span style="font-size:1.5rem;">&#128081;</span>
          <span style="font-size:1.2rem; font-weight:700; color:#FFD700; margin-left:10px;">Painel do Administrador</span>
          <span style="font-size:0.8rem; color:#7A7F9A; margin-left:10px;">Acesso restrito</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Stats Globais ──
        stats = stats_globais()
        st.markdown('<p class="section-title" style="color:#FFD700;border-color:#FFD700;">📊 Visão Geral do Sistema</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col, label, valor, cor in [
            (c1, "👥 Usuários",          stats["total_usuarios"],        "#00C896"),
            (c2, "📝 Registros de gastos", stats["total_registros"],        "#00C896"),
            (c3, "💰 Total em gastos",     f"R$ {stats['total_valor']:,.2f}", "#00C896"),
            (c4, "⏳ Contas pendentes",     f"R$ {stats['valor_pendente']:,.2f}", "#FF6B6B"),
        ]:
            col.markdown(f"""
            <div style="background:#1A1D2E; border:1px solid {cor}40;
                        border-radius:14px; padding:16px; text-align:center;">
              <div style="font-size:0.75rem; color:{cor}; font-weight:600;
                          text-transform:uppercase; letter-spacing:0.05em;">{label}</div>
              <div style="font-size:1.6rem; font-weight:700; color:#F0F2F6;
                          margin-top:4px;">{valor}</div>
            </div>""", unsafe_allow_html=True)

        # ── Gastos por usuário (gráfico) ──
        if stats["gastos_por_usuario"]:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p class="section-title" style="color:#FFD700;border-color:#FFD700;">📊 Gastos por Usuário</p>', unsafe_allow_html=True)
            df_gpu = pd.DataFrame(stats["gastos_por_usuario"], columns=["Usuário", "Total (R$)"])
            st.bar_chart(df_gpu.set_index("Usuário"), color="#FFD700")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gestão de Usuários ──
        st.markdown('<p class="section-title" style="color:#FFD700;border-color:#FFD700;">👥 Gestão de Usuários</p>', unsafe_allow_html=True)
        usuarios_lista = listar_usuarios()

        for email_u, is_adm in usuarios_lista:
            _dname_u = email_u.split("@")[0].capitalize()
            badge = (
                '<span style="background:#FFD70022;color:#FFD700;padding:2px 10px;'
                'border-radius:20px;font-size:0.72rem;font-weight:600;">&#11088; Admin</span>'
                if is_adm else
                '<span style="background:#1A1D2E;color:#7A7F9A;padding:2px 10px;'
                'border-radius:20px;font-size:0.72rem;">Usuário</span>'
            )
            st.markdown(f"""
            <div style="background:#1A1D2E; border:1px solid #2C3050; border-radius:12px;
                        padding:12px 18px; margin-bottom:8px;
                        display:flex; justify-content:space-between; align-items:center;">
              <div>
                <span style="font-weight:600; color:#F0F2F6;">{_dname_u}</span>
                <span style="font-size:0.78rem; color:#7A7F9A; margin-left:8px;">{email_u}</span>
              </div>
              {badge}
            </div>""", unsafe_allow_html=True)

            ca, cb, cc = st.columns([2, 2, 2])

            with ca:
                novo_adm = 0 if is_adm else 1
                label_adm = "⬇️ Remover admin" if is_adm else "⬆️ Tornar admin"
                if email_u != usuario:  # não rebaixa a si mesmo
                    if st.button(label_adm, key=f"adm_{email_u}", use_container_width=True):
                        alterar_admin(email_u, novo_adm)
                        st.success(f"Permissão de '{email_u}' atualizada.")
                        st.rerun()

            with cb:
                with st.form(f"form_senha_{email_u}"):
                    nova_senha = st.text_input("Nova senha", type="password", key=f"ns_{email_u}",
                                              label_visibility="collapsed",
                                              placeholder=f"Nova senha para {_dname_u}")
                    if st.form_submit_button("🔑 Resetar senha", use_container_width=True):
                        if nova_senha.strip():
                            resetar_senha_usuario(email_u, nova_senha.strip())
                            st.success(f"Senha de '{_dname_u}' atualizada.")
                        else:
                            st.warning("⚠️ Digite a nova senha.")

            with cc:
                if email_u != usuario:  # não exclui a si mesmo
                    with st.form(f"form_del_{email_u}"):
                        st.markdown(f"<span style='color:#FF6B6B;font-size:0.78rem;'>Excluir {_dname_u} e todos seus dados</span>",
                                    unsafe_allow_html=True)
                        confirmar = st.text_input("", placeholder=f"Digite '{email_u}' para confirmar",
                                                  key=f"conf_{email_u}", label_visibility="collapsed")
                        if st.form_submit_button("🗑️ Excluir usuário", use_container_width=True):
                            if confirmar == email_u:
                                excluir_usuario(email_u)
                                st.success(f"Usuário '{_dname_u}' excluído com sucesso.")
                                st.rerun()
                            else:
                                st.error("❌ E-mail não confere. Nenhuma ação realizada.")

            st.markdown("<hr style='border-color:#2C3050;margin:4px 0 8px 0;'>", unsafe_allow_html=True)

        # ── Todos os gastos ──
        st.markdown('<p class="section-title" style="color:#FFD700;border-color:#FFD700;margin-top:20px;">📝 Todos os Gastos</p>', unsafe_allow_html=True)
        todos_gastos = listar_todos_gastos()
        if todos_gastos:
            df_admin = pd.DataFrame(todos_gastos, columns=["ID", "Usuário", "Nome", "Valor", "Mês"])
            filtro_u = st.selectbox("Filtrar por usuário", ["Todos"] + sorted(df_admin["Usuário"].unique().tolist()))
            df_adm_exibir = df_admin if filtro_u == "Todos" else df_admin[df_admin["Usuário"] == filtro_u]
            st.dataframe(df_adm_exibir, width="stretch")
            st.download_button(
                label="📤 Exportar todos os gastos (CSV)",
                data=df_adm_exibir.to_csv(index=False).encode("utf-8"),
                file_name="todos_gastos_admin.csv",
                mime="text/csv",
            )
        else:
            st.info("ℹ️ Nenhum gasto registrado no sistema.")

        # ── Backup / Exportação ──
        st.markdown('<p class="section-title" style="color:#FFD700;border-color:#FFD700;margin-top:20px;">💾 Exportar Dados</p>', unsafe_allow_html=True)
        todos_gastos_bkp = listar_todos_gastos()
        todas_contas_bkp = listar_todas_contas()
        col_bkp1, col_bkp2 = st.columns(2)
        with col_bkp1:
            if todos_gastos_bkp:
                df_bkp = pd.DataFrame(todos_gastos_bkp, columns=["ID", "Usuário", "Nome", "Valor", "Mês"])
                st.download_button(
                    label="⬇️ Exportar todos os gastos (CSV)",
                    data=df_bkp.to_csv(index=False).encode("utf-8"),
                    file_name="backup_gastos.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with col_bkp2:
            if todas_contas_bkp:
                df_contas_bkp = pd.DataFrame(todas_contas_bkp,
                    columns=["Usuário","Descrição","Valor","Parcela","Total Parc.","Dia","Mês","Status"])
                st.download_button(
                    label="⬇️ Exportar contas a vencer (CSV)",
                    data=df_contas_bkp.to_csv(index=False).encode("utf-8"),
                    file_name="backup_contas.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
