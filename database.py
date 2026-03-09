import hashlib
import os
import uuid
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

# Carrega .env local (não faz nada se não existir)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 1. Tenta variável de ambiente (local via .env)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Tenta st.secrets (Streamlit Cloud)
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets["DATABASE_URL"]
    except Exception:
        pass

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL nao encontrada. "
        "Configure o arquivo .env (local) ou Secrets no Streamlit Cloud."
    )

DB_PATH = None


def _conn():
    return psycopg2.connect(DATABASE_URL)


def _hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def init_db():
    conn = _conn()
    cur = conn.cursor()
    # Migração: renomeia coluna 'nome' → 'email' se ainda existir
    cur.execute("""
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='usuarios' AND column_name='nome'
          ) THEN
            ALTER TABLE usuarios RENAME COLUMN nome TO email;
          END IF;
        END $$;
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email       TEXT PRIMARY KEY,
            senha_hash  TEXT NOT NULL,
            is_admin    INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id       SERIAL PRIMARY KEY,
            nome     TEXT,
            valor    REAL,
            mes      TEXT,
            usuario  TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contas_a_vencer (
            id              SERIAL PRIMARY KEY,
            grupo_id        TEXT,
            descricao       TEXT,
            valor           REAL,
            parcela_num     INTEGER,
            parcela_total   INTEGER,
            dia_vencimento  INTEGER,
            mes_vencimento  TEXT,
            status          TEXT DEFAULT 'pendente',
            usuario         TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receitas (
            id        SERIAL PRIMARY KEY,
            descricao TEXT,
            valor     REAL,
            tipo      TEXT,
            mes       TEXT,
            usuario   TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    os.makedirs(os.path.join(BASE_DIR, "pdfs"), exist_ok=True)


def usuario_existe(email: str) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM usuarios WHERE email = %s", (email,))
    existe = cur.fetchone() is not None
    cur.close(); conn.close()
    return existe


def cadastrar_usuario(email: str, senha: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total = cur.fetchone()[0]
    is_admin = 1 if total == 0 else 0
    cur.execute(
        "INSERT INTO usuarios (email, senha_hash, is_admin) VALUES (%s, %s, %s)",
        (email, _hash_senha(senha), is_admin)
    )
    conn.commit()
    cur.close(); conn.close()


def verificar_senha(email: str, senha: str) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT senha_hash FROM usuarios WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row is None:
        return False
    return row[0] == _hash_senha(senha)


def eh_admin(email: str) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM usuarios WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return bool(row and row[0])


def adicionar_gasto(nome, valor, mes, usuario):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO gastos (nome, valor, mes, usuario) VALUES (%s, %s, %s, %s)",
        (nome, valor, mes, usuario)
    )
    conn.commit()
    cur.close(); conn.close()


def listar_gastos_por_usuario(usuario):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, valor, mes FROM gastos WHERE usuario = %s", (usuario,))
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def listar_gastos_por_mes(mes, usuario):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome, valor, mes FROM gastos WHERE mes = %s AND usuario = %s",
        (mes, usuario)
    )
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def calcular_total_geral(usuario):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(valor), 0) FROM gastos WHERE usuario = %s", (usuario,))
    total = cur.fetchone()[0]
    cur.close(); conn.close()
    return total


def excluir_gasto(id):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM gastos WHERE id = %s", (id,))
    conn.commit()
    cur.close(); conn.close()


def adicionar_gasto_recorrente(nome, valor, meses, mes_inicial, usuario):
    meses_ano = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    try:
        indice_inicial = meses_ano.index(mes_inicial.capitalize())
    except ValueError:
        raise Exception(f"Mes invalido: {mes_inicial}")
    ano_atual = datetime.now().year
    conn = _conn()
    cur = conn.cursor()
    for i in range(int(meses)):
        indice_mes = (indice_inicial + i) % 12
        ano = ano_atual + ((indice_inicial + i) // 12)
        mes_destino = f"{meses_ano[indice_mes]} {ano}"
        cur.execute(
            "INSERT INTO gastos (nome, valor, mes, usuario) VALUES (%s, %s, %s, %s)",
            (f"{nome} (fixo)", valor, mes_destino, usuario)
        )
    conn.commit()
    cur.close(); conn.close()


MESES_ANO = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def adicionar_contas_parceladas(descricao, valor_parcela, num_parcelas, dia_vencimento, mes_inicio, usuario):
    try:
        indice_inicial = MESES_ANO.index(mes_inicio)
    except ValueError:
        raise Exception(f"Mes invalido: {mes_inicio}")
    grupo = str(uuid.uuid4())
    ano_atual = datetime.now().year
    conn = _conn()
    cur = conn.cursor()
    for i in range(int(num_parcelas)):
        idx_mes = (indice_inicial + i) % 12
        ano = ano_atual + (indice_inicial + i) // 12
        mes_venc = f"{MESES_ANO[idx_mes]} {ano}"
        cur.execute("""
            INSERT INTO contas_a_vencer
            (grupo_id, descricao, valor, parcela_num, parcela_total,
             dia_vencimento, mes_vencimento, status, usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendente', %s)
        """, (grupo, descricao, valor_parcela, i + 1, int(num_parcelas),
              int(dia_vencimento), mes_venc, usuario))
    conn.commit()
    cur.close(); conn.close()


def listar_contas_a_vencer(usuario):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, descricao, valor, parcela_num, parcela_total,
               dia_vencimento, mes_vencimento, status
        FROM contas_a_vencer
        WHERE usuario = %s
        ORDER BY
            CASE split_part(mes_vencimento, ' ', 1)
                WHEN 'Janeiro'   THEN 1  WHEN 'Fevereiro' THEN 2
                WHEN 'Março'     THEN 3  WHEN 'Abril'     THEN 4
                WHEN 'Maio'      THEN 5  WHEN 'Junho'     THEN 6
                WHEN 'Julho'     THEN 7  WHEN 'Agosto'    THEN 8
                WHEN 'Setembro'  THEN 9  WHEN 'Outubro'   THEN 10
                WHEN 'Novembro'  THEN 11 WHEN 'Dezembro'  THEN 12
                ELSE 99
            END,
            CAST(split_part(mes_vencimento, ' ', 2) AS INTEGER),
            dia_vencimento
    """, (usuario,))
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def marcar_conta_status(id, status):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE contas_a_vencer SET status = %s WHERE id = %s", (status, id))
    conn.commit()
    cur.close(); conn.close()


def excluir_conta_a_vencer(id):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM contas_a_vencer WHERE id = %s", (id,))
    conn.commit()
    cur.close(); conn.close()


def listar_usuarios():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT email, is_admin FROM usuarios ORDER BY is_admin DESC, email")
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def alterar_admin(email: str, is_admin: int) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET is_admin = %s WHERE email = %s", (is_admin, email))
    conn.commit()
    cur.close(); conn.close()


def resetar_senha_usuario(email: str, nova_senha: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET senha_hash = %s WHERE email = %s", (_hash_senha(nova_senha), email))
    conn.commit()
    cur.close(); conn.close()


def excluir_usuario(email: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM gastos WHERE usuario = %s", (email,))
    cur.execute("DELETE FROM contas_a_vencer WHERE usuario = %s", (email,))
    cur.execute("DELETE FROM usuarios WHERE email = %s", (email,))
    conn.commit()
    cur.close(); conn.close()


def stats_globais():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*), COALESCE(SUM(valor), 0) FROM gastos")
    total_registros, total_valor = cur.fetchone()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(valor), 0) FROM contas_a_vencer WHERE status = 'pendente'")
    total_contas_pendentes, valor_pendente = cur.fetchone()
    cur.execute("SELECT usuario, COALESCE(SUM(valor), 0) FROM gastos GROUP BY usuario ORDER BY SUM(valor) DESC")
    gastos_por_usuario = cur.fetchall()
    cur.close(); conn.close()
    return {
        "total_usuarios": total_usuarios,
        "total_registros": total_registros,
        "total_valor": total_valor,
        "total_contas_pendentes": total_contas_pendentes,
        "valor_pendente": valor_pendente,
        "gastos_por_usuario": gastos_por_usuario,
    }


def listar_todos_gastos():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, usuario, nome, valor, mes FROM gastos ORDER BY usuario, mes")
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def listar_todas_contas():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT usuario, descricao, valor, parcela_num, parcela_total,
               dia_vencimento, mes_vencimento, status
        FROM contas_a_vencer ORDER BY usuario, mes_vencimento, dia_vencimento
    """)
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


# ── Receitas ──────────────────────────────────────────────────────────────────

def adicionar_receita(descricao: str, valor: float, tipo: str, mes: str, usuario: str) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO receitas (descricao, valor, tipo, mes, usuario) VALUES (%s, %s, %s, %s, %s)",
        (descricao, valor, tipo, mes, usuario)
    )
    conn.commit()
    cur.close(); conn.close()


def listar_receitas_por_usuario(usuario: str):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, descricao, valor, tipo, mes FROM receitas WHERE usuario = %s ORDER BY mes, tipo, descricao",
        (usuario,)
    )
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def listar_receitas_por_mes(mes: str, usuario: str):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, descricao, valor, tipo, mes FROM receitas WHERE mes = %s AND usuario = %s",
        (mes, usuario)
    )
    dados = cur.fetchall()
    cur.close(); conn.close()
    return dados


def calcular_total_receitas(usuario: str) -> float:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(valor), 0) FROM receitas WHERE usuario = %s", (usuario,))
    total = cur.fetchone()[0]
    cur.close(); conn.close()
    return float(total)


def excluir_receita(id: int) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM receitas WHERE id = %s", (id,))
    conn.commit()
    cur.close(); conn.close()
