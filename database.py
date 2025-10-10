import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            valor REAL,
            mes TEXT,
            usuario TEXT
        )
    """)
    conn.commit()
    conn.close()

def adicionar_gasto(nome, valor, mes, usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (nome, valor, mes, usuario) VALUES (?, ?, ?, ?)", (nome, valor, mes, usuario))
    conn.commit()
    conn.close()

def listar_gastos_por_usuario(usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, valor, mes FROM gastos WHERE usuario = ?", (usuario,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def listar_gastos_por_mes(mes, usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, valor, mes FROM gastos WHERE mes = ? AND usuario = ?", (mes, usuario))
    dados = cursor.fetchall()
    conn.close()
    return dados

def calcular_total_geral(usuario):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM gastos WHERE usuario = ?", (usuario,))
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def excluir_gasto(id):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def adicionar_gasto_recorrente(nome, valor, meses, mes_inicial, usuario):
    meses_ano = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    try:
        indice_inicial = meses_ano.index(mes_inicial.capitalize())
    except ValueError:
        raise Exception(f"Mês inválido: {mes_inicial}")

    ano_atual = datetime.now().year
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()

    for i in range(meses):
        indice_mes = (indice_inicial + i) % 12
        ano = ano_atual + ((indice_inicial + i) // 12)
        mes_destino = f"{meses_ano[indice_mes]} {ano}"
        cursor.execute("INSERT INTO gastos (nome, valor, mes, usuario) VALUES (?, ?, ?, ?)",
                       (f"{nome} (fixo)", valor, mes_destino, usuario))

    conn.commit()
    conn.close()
